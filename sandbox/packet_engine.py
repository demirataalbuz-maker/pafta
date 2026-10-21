"""Offline packet filters: native TShark display filters and native libpcap BPF.

Student text is passed as one argument, never through a shell. Only supplied
capture bytes are read; neither backend opens a capture interface.
Both backends accept classic Ethernet PCAP 2.4 only (not pcapng). Display
address operands are numeric; DNS/HTTP string fields still accept text.
"""
import base64
import functools
import ipaddress
import json
import os
import re
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
_PCAP_MAGIC = {b"\xd4\xc3\xb2\xa1": ("<", False), b"\xa1\xb2\xc3\xd4": (">", False),
               b"\x4d\x3c\xb2\xa1": ("<", True), b"\xa1\xb2\x3c\x4d": (">", True)}
_IP_FIELD = re.compile(r"(?:(?:ip|ipv6)\.(?:addr|src|dst)|arp\.(?:src|dst)\.proto_ipv4|dns\.(?:a|aaaa))(?:#[0-9]+)?\Z")
_DISPLAY_TOKEN = re.compile(r'r?"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|===|!==|==|!=|<=|>=|&&|\|\||\^\^|[A-Za-z0-9_.:/]+(?:#[0-9]+)?|[^\s]')
_COMPARISON = frozenset(("==", "!=", "===", "!==", "<", ">", "<=", ">=", "eq", "ne",
                         "gt", "lt", "ge", "le", "any_eq", "all_eq", "any_ne", "all_ne", "in"))


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
    if not isinstance(text, str):
        raise PacketError("Girdi JSON metni olmalı.")
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
    pcap_lengths(raw)  # Reject unsupported/malformed input before either native backend.
    return raw


def input_capture(config):
    if "pcap_base64" in config:
        value = config["pcap_base64"]
        if not isinstance(value, str) or len(value) > MAX_CAPTURE * 2:
            raise PacketError("pcap_base64 boyutu/türü geçersiz.")
        try:
            decoded = base64.b64decode(value, validate=True)
        except ValueError as exc:
            raise PacketError("pcap_base64 geçerli Base64 olmalı.") from exc
        return capture_bytes(decoded)
    return capture_bytes(config.get("kayit", "temel"))


def _numeric_ip_operand(token):
    if _IP_FIELD.fullmatch(token):
        return True  # Address field-to-field comparisons need no lookup.
    if token.startswith('r"') and token.endswith('"'):
        token = token[2:-1]
    elif token[:1] in ('"', "'") and token[-1:] == token[:1]:
        token = token[1:-1]
    if "\\" in token or "%" in token:
        return False  # No escaped names or platform-specific zone identifiers.
    try:
        if "/" in token:
            ipaddress.ip_network(token, strict=False)
        else:
            ipaddress.ip_address(token)
        return True
    except ValueError:
        return False


def _display_numeric_addresses(code):
    """Validate direct IP operands without interpreting filter truth values.

    The native engine owns parsing/evaluation. This deliberately narrow guard
    accepts numeric IP/CIDR/range sets and address-field comparisons. Text
    fields (dns.qry.name/http.host, including their strings) are unaffected.
    -n plus the explicit resolver preference also disables native name lookup.
    """
    tokens = _DISPLAY_TOKEN.findall(code)
    for index, token in enumerate(tokens):
        if not _IP_FIELD.fullmatch(token):
            continue
        for direction in (1, -1):
            at = index + direction
            while 0 <= at < len(tokens) and tokens[at] == (")" if direction == 1 else "("):
                at += direction
            if not 0 <= at < len(tokens) or tokens[at] not in _COMPARISON:
                continue
            at += direction
            while 0 <= at < len(tokens) and tokens[at] == ("(" if direction == 1 else ")"):
                at += direction
            if not 0 <= at < len(tokens):
                continue  # Native compiler reports the incomplete expression.
            operands = [tokens[at]]
            if direction == 1 and tokens[at] == "{":
                end = at + 1
                while end < len(tokens) and tokens[end] != "}":
                    end += 1
                operands = [value for value in tokens[at + 1:end] if value not in (",", "..")]
            for value in operands:
                # A range without surrounding whitespace is one lexical token.
                if all(_numeric_ip_operand(part) for part in value.split("..")):
                    continue
                raise PacketError("IP adres alanlarında yalnız sayısal IP/CIDR veya IP alanı "
                                  "kullanılabilir; sunucu adı çözülmez: " + value)


