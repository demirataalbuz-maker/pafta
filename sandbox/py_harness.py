# -*- coding: utf-8 -*-
"""Pafta · Python koşum düzeneği.

Ayrı bir süreçte `python -I -X utf8 py_harness.py job.json result.json` olarak
çalışır. Kullanıcının kodunu yakalanmış stdin/stdout ile yürütür; moda göre
testleri koşar, adım adım iz (Röntgen) çıkarır ya da bytecode döker. Sonucu
result.json'a yazar ve os._exit ile çıkar: kullanıcının açık bıraktığı thread'ler
süreci asılı tutmasın.
"""
import ast
import builtins
import contextlib
import difflib
import dis
import io
import json
import linecache
import os
import re
import reprlib
import sqlite3
import subprocess
import sys
import traceback
import types

FNAME = "<kod>"
TEST_FNAME = "<test>"
OUT_LIMIT = 200_000
SHORT_LIMIT = 300
TRACE_LIMIT = 500
VARS_PER_FRAME = 40


# ── çıktı yakalama ────────────────────────────────────────────────────────────

class Capture:
    """stdout / stderr / girdi yankısını tür etiketli parçalar halinde toplar."""

    def __init__(self):
        self.segs = []
        self.size = 0
        self.truncated = False

    def add(self, kind, s):
        if not s or self.truncated:
            return
        room = OUT_LIMIT - self.size
        if len(s) > room:
            s = s[:room]
            self.truncated = True
        self.size += len(s)
        if self.segs and self.segs[-1][0] == kind:
            self.segs[-1][1] += s
        else:
            self.segs.append([kind, s])

    def text(self, kinds=("out",)):
        return "".join(t for k, t in self.segs if k in kinds)

    def plain(self):
        return "".join(t for _, t in self.segs)


class Stream(io.TextIOBase):
    def __init__(self, cap, kind):
        super().__init__()
        self._cap, self._kind = cap, kind

    def writable(self):
        return True

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError(f"write() argümanı str olmalı, {type(s).__name__} geldi")
        self._cap.add(self._kind, s)
        return len(s)

    def flush(self):
        pass

    @property
    def encoding(self):
        return "utf-8"


class Feeder:
    """input() ve sys.stdin için hazır girdi metni."""

    def __init__(self, text, cap, echo):
        self.buf = io.StringIO(text or "")
        self.cap, self.echo = cap, echo

    def input(self, prompt=""):
        # Test modunda (echo=False) soru metni çıktıya yazılmaz: testler
        # input("Sayı: ") ile input() arasında fark görmesin.
        prompt = str(prompt)
        if prompt and self.echo:
            self.cap.add("out", prompt)
        line = self.buf.readline()
        if not line:
            raise EOFError("input() girdi bekledi ama Girdi kutusunda okunacak satır kalmadı")
        if line.endswith("\n"):
            line = line[:-1]
        if line.endswith("\r"):
            line = line[:-1]
        if self.echo:
            self.cap.add("in", line + "\n")
        return line


class Redirect:
    def __init__(self, cap, feeder, argv=None):
        self.cap, self.feeder, self.argv = cap, feeder, argv

    def __enter__(self):
        self.saved = (sys.stdout, sys.stderr, sys.stdin, builtins.input, sys.argv)
        sys.stdout = Stream(self.cap, "out")
        sys.stderr = Stream(self.cap, "err")
        sys.stdin = self.feeder.buf
        builtins.input = self.feeder.input
        sys.argv = ["kod.py"] + list(self.argv or [])
        return self

    def __exit__(self, *exc):
        sys.stdout, sys.stderr, sys.stdin, builtins.input, sys.argv = self.saved
        return False


# ── hata bilgisi ──────────────────────────────────────────────────────────────

def _suggest(e, ns):
    try:
        if isinstance(e, NameError) and getattr(e, "name", None):
            pool = [k for k in ns if not k.startswith("__")] + dir(builtins)
            m = difflib.get_close_matches(e.name, pool, n=1, cutoff=0.7)
            return m[0] if m else None
        if isinstance(e, AttributeError) and getattr(e, "name", None):
            obj = getattr(e, "obj", None)
            if obj is not None:
                pool = [a for a in dir(obj) if not a.startswith("__")]
                m = difflib.get_close_matches(e.name, pool, n=1, cutoff=0.7)
                return m[0] if m else None
    except Exception:
        pass
    return None


def err_info(e, ns=None, where="kod"):
    if isinstance(e, SyntaxError):
        return {
            "type": type(e).__name__, "msg": e.msg, "line": e.lineno, "col": e.offset,
            "text": (e.text or "").rstrip("\n"), "frames": [],
            "where": "test" if e.filename == TEST_FNAME else where,
        }
    tb = traceback.extract_tb(e.__traceback__)
    frames = [{"line": f.lineno, "func": f.name, "text": (f.line or "").strip()}
              for f in tb if f.filename == FNAME]
    info = {
        "type": type(e).__name__, "msg": str(e), "frames": frames,
        "line": frames[-1]["line"] if frames else None, "where": where,
    }
    s = _suggest(e, ns or {})
    if s:
        info["suggest"] = s
    return info


def short(v):
    try:
        r = repr(v)
    except Exception as e:  # kullanıcının __repr__'ı patlayabilir
        r = f"<repr hatası: {type(e).__name__}>"
    return r if len(r) <= SHORT_LIMIT else r[:SHORT_LIMIT] + "…"


# ── kullanıcı kodunu yürütme ──────────────────────────────────────────────────

def register_source(code):
    linecache.cache[FNAME] = (len(code), None, code.splitlines(True), FNAME)


def exec_user(code, stdin="", echo=False, argv=None):
    cap = Capture()
    feeder = Feeder(stdin, cap, echo)
    ns = {"__name__": "__main__", "__builtins__": builtins, "__file__": "kod.py"}
    err = None
    with Redirect(cap, feeder, argv):
        try:
            exec(compile(code, FNAME, "exec"), ns)
        except SystemExit as e:
            if e.code not in (None, 0):
                cap.add("err", f"[program sys.exit({e.code!r}) ile bitti]\n")
        except BaseException as e:
            err = err_info(e, ns)
    return ns, cap, err


