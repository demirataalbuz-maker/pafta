# -*- coding: utf-8 -*-
"""Dil koşucuları.

Her yolun track.json'ındaki "runner" alanı buradaki bir koşucuyu seçer. Bütün
koşucular aynı düzeneği (sandbox/py_harness.py) ayrı bir süreçte çalıştırır;
fark, düzeneğe hangi modla ve hangi ek bilgilerle gidildiğidir:

    python      → run / test / trace (Röntgen) / dis (Bytecode)
    regex       → kod = desen, girdi = metin; regex_run / regex_test / regex_dis (ağaç);
                  adım meta'sında motor: pcre2 → aynı modlar gerçek PCRE2'de (sandbox/pcre2_engine.py);
                  motor: dotnet / javascript → .NET ya da Node motorunda (sandbox/regex_motorlar.py)
    bash, powershell → kod bir betik dosyasına yazılır; proc_run / proc_test / proc_trace
    sql         → bellek içi SQLite; örnek veritabanı (tracks/sql/ornek.sql) + görev hazırlığı;
                  sql_run / sql_test / sql_dis (sorgu planı); adım meta'sında motor: postgres →
                  WSL'deki gerçek PostgreSQL (sandbox/pg_lab.py), pg_run / pg_test; motor: mariadb →
                  WSL'deki gerçek MariaDB (sandbox/mariadb_lab.py), my_run / my_test

Yeni dil = yeni bir Runner nesnesi + RUNNERS'a kayıt.
"""
import json
import copy
import glob
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(ROOT, "sandbox", "py_harness.py")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def argv_coz(meta):
    """Görevin meta'sındaki argv: liste ya da kabuktaki gibi tırnaklanmış metin ('"yıllık rapor.txt" notlar.txt')."""
    argv = (meta or {}).get("argv")
    if argv is None:
        return None
    if isinstance(argv, (list, tuple)):
        return [str(a) for a in argv]
    return shlex.split(str(argv))
MAX_TIMEOUT = 60


def python_exe():
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        cand = exe[:-len("pythonw.exe")] + "python.exe"
        if os.path.exists(cand):
            return cand
    return exe


def _kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
    else:
        proc.kill()


class HarnessRunner:
    """Düzeneği ayrı süreçte çalıştıran ortak taban."""
    name = "?"
    default_timeout = 6
    test_timeout = 6
    ozellik = {"roentgen": False, "dis": None}
    modlar = {}            # run/test/trace/dis → düzenek modu
    ek = {}                # her işe eklenecek alanlar

    def available(self):
        return True

    def execute(self, job, timeout=None):
        timeout = min(int(timeout or self.default_timeout), MAX_TIMEOUT)
        job = dict(self.ek, **job)
        tmp = tempfile.mkdtemp(prefix="pafta_")
        work = os.path.join(tmp, "calisma")
        os.makedirs(work)
        job_path = os.path.join(tmp, "job.json")
        res_path = os.path.join(tmp, "result.json")
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False)
        cmd = [python_exe(), "-I", "-X", "utf8", HARNESS, job_path, res_path]
        try:
            proc = subprocess.Popen(cmd, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=NO_WINDOW)
            try:
                raw_out, raw_err = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                _kill_tree(proc)
                try:
                    proc.communicate(timeout=3)
                except Exception:
                    pass
                return {"status": "timeout", "timeout": timeout,
                        "error": {"type": "Zaman aşımı", "line": None, "frames": [], "where": "kod",
                                  "msg": f"Program {timeout} saniyede bitmedi."}}
            try:
                with open(res_path, encoding="utf-8") as f:
                    res = json.load(f)
            except (OSError, ValueError):
                res = {"status": "error", "error": {
                    "type": "SüreçBitti", "line": None, "frames": [], "where": "kod",
                    "msg": "Program sonuç yazamadan süreci sonlandırdı (os._exit ya da çökme)."}}
            extra = (raw_out or b"").decode("utf-8", "replace") + (raw_err or b"").decode("utf-8", "replace")
            if extra.strip():
                res.setdefault("segs", []).append(["raw", extra])
            return res
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def run(self, code, stdin="", setup=None, timeout=None, argv=None):
        return self.execute({"mode": self.modlar["run"], "code": code, "stdin": stdin,
                             "setup": setup, "argv": argv}, timeout)

    def test(self, code, step):
        meta = step.get("meta", {})
        argv = argv_coz(meta)
        job = {"mode": self.modlar["test"], "code": code, "stdin": step.get("stdin", ""),
               "test": step.get("test", "ok(False, 'Bu görevin testi yazılmamış')"),
               "setup": step.get("setup"), "argv": argv}
        return self.execute(job, meta.get("timeout") or self.test_timeout)

    def trace(self, code, stdin="", setup=None, argv=None):
        if "trace" not in self.modlar:
            return None
        return self.execute({"mode": self.modlar["trace"], "code": code, "stdin": stdin, "setup": setup,
                             "argv": argv}, max(10, self.default_timeout))

    def dis(self, code, setup=None):
        if "dis" not in self.modlar:
            return None
        return self.execute({"mode": self.modlar["dis"], "code": code, "setup": setup}, 5)


