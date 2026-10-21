"""Elastic reading track: structure, Python exercises and fixed answer consistency.

These checks do NOT execute queries in Elasticsearch. A prediction's hidden
`test` block is a small independent Python reader of its declared JSON corpus;
it verifies the hand-authored `gercek` answer, not arbitrary query semantics.
"""
import json
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.lessons import Library, public_step
from engine.runners import get


class ElasticCurriculumTests(unittest.TestCase):
    def setUp(self):
        self.library = Library()
        self.outline = self.library.outline("elastic")

    def test_catalog_and_source_contract(self):
        self.assertEqual(self.outline["runner"], "python")
        self.assertEqual(self.outline["okuma_dili"], "elastic")
        self.assertEqual(self.outline["order"], [f"el{i:02}" for i in range(1, 19)])
        self.assertEqual({m["rank"] for m in self.outline["modules"]},
                         {r["id"] for r in self.outline["ranks"]})
        self.assertEqual(len(self.outline["modules"]), 6)
        for path in (ROOT / "tracks" / "elastic").rglob("*"):
            if path.is_file():
                data = path.read_bytes()
                self.assertNotIn(b"\r", data, str(path))
                self.assertFalse(data.startswith(b"\xef\xbb\xbf"), str(path))
                data.decode("utf-8")
        for number, lesson_id in enumerate(self.outline["order"], 1):
            with self.subTest(lesson=lesson_id):
                lesson = self.library.lesson("elastic", lesson_id)
                self.assertEqual(lesson["id"], lesson_id)
                predictions = [s for s in lesson["steps"] if s["kind"] == "tahmin"]
                self.assertTrue(predictions)
                tasks = [s for s in lesson["steps"] if s["kind"] == "gorev"]
                self.assertGreaterEqual(len(tasks), 2)
                for prediction in predictions:
                    expected_language = "kibana" if number <= 6 else "lucene" if number <= 12 else "eql"
                    self.assertEqual(prediction["code_dil"], expected_language)
                    self.assertTrue(prediction["code"])
                    self.assertTrue(prediction["gercek"])
                    self.assertTrue(prediction["test"])
                    self.assertIn("???", prediction["body"])
                    json.loads(prediction["stdin"])
                    public = public_step(prediction)
                    for secret in ("gercek", "test", "solution"):
                        self.assertNotIn(secret, public)
                for task in tasks:
                    for key in ("test", "solution", "starter", "hints"):
                        self.assertTrue(task[key], (lesson_id, key))

    def test_fixed_prediction_answers_match_declared_python_models(self):
        jobs = [(lesson_id, step) for lesson_id in self.outline["order"]
                for step in self.library.lesson("elastic", lesson_id)["steps"]
                if step["kind"] == "tahmin"]
        def check(job):
            lesson_id, step = job
            result = get("python").run(step["test"], step["stdin"])
            output = "".join(text for kind, text in result.get("segs", []) if kind == "out")
            return lesson_id, step, result, output
        with ThreadPoolExecutor(max_workers=6) as pool:
            for lesson_id, step, result, output in pool.map(check, jobs):
                with self.subTest(lesson=lesson_id):
                    self.assertEqual(result["status"], "ok", result)
                    self.assertEqual(output.strip(), step["gercek"].strip())

    def test_exercise_solutions_pass_and_starters_do_not(self):
        jobs = [(lesson_id, index, step) for lesson_id in self.outline["order"]
                for index, step in enumerate(self.library.lesson("elastic", lesson_id)["steps"])
                if step["kind"] == "gorev"]
        def check(job):
            lesson_id, index, step = job
            return lesson_id, index, get("python").test(step["solution"], step), get("python").test(step["starter"], step)
        with ThreadPoolExecutor(max_workers=6) as pool:
            for lesson_id, index, solution, starter in pool.map(check, jobs):
                with self.subTest(lesson=lesson_id, step=index):
                    self.assertEqual(solution["status"], "pass", solution)
                    self.assertNotEqual(starter["status"], "pass", starter)


if __name__ == "__main__":
    unittest.main(verbosity=2)