def run_setup(job):
    # Yolun ortak veri dosyaları (ör. PowerShell'in olaylar.json'u) her çalıştırmada klasöre kopyalanır
    for yol in job.get("kopyala") or []:
        if os.path.isfile(yol):
            with open(yol, "rb") as kaynak, open(os.path.basename(yol), "wb") as hedef:
                hedef.write(kaynak.read())
    setup = job.get("setup")
    if not setup:
        return
    sink = Capture()
    with Redirect(sink, Feeder("", sink, False)):
        exec(compile(setup, "<setup>", "exec"), {"__name__": "__setup__"})


def do_run(job):
    run_setup(job)
    _, cap, err = exec_user(job["code"], job.get("stdin", ""), echo=True, argv=job.get("argv"))
    return {"status": "error" if err else "ok", "segs": cap.segs,
            "truncated": cap.truncated, "error": err}


# ── test modu ─────────────────────────────────────────────────────────────────

class Stop(Exception):
    """Test erken bitsin (ön koşul sağlanmadı)."""


class UserRunError(Exception):
    def __init__(self, info, stdin):
        super().__init__(info.get("msg", ""))
        self.info, self.stdin = info, stdin


KINDS = {
    "for": ast.For, "while": ast.While, "if": ast.If, "def": ast.FunctionDef,
    "class": ast.ClassDef, "lambda": ast.Lambda, "listcomp": ast.ListComp,
    "dictcomp": ast.DictComp, "setcomp": ast.SetComp, "genexp": ast.GeneratorExp,
    "yield": (ast.Yield, ast.YieldFrom), "yieldfrom": ast.YieldFrom, "with": ast.With,
    "try": tuple(t for t in (ast.Try, getattr(ast, "TryStar", None)) if t),
    "fstring": ast.JoinedStr, "match": ast.Match, "asyncdef": ast.AsyncFunctionDef,
    "await": ast.Await, "asyncfor": ast.AsyncFor, "asyncwith": ast.AsyncWith,
    "return": ast.Return, "global": ast.Global, "nonlocal": ast.Nonlocal,
    "break": ast.Break, "continue": ast.Continue, "ifexp": ast.IfExp,
    "raise": ast.Raise, "assert": ast.Assert, "import": (ast.Import, ast.ImportFrom),
    "walrus": ast.NamedExpr, "slice": ast.Slice, "starred": ast.Starred,
    "augassign": ast.AugAssign, "comp": (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp),
}


def _same(got, exp):
    """== eşitliği + makul tür uyumu: 1 ile True, '5' ile 5 karışmasın."""
    try:
        if not bool(got == exp):
            return False
    except Exception:
        return False
    if isinstance(exp, bool) or isinstance(got, bool):
        return isinstance(got, bool) and isinstance(exp, bool)
    if isinstance(exp, (int, float)) and isinstance(got, (int, float)):
        return True
    return isinstance(got, type(exp))


class Tester:
    def __init__(self, code, ns, cap, stdin, job):
        self.code, self.ns, self.cap, self.stdin, self.job = code, ns, cap, stdin, job
        self.results = []
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = ast.parse("")

    def _rec(self, ok, msg, got=None, exp=None):
        r = {"ok": bool(ok), "msg": msg or "Koşul"}
        if not ok:
            if got is not None:
                r["got"] = got
            if exp is not None:
                r["exp"] = exp
        self.results.append(r)
        return bool(ok)

    # — karşılaştırmalar —
    def eq(self, got, exp, msg=None):
        return self._rec(_same(got, exp), msg or f"Beklenen: {short(exp)}", short(got), short(exp))

    def ok(self, cond, msg=None, got=None):
        return self._rec(bool(cond), msg, None if got is None else short(got))

    def yakin(self, got, exp, msg=None, tol=1e-6):
        try:
            same = abs(got - exp) <= tol
        except Exception:
            same = False
        return self._rec(same, msg or f"≈ {exp!r}", short(got), short(exp))

    def raises(self, exc, fn, *a, msg=None, **kw):
        try:
            fn(*a, **kw)
        except exc:
            return self._rec(True, msg or f"{exc.__name__} yükseltmeli")
        except Exception as e:
            return self._rec(False, msg or f"{exc.__name__} yükseltmeli",
                             f"{type(e).__name__}: {e}", exc.__name__)
        return self._rec(False, msg or f"{exc.__name__} yükseltmeli", "hata yükselmedi", exc.__name__)

    # — program düzeyi —
    def run(self, stdin="", argv=None):
        _, cap, err = exec_user(self.code, stdin, echo=False, argv=argv)
        if err:
            raise UserRunError(err, stdin)
        return cap.text()

    def run_code(self, code, stdin="", argv=None):
        """Kullanıcının kodunun değiştirilmiş bir halini çalıştır (ör. sabit değeri başka değerle)."""
        _, cap, err = exec_user(code, stdin, echo=False, argv=argv)
        if err:
            raise UserRunError(err, stdin)
        return cap.text()

    def capture(self, fn, *a, **kw):
        cap = Capture()
        with Redirect(cap, Feeder("", cap, False)):
            res = fn(*a, **kw)
        return res, cap.text()

    # — kaynak analizi —
    def uses(self, kind):
        if kind == "decorator":
            return any(getattr(n, "decorator_list", None) for n in ast.walk(self.tree))
        t = KINDS[kind]
        return any(isinstance(n, t) for n in ast.walk(self.tree))

    def calls(self, name):
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Call):
                f = n.func
                if (isinstance(f, ast.Name) and f.id == name) or (isinstance(f, ast.Attribute) and f.attr == name):
                    return True
        return False

    def need(self, name, what="fonksiyon"):
        obj = self.ns.get(name)
        if obj is None or (what == "fonksiyon" and not callable(obj)):
            self._rec(False, f"`{name}` adında bir {what} tanımlamalısın",
                      "bulunamadı", name)
            raise Stop()
        if what == "sınıf" and not isinstance(obj, type):
            self._rec(False, f"`{name}` bir sınıf (class) olmalı", type(obj).__name__, "class")
            raise Stop()
        return obj

    def stop(self):
        raise Stop()

    def namespace(self):
        out = self.cap.text()
        tns = dict(self.ns)
        tns.update(
            eq=self.eq, ok=self.ok, yakin=self.yakin, raises=self.raises, run=self.run,
            run_code=self.run_code,
            capture=self.capture, uses=self.uses, calls=self.calls, need=self.need,
            stop=self.stop, out=out, lines=[l.rstrip() for l in out.strip("\n").splitlines()],
            src=self.code, tree=self.tree, kullanici=self.ns, girdi=self.stdin,
            __name__="__test__", __builtins__=builtins,
        )
        return tns