class PythonRunner(HarnessRunner):
    name = "python"
    ozellik = {"roentgen": True, "dis": "Bytecode"}
    modlar = {"run": "run", "test": "test", "trace": "trace", "dis": "dis"}


class WslRunner(HarnessRunner):
    """Opt-in Linux Python/Bash, with the guardian owning timeout and cleanup."""
    default_timeout = 60
    test_timeout = 120

    def __init__(self, language):
        if language not in ("python", "bash"):
            raise ValueError("WSL backend yalnız Python ve Bash için tanımlı.")
        self.language = language
        self.name = language + "-wsl"
        if language == "python":
            self.modlar = dict(PythonRunner.modlar)
            self.ozellik = dict(PythonRunner.ozellik)
            self.ek = {}
        else:
            self.modlar = {"run": "proc_run", "test": "proc_test", "trace": "proc_trace"}
            self.ozellik = {"roentgen": True, "dis": None}
            self.ek = {"proc": {
                "cmd": ["/bin/bash", "--noprofile", "--norc"],
                "iz_cmd": ["/bin/bash", "--noprofile", "--norc", "-x"],
                "dosya": "betik.sh", "env": {"PS4": "+ ${LINENO}: ", "LC_ALL": "C.UTF-8"},
                "satir_deseni": r"betik\.sh: (?:line|satır) (\d+)",
                "iz_deseni": r"^(?P<derinlik>\++) (?P<satir>\d+): (?P<komut>.*)$",
            }}

    def available(self):
        from sandbox.wsl_process import available
        return available()

    def execute(self, job, timeout=None, cancel_event=None):
        from sandbox.wsl_process import execute, seconds
        timeout = seconds(timeout, self.default_timeout)
        job = dict(self.ek, **job)
        if "proc" in job:
            # The outside Linux guardian must expire first, including during
            # setup/tests and repeated calis()/run() invocations.
            job["proc"] = dict(job["proc"], sure=timeout + 2)
        return execute(job, timeout, cancel_event)

    def dis(self, code, setup=None):
        if "dis" not in self.modlar:
            return None
        return self.execute({"mode": "dis", "code": code, "setup": setup})

    def trace(self, code, stdin="", setup=None, argv=None):
        return self.execute({"mode": self.modlar["trace"], "code": code,
                             "stdin": stdin, "setup": setup, "argv": argv})

    def test(self, code, step):
        meta = step.get("meta", {})
        return self.execute({"mode": self.modlar["test"], "code": code,
                             "stdin": step.get("stdin", ""), "setup": step.get("setup"),
                             "argv": argv_coz(meta),
                             "test": step.get("test", "ok(False, 'Bu görevin testi yazılmamış')")},
                            meta.get("timeout", self.test_timeout))


def for_step(runner, step):
    """Resolve authoritative lesson/step metadata identically in every caller."""
    meta = (step or {}).get("meta", {})
    backend = meta.get("backend")
    if backend not in (None, "native", "wsl"):
        raise ValueError(f"Bilinmeyen backend: {backend!r}; native veya wsl kullanın.")
    if backend == "wsl":
        name = getattr(runner, "language", getattr(runner, "name", None))
        runner = WslRunner(name)
    elif backend == "native" and isinstance(runner, WslRunner):
        runner = RUNNERS[runner.language]
    motor = meta.get("motor")
    if motor not in (None, "python", "pcre2", "dotnet", "javascript", "sqlite", "postgres", "mariadb"):
        raise ValueError(f"Bilinmeyen motor: {motor!r}; python, pcre2, dotnet, javascript, sqlite, postgres veya mariadb kullanın.")
    if motor in ("pcre2", "dotnet", "javascript"):
        if not isinstance(runner, RegexRunner):
            raise ValueError(f"motor: {motor} yalnız regex yolunda tanımlı.")
        runner = Pcre2Runner() if motor == "pcre2" else RegexMotorRunner(motor)
    elif motor == "postgres":
        if type(runner) is not SqlRunner:
            raise ValueError("motor: postgres yalnız SQL yolunda tanımlı.")
        runner = PostgresRunner()
    elif motor == "mariadb":
        if type(runner) is not SqlRunner:
            raise ValueError("motor: mariadb yalnız SQL yolunda tanımlı.")
        runner = MariadbRunner()
    if "timeout" in meta:
        from sandbox.wsl_process import seconds
        timeout = seconds(meta["timeout"])
        runner = copy.copy(runner)
        runner.default_timeout = timeout
        runner.test_timeout = timeout
    return runner


