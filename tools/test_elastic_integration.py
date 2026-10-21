"""Reading-track API contract with disposable progress and no Elastic server."""
import json
import os
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import server


class ElasticIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="pafta_elastic_test_")
        cls.environment = patch.dict(os.environ, {"PAFTA_DATA": cls.temp.name})
        cls.environment.start()
        cls.app, cls.httpd = server.start(0)
        cls.base = f"http://127.0.0.1:{cls.app.port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.environment.stop()
        cls.temp.cleanup()

    def request(self, path, payload=None):
        headers = {"X-Pafta-Token": self.app.token, "Origin": self.base}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def test_catalog_and_native_languages_remain_distinct(self):
        state = self.request("/api/state")
        info = next(t for t in state["tracks"] if t["id"] == "elastic")
        self.assertEqual(info["status"], "active")
        self.assertTrue(info["hazir"])
        self.assertEqual(info["lessons_total"], 18)
        self.assertEqual(info["dil"], "python")
        self.assertEqual(info["okuma_dili"], "elastic")
        kusto = next(t for t in state["tracks"] if t["id"] == "kql")
        self.assertIn("Kusto", kusto["name"])
        for lesson_id, language in (("el01", "kibana"), ("el07", "lucene"), ("el13", "eql")):
            with self.subTest(lesson=lesson_id):
                view = self.request(f"/api/lesson/elastic/{lesson_id}")
                self.assertEqual(view["track"]["okuma_dili"], "elastic")
                prediction = next(s for s in view["lesson"]["steps"] if s["kind"] == "tahmin")
                self.assertEqual(prediction["code_dil"], language)
                self.assertTrue(prediction["code"])
                for step in view["lesson"]["steps"]:
                    self.assertFalse({"gercek", "test", "solution", "setup"} & step.keys())

    def test_fixed_guess_does_not_invoke_a_query_engine(self):
        for lesson_id in ("el01", "el07", "el13", "el18"):
            lesson = self.app.lib.lesson("elastic", lesson_id)
            index = next(i for i, s in enumerate(lesson["steps"]) if s["kind"] == "tahmin")
            step = lesson["steps"][index]
            payload = {"track": "elastic", "lesson": lesson_id, "step": index}
            # Native queries must use the author's fixed answer. Accidentally
            # passing one to Python (or a future fake query evaluator) fails here.
            with patch.object(self.app, "runner_for", side_effect=AssertionError("native query executed")):
                wrong = self.request("/api/guess", dict(payload, guess="__wrong__"))
                right = self.request("/api/guess", dict(payload, guess=step["gercek"]))
            self.assertFalse(wrong["correct"])
            self.assertTrue(right["correct"], right)
            self.assertEqual(right["expected"], server.normalize(step["gercek"]))

    def test_python_grading_and_saved_review(self):
        lesson = self.app.lib.lesson("elastic", "el01")
        index = next(i for i, s in enumerate(lesson["steps"]) if s["kind"] == "gorev")
        task = lesson["steps"][index]
        payload = {"track": "elastic", "lesson": "el01", "step": index}
        failed = self.request("/api/check", dict(payload, code=task["starter"]))
        self.assertNotEqual(failed["status"], "pass")
        passed = self.request("/api/check", dict(payload, code=task["solution"]))
        self.assertEqual(passed["status"], "pass", passed)
        run = self.request("/api/run", {"track": "elastic", "code": 'print("Python alıştırması")'})
        self.assertEqual(run["status"], "ok", run)
        self.assertEqual("".join(t for k, t in run["segs"] if k == "out"), "Python alıştırması\n")
        progress_path = Path(self.app.prog.path)
        self.assertTrue(progress_path.is_relative_to(Path(self.temp.name)))
        saved = json.loads(progress_path.read_text(encoding="utf-8"))
        track = saved["tracks"]["elastic"]
        self.assertTrue(track["steps"][f"el01:{index}"]["done"])
        self.assertIn(f"el01:{index}", track["review"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