def test_error(e, tns):
    if isinstance(e, UserRunError):
        info = dict(e.info)
        info["where"] = "kod-girdi"
        info["stdin"] = e.stdin
        return info
    tb = traceback.extract_tb(e.__traceback__)
    in_user = any(f.filename == FNAME for f in tb)
    if in_user:
        return err_info(e, tns, where="kod-test")
    info = err_info(e, tns, where="test")
    if isinstance(e, NameError) and getattr(e, "name", None):
        info["missing"] = e.name
    return info


def do_test(job):
    run_setup(job)
    code, stdin = job["code"], job.get("stdin", "")
    ns, cap, err = exec_user(code, stdin, echo=False, argv=job.get("argv"))
    if err:
        return {"status": "error", "segs": cap.segs, "error": err, "checks": []}
    tester = Tester(code, ns, cap, stdin, job)
    tns = tester.namespace()
    return _test_kos(tester, tns, job, cap.segs)


def _test_kos(tester, tns, job, segs):
    """Görev testini (Python) verilen ad alanında koş ve sonucu paketle."""
    tcap = Capture()
    exc = None
    with Redirect(tcap, Feeder(job.get("stdin", ""), tcap, False)):
        try:
            exec(compile(job["test"], TEST_FNAME, "exec"), tns)
        except Stop:
            pass
        except AssertionError as e:
            tester._rec(False, str(e) or "Bir test koşulu sağlanmadı")
        except BaseException as e:
            exc = test_error(e, tns)
    passed = exc is None and bool(tester.results) and all(r["ok"] for r in tester.results)
    return {"status": "pass" if passed else "fail", "checks": tester.results,
            "segs": segs, "error": exc}


# ── Röntgen: adım adım iz ─────────────────────────────────────────────────────

_rep = reprlib.Repr()
_rep.maxlevel, _rep.maxlist, _rep.maxtuple, _rep.maxset = 3, 12, 12, 12
_rep.maxdict, _rep.maxstring, _rep.maxother, _rep.maxlong = 10, 70, 90, 60
_rep.maxfrozenset, _rep.maxdeque, _rep.maxarray = 12, 12, 12


def ser(v):
    t = type(v)
    if isinstance(v, types.FunctionType):
        r = f"<fonksiyon {v.__name__}>"
    elif isinstance(v, type):
        r = f"<sınıf {v.__name__}>"
    elif isinstance(v, types.MethodType):
        r = f"<metot {v.__func__.__name__}>"
    else:
        try:
            r = _rep.repr(v)
        except Exception as e:
            r = f"<repr hatası: {type(e).__name__}>"
    if len(r) > 160:
        r = r[:160] + "…"
    return {"t": t.__name__, "r": r, "id": id(v)}


def _vars(d):
    out = []
    for k, v in d.items():
        if k.startswith("__") or isinstance(v, types.ModuleType):
            continue
        out.append([k, ser(v)])
        if len(out) >= VARS_PER_FRAME:
            break
    return out


def do_trace(job):
    run_setup(job)
    code = job["code"]
    try:
        compiled = compile(code, FNAME, "exec")
    except SyntaxError as e:
        return {"status": "error", "error": err_info(e), "steps": [], "out": ""}
    cap = Capture()
    feeder = Feeder(job.get("stdin", ""), cap, True)
    ns = {"__name__": "__main__", "__builtins__": builtins, "__file__": "kod.py"}
    steps = []
    state = {"over": False}

    def record(frame, event, arg):
        if len(steps) >= TRACE_LIMIT:
            state["over"] = True
            sys.settrace(None)
            return
        chain, f = [], frame
        while f is not None:
            if f.f_code.co_filename == FNAME:
                chain.append(f)
            f = f.f_back
        chain.reverse()
        frames = []
        for fr in chain:
            local = fr.f_globals if fr.f_code.co_name == "<module>" else fr.f_locals
            frames.append({"name": fr.f_code.co_name, "line": fr.f_lineno, "vars": _vars(local)})
        step = {"ev": event, "line": frame.f_lineno, "frames": frames, "out": cap.size}
        if event == "return":
            step["ret"] = ser(arg)
        elif event == "exception":
            step["exc"] = f"{arg[0].__name__}: {arg[1]}"
        steps.append(step)

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FNAME:
            return None
        if event in ("line", "return", "exception"):
            record(frame, event, arg)
        return tracer

    err = None
    with Redirect(cap, feeder):
        sys.settrace(tracer)
        try:
            exec(compiled, ns)
        except SystemExit:
            pass
        except BaseException as e:
            err = err_info(e, ns)
        finally:
            sys.settrace(None)
    return {"status": "error" if err else "ok", "steps": steps, "truncated": state["over"],
            "out": cap.plain(), "error": err}


def do_dis(job):
    buf = io.StringIO()
    try:
        dis.dis(compile(job["code"], FNAME, "exec"), file=buf)
    except SyntaxError as e:
        return {"status": "error", "error": err_info(e), "text": ""}
    return {"status": "ok", "text": buf.getvalue()}


# ── Regex yolu: kod = desen, girdi = aranacak metin ───────────────────────────