@functools.lru_cache(maxsize=32)
def _display(code, raw):
    _display_numeric_addresses(code)
    exe = tshark_path()
    if not exe:
        raise PacketError("TShark bulunamadı. Wireshark/TShark kur veya PAFTA_TSHARK değişkenine tshark.exe tam yolunu ver.")
    with tempfile.TemporaryDirectory(prefix="pafta_tshark_") as config:
        env = dict(os.environ, WIRESHARK_CONFIG_DIR=config, WIRESHARK_PLUGIN_DIR=config,
                   WIRESHARK_EXTCAP_DIR=config, TZ="UTC")
        # Ignore inherited development data paths; keep the installed TShark's
        # own protocol data and an empty personal configuration/plugin folder.
        env.pop("WIRESHARK_RUN_FROM_BUILD_DIRECTORY", None)
        env.pop("WIRESHARK_DATA_DIR", None)
        command = [exe, "-n", "-o", "nameres.use_external_name_resolver:FALSE",
                   "-r", "-", "-Y", code, "-T", "fields", "-e", "frame.number"]
        try:
            result = subprocess.run(command, input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=8, env=env, creationflags=NO_WINDOW)
        except subprocess.TimeoutExpired as exc:
            raise PacketError("TShark 8 saniyede bitmedi.") from exc
        except OSError as exc:
            raise PacketError("TShark başlatılamadı; PAFTA_TSHARK yolunu ve çalıştırılabilir "
                              "dosyayı doğrulayın: " + str(exc)) from exc
    stderr = result.stderr.decode("utf-8", "replace").strip()
    if result.returncode:
        raise PacketError(stderr or "TShark hata kodu: " + str(result.returncode))
    try:
        ids = tuple(int(line) for line in result.stdout.decode("utf-8").splitlines() if line.strip())
        count = len(pcap_lengths(raw))
        if any(i < 1 or i > count for i in ids) or any(a >= b for a, b in zip(ids, ids[1:])):
            raise ValueError("invalid frame number/order")
        return ids
    except (ValueError, UnicodeError) as exc:
        raise PacketError("TShark beklenmeyen paket numarası döndürdü.") from exc


@functools.lru_cache(maxsize=32)
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
    """Validate the shared classic-Ethernet format and retain honest lengths.

    Microsecond/nanosecond PCAP, either byte order, supports explicit snapshot
    truncation: caplen may be less than wirelen, but never the reverse.
    This inventory does not dissect packets; native backends decide matches.
    """
    if not isinstance(raw, bytes) or len(raw) < 24 or raw[:4] not in _PCAP_MAGIC:
        raise PacketError("Yalnız classic Ethernet PCAP 2.4 desteklenir; PCAPNG veya eksik başlık kabul edilmez.")
    endian, nano = _PCAP_MAGIC[raw[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack_from(endian + "HHiIII", raw, 4)
    if (major, minor) != (2, 4) or linktype != 1:
        raise PacketError("Kayıt classic PCAP 2.4 ve LINKTYPE_ETHERNET=1 olmalı.")
    if not 1 <= snaplen <= 0x7fffffff:
        raise PacketError("PCAP snaplen 1..2147483647 aralığında olmalı.")
    rows, pos, index = {}, 24, 1
    while pos < len(raw):
        if pos + 16 > len(raw):
            raise PacketError("PCAP paket başlığı eksik.")
        _, subsec, caplen, wirelen = struct.unpack_from(endian + "IIII", raw, pos)
        if subsec >= (1000000000 if nano else 1000000):
            raise PacketError("PCAP paket zamanı kesir alanı geçersiz.")
        if caplen > snaplen or caplen > wirelen:
            raise PacketError("PCAP caplen, snaplen veya wirelen değerini aşamaz.")
        if pos + 16 + caplen > len(raw):
            raise PacketError("PCAP paket baytları eksik.")
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
    result = {"status": "ok", "error": None, "segs": [["out", out]],
            "tablolar": [{"satir": 1, "sutunlar": ["Paket", "Yakalanan bayt", "Hat uzunluğu"], "satirlar": rows}],
            "packet_ids": ids, "packet_backend": backend, "packet_dialect": config["dil"]}
    if "pcap_base64" not in config:
        names = {1: "ICMP", 6: "TCP", 17: "UDP", 58: "ICMPv6", 132: "SCTP"}
        inventory = []
        for packet in packet_fixtures.describe(config.get("kayit", "temel")):
            protocol = names.get(packet.get("proto"), str(packet.get("proto", "Ethernet")))
            if "sport" in packet and "dport" in packet:
                protocol += " " + str(packet["sport"]) + " → " + str(packet["dport"])
            description = packet["note"]
            if "flags" in packet:
                description += f"; TCP flags 0x{packet['flags']:02x}"
            if "vlan" in packet:
                description += "; VLAN " + "/".join(map(str, packet["vlan"]))
            if "fragment_offset" in packet:
                description += f"; fragment offset {packet['fragment_offset']} × 8 bayt"
            inventory.append([packet["id"], packet.get("src", packet.get("eth_src", "")),
                              packet.get("dst", packet.get("eth_dst", "")), protocol,
                              str(packet["wirelen"]) + " / " + str(packet["caplen"]), description,
                              packet["time_relative"]])
        result["packet_inventory"] = {
            "baslik": "Sentetik kayıt dökümü · fixture açıklamaları, native ayrıştırma değildir",
            "sutunlar": ["Paket", "Kaynak", "Hedef", "Protokol / port", "Boy / yakalanan", "Açıklama", "Göreli saniye"],
            "satirlar": inventory}
    return result


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
