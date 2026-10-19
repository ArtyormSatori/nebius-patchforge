"""Tests for hermetic patch verifier."""

from app.core.models import Language
from app.core.verifier import PatchVerifier


def test_syntax_checker_python_valid():
    code = "def foo():\n    return 42\n"
    ok, errors = PatchVerifier.verify_syntax(code, Language.PYTHON)
    assert ok is True
    assert len(errors) == 0


def test_syntax_checker_python_invalid():
    code = "def foo(\n    broken syntax"
    ok, errors = PatchVerifier.verify_syntax(code, Language.PYTHON)
    assert ok is False
    assert len(errors) > 0


def test_syntax_checker_generic_brackets():
    valid_js = "function add(a, b) { return a + b; }"
    ok, errors = PatchVerifier.verify_syntax(valid_js, Language.JAVASCRIPT)
    assert ok is True

    invalid_js = "function add(a, b) { return (a + b; }"
    ok, errors = PatchVerifier.verify_syntax(invalid_js, Language.JAVASCRIPT)
    assert ok is False
    assert len(errors) > 0


def test_unified_diff_validation():
    valid_diff = """--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
-foo = 1
+foo = 2
"""
    ok, errors = PatchVerifier.validate_unified_diff(valid_diff)
    assert ok is True
    assert len(errors) == 0


def test_patch_verifier_full_suite():
    orig = "x = 1\n"
    patched = "x = 2\n"
    diff = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-x = 1
+x = 2
"""
    ver = PatchVerifier.verify(orig, patched, diff, Language.PYTHON)
    assert ver.applied_cleanly is True
    assert ver.syntax_ok is True
    assert ver.tests_passed is True
    assert ver.diff_stats["additions"] == 1
    assert ver.diff_stats["deletions"] == 1
    assert ver.diff_stats["net_lines"] == 0