def _desen(code):
    return (code or "").rstrip("\r\n")


def _regex_derle(desen):
    try:
        return re.compile(desen), None
    except re.error as e:
        satir = e.lineno or 1
        return None, {"type": "DesenHatası", "msg": e.msg, "line": satir,
                      "col": e.colno if e.colno is not None else e.pos, "frames": [], "where": "kod",
                      "text": (desen.splitlines() or [""])[min(satir, max(1, len(desen.splitlines()))) - 1]}


def do_regex_run(job):
    rx, err = _regex_derle(_desen(job["code"]))
    if err:
        return {"status": "error", "error": err, "segs": []}
    metin = job.get("stdin", "")
    es = []
    for m in rx.finditer(metin):
        es.append({"bas": m.start(), "son": m.end(), "metin": m.group(0),
                   "gruplar": list(m.groups()), "adli": m.groupdict()})
        if len(es) >= 500:
            break
    cikti = "".join(e["metin"] + "\n" for e in es)
    return {"status": "ok", "segs": [["out", cikti]] if cikti else [], "eslesmeler": es,
            "metin": metin[:50_000], "error": None}


def do_regex_test(job):
    desen = _desen(job["code"])
    rx, err = _regex_derle(desen)
    if err:
        return {"status": "error", "error": err, "checks": [], "segs": []}
    tester = Tester("", {}, Capture(), job.get("stdin", ""), job)
    tns = tester.namespace()

    def ilk(s):
        return rx.search(s)

    tns.update(
        desen=desen, src=desen, rx=rx,
        eslesir=lambda s: rx.search(s) is not None,
        tam=lambda s: rx.fullmatch(s) is not None,
        bul=lambda s: [m.group(0) for m in rx.finditer(s)],
        grup=lambda s, i=1: (ilk(s).group(i) if ilk(s) else None),
        gruplar=lambda s: (ilk(s).groups() if ilk(s) else None),
        adli=lambda s: (ilk(s).groupdict() if ilk(s) else None),
        hepsi=lambda s: [m.groupdict() or m.groups() for m in rx.finditer(s)],
        degistir=lambda s, yeni, n=0: rx.sub(yeni, s, count=n),
        bol=lambda s: rx.split(s),
    )
    return _test_kos(tester, tns, job, [])


def do_regex_dis(job):
    desen = _desen(job["code"])
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            re.compile(desen, re.DEBUG)
    except re.error:
        return {"status": "error", "error": _regex_derle(desen)[1], "text": ""}
    return {"status": "ok", "text": buf.getvalue()}


# ── Süreç yolları (Bash, PowerShell): kod bir betik dosyasına yazılıp çalışır ──

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _betik_yaz(job):
    p = job["proc"]
    on_ek = p.get("on_ek", "")
    with open(p["dosya"], "w", encoding="utf-8-sig" if p.get("bom") else "utf-8", newline="\n") as f:
        f.write(on_ek + (job.get("code") or "").replace("\r\n", "\n"))
    return on_ek.count("\n")


