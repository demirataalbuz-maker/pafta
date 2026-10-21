"""Offline numeric BPF filters using the pinned wheel's native libpcap DLL.

Only pcap_open_dead, compile, offline_filter, freecode and close are called.
No adapter, capture service, live handle or packet transmission is involved.
Input is classic Ethernet PCAP (micro/nanoseconds, either byte order).
Name/service lookups are deliberately disabled: use numeric addresses/ports.
"""
import ctypes as ct
import ipaddress
import os
from pathlib import Path
import re
import struct
import threading


class BpfUnavailableError(RuntimeError):
    pass


class BpfFilterError(ValueError):
    pass


class PcapFormatError(ValueError):
    pass


class _Timeval(ct.Structure):
    _fields_ = [("tv_sec", ct.c_long), ("tv_usec", ct.c_long)]


class _PcapHeader(ct.Structure):
    _fields_ = [("ts", _Timeval), ("caplen", ct.c_uint32), ("len", ct.c_uint32)]


class _BpfInsn(ct.Structure):
    _fields_ = [("code", ct.c_ushort), ("jt", ct.c_ubyte),
                ("jf", ct.c_ubyte), ("k", ct.c_uint32)]


class _BpfProgram(ct.Structure):
    _fields_ = [("bf_len", ct.c_uint), ("bf_insns", ct.POINTER(_BpfInsn))]


_DLL = None
_LOCK = threading.Lock()
_DLL_FOLDER = (Path(__file__).resolve().parent.parent / ".deps" / "libpcap" /
               "_platform" / "windows" / "x86_64" / "tcpdump")
_MAGIC = {b"\xd4\xc3\xb2\xa1": ("<", False),
          b"\xa1\xb2\xc3\xd4": (">", False),
          b"\x4d\x3c\xb2\xa1": ("<", True),
          b"\xa1\xb2\x3c\x4d": (">", True)}
_WORDS = frozenset("""
and or not src dst host net mask port portrange ether link ip ip6 arp rarp
tcp udp sctp icmp icmp6 igmp ah esp pim proto protochain broadcast multicast
less greater len vlan mpls pppoed pppoes geneve tcpflags icmptype icmpcode
icmp6type icmp6code tcp-fin tcp-syn tcp-rst tcp-push tcp-ack tcp-urg tcp-ece
tcp-cwr icmp-echoreply icmp-unreach icmp-sourcequench icmp-redirect icmp-echo
icmp-routeradvert icmp-routersolicit icmp-timxceed icmp-paramprob icmp-tstamp
icmp-tstampreply icmp-ireq icmp-ireqreply icmp-maskreq icmp-maskreply
icmp6-destinationunreach icmp6-packettoobig icmp6-timeexceeded
icmp6-parameterproblem icmp6-echo icmp6-echoreply
""".split())


def _library():
    global _DLL
    if _DLL is not None:
        return _DLL
    with _LOCK:
        if _DLL is not None:
            return _DLL
        if os.name != "nt" or ct.sizeof(ct.c_void_p) != 8:
            raise BpfUnavailableError("BPF: bu paket Windows x64 Python gerektirir.")
        if (ct.sizeof(_PcapHeader), _PcapHeader.caplen.offset,
                _PcapHeader.len.offset) != (16, 8, 12):
            raise BpfUnavailableError("BPF: beklenen Windows pcap_pkthdr ABI'si 16/8/12 değil.")
        path = _DLL_FOLDER / "pcap.dll"
        missing = [name for name in ("pcap.dll", "libssl-3-x64.dll", "libcrypto-3-x64.dll")
                   if not (_DLL_FOLDER / name).is_file()]
        if missing:
            raise BpfUnavailableError(
                "BPF DLL eksik: " + ", ".join(missing) + ". "
                "Proje kökünde python -m pip install --target .deps --no-deps "
                "libpcap==1.11.0b29 çalıştırın. Sürücü gerekmez. Yol: " + str(path))
        try:
            with os.add_dll_directory(str(_DLL_FOLDER)):
                dll = ct.CDLL(str(path))
            dll.pcap_lib_version.argtypes = []
            dll.pcap_lib_version.restype = ct.c_char_p
            dll.pcap_open_dead.argtypes = [ct.c_int, ct.c_int]
            dll.pcap_open_dead.restype = ct.c_void_p
            dll.pcap_compile.argtypes = [ct.c_void_p, ct.POINTER(_BpfProgram),
                                         ct.c_char_p, ct.c_int, ct.c_uint32]
            dll.pcap_compile.restype = ct.c_int
            dll.pcap_geterr.argtypes = [ct.c_void_p]
            dll.pcap_geterr.restype = ct.c_char_p
            dll.pcap_offline_filter.argtypes = [ct.POINTER(_BpfProgram),
                                                ct.POINTER(_PcapHeader), ct.c_void_p]
            dll.pcap_offline_filter.restype = ct.c_uint
            dll.pcap_freecode.argtypes = [ct.POINTER(_BpfProgram)]
            dll.pcap_freecode.restype = None
            dll.pcap_close.argtypes = [ct.c_void_p]
            dll.pcap_close.restype = None
        except (OSError, AttributeError) as exc:
            raise BpfUnavailableError(
                f"BPF DLL yüklenemedi: {path}. Aynı klasördeki iki OpenSSL DLL'ini "
                "ve x64 Python'u doğrulayın; libpcap==1.11.0b29 wheel'ini .deps'e "
                f"yeniden açın. Native ayrıntı: {exc}") from exc
        _DLL = dll
        return dll


