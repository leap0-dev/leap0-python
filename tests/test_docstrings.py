from __future__ import annotations

import ast
from pathlib import Path


SDK_ROOT = Path(__file__).resolve().parents[1] / "leap0"
STRICT_SECTION_DIRS = {"_sync", "_async"}


def _iter_missing_public_docstrings() -> list[str]:
    missing: list[str] = []
    for path in SDK_ROOT.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        rel = path.relative_to(SDK_ROOT)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                if not ast.get_docstring(node):
                    missing.append(f"{rel}:{node.name}")

            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                        if not ast.get_docstring(item):
                            missing.append(f"{rel}:{node.name}.{item.name}")
    return missing


def _iter_docstring_section_failures() -> list[str]:
    failures: list[str] = []
    for path in SDK_ROOT.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        rel = path.relative_to(SDK_ROOT)
        if rel.parts[0] not in STRICT_SECTION_DIRS:
            continue

        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                doc = ast.get_docstring(node) or ""
                if rel.parts[0] in STRICT_SECTION_DIRS and "Attributes:" not in doc:
                    failures.append(f"{rel}:{node.name} missing Attributes")

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                        doc = ast.get_docstring(item) or ""
                        args = [a.arg for a in item.args.args + item.args.kwonlyargs if a.arg != "self" and a.arg != "cls"]
                        if args and "Args:" not in doc:
                            failures.append(f"{rel}:{node.name}.{item.name} missing Args")
                        returns_none = False
                        if item.returns is None:
                            returns_none = True
                        elif isinstance(item.returns, ast.Constant) and item.returns.value is None:
                            returns_none = True
                        if not returns_none and "Returns:" not in doc and "Yields:" not in doc:
                            failures.append(f"{rel}:{node.name}.{item.name} missing Returns/Yields")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                doc = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args + node.args.kwonlyargs]
                if args and "Args:" not in doc:
                    failures.append(f"{rel}:{node.name} missing Args")
                returns_none = False
                if node.returns is None:
                    returns_none = True
                elif isinstance(node.returns, ast.Constant) and node.returns.value is None:
                    returns_none = True
                if not returns_none and "Returns:" not in doc and "Yields:" not in doc:
                    failures.append(f"{rel}:{node.name} missing Returns/Yields")
    return failures


def test_public_sdk_apis_have_docstrings() -> None:
    missing = _iter_missing_public_docstrings()
    assert missing == [], "Missing docstrings:\n" + "\n".join(missing)


def test_public_sdk_docstrings_have_expected_sections() -> None:
    failures = _iter_docstring_section_failures()
    assert failures == [], "Docstring section failures:\n" + "\n".join(failures)