def _calistir(job, stdin="", argv=None, iz=False):
    """(kod, stdout, stderr, kayma) ya da zaman aşımında None."""
    p = job["proc"]
    kayma = _betik_yaz(job)
    hedef = p["dosya"]
    if p.get("sarmal"):
        # Hazırlık (kodlama, Girdi) betiğin içine değil ayrı bir sarmalayıcıya yazılır:
        # böylece param() ilk ifade kalır ve hata satır numaraları kaymaz.
        sarmal = p["sarmal"].replace("{IZ}", p.get("iz_satiri", "") if iz else "")
        with open(p["sarmal_dosya"], "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(sarmal)
        hedef = p["sarmal_dosya"]
    cmd = list(p["iz_cmd"] if iz and p.get("iz_cmd") else p["cmd"]) + [hedef] + [str(a) for a in (argv or [])]
    env = dict(os.environ)
    env.update(p.get("env", {}))
    try:
        r = subprocess.run(cmd, input=(stdin or "").encode("utf-8"), capture_output=True,
                           timeout=p.get("sure", 15), env=env, creationflags=NO_WINDOW)
    except subprocess.TimeoutExpired:
        return None
    return (r.returncode, r.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
            r.stderr.decode("utf-8", "replace").replace("\r\n", "\n"), kayma)


def _hata_satiri(job, metin, kayma):
    desen = job["proc"].get("satir_deseni")
    if not desen:
        return None
    m = re.search(desen, metin)
    if not m:
        return None
    n = int(m.group(1)) - kayma
    return n if n >= 1 else None


def _surec_hatasi(job, kod, hata, kayma):
    son = [s for s in hata.splitlines() if s.strip()]
    return {"type": "ÇıkışKodu", "msg": f"betik {kod} koduyla bitti" + (f": {son[0].strip()}" if son else ""),
            "line": _hata_satiri(job, hata, kayma), "frames": [], "where": "kod", "kod": kod}


def _zaman_asimi(job):
    return {"type": "Zaman aşımı", "msg": f"Betik {job['proc'].get('sure', 15)} saniyede bitmedi.",
            "line": None, "frames": [], "where": "kod"}


def do_proc_run(job):
    run_setup(job)
    r = _calistir(job, job.get("stdin", ""), job.get("argv"))
    if r is None:
        return {"status": "timeout", "segs": [], "error": _zaman_asimi(job)}
    kod, cikti, hata, kayma = r
    segs = [["out", cikti]] if cikti else []
    if hata:
        segs.append(["err", hata])
    err = _surec_hatasi(job, kod, hata, kayma) if kod != 0 else None
    res = {"status": "error" if err else "ok", "segs": segs, "error": err, "kod": kod}
    if not err and hata:
        res["uyari_satir"] = _hata_satiri(job, hata, kayma)
    return res


def do_proc_trace(job):
    run_setup(job)
    r = _calistir(job, job.get("stdin", ""), job.get("argv"), iz=True)
    if r is None:
        return {"status": "timeout", "steps": [], "error": _zaman_asimi(job)}
    kod, cikti, hata, kayma = r
    desen = re.compile(job["proc"]["iz_deseni"])
    disla = job["proc"].get("iz_disla", [])
    adimlar, temiz = [], []
    for kaynak, metin in (("out", cikti), ("err", hata)):
        for satir in metin.splitlines():
            m = desen.match(satir)
            if m and any(d in satir for d in disla):
                continue
            if m:
                n = int(m.group("satir")) - kayma
                if n >= 1:
                    adimlar.append({"line": n, "metin": m.group("komut").replace(">>>>", "").strip(),
                                    "derinlik": len(m.groupdict().get("derinlik") or "+")})
            elif kaynak == "out":
                temiz.append(satir)
    hata_temiz = "\n".join(s for s in hata.splitlines() if not desen.match(s))
    err = _surec_hatasi(job, kod, hata_temiz, kayma) if kod != 0 else None
    return {"status": "error" if err else "ok", "kind": "iz", "iz": adimlar[:TRACE_LIMIT],
            "out": "\n".join(temiz) + ("\n" if temiz else ""), "error": err}


class ProcTester(Tester):
    def __init__(self, job, cikti):
        super().__init__("", {}, Capture(), job.get("stdin", ""), job)
        self.cap.add("out", cikti)
        self.code = job.get("code", "")

    def calis(self, stdin="", argv=None):
        r = _calistir(self.job, stdin, argv)
        if r is None:
            raise TimeoutError("betik zaman aşımına uğradı")
        return {"kod": r[0], "cikti": r[1], "hata": r[2]}

    def run(self, stdin="", argv=None):
        r = self.calis(stdin, argv)
        if r["kod"] != 0:
            raise UserRunError(_surec_hatasi(self.job, r["kod"], r["hata"], 0), stdin)
        return r["cikti"]


def do_proc_test(job):
    run_setup(job)
    r = _calistir(job, job.get("stdin", ""), job.get("argv"))
    if r is None:
        return {"status": "timeout", "checks": [], "segs": [], "error": _zaman_asimi(job)}
    kod, cikti, hata, kayma = r
    segs = [["out", cikti]] if cikti else []
    if hata:
        segs.append(["err", hata])
    if kod != 0:
        return {"status": "error", "checks": [], "segs": segs, "error": _surec_hatasi(job, kod, hata, kayma)}
    tester = ProcTester(job, cikti)
    tns = tester.namespace()
    tns.update(calis=tester.calis, run=tester.run, src=job.get("code", ""), hata_cikti=hata)
    return _test_kos(tester, tns, job, segs)


# ── SQL yolu: bellek içi SQLite; örnek veritabanı + görevin hazırlığı + kullanıcının betiği ──

SQL_SATIR_LIMIT = 500
_SQL_BASI = re.compile(r"(?:\s+|--[^\n]*(?:\n|$)|/\*.*?\*/)*", re.S)
_SQL_HATA_TR = [
    (r"no such table: (\S+)", "böyle bir tablo yok: {0}"),
    (r"no such column: (\S+)", "böyle bir sütun yok: {0}"),
    (r'near "(.+?)": syntax error', 'sözdizimi hatası, şunun yakınında: "{0}"'),
    (r"incomplete input", "ifade yarım kaldı (kapanmamış parantez ya da tırnak?)"),
    (r"unrecognized token: (.+)", "tanınmayan simge: {0} (kapanmamış tırnak?)"),
    (r"ambiguous column name: (\S+)", "sütun adı belirsiz: {0} (birden çok tabloda var; tablo.sütun biçiminde yaz)"),
    (r"misuse of aggregate(?: function)?:? (\S+)", "toplama fonksiyonu yanlış yerde: {0} (WHERE yerine HAVING mi olmalı?)"),
    (r"a GROUP BY clause is required before HAVING", "HAVING için önce GROUP BY gerekir"),
    (r"(UNIQUE|NOT NULL|CHECK|FOREIGN KEY|PRIMARY KEY) constraint failed:? ?(.*)", "{0} kısıtı ihlal edildi {1}"),
    (r"table (\S+) already exists", "{0} tablosu zaten var"),
    (r"(\d+) values for (\d+) columns", "{1} sütuna {0} değer verildi"),
    (r"no such function: (\S+)", "böyle bir fonksiyon yok: {0}"),
    (r"wrong number of arguments to function (\S+)", "{0} fonksiyonuna yanlış sayıda argüman verildi"),
    (r"sub-select returns (\d+) columns - expected 1", "alt sorgu {0} sütun döndürüyor, 1 bekleniyordu"),
    (r"cannot start a transaction within a transaction", "açık bir işlem varken yeni BEGIN yazılamaz"),
    (r"cannot commit - no transaction is active", "COMMIT için açık bir işlem yok"),
]


def _sql_parcala(kod):
    """Betiği ifadelere böl → [(ifade, başladığı satır)]. Tırnak, yorum ya da tetikleyici içindeki ; bölmez."""
    kod = (kod or "").replace("\r\n", "\n")
    sonuc, bas = [], 0
    for m in re.finditer(";", kod):
        parca = kod[bas:m.end()]
        if sqlite3.complete_statement(parca):
            sonuc.append((parca, bas))
            bas = m.end()
    if kod[bas:].strip():
        sonuc.append((kod[bas:], bas))
    cikti = []
    for parca, konum in sonuc:
        on = _SQL_BASI.match(parca).end()
        govde = parca[on:]
        if not govde.strip().rstrip(";").strip():
            continue                              # yalnızca yorum ya da boş ifade
        cikti.append((govde, kod.count("\n", 0, konum + on) + 1))
    return cikti


def _sql_hatasi(e, satir=None, ifade=""):
    ham = str(e)
    msg = ham
    for desen, tr in _SQL_HATA_TR:
        m = re.search(desen, ham)
        if m:
            msg = tr.format(*m.groups()).strip() + f"  ·  ({ham})"
            break
    # Hatanın geçtiği satırı ifadenin içinde bul: hatalı simge ya da (toplama hatasında) WHERE
    kayma = 0
    m = re.search(r'near "(.+?)"|no such (?:column|table|function): (\S+)|ambiguous column name: (\S+)', ham)
    simge = next((g for g in m.groups() if g), None) if m else None
    konum = -1
    if simge:
        konum = ifade.find(simge)
    elif "misuse of aggregate" in ham:
        w = re.search(r"\bWHERE\b", ifade, re.I)
        konum = w.start() if w else -1
    if konum >= 0:
        kayma = ifade[:konum].count("\n")
    satirlar = ifade.split("\n")
    metin = satirlar[kayma] if kayma < len(satirlar) else ""
    return {"type": "SQLHatası", "msg": msg, "line": None if satir is None else satir + kayma,
            "frames": [], "where": "kod", "text": metin}


def _sql_deger(v):
    if v is None:
        return "NULL"
    if isinstance(v, bytes):
        return "x'" + v.hex() + "'"
    return str(v)


def _sql_baglan(job, ek=""):
    db = sqlite3.connect(":memory:", isolation_level=None)    # işlemleri kullanıcı yönetir
    db.execute("PRAGMA foreign_keys = ON")
    for parca in (job.get("tohum_sql"), job.get("setup"), ek):
        if parca:
            db.executescript(parca)
    return db


def _sql_kos(db, kod):
    """Betiği ifade ifade çalıştır → (tablolar, ham satırlar listesi, hata)."""
    tablolar, hamlar = [], []
    for ifade, satir in _sql_parcala(kod):
        try:
            cur = db.execute(ifade)
            if cur.description:
                sutunlar = [d[0] for d in cur.description]
                satirlar = cur.fetchmany(SQL_SATIR_LIMIT + 1)
                kesildi = len(satirlar) > SQL_SATIR_LIMIT
                satirlar = [tuple(r) for r in satirlar[:SQL_SATIR_LIMIT]]
                hamlar.append(satirlar)
                tablolar.append({"satir": satir, "sutunlar": sutunlar, "kesildi": kesildi,
                                 "satirlar": [[None if v is None else _sql_deger(v) for v in r] for r in satirlar]})
            else:
                komut = ifade.split(None, 1)[0].upper()
                if komut in ("INSERT", "UPDATE", "DELETE", "REPLACE"):
                    tablolar.append({"satir": satir, "komut": komut, "degisen": cur.rowcount})
                else:
                    tablolar.append({"satir": satir, "komut": komut})
        except sqlite3.Error as e:
            return tablolar, hamlar, _sql_hatasi(e, satir, ifade)
    return tablolar, hamlar, None


def _sql_metin(tablolar):
    """sqlite3 kabuğunun 'list' biçimi: başlıksız, değerler | ile ayrık, NULL açıkça."""
    return "".join("|".join("NULL" if v is None else v for v in r) + "\n"
                   for t in tablolar if "sutunlar" in t for r in t["satirlar"])


def _sql_tohum(job):
    yol = job.get("tohum")
    if yol and os.path.isfile(yol) and "tohum_sql" not in job:
        with open(yol, encoding="utf-8") as f:
            job["tohum_sql"] = f.read()


def _sql_hazirla(job):
    _sql_tohum(job)
    try:
        return _sql_baglan(job), None
    except sqlite3.Error as e:
        return None, dict(_sql_hatasi(e), where="test", msg="Görevin hazırlık verisi yüklenemedi: " + str(e))


def do_sql_run(job):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "segs": [], "tablolar": []}
    tablolar, _, err = _sql_kos(db, job["code"])
    cikti = _sql_metin(tablolar)
    return {"status": "error" if err else "ok", "segs": [["out", cikti]] if cikti else [],
            "tablolar": tablolar, "error": err}