def available():
    """Return whether the local native DLL and its required exports load."""
    try:
        _library()
        return True
    except BpfUnavailableError:
        return False


def version():
    """Return the C library version, distinct from the Python wheel version."""
    return _library().pcap_lib_version().decode("utf-8", "replace")


def _numeric_filter(text):
    if not isinstance(text, str):
        raise TypeError("BPF filtresi metin olmalı.")
    # libpcap can resolve host/service names while compiling even without a
    # live handle. An allowlist prevents such lookups; native libpcap still
    # parses and evaluates every accepted expression, including byte accessors.
    if not re.fullmatch(r"[A-Za-z0-9_.:\s()/\[\]&|!<>=+*%^,\-]*", text):
        raise BpfFilterError("BPF: yalnız sayısal adres/port ve offline anahtar sözcükler; "
                             "tırnak, ters bölü veya diğer karakterler desteklenmiyor.")
    for token in re.findall(r"[A-Za-z0-9_.:]+(?:-[A-Za-z0-9_]+)*", text):
        if token in _WORDS or re.fullmatch(r"(?:0[xX][0-9A-Fa-f]+|[0-9]+)(?:-[0-9]+)?", token):
            continue
        if re.fullmatch(r"[0-9]+:[0-9]+", token):
            continue  # byte-offset:size, never a DNS name
        if re.fullmatch(r"[0-9A-Fa-f]{1,2}(?::[0-9A-Fa-f]{1,2}){5}", token):
            continue
        try:
            ipaddress.ip_address(token)
        except ValueError:
            raise BpfFilterError(
                f"BPF: {token!r} desteklenmiyor; DNS/servis adı çözülmez. "
                "Tam sayısal IP, MAC, port veya protokol numarası kullanın.") from None
    return text.encode("ascii")


def _records(raw):
    if not isinstance(raw, (bytes, bytearray, memoryview)):
        raise TypeError("PCAP girdisi bayt olmalı.")
    raw = bytes(raw)
    if len(raw) < 24 or raw[:4] not in _MAGIC:
        raise PcapFormatError("Classic PCAP bekleniyor; pcapng veya eksik başlık desteklenmiyor.")
    order, nano = _MAGIC[raw[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack_from(order + "HHiIII", raw, 4)
    if (major, minor) != (2, 4):
        raise PcapFormatError("Yalnız classic PCAP 2.4 destekleniyor.")
    if linktype != 1:
        raise PcapFormatError("Yalnız LINKTYPE_ETHERNET=1 destekleniyor.")
    if not 1 <= snaplen <= 0x7fffffff:
        raise PcapFormatError("PCAP snaplen 1..2147483647 aralığında olmalı.")
    records = []
    at = 24
    while at < len(raw):
        if len(raw) - at < 16:
            raise PcapFormatError("PCAP paket başlığı eksik.")
        sec, subsec, caplen, wirelen = struct.unpack_from(order + "IIII", raw, at)
        at += 16
        if subsec >= (1000000000 if nano else 1000000):
            raise PcapFormatError("PCAP paket zamanının kesir alanı geçersiz.")
        if caplen > snaplen or caplen > wirelen:
            raise PcapFormatError("PCAP caplen, snaplen veya wirelen değerini aşamaz.")
        if caplen > len(raw) - at:
            raise PcapFormatError("PCAP paket baytları eksik.")
        records.append((sec, subsec // 1000 if nano else subsec,
                        caplen, wirelen, raw[at:at + caplen]))
        at += caplen
    return snaplen, records


def evaluate(filter_text, pcap_bytes):
    """Return matching 1-based frame numbers; never open a capture interface.

    Native errors are BpfFilterError, invalid classic PCAP is PcapFormatError,
    missing local runtime is BpfUnavailableError. IPv4 broadcast tests have no
    assumed interface mask (PCAP_NETMASK_UNKNOWN), so libpcap rejects them.
    """
    expression = _numeric_filter(filter_text)
    snaplen, packets = _records(pcap_bytes)
    dll = _library()
    handle = dll.pcap_open_dead(1, snaplen)
    if not handle:
        raise BpfUnavailableError("BPF: pcap_open_dead Ethernet handle oluşturamadı.")
    program = _BpfProgram()
    compiled = False
    try:
        if dll.pcap_compile(handle, ct.byref(program), expression, 1, 0xffffffff):
            message = (dll.pcap_geterr(handle) or b"unknown compile error").decode("utf-8", "replace")
            raise BpfFilterError("BPF derleme hatası: " + message)
        compiled = True
        matched = []
        for number, (sec, usec, caplen, wirelen, packet) in enumerate(packets, 1):
            header = _PcapHeader(_Timeval(sec, usec), caplen, wirelen)
            buffer = ct.create_string_buffer(packet)
            if dll.pcap_offline_filter(ct.byref(program), ct.byref(header), buffer):
                matched.append(number)
        return matched
    finally:
        if compiled:
            dll.pcap_freecode(ct.byref(program))
        dll.pcap_close(handle)
