"""Audit single Python reading-exercise faults; this is not an Elastic backend.

Comparisons at a numeric/time boundary and AND/OR combinations are changed one
at a time. A survivor needs an added counterexample or a documented equivalence.
Run `python tools/audit_elastic_mutations.py [el01 ...]` from the project folder.
"""
import ast
import copy
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.lessons import Library
from engine.runners import get


def mutations(source):
    tree = ast.parse(source)
    replacements = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt}
    nodes = list(ast.walk(tree))
    for index, node in enumerate(nodes):
        if isinstance(node, ast.Compare):
            for position, operator in enumerate(node.ops):
                if type(operator) not in replacements:
                    continue
                mutated = copy.deepcopy(tree)
                changed = list(ast.walk(mutated))[index]
                changed.ops[position] = replacements[type(operator)]()
                yield f"s.{node.lineno} {type(operator).__name__} -> {replacements[type(operator)].__name__}", ast.unparse(mutated)
        elif isinstance(node, ast.BoolOp):
            changed_type = ast.Or if isinstance(node.op, ast.And) else ast.And
            mutated = copy.deepcopy(tree)
            list(ast.walk(mutated))[index].op = changed_type()
            yield f"s.{node.lineno} {type(node.op).__name__} -> {changed_type.__name__}", ast.unparse(mutated)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    library = Library()
    wanted = set(sys.argv[1:])
    tasks, jobs = [], []
    for lesson_id in library.outline("elastic")["order"]:
        if wanted and lesson_id not in wanted:
            continue
        for index, step in enumerate(library.lesson("elastic", lesson_id)["steps"]):
            if step["kind"] != "gorev":
                continue
            reference = f"{lesson_id}:{index}"
            tasks.append((reference, step))
            jobs.extend((reference, step, label, code) for label, code in mutations(step["solution"]))
    def original(job):
        reference, step = job
        return reference, get("python").test(step["solution"], step)
    with ThreadPoolExecutor(max_workers=6) as pool:
        baseline = list(pool.map(original, tasks))
    invalid = [(ref, result) for ref, result in baseline if result["status"] != "pass"]
    if invalid:
        for reference, result in invalid:
            print("ORIGINAL FAILED", reference, result)
        return 1
    def check(job):
        reference, step, label, code = job
        return reference, label, get("python").test(code, step)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(check, jobs))
    survivors = [(ref, label) for ref, label, result in results if result["status"] == "pass"]
    unexpected = [(ref, label, result["status"]) for ref, label, result in results
                  if result["status"] not in ("pass", "fail")]
    rejected = sum(result["status"] == "fail" for _, _, result in results)
    print(f"{len(tasks)} original solutions pass; {len(jobs)} single mutations; "
          f"{rejected} rejected with fail; {len(survivors)} survivors; {len(unexpected)} unexpected statuses")
    for reference, label in survivors:
        print("SURVIVED", reference, label)
    for reference, label, status in unexpected:
        print("UNEXPECTED", reference, label, status)
    return bool(survivors or unexpected)


if __name__ == "__main__":
    sys.exit(main())
