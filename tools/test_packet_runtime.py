"""Native filter integration, using a tiny independent Ethernet/IPv4 corpus."""
import base64
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine.runners import get
from sandbox import packet_engine as engine


def corpus():
    header = struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    frames = []
    # Source/destination semantics, exact numeric boundaries, and absent fields.
    for index, (proto, src, dst, length) in enumerate([
            (6, 50000, 79, 63), (6, 50000, 80, 64), (6, 80, 50000, 65),
            (6, 50000, 81, 127), (17, 50000, 53, 128), (1, 0, 0, 129)]):
        transport = (struct.pack("!HHIIBBHHH", src, dst, index, 0, 0x50, 2, 8192, 0, 0) if proto == 6
                     else struct.pack("!HHHH", src, dst, length - 34, 0) if proto == 17 else b"\x08\0\0\0\0\0\0\0")
        payload = transport + b"X" * (length - 34 - len(transport))
        ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(payload), index, 0, 64, proto, 0,
                         bytes([192, 0, 2, 1]), bytes([198, 51, 100, 1]))
        frame = bytes.fromhex("0200000000020200000000010800") + ip + payload
        frames.append(struct.pack("<IIII", 1700000000 + index, 0, len(frame), len(frame)) + frame)
    return header + b"".join(frames)


class PacketRuntimeTests(unittest.TestCase):
    def test_native_backends_select_ports(self):
        raw = corpus()
        self.assertEqual(engine.evaluate("tcp.dstport == 80", raw), [2])
        self.assertEqual(engine.evaluate("tcp dst port 80", raw, "bpf"), [2])
        self.assertEqual(engine.evaluate("tcp port 80", raw, "bpf"), [2, 3])

    def test_length_boundaries_both_dialects(self):
        raw = corpus()
        self.assertEqual(engine.evaluate("frame.len <= 64", raw), [1, 2])
        self.assertEqual(engine.evaluate("frame.len < 64", raw), [1])
        self.assertEqual(engine.evaluate("less 64", raw, "bpf"), [1, 2])
        self.assertEqual(engine.evaluate("len < 64", raw, "bpf"), [1])
        self.assertEqual(engine.evaluate("greater 128", raw, "bpf"), [5, 6])
        self.assertEqual(engine.evaluate("len > 128", raw, "bpf"), [6])

    def test_missing_fields_and_bpf_precedence(self):
        raw = corpus()
        self.assertEqual(engine.evaluate("tcp.port != 80", raw), [1, 4])
        self.assertEqual(engine.evaluate("not (tcp.port == 80)", raw), [1, 4, 5, 6])
        self.assertEqual(engine.evaluate("tcp or udp and port 53", raw, "bpf"), [5])
        self.assertEqual(engine.evaluate("tcp or (udp and port 53)", raw, "bpf"), [1, 2, 3, 4, 5])

    def test_invalid_filters_are_errors_not_empty_results(self):
        for dialect, query in [("wireshark", "tcp dst port 80"), ("bpf", "tcp.dstport == 80"),
                               ("wireshark", "tcp; echo BAD"), ("bpf", "tcp and (")]:
            with self.subTest(dialect=dialect, query=query), self.assertRaises(ValueError):
                engine.evaluate(query, corpus(), dialect)

    def test_input_validation(self):
        for value in ['[]', '{"dil":"powershell"}', '{"dosya":"C:/x.pcap"}',
                      '{"kayit":"temel","pcap_base64":"AA=="}']:
            with self.assertRaises(engine.PacketError):
                engine.options(value)
        with self.assertRaises(engine.PacketError):
            engine.capture_bytes("olmayan")
        with self.assertRaises(engine.PacketError):
            engine.evaluate("tcp\0or udp", corpus())

    def test_runner_run_test_and_real_byte_input(self):
        data = json.dumps({"dil": "bpf", "pcap_base64": base64.b64encode(corpus()).decode()})
        runner = get("packets")
        result = runner.run("tcp dst port 80", data)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["packet_ids"], [2])
        self.assertEqual(result["segs"], [["out", "Paketler: 2\n"]])
        self.assertIn("libpcap", result["packet_backend"])
        step = {"stdin": data, "test": 'eq(eslesenler(), [2], "tam seçim")'}
        self.assertEqual(runner.test("tcp dst port 80", step)["status"], "pass")
        self.assertEqual(runner.test("tcp src port 80", step)["status"], "fail")

    def test_missing_tshark_has_installation_message(self):
        engine._display.cache_clear()
        with patch.object(engine, "tshark_path", return_value=None), self.assertRaisesRegex(engine.PacketError, "PAFTA_TSHARK"):
            engine.evaluate("tcp", corpus())


if __name__ == "__main__":
    unittest.main()