class RegexRunner(HarnessRunner):
    name = "regex"
    ozellik = {"roentgen": False, "dis": "Ağaç"}
    modlar = {"run": "regex_run", "test": "regex_test", "dis": "regex_dis"}


class Pcre2Runner(RegexRunner):
    """Adım meta'sında motor: pcre2 → aynı regex modları, gerçek PCRE2 kitaplığında (sandbox/pcre2_engine.py)."""
    name = "regex-pcre2"
    ozellik = {"roentgen": False, "dis": "PCRE2"}
    ek = {"motor": "pcre2"}

    def available(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pafta_pcre2_engine", os.path.join(ROOT, "sandbox", "pcre2_engine.py"))
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.available()


class RegexMotorRunner(RegexRunner):
    """Adım meta'sında motor: dotnet / javascript → aynı regex modları, gerçek .NET ya da Node motorunda
    (sandbox/regex_motorlar.py; motor ayrı bir süreçte iş başına bir kez açılır)."""
    test_timeout = 30
    default_timeout = 20

    def __init__(self, motor):
        self.motor = motor
        self.name = "regex-" + motor
        self.ozellik = {"roentgen": False, "dis": {"dotnet": ".NET", "javascript": "JavaScript"}[motor]}
        self.ek = {"motor": motor}

    def available(self):
        if self.motor == "javascript":
            return bool(NODE)
        return shutil.which("powershell.exe") is not None


class DetectionRunner(HarnessRunner):
    """Sigma events / native YARA bytes, isolated like the existing runners."""
    default_timeout = 12
    test_timeout = 20

    def __init__(self, name, package):
        self.name = name
        self.package = package
        self.modlar = {"run": name + "_run", "test": name + "_test"}

    def available(self):
        import importlib.util
        local = os.path.join(ROOT, ".deps")
        return (os.path.isdir(os.path.join(local, self.package))
                or bool(glob.glob(os.path.join(local, self.package + "*.pyd")))
                or importlib.util.find_spec(self.package) is not None)


class PacketRunner(HarnessRunner):
    name = "packets"
    default_timeout = 30  # Cold WSL startup + bounded loopback capture (inner limit 20 s).
    test_timeout = 60
    modlar = {"run": "packet_run", "test": "packet_test"}

    def available(self):
        from sandbox.packet_engine import tshark_path
        from sandbox.bpf_native import available
        return bool(tshark_path() and available())


class ElasticRunner(HarnessRunner):
    """Bounded Elastic dialects; queries run in isolated native/local engines."""
    name = "elastic"
    default_timeout = 20
    test_timeout = 60
    modlar = {"run": "elastic_run", "test": "elastic_test"}

    def available(self):
        from sandbox.elastic_lucene import available
        return available()


class AdRunner(HarnessRunner):
    name = "ad"
    ozellik = {"roentgen": False, "dis": "LDAP"}
    modlar = {"run": "ad_run", "test": "ad_test", "dis": "ad_dis"}


class SqlRunner(HarnessRunner):
    name = "sql"
    ozellik = {"roentgen": False, "dis": "Plan"}
    modlar = {"run": "sql_run", "test": "sql_test", "dis": "sql_dis"}
    ek = {"tohum": os.path.join(ROOT, "tracks", "sql", "ornek.sql")}


class PostgresRunner(HarnessRunner):
    """Adım meta'sında motor: postgres → WSL'deki gerçek PostgreSQL kümesi (sandbox/pg_lab.py, py_harness pg_*).

    Her iş geçici bir veritabanı ve rollerle başlar, iş bitince hepsi silinir; SQLite'ın
    örnek veritabanı yüklenmez, tabloları görevin hazırlığı kurar."""
    name = "sql-postgres"
    ozellik = {"roentgen": False, "dis": None}
    modlar = {"run": "pg_run", "test": "pg_test"}
    default_timeout = 45
    test_timeout = 90

    def available(self):
        from sandbox.pg_lab import available
        return available()

    kapali_hatasi = "PostgreSQLKapalı"
    yok_hatasi = "PostgreSQLYok"

    def lab(self):
        from sandbox import pg_lab
        return pg_lab

    def execute(self, job, timeout=None, cancel_event=None):
        from sandbox.wsl_process import execute, seconds
        timeout = seconds(timeout, self.default_timeout)
        job = dict(self.ek, **job)
        for deneme in range(2):
            sorun = self.lab().hazirla()
            if sorun:
                return {"status": "error", "segs": [], "error": {
                    "type": self.yok_hatasi, "msg": sorun, "line": None, "frames": [], "where": "kod"}}
            res = execute(job, timeout, cancel_event)
            if (res.get("error") or {}).get("type") != self.kapali_hatasi:
                return res
        return res


class MariadbRunner(PostgresRunner):
    """Adım meta'sında motor: mariadb → WSL'deki gerçek MariaDB (sandbox/mariadb_lab.py, py_harness my_*).

    Her iş adı pafta_lab_ ile başlayan geçici bir veritabanıyla başlar, iş bitince silinir;
    SQLite'ın örnek veritabanı yüklenmez, tabloları görevin hazırlığı kurar."""
    name = "sql-mariadb"
    modlar = {"run": "my_run", "test": "my_test"}
    kapali_hatasi = "MariaDBKapalı"
    yok_hatasi = "MariaDBYok"

    def available(self):
        from sandbox.mariadb_lab import available
        return available()

    def lab(self):
        from sandbox import mariadb_lab
        return mariadb_lab


class KqlRunner(SqlRunner):
    name = "kql"
    ozellik = {"roentgen": False, "dis": "SQL"}
    modlar = {"run": "kql_run", "test": "kql_test", "dis": "kql_dis"}
    ek_veri = (os.path.join(ROOT, "tracks", "kql", "veri.sql"),)

    def execute(self, job, timeout=None):
        # SQL veritabanının üstüne günlük tabloları (istekler, gunluk, dagitimlar) eklenir
        parcalar = []
        for yol in (self.ek["tohum"],) + self.ek_veri:
            with open(yol, encoding="utf-8") as f:
                parcalar.append(f.read())
        return super().execute(dict(job, tohum_sql="\n".join(parcalar)), timeout)


class SplRunner(KqlRunner):
    name = "spl"
    ozellik = {"roentgen": False, "dis": "SQL"}
    modlar = {"run": "spl_run", "test": "spl_test", "dis": "spl_dis"}
    ek_veri = KqlRunner.ek_veri + (os.path.join(ROOT, "tracks", "spl", "veri.sql"),)   # + Splunk'ın _time alanı


class HttpRunner(PythonRunner):
    """Python; her çalıştırmadan önce sandbox/http_tezgah.py demo web uygulamasını (127.0.0.1, boş port)
    başlatır ve kullanıcı koduna `tezgah` modülünü (SUNUCU, gonder, yanit) açar."""
    name = "http"
    tezgah = os.path.join(ROOT, "sandbox", "http_tezgah.py")

    def execute(self, job, timeout=None):
        on = f"import runpy as _r\n_r.run_path({self.tezgah!r}, run_name='__tezgah__')\n"
        return super().execute(dict(job, setup=on + (job.get("setup") or "")), timeout)


def _bash_yolu():
    for aday in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if os.path.isfile(aday):
            return aday
    yol = shutil.which("bash")
    return yol if yol and "system32" not in yol.lower() else None


class ProcRunner(HarnessRunner):
    ozellik = {"roentgen": True, "dis": None}
    modlar = {"run": "proc_run", "test": "proc_test", "trace": "proc_trace"}

    def __init__(self, name, proc, default_timeout, test_timeout, kopyala=(), iz=True):
        self.name = name
        self.ek = {"proc": proc, "kopyala": [p for p in kopyala]}    # kopyala: her çalıştırmada hazır olacak veri dosyaları
        self.default_timeout = default_timeout
        self.test_timeout = test_timeout
        if not iz:                                                   # iz modu olmayan yorumlayıcı (ör. Node)
            self.ozellik = {"roentgen": False, "dis": None}
            self.modlar = {"run": "proc_run", "test": "proc_test"}

    def available(self):
        return bool(self.ek["proc"]["cmd"][0])


BASH = _bash_yolu()
NODE = shutil.which("node") or (r"C:\Program Files\nodejs\node.exe" if os.path.isfile(r"C:\Program Files\nodejs\node.exe") else None)
CMD = shutil.which("cmd.exe") if os.name == "nt" else None
# Sarmalayıcı: UTF-8 çıktı, Girdi kutusunu $Girdi dizisine okur, betiği argümanlarıyla çağırır.
PS_SARMAL = (
    "[Console]::OutputEncoding = [Text.Encoding]::UTF8\n"
    "$OutputEncoding = [Text.Encoding]::UTF8\n"
    "$__okuyucu = New-Object System.IO.StreamReader([Console]::OpenStandardInput(), (New-Object System.Text.UTF8Encoding $false))\n"
    "$global:Girdi = @(); while ($null -ne ($__satir = $__okuyucu.ReadLine())) { $global:Girdi += $__satir }\n"
    "$global:LASTEXITCODE = 0\n"
    "{IZ}& \"$PSScriptRoot\\betik.ps1\" @args\n"
    "exit $LASTEXITCODE\n"
)

RUNNERS = {
    "python": PythonRunner(),
    "python-wsl": WslRunner("python"),
    "bash-wsl": WslRunner("bash"),
    "http": HttpRunner(),
    "regex": RegexRunner(),
    "sql": SqlRunner(),
    "kql": KqlRunner(),
    "spl": SplRunner(),
    "sigma": DetectionRunner("sigma", "sigma"),
    "yara": DetectionRunner("yara", "yara"),
    "packets": PacketRunner(),
    "elastic": ElasticRunner(),
    "ad": AdRunner(),
    "bash": ProcRunner("bash", {
        "cmd": [BASH or ""], "iz_cmd": [BASH or "", "-x"], "dosya": "betik.sh",
        "env": {"PS4": "+ ${LINENO}: ", "LC_ALL": "C.UTF-8"}, "sure": 10,
        "satir_deseni": r"betik\.sh: (?:line|satır) (\d+)",
        "iz_deseni": r"^(?P<derinlik>\++) (?P<satir>\d+): (?P<komut>.*)$",
    }, default_timeout=15, test_timeout=30),
    "powershell": ProcRunner("powershell", {
        "cmd": ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File"],
        "dosya": "betik.ps1", "bom": True, "sarmal": PS_SARMAL, "sarmal_dosya": "_pafta.ps1",
        "iz_satiri": "Set-PSDebug -Trace 1; ", "iz_disla": ["betik.ps1", "LASTEXITCODE"],
        "sure": 20, "satir_deseni": r"betik\.ps1:(\d+)",
        "iz_deseni": r"^DEBUG:\s+(?P<satir>\d+)\+\s*(?P<komut>.*)$",
        # Proje kapsamında sabitlenen modüller (Pester 5.9.0) önce aransın: .deps\psmodules
        "env": {"PSModulePath": os.path.join(ROOT, ".deps", "psmodules") + os.pathsep + os.environ.get("PSModulePath", "")},
    }, default_timeout=25, test_timeout=50,
        kopyala=[os.path.join(ROOT, "tracks", "powershell", "veri", "olaylar.json")]),
    "javascript": ProcRunner("javascript", {
        "cmd": [NODE or ""], "dosya": "betik.js", "sure": 10,
        # Proje kapsamında sabitlenen npm paketleri (Express 5.3.0): tools/js_bagimlilik_kur.py
        "env": {"NODE_PATH": os.path.join(ROOT, ".deps", "npm", "node_modules")},
        "satir_deseni": r"betik\.js:(\d+)",
    }, default_timeout=15, test_timeout=30, iz=False),
    "cmd": ProcRunner("cmd", {
        "cmd": [CMD or "", "/d", "/q", "/e:on", "/v:off", "/c"],
        "dosya": "betik.cmd", "batch": True, "sure": 10,
        # Sürümü doğrulanmış Sysinternals araçları (sigcheck64, autorunsc64): tools/sysinternals_kur.ps1
        "env": {"PATH": os.path.join(ROOT, ".deps", "sysinternals") + os.pathsep + os.environ.get("PATH", "")},
    }, default_timeout=15, test_timeout=35, iz=False,
        kopyala=[os.path.join(ROOT, "sandbox", "evtx_fixtures.py")]),
}


def get(name):
    return RUNNERS.get(name)