class SqlTester(Tester):
    def __init__(self, job, db, hamlar, cikti):
        super().__init__("", {}, Capture(), "", job)
        self.cap.add("out", cikti)
        self.code = job.get("code", "")
        self.db = db
        self.hamlar = hamlar

    def sorgu(self, sql, *params):
        """Kullanıcının betiğinden SONRAKİ veritabanında bir sorgu çalıştır."""
        return [tuple(r) for r in self.db.execute(sql, params).fetchall()]

    def dene(self, hazirlik=""):
        """Temiz bir veritabanına `hazirlik`ı ekleyip kullanıcının betiğini yeniden çalıştır → son sorgunun satırları."""
        db = _sql_baglan(self.job, hazirlik)
        _, hamlar, err = _sql_kos(db, self.code)
        if err:
            raise UserRunError(err, hazirlik)
        return hamlar[-1] if hamlar else []

    def kullanir(self, kelime):
        """Anahtar kelime betikte (yorum ve metinler dışında) geçiyor mu? 'group by' gibi çok kelimeli olabilir."""
        temiz = re.sub(r"--[^\n]*|/\*.*?\*/|'(?:[^']|'')*'", " ", self.code, flags=re.S)
        desen = r"\b" + r"\s+".join(map(re.escape, kelime.split())) + r"\b"
        return re.search(desen, temiz, re.I) is not None


def do_sql_test(job):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "checks": [], "segs": []}
    tablolar, hamlar, err = _sql_kos(db, job["code"])
    cikti = _sql_metin(tablolar)
    segs = [["out", cikti]] if cikti else []
    if err:
        return {"status": "error", "checks": [], "segs": segs, "error": err}
    tester = SqlTester(job, db, hamlar, cikti)
    tns = tester.namespace()
    son = next((t for t in reversed(tablolar) if "sutunlar" in t), None)
    tns.update(src=job.get("code", ""), sonuc=hamlar[-1] if hamlar else [], sonuclar=hamlar,
               sutunlar=son["sutunlar"] if son else [], sorgu=tester.sorgu, dene=tester.dene,
               kullanir=tester.kullanir)
    return _test_kos(tester, tns, job, segs)


