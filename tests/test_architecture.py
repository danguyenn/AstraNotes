"""Architecture fitness tests (NFR-3 + Working Agreement).

These parse the source with the `ast` module and fail the build if the layer
boundaries from the Week 4.2 class diagram are violated. The import direction
must always point downward: web -> services -> storage -> domain. Nothing
imports upward, and route handlers never reach into storage or domain directly.
"""

import ast
import pathlib

import astranotes

ROOT = pathlib.Path(astranotes.__file__).resolve().parent
LAYERS = {"domain": 0, "storage": 1, "services": 2, "web": 3}


def _modules():
    for path in ROOT.rglob("*.py"):
        parts = path.relative_to(ROOT).with_suffix("").parts
        yield path, parts


def _astranotes_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("astranotes")
        ):
            yield node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("astranotes"):
                    yield alias.name


def test_no_upward_layer_imports():
    violations = []
    for path, parts in _modules():
        source_layer = LAYERS.get(parts[0])
        if source_layer is None:
            continue  # shared leaf (config, errors, timeutil, wsgi)
        for module in _astranotes_imports(path):
            target = module.split(".")[1:]
            if not target:
                continue
            target_layer = LAYERS.get(target[0])
            if target_layer is not None and target_layer > source_layer:
                violations.append(f"{'.'.join(parts)} imports {module}")
    assert not violations, f"Upward layer imports found: {violations}"


def test_routes_never_import_storage_or_domain_directly():
    violations = []
    for path, parts in _modules():
        if parts[:2] != ("web", "routes"):
            continue
        for module in _astranotes_imports(path):
            head = module.split(".")[1:2]
            if head and head[0] in ("storage", "domain"):
                violations.append(f"{'.'.join(parts)} imports {module}")
    assert not violations, f"Routes reaching past the service layer: {violations}"


def test_domain_depends_on_nothing_above_itself():
    for path, parts in _modules():
        if parts[0] != "domain":
            continue
        for module in _astranotes_imports(path):
            head = module.split(".")[1:2]
            assert not (head and head[0] in ("storage", "services", "web")), (
                f"domain module {'.'.join(parts)} imports {module}"
            )
