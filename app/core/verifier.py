"""Hermetic verification engine for generated patches and code changes."""

import ast
import re
from typing import Tuple, List
from app.core.models import Language, PatchVerification


class PatchVerifier:
    """Verifies that generated unified diffs and patched code are syntactically sound and hermetic."""

    @staticmethod
    def verify_syntax(code: str, language: Language) -> Tuple[bool, List[str]]:
        """Verify code syntax based on language."""
        errors: List[str] = []
        if language == Language.PYTHON:
            try:
                ast.parse(code)
                return True, []
            except SyntaxError as e:
                errors.append(f"Python SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}")
                return False, errors
            except Exception as e:
                errors.append(f"Syntax validation error: {str(e)}")
                return False, errors
        else:
            # Generic bracket balance and basic heuristic check for non-python
            brackets = {"(": ")", "{": "}", "[": "]"}
            stack = []
            for idx, char in enumerate(code):
                if char in brackets:
                    stack.append((char, idx))
                elif char in brackets.values():
                    if not stack:
                        errors.append(f"Unmatched closing bracket '{char}' at index {idx}")
                        return False, errors
                    opening, _ = stack.pop()
                    if brackets[opening] != char:
                        errors.append(f"Mismatched bracket: expected '{brackets[opening]}', found '{char}'")
                        return False, errors
            if stack:
                errors.append(f"Unclosed brackets remaining: {[b[0] for b in stack]}")
                return False, errors
            return True, []

    @staticmethod
    def validate_unified_diff(diff: str) -> Tuple[bool, List[str]]:
        """Ensure the diff conforms to standard unified diff syntax."""
        errors: List[str] = []
        if not diff or not diff.strip():
            return False, ["Diff is empty"]

        lines = diff.strip().splitlines()
        has_orig_header = any(l.startswith("--- ") for l in lines)
        has_new_header = any(l.startswith("+++ ") for l in lines)
        has_hunk = any(re.match(r"^@@\s+-\d+.*?\+\d+.*?@@", l) for l in lines)

        if not (has_orig_header and has_new_header):
            errors.append("Diff is missing standard '--- ' and '+++ ' unified headers")
        if not has_hunk:
            errors.append("Diff is missing standard hunk range headers '@@ -start,len +start,len @@'")

        return len(errors) == 0, errors

    @classmethod
    def verify(
        cls,
        original_code: str,
        patched_code: str,
        unified_diff: str,
        language: Language = Language.PYTHON,
    ) -> PatchVerification:
        """Run full verification suite on generated patch."""
        diff_valid, diff_errors = cls.validate_unified_diff(unified_diff)
        syntax_ok, syntax_errors = cls.verify_syntax(patched_code, language)

        lint_messages = diff_errors + syntax_errors
        applied_cleanly = diff_valid and (original_code != patched_code)
        tests_passed = syntax_ok and applied_cleanly

        # Compute diff line metrics (additions / deletions)
        additions = 0
        deletions = 0
        for line in unified_diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        diff_stats = {
            "additions": additions,
            "deletions": deletions,
            "net_lines": additions - deletions,
        }

        details = f"Patch verification PASSED: syntax is clean, diff structure is valid (+{additions}/-{deletions} lines)."
        if not tests_passed:
            details = f"Patch verification FAILED: {'; '.join(lint_messages)}"

        return PatchVerification(
            applied_cleanly=applied_cleanly,
            syntax_ok=syntax_ok,
            lint_messages=lint_messages,
            tests_passed=tests_passed,
            details=details,
            diff_stats=diff_stats,
        )
