import ast
from collections import Counter
from pathlib import Path


def extract_string_from_file(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def main():
    counter = Counter()
    for path in Path().rglob("*.py"):
        strings = extract_string_from_file(path)
        counter.update(strings)
    for s, n in counter.most_common():
        print(f"{s!r}: {n}")
