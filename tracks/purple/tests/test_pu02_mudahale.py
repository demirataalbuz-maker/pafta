"""PU02 madde 93 regresyonları: yanlış sıra, kanıt kaybı ve kök dışı yollar.

Kök klasörden: python tracks/purple/tests/test_pu02_mudahale.py
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from engine.lessons import Library  # noqa: E402
from engine.runners import get  # noqa: E402


class PU02MudahaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = get("purple")
        lesson = Library().lesson("purple", "pu02")
        cls.steps = [s for s in lesson["steps"] if s["kind"] == "gorev"]
        if len(cls.steps) != 5:
            raise AssertionError(f"PU02 görev sayısı değişti: {len(cls.steps)}")

    @staticmethod
    def detail(result):
        return {
            "status": result.get("status"),
            "error": result.get("error"),
            "failed": [c for c in result.get("checks", []) if not c["ok"]],
        }

    def run_code(self, step_index, code):
        return self.runner.test(code, self.steps[step_index])

    def evidence_functions(self):
        code = self.steps[4]["solution"].split("\n\nM = kanit_paketle", 1)[0]
        namespace = {}
        exec(compile(code, "pu02-solution", "exec"), namespace)
        return namespace

    @staticmethod
    def write_manifest(root, relative, data):
        manifest = {"dosyalar": [{"yol": relative, "boyut": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest()}]}
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_new_solutions_pass_and_starters_stay_rejected(self):
        for index in (2, 3, 4):
            step = self.steps[index]
            with self.subTest(step=step["title"], code="solution"):
                result = self.run_code(index, step["solution"])
                self.assertEqual(result.get("status"), "pass", self.detail(result))
            with self.subTest(step=step["title"], code="starter"):
                result = self.run_code(index, step["starter"])
                self.assertNotEqual(result.get("status"), "pass", "starter görevi geçmemeli")
                self.assertNotEqual(result.get("status"), "internal", self.detail(result))

    def test_reversed_playbook_order_is_rejected(self):
        solution = self.steps[2]["solution"]
        mutant = solution.replace("sonuc.append(ad)", "sonuc.insert(0, ad)")
        self.assertNotEqual(mutant, solution)
        result = self.run_code(2, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))

    def test_containment_without_evidence_is_rejected(self):
        solution = self.steps[3]["solution"]
        mutant = solution.replace('if not yeni["kanit_toplandi"]:', "if False:")
        self.assertNotEqual(mutant, solution)
        result = self.run_code(3, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))

    def test_mutating_original_incident_state_is_rejected(self):
        solution = self.steps[3]["solution"]
        mutant = solution.replace("yeni = copy.deepcopy(durum)", "yeni = durum")
        self.assertNotEqual(mutant, solution)
        result = self.run_code(3, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))

    def test_deleting_source_evidence_is_rejected(self):
        solution = self.steps[4]["solution"]
        mutant = solution.replace(
            "    return manifest\n\n\ndef kanit_yolu",
            "    shutil.rmtree(kaynak)\n    return manifest\n\n\ndef kanit_yolu",
        )
        self.assertNotEqual(mutant, solution)
        result = self.run_code(4, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))

    def test_accepting_changed_evidence_is_rejected(self):
        solution = self.steps[4]["solution"]
        old = 'if yol.stat().st_size != kayit["boyut"] or ozet(yol) != kayit["sha256"]:'
        mutant = solution.replace(old, "if False:")
        self.assertNotEqual(mutant, solution)
        result = self.run_code(4, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))

    def test_manifest_traversal_and_absolute_paths_are_rejected(self):
        verify = self.evidence_functions()["kanit_dogrula"]
        data = b"paket disindaki gecerli kanit baytlari\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "paket"
            root.mkdir()
            outside = Path(tmp) / "disarida.txt"
            outside.write_bytes(data)
            bad_paths = (
                "../disarida.txt",
                str(outside),
                outside.as_posix(),
                "C:disarida.txt",
                "C:/Windows/disarida.txt",
                "\\\\sunucu\\paylasim\\disarida.txt",
                "//sunucu/paylasim/disarida.txt",
                "notlar/../../disarida.txt",
                "notlar\\..\\disarida.txt",
            )
            for bad in bad_paths:
                with self.subTest(path=bad):
                    self.write_manifest(root, bad, data)
                    with self.assertRaises(ValueError):
                        verify(str(root))

    def test_symlink_escape_is_rejected_when_supported(self):
        verify = self.evidence_functions()["kanit_dogrula"]
        data = b"symlink hedefindeki paket disi kanit\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "paket"
            root.mkdir()
            outside = Path(tmp) / "disarida.txt"
            outside.write_bytes(data)
            try:
                os.symlink(outside, root / "bagli.txt")
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Bu ortam symlink kurmaya izin vermiyor: {exc}")
            self.write_manifest(root, "bagli.txt", data)
            with self.assertRaises(ValueError):
                verify(str(root))

    def test_auditors_unsafe_join_solution_is_rejected(self):
        solution = self.steps[4]["solution"]
        mutant = solution.replace(
            '        yol = kanit_yolu(hedef, kayit["yol"])',
            '        yol = os.path.join(hedef, *kayit["yol"].split("/"))\n'
            '        if not os.path.isfile(yol):\n'
            '            raise ValueError("Kanıt eksik")',
        ).replace("yol.stat().st_size", "os.path.getsize(yol)")
        self.assertNotIn("yol = kanit_yolu(hedef", mutant)
        result = self.run_code(4, mutant)
        self.assertNotEqual(result.get("status"), "pass", self.detail(result))


if __name__ == "__main__":
    unittest.main(verbosity=2)