_PLAN_NOTU = [
    (r"^SCAN ", "tablonun tamamı satır satır okunuyor"),
    (r"^SEARCH .* USING (?:COVERING )?INDEX", "indeksle doğrudan arama"),
    (r"^SEARCH .* USING (?:INTEGER )?PRIMARY KEY", "birincil anahtarla doğrudan erişim"),
    (r"USE TEMP B-TREE FOR (ORDER BY|GROUP BY|DISTINCT)", "sıralamak/gruplamak için geçici yapı kuruluyor"),
    (r"^CORRELATED ", "her dış satır için yeniden çalışan alt sorgu"),
    (r"^(?:LIST )?SUBQUERY|^SCALAR SUBQUERY", "alt sorgu"),
    (r"^MATERIALIZE|^CO-ROUTINE", "ara sonuç (CTE ya da alt sorgu) hazırlanıyor"),
    (r"AUTOMATIC .*INDEX", "SQLite bu sorgu için geçici bir indeks kuruyor"),
]


def do_sql_dis(job):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "text": ""}
    satirlar = []
    for ifade, satir in _sql_parcala(job["code"]):
        bas = ifade.split(None, 1)[0].upper()
        try:
            if bas not in ("SELECT", "WITH", "VALUES"):
                db.execute(ifade)                 # CREATE INDEX vb. planı etkilesin diye uygulanır
                continue
            plan = db.execute("EXPLAIN QUERY PLAN " + ifade).fetchall()
        except sqlite3.Error as e:
            return {"status": "error", "error": _sql_hatasi(e, satir, ifade), "text": ""}
        satirlar.append(f"-- satır {satir}: {' '.join(ifade.split())[:70]}")
        derinlik = {0: -1}
        for kimlik, ust, _, detay in plan:
            d = derinlik.get(ust, -1) + 1
            derinlik[kimlik] = d
            not_ = next((n for desen, n in _PLAN_NOTU if re.search(desen, detay)), "")
            satirlar.append("   " * d + detay + (f"    ← {not_}" if not_ else ""))
        satirlar.append("")
    if not satirlar:
        satirlar = ["(planı gösterilecek SELECT sorgusu yok)"]
    return {"status": "ok", "text": "\n".join(satirlar)}


# ── KQL ve SPL yolları: sandbox/kql.py ve sandbox/spl.py sorguyu SQLite'a çevirir,
#    SQL yolunun veritabanında çalışır ──

_CEVIRICILER = {}


def _cevirici(ad):
    if ad not in _CEVIRICILER:
        import importlib.util
        yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), ad + ".py")
        spec = importlib.util.spec_from_file_location("pafta_" + ad, yol)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        _CEVIRICILER[ad] = modul
    return _CEVIRICILER[ad]


def _sorgu_bloklari(kod):
    """Boş satırla ayrılmış her blok ayrı bir sorgudur → [(blok, başladığı satır)]."""
    satirlar = (kod or "").replace("\r\n", "\n").split("\n")
    bloklar, simdiki, bas = [], [], 0
    for n, s in enumerate(satirlar + [""], 1):
        if s.strip():
            if not simdiki:
                bas = n
            simdiki.append(s)
        elif simdiki:
            if any(x.strip() and not x.strip().startswith("//") for x in simdiki):
                bloklar.append(("\n".join(simdiki), bas))
            simdiki = []
    return bloklar


def _ceviri_hatasi(tur, msg, blok, satir, konum):
    kayma = blok[:konum].count("\n") if konum is not None else 0
    satirlar = blok.split("\n")
    return {"type": tur, "msg": msg, "line": satir + kayma, "frames": [], "where": "kod",
            "text": satirlar[kayma] if kayma < len(satirlar) else ""}


def _ceviri_kos(db, kod, dil):
    """Her sorguyu çevirip çalıştır → (tablolar, ham satırlar, hata, üretilen SQL'ler)."""
    C = _cevirici(dil)
    C.fonksiyonlari_kaydet(db)
    tur = dil.upper() + "Hatası"
    tablolar, hamlar, sqller = [], [], []

    def sutun_bul(sql):
        return [d[0] for d in db.execute(sql).description]
    sutun_bul.satirlar = lambda sql: db.execute(sql).fetchall()     # çevirici veriye bakabilsin (chart, timechart)
    donustur = getattr(C, "satir_donustur", None)                  # SPL: _time okunur tarih, çok değerli alanlar

    for blok, satir in _sorgu_bloklari(kod):
        try:
            sql = C.cevir(blok, sutun_bul)
            cur = db.execute(sql)
        except C.Hata as e:
            return tablolar, hamlar, _ceviri_hatasi(tur, e.msg, blok, satir, e.konum), sqller
        except sqlite3.Error as e:
            return tablolar, hamlar, dict(_sql_hatasi(e, satir, blok), type=tur), sqller
        sqller.append((satir, sql))
        cols = [d[0] for d in cur.description]
        tut = [n for n, c in enumerate(cols) if c != "__sira"]
        satirlar = cur.fetchmany(SQL_SATIR_LIMIT + 1)
        kesildi = len(satirlar) > SQL_SATIR_LIMIT
        satirlar = [tuple(r[n] for n in tut) for r in satirlar[:SQL_SATIR_LIMIT]]
        goster = satirlar
        if donustur:
            satirlar, goster = donustur([cols[n] for n in tut], satirlar)
        hamlar.append(satirlar)
        tablolar.append({"satir": satir, "sutunlar": [cols[n] for n in tut], "kesildi": kesildi,
                         "satirlar": [[None if v is None else _sql_deger(v) for v in r] for r in goster]})
    return tablolar, hamlar, None, sqller


def _ceviri_metin(tablolar):
    """KQL ve SPL'de boş değer boş görünür; çok değerli alanın değerleri virgülle ayrılır."""
    return "".join("|".join("" if v is None else v.replace("\x1f", ",") for v in r) + "\n"
                   for t in tablolar if "sutunlar" in t for r in t["satirlar"])


