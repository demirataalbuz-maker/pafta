# -*- coding: utf-8 -*-
"""Dil koşucuları.

Her yolun track.json'ındaki "runner" alanı buradaki bir koşucuyu seçer. Bütün
koşucular aynı düzeneği (sandbox/py_harness.py) ayrı bir süreçte çalıştırır;
fark, düzeneğe hangi modla ve hangi ek bilgilerle gidildiğidir:

    python      → run / test / trace (Röntgen) / dis (Bytecode)
    regex       → kod = desen, girdi = metin; regex_run / regex_test / regex_dis (ağaç)
    bash, powershell → kod bir betik dosyasına yazılır; proc_run / proc_test / proc_trace
    sql         → bellek içi SQLite; örnek veritabanı (tracks/sql/ornek.sql) + görev hazırlığı;
                  sql_run / sql_test / sql_dis (sorgu planı)

Yeni dil = yeni bir Runner nesnesi + RUNNERS'a kayıt.
"""
import json
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


class RegexRunner(HarnessRunner):
    name = "regex"
    ozellik = {"roentgen": False, "dis": "Ağaç"}
    modlar = {"run": "regex_run", "test": "regex_test", "dis": "regex_dis"}


class SqlRunner(HarnessRunner):
    name = "sql"
    ozellik = {"roentgen": False, "dis": "Plan"}
    modlar = {"run": "sql_run", "test": "sql_test", "dis": "sql_dis"}
    ek = {"tohum": os.path.join(ROOT, "tracks", "sql", "ornek.sql")}


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
    "regex": RegexRunner(),
    "sql": SqlRunner(),
    "kql": KqlRunner(),
    "spl": SplRunner(),
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
    }, default_timeout=25, test_timeout=50,
        kopyala=[os.path.join(ROOT, "tracks", "powershell", "veri", "olaylar.json")]),
    "javascript": ProcRunner("javascript", {
        "cmd": [NODE or ""], "dosya": "betik.js", "sure": 10,
        "satir_deseni": r"betik\.js:(\d+)",
    }, default_timeout=15, test_timeout=30, iz=False),
}


def get(name):
    return RUNNERS.get(name)
