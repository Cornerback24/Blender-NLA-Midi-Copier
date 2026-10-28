#!/usr/bin/env python3
"""Run the NLA Midi Copier regression suite.

From a shell, pass the Blender executable:

    python tests/run_tests.py /path/to/blender

That launches:

    blender -b --factory-startup --python tests/run_tests.py

The same script then installs this checkout as an extension, runs the MIDI
parser unit tests, and runs the headless Blender tests. Each test is reported
as PASS, FAIL, or SKIP. The process exits with status 1 when any test fails.

Parser tests can also be run without Blender:

    python -m unittest tests.test_midi_parser
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import traceback
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = Path(__file__).resolve()


def _inside_blender():
    try:
        import bpy  # noqa: F401
    except ImportError:
        return False
    return True


def _launch_blender(blender, results_path, from_test=None):
    import subprocess
    command = [
        str(blender),
        "-b",
        "--factory-startup",
        "--python",
        str(RUNNER),
        "--",
    ]
    if results_path is not None:
        command.extend(["--results", str(results_path)])
    if from_test:
        command.extend(["--from-test", from_test])
    print(" ".join(command), flush=True)
    completed = subprocess.run(command)
    return completed.returncode


def _zip_addon(destination):
    excluded = {".git", "images", "__pycache__", "tests", ".idea", "bpy"}
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            dirnames[:] = [name for name in dirnames if name not in excluded and not name.endswith(".egg-info")]
            for filename in filenames:
                if filename.endswith((".pyc", ".zip")) or filename.startswith("."):
                    continue
                full = Path(dirpath) / filename
                archive.write(full, full.relative_to(REPO_ROOT).as_posix())
    return destination


def _install_addon():
    import addon_utils
    import bpy

    handle = tempfile.NamedTemporaryFile(prefix="nla_midi_copier-", suffix=".zip", delete=False)
    handle.close()
    _zip_addon(handle.name)
    operator = bpy.ops.extensions.package_install_files
    arguments = {"filepath": handle.name, "repo": "user_default", "enable_on_install": True}
    try:
        result = operator(**arguments, overwrite=True)
    except TypeError:
        result = operator(**arguments)
    if result != {"FINISHED"}:
        raise RuntimeError(f"extension install returned {result}")

    match = None
    for module in addon_utils.modules():
        info = getattr(module, "bl_info", None) or {}
        if info.get("name") in ("NLA Midi Copier", "Blender NLA Midi Copier"):
            match = module
            break
    if match is None:
        raise RuntimeError("installed add-on module was not found")
    import importlib
    # addon_utils.modules() yields a bl_info stub. Import the package so submodules exist.
    loaded = importlib.import_module(match.__name__)
    enabled = addon_utils.check(match.__name__)[1]
    registered = hasattr(bpy.types.Scene, "nla_midi_copier_main_property_group")
    if enabled and not registered:
        addon_utils.disable(match.__name__)
        enabled = False
    if not enabled:
        addon_utils.enable(match.__name__, default_set=True, persistent=True)
        loaded = importlib.import_module(match.__name__)
    if not hasattr(loaded, "midi_data"):
        raise RuntimeError(f"{loaded.__name__} did not finish importing")
    return loaded


class _ParserResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.rows = []

    def _record(self, test, status, detail=""):
        self.rows.append({"name": test.id(), "status": status, "detail": detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", "".join(traceback.format_exception(*err)))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "FAIL", "".join(traceback.format_exception(*err)))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP", str(reason))


def _parser_rows():
    stream = open(os.devnull, "w")
    runner = unittest.TextTestRunner(stream=stream, resultclass=_ParserResult, verbosity=1)
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_midi_parser")
    result = runner.run(suite)
    stream.close()
    return result.rows


def _blender_rows(on_update=None, from_test=None):
    import tests.test_dope_sheet  # noqa: F401
    import tests.test_graph_editor  # noqa: F401
    import tests.test_nla  # noqa: F401
    import tests.test_properties_ui  # noqa: F401
    from tests.harness import TESTS
    from tests.support import SkipTest

    rows = []
    started = from_test is None
    for test in TESTS:
        if not started:
            if from_test not in test.__name__:
                continue
            started = True
        name = f"{test.__module__}.{test.__name__}"
        try:
            test()
        except SkipTest as exc:
            rows.append({"name": name, "status": "SKIP", "detail": str(exc)})
            print(f"SKIP {name}: {exc}", flush=True)
        except Exception as exc:
            detail = traceback.format_exc()
            rows.append({"name": name, "status": "FAIL", "detail": detail})
            print(f"FAIL {name}\n{detail}", flush=True)
        else:
            rows.append({"name": name, "status": "PASS", "detail": ""})
            print(f"PASS {name}", flush=True)
        if on_update is not None:
            on_update(rows)
    return rows


def _print_summary(rows):
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print("-" * 60)
    print(f"{counts['PASS']} passed, {counts['FAIL']} failed, {counts['SKIP']} skipped, {len(rows)} total")
    return counts


def _run_inside_blender(results_path, from_test=None):
    import bpy

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    module = _install_addon()
    from tests import runtime
    runtime.MOD = module

    print(f"\n=== NLA Midi Copier tests: Blender {bpy.app.version_string} ===", flush=True)
    rows = []
    parser_rows = _parser_rows()
    for row in parser_rows:
        print(f"{row['status']} {row['name']}", flush=True)
        if row["status"] == "FAIL":
            print(row["detail"], flush=True)
    rows.extend(parser_rows)

    def save(blender_rows):
        if results_path is None:
            return
        combined = rows + blender_rows
        counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        for item in combined:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        Path(results_path).write_text(json.dumps({
            "blender": bpy.app.version_string,
            "version": list(bpy.app.version),
            "passed": counts["PASS"],
            "failed": counts["FAIL"],
            "skipped": counts["SKIP"],
            "tests": combined,
        }, indent=2))

    rows.extend(_blender_rows(on_update=save, from_test=from_test))
    counts = _print_summary(rows)
    payload = {
        "blender": bpy.app.version_string,
        "version": list(bpy.app.version),
        "passed": counts["PASS"],
        "failed": counts["FAIL"],
        "skipped": counts["SKIP"],
        "tests": rows,
    }
    if results_path is not None:
        Path(results_path).write_text(json.dumps(payload, indent=2))
        print(f"wrote {results_path}")
    return 1 if counts["FAIL"] else 0


def main(argv):
    parser = argparse.ArgumentParser(description="Run the NLA Midi Copier regression suite.")
    parser.add_argument("blender", nargs="?", help="Path to a Blender executable. Required outside Blender.")
    parser.add_argument("--results", help="Write a JSON results file.")
    parser.add_argument("--from-test", help="Skip Blender tests before this substring. Parser tests still run.")
    if _inside_blender():
        if "--" in argv:
            argv = argv[argv.index("--") + 1:]
        else:
            argv = []
        args = parser.parse_args(argv)
        code = _run_inside_blender(args.results, args.from_test)
        raise SystemExit(code)

    args = parser.parse_args(argv)
    if not args.blender:
        parser.error("pass the path to a Blender executable")
    blender = Path(args.blender)
    if not blender.is_file():
        parser.error(f"Blender executable not found: {blender}")
    raise SystemExit(_launch_blender(blender, args.results, args.from_test))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