def do_ceviri_run(job, dil):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "segs": [], "tablolar": []}
    tablolar, _, err, _ = _ceviri_kos(db, job["code"], dil)
    cikti = _ceviri_metin(tablolar)
    return {"status": "error" if err else "ok", "segs": [["out", cikti]] if cikti else [],
            "tablolar": tablolar, "kql": True, "error": err}


class CeviriTester(SqlTester):
    def __init__(self, job, db, hamlar, cikti, dil):
        super().__init__(job, db, hamlar, cikti)
        self.dil = dil

    def dene(self, hazirlik=""):
        db = _sql_baglan(self.job, hazirlik)
        _, hamlar, err, _ = _ceviri_kos(db, self.code, self.dil)
        if err:
            raise UserRunError(err, hazirlik)
        return hamlar[-1] if hamlar else []

    def kullanir(self, kelime):
        temiz = re.sub(r"//[^\n]*|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", " ", self.code)
        desen = r"(?<![\w-])" + r"\s+".join(map(re.escape, kelime.split())) + r"(?![\w-])"
        return re.search(desen, temiz, re.I if self.dil == "spl" else 0) is not None


def do_ceviri_test(job, dil):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "checks": [], "segs": []}
    tablolar, hamlar, err, _ = _ceviri_kos(db, job["code"], dil)
    cikti = _ceviri_metin(tablolar)
    segs = [["out", cikti]] if cikti else []
    if err:
        return {"status": "error", "checks": [], "segs": segs, "error": err}
    tester = CeviriTester(job, db, hamlar, cikti, dil)
    tns = tester.namespace()
    son = tablolar[-1] if tablolar else None
    tns.update(src=job.get("code", ""), sonuc=hamlar[-1] if hamlar else [], sonuclar=hamlar,
               sutunlar=son["sutunlar"] if son else [], sorgu=tester.sorgu, dene=tester.dene,
               kullanir=tester.kullanir)
    return _test_kos(tester, tns, job, segs)


def do_ceviri_dis(job, dil):
    db, err = _sql_hazirla(job)
    if err:
        return {"status": "error", "error": err, "text": ""}
    _, _, err, sqller = _ceviri_kos(db, job["code"], dil)
    if err:
        return {"status": "error", "error": err, "text": ""}
    metin = "\n\n".join(f"-- satır {satir}\n{sql};" for satir, sql in sqller)
    return {"status": "ok", "text": metin or "(çevrilecek sorgu yok)"}


def _detection_module(name):
    import importlib
    folder = os.path.dirname(os.path.abspath(__file__))
    if folder not in sys.path:
        sys.path.insert(0, folder)
    return importlib.import_module(name + "_engine")


def _detection_error(exc, name):
    mark = getattr(exc, "problem_mark", None)
    line = mark.line + 1 if mark is not None else None
    if line is None:
        match = re.search(r"line (\d+)", str(exc), re.I)
        line = int(match.group(1)) if match else None
    return {"type": name.upper() + "Hatası", "msg": str(exc), "line": line,
            "frames": [], "where": "kod"}


def do_detection_run(job, name):
    try:
        module = _detection_module(name)
        if name == "sigma":
            return module.SigmaProgram(job["code"]).run(module.parse_events(job.get("stdin", "")))
        rules = module.compile_rules(job["code"])
        return module.format_result(rules, module.decode_data(job.get("stdin", "")))
    except Exception as exc:
        return {"status": "error", "error": _detection_error(exc, name), "segs": []}


def do_detection_test(job, name):
    run_setup(job)
    code, stdin = job["code"], job.get("stdin", "")
    try:
        module = _detection_module(name)
        if name == "sigma":
            program = module.SigmaProgram(code)
            helpers = {"eslesir": program.matches, "eslesenler": program.matching_events,
                       "kural_adlari": program.names,
                       "kurallar": [item.rule.to_dict() for item in program.rules]}
        else:
            rules = module.compile_rules(code)
            def names(data):
                return [match.rule for match in module.match_rules(rules, data)]
            helpers = {"eslesenler": names,
                       "eslesir": lambda data, rule_name=None: any(rule_name is None or n == rule_name for n in names(data)),
                       "derle": module.compile_rules}
    except Exception as exc:
        return {"status": "error", "error": _detection_error(exc, name), "checks": [], "segs": []}
    tester = Tester("", {}, Capture(), stdin, job)
    namespace = tester.namespace()
    namespace.update(src=code, **helpers)
    return _test_kos(tester, namespace, job, [])


MODES = {"run": do_run, "test": do_test, "trace": do_trace, "dis": do_dis,
         "sigma_run": lambda j: do_detection_run(j, "sigma"), "sigma_test": lambda j: do_detection_test(j, "sigma"),
         "yara_run": lambda j: do_detection_run(j, "yara"), "yara_test": lambda j: do_detection_test(j, "yara"),
         "kql_run": lambda j: do_ceviri_run(j, "kql"), "kql_test": lambda j: do_ceviri_test(j, "kql"),
         "kql_dis": lambda j: do_ceviri_dis(j, "kql"),
         "spl_run": lambda j: do_ceviri_run(j, "spl"), "spl_test": lambda j: do_ceviri_test(j, "spl"),
         "spl_dis": lambda j: do_ceviri_dis(j, "spl"),
         "regex_run": do_regex_run, "regex_test": do_regex_test, "regex_dis": do_regex_dis,
         "proc_run": do_proc_run, "proc_test": do_proc_test, "proc_trace": do_proc_trace,
         "sql_run": do_sql_run, "sql_test": do_sql_test, "sql_dis": do_sql_dis}


def main():
    job_path, result_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding="utf-8") as f:
        job = json.load(f)
    sys.argv = ["kod.py"]
    register_source(job.get("code", ""))
    try:
        res = MODES[job["mode"]](job)
    except BaseException:
        res = {"status": "internal", "detail": traceback.format_exc()}
    data = json.dumps(res, ensure_ascii=False, default=repr)
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(data)
    try:
        sys.__stdout__.flush()
    except Exception:
        pass
    os._exit(0)


if __name__ == "__main__":
    main()
