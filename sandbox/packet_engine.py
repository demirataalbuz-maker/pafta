"""Offline packet filters: native TShark display filters and native libpcap BPF.

Student text is passed as one argument, never through a shell. Only supplied
capture bytes are read; neither backend opens a capture interface.
"""
import base64
import functools
import json
import os
import shutil
import struct
import subprocess
import tempfile

try:
    from . import bpf_native, packet_fixtures
except ImportError:
    import bpf_native
    import packet_fixtures

MAX_CAPTURE = 8 * 1024 * 1024
MAX_FILTER = 16000
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class PacketError(ValueError):
    pass


def tshark_path():
    configured = os.environ.get("PAFTA_TSHARK")
    if configured and os.path.isfile(configured):
        return configured
    found = shutil.which("tshark")
    if found:
        return found
    candidate = r"C:\Program Files\Wireshark\tshark.exe"
    return candidate if os.path.isfile(candidate) else None


def options(text=""):
    if not text or not text.strip():
        return {"dil": "wireshark", "kayit": "temel"}
    try:
        value = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise PacketError('Girdi JSON olmalı: {"dil":"wireshark","kayit":"temel"}') from exc
    if not isinstance(value, dict) or set(value) - {"dil", "kayit", "pcap_base64"}:
        raise PacketError("Girdi yalnız dil, kayit veya pcap_base64 alanlarını kabul eder.")
    if "kayit" in value and "pcap_base64" in value:
        raise PacketError("kayit ile pcap_base64 birlikte verilmez.")
    if value.get("dil", "wireshark") not in ("wireshark", "bpf"):
        raise PacketError("dil wireshark ya da bpf olmalı; iki dilin sözdizimi farklıdır.")
    return dict({"dil": "wireshark", "kayit": "temel"} if "pcap_base64" not in value
                else {"dil": "wireshark"}, **value)


def capture_bytes(capture):
    if isinstance(capture, bytes):
        raw = capture
    elif isinstance(capture, str):
        try:
            raw = packet_fixtures.get_capture(capture)
        except (KeyError, ValueError) as exc:
            raise PacketError("Bilinmeyen kayıt: " + capture + ". Seçenekler: " + ", ".join(packet_fixtures.captures())) from exc
    else:
        raise PacketError("Kayıt adı ya da PCAP baytları gerekli.")
    if len(raw) > MAX_CAPTURE:
        raise PacketError("Kayıt en fazla 8 MiB olabilir.")
    return raw


def input_capture(config):
    if "pcap_base64" in config:
        value = config["pcap_base64"]
        if not isinstance(value, str) or len(value) > MAX_CAPTURE * 2:
            raise PacketError("pcap_base64 boyutu/türü geçersiz.")
        try:
            return capture_bytes(base64.b64decode(value, validate=True))
        except ValueError as exc:
            raise PacketError("pcap_base64 geçerli Base64 olmalı.") from exc
    return capture_bytes(config.get("kayit", "temel"))


@functools.lru_cache(maxsize=256)
def _display(code, raw):
    exe = tshark_path()
    if not exe:
        raise PacketError("TShark bulunamadı. Wireshark/TShark kur veya PAFTA_TSHARK değişkenine tshark.exe tam yolunu ver.")
    with tempfile.TemporaryDirectory(prefix="pafta_tshark_") as config:
        env = dict(os.environ, WIRESHARK_CONFIG_DIR=config, TZ="UTC")
        command = [exe, "-n", "-r", "-", "-Y", code, "-T", "fields", "-e", "frame.number"]
        try:
            result = subprocess.run(command, input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=8, env=env, creationflags=NO_WINDOW)
        except subprocess.TimeoutExpired as exc:
            raise PacketError("TShark 8 saniyede bitmedi.") from exc
    stderr = result.stderr.decode("utf-8", "replace").strip()
    if result.returncode:
        raise PacketError(stderr or "TShark hata kodu: " + str(result.returncode))
    try:
        return tuple(int(line) for line in result.stdout.decode("utf-8").splitlines() if line.strip())
    except ValueError as exc:
        raise PacketError("TShark beklenmeyen paket numarası döndürdü.") from exc


@functools.lru_cache(maxsize=256)
def _bpf(code, raw):
    return tuple(bpf_native.evaluate(code, raw))


def evaluate(code, capture="temel", dialect="wireshark"):
    if not isinstance(code, str) or len(code.encode("utf-8")) > MAX_FILTER or "\0" in code:
        raise PacketError("Filtre en fazla 16 kB, NUL içermeyen metin olmalı.")
    raw = capture_bytes(capture)
    if dialect == "wireshark":
        return list(_display(code, raw))
    if dialect == "bpf":
        return list(_bpf(code, raw))
    raise PacketError("Bilinmeyen filtre dili: " + str(dialect))


def pcap_lengths(raw):
    """Small output inventory; native backends remain authoritative for filtering."""
    if len(raw) < 24:
        return {}
    endian = "<" if raw[:4] in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1") else ">"
    rows, pos, index = {}, 24, 1
    while pos + 16 <= len(raw):
        _, _, caplen, wirelen = struct.unpack_from(endian + "IIII", raw, pos)
        if pos + 16 + caplen > len(raw):
            break
        rows[index] = (caplen, wirelen)
        pos += 16 + caplen
        index += 1
    return rows


def run(code, stdin=""):
    config = options(stdin)
    raw = input_capture(config)
    ids = evaluate(code, raw, config["dil"])
    out = "Paketler: " + (", ".join(map(str, ids)) if ids else "(yok)") + "\n"
    lengths = pcap_lengths(raw)
    rows = [[i, *lengths.get(i, ("?", "?"))] for i in ids]
    backend = "TShark" if config["dil"] == "wireshark" else bpf_native.version()
    return {"status": "ok", "error": None, "segs": [["out", out]],
            "tablolar": [{"satir": 1, "sutunlar": ["Paket", "Yakalanan bayt", "Hat uzunluğu"], "satirlar": rows}],
            "packet_ids": ids, "packet_backend": backend, "packet_dialect": config["dil"]}


def test_helpers(code, stdin=""):
    config = options(stdin)
    selected = input_capture(config)
    dialect = config["dil"]
    evaluate(code, selected, dialect)  # Invalid filters cannot pass a vacuous test.
    return {"src": code,
            "eslesenler": lambda kayit=None: evaluate(code, selected if kayit is None else kayit, dialect),
            "referans": lambda filtre, kayit=None, dil=None: evaluate(filtre, selected if kayit is None else kayit, dil or dialect),
            "korpuslar": tuple(packet_fixtures.captures()),
            "paketler": packet_fixtures.describe}
