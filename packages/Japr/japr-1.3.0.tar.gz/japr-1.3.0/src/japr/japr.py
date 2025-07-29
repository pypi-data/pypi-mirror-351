import argparse
from japr.check_providers import check_providers
from japr.check import Result, Severity
import json
import os
import sys
import time
import yaml


PROJECT_TYPES = ["open-source", "inner-source", "team", "personal"]


class Japr:
    def __init__(self, is_summary=False, is_profile=False, fix=False, is_json=False):
        self.is_summary = is_summary
        self.is_profile = is_profile
        self.fix = fix
        self.is_json = is_json

        if self.fix:
            self.is_summary = True

    def _print_result(self, result, check, profile_time, suppressed_checks):
        if (
            result.result == Result.FAILED and result.id not in suppressed_checks
        ) or self.is_profile:
            # Build up components then display for code clarity
            if result.result == Result.FAILED:
                emoji_block = "\N{CROSS MARK}"
            elif result.result == Result.PASSED:
                emoji_block = "\N{WHITE HEAVY CHECK MARK}"
            elif result.result == Result.PRE_REQUISITE_CHECK_FAILED:
                emoji_block = "\N{WHITE QUESTION MARK ORNAMENT}"
            else:
                emoji_block = "\N{HEAVY MINUS SIGN}"

            if check.severity == Severity.HIGH:
                severity_color = "\033[1;31m"
            elif check.severity == Severity.MEDIUM:
                severity_color = "\033[1;33m"
            else:
                severity_color = "\033[37m"

            profile_block = (str(round(profile_time * 1000)) + "ms").ljust(8)

            if result.file_path is not None:
                file_block = f"[{result.file_path}] "
            else:
                file_block = ""

            if result.fix is not None:
                fix_block = f" - A fix is available \N{WRENCH}"
            else:
                fix_block = ""

            if self.is_summary:
                print(
                    f"{severity_color}{check.severity.name.ljust(6)}\033[0;0m -"
                    f" \033[1m{check.id}\033[0;0m {file_block}{check.reason}"
                    f"{fix_block}"
                )
            elif self.is_profile:
                print(
                    f"{emoji_block} {severity_color}{check.severity.name.ljust(6)}\033[0;0m"
                    f" - {profile_block} - \033[1m{check.id}\033[0;0m"
                    f" {file_block}{check.reason}{fix_block}"
                )
            else:
                print(
                    f"{severity_color}{check.severity.name.ljust(6)}\033[0;0m -"
                    f" \033[1m{check.id}\033[0;0m {file_block}{check.reason}"
                    f"{fix_block}"
                )
                print()
                print(check.advice)
                print()
                print("-" * 10)

    def _print_fix_result(self, result):
        if result.is_fixed:
            print(f"\N{WHITE HEAVY CHECK MARK} {result.fix.success_message}")
        else:
            print(f"\N{CROSS MARK} {result.fix.failure_message}")

    def _print_json(
        self,
        issues,
        score,
        passed,
        failed,
        cannot_run,
        suppressed,
        fixed,
        failed_to_fix,
        suppressed_checks,
    ):
        out = {
            "results": [
                {
                    "id": result.id,
                    "result": result.result.name,
                    "filePath": result.file_path,
                    "isFixAvailable": result.fix is not None,
                    "severity": check.severity.name,
                    "reason": check.reason,
                    "advice": check.advice,
                    "isSuppressed": result.id in suppressed_checks,
                    "isFixed": result.is_fixed,
                }
                for (result, check, _) in issues
            ],
            "score": score,
            "passed": passed,
            "failed": failed,
            "cannotRun": cannot_run,
            "suppressed": suppressed,
            "fixed": fixed,
            "failedToFix": failed_to_fix,
        }
        print(json.dumps(out, indent=2))

    def _print_summary(
        self, score, passed, failed, cannot_run, suppressed, fixed, failed_to_fix
    ):
        print(
            "\033[1mProject score: "
            + "\N{GLOWING STAR}" * score
            + "\N{HEAVY MINUS SIGN}" * (5 - score)
            + "\033[0;0m"
        )

        print(
            f"\033[1m\033[1;32mPassed: {passed}\033[0;0m, \033[1m\033[1;31mFailed:"
            f" {failed}\033[0;0m, \033[1m\033[1;37mCannot Run Yet: {cannot_run},"
            f" Suppressed {suppressed}\033[0;0m"
        )

        if self.fix:
            print(
                f"\033[1m\033[1;32mFixed: {fixed}\033[0;0m, \033[1m\033[1;31mFailed to"
                f" Fix: {failed_to_fix}\033[0;0m"
            )

        if score == 5:
            print()
            print("\033[1mCongratulations on a fantastic score \U0001f389\033[0;0m")

    def check_directory(
        self,
        directory,
        project_type,
    ):
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            print(
                f"'{directory}' is not a valid directory so cannot be checked",
                file=sys.stderr,
            )
            return

        if os.path.isfile(os.path.join(directory, ".japr.yaml")):
            with open(os.path.join(directory, ".japr.yaml"), "r") as f:
                data = yaml.safe_load(f)
                try:
                    suppressed_checks = [
                        override["id"]
                        for override in data["override"]
                        if override["suppress"]
                    ]
                except KeyError:
                    suppressed_checks = []
                if project_type is None:
                    try:
                        project_type = data["projectType"]
                    except KeyError:
                        project_type = None
        else:
            suppressed_checks = []

        if project_type is None:
            print(
                (
                    "No project type specified. You can specify this with the -t flag"
                    " or add to your .japr.yaml configuration file."
                ),
                file=sys.stderr,
            )
            return

        if project_type not in PROJECT_TYPES:
            print(
                f"Invalid project type. Must be one of {', '.join(PROJECT_TYPES)}.",
                file=sys.stderr,
            )
            return

        issues = []
        for check_provider in check_providers:
            checks = {check.id: check for check in check_provider.checks()}

            results = check_provider.test(directory)

            # results is actually a generator so we can time how long it takes to make each result
            start = time.time()
            for result in results:
                end = time.time()
                try:
                    if project_type in checks[result.id].project_types:
                        check = checks[result.id]
                        profile_time = end - start
                        issues.append((result, check, profile_time))
                        if not self.is_json:
                            self._print_result(
                                result, check, profile_time, suppressed_checks
                            )
                        if (
                            self.fix
                            and result.result == Result.FAILED
                            and result.fix is not None
                        ):
                            result.is_fixed = result.fix.fix(
                                directory, result.file_path
                            )
                            if not self.is_json:
                                self._print_fix_result(result)
                except KeyError:
                    raise Exception(
                        f"Check {result.id} is not defined in the"
                        f" {check_provider.name()} check provider but a result was"
                        " returned for it. Ensure the result is returning the correct"
                        " ID and the check is defined correctly in the provider."
                    )
                start = time.time()

        sev_bad_checks = sum(
            check.severity.value
            for (result, check, _) in issues
            if result.result == Result.FAILED
            or result.result == Result.PRE_REQUISITE_CHECK_FAILED
        )
        sev_all_checks = sum(check.severity.value for (_, check, _) in issues)
        score = int(5 - sev_bad_checks / sev_all_checks * 5)

        passed = len(
            [
                result
                for (result, _, _) in issues
                if result.result == Result.PASSED and result.id not in suppressed_checks
            ]
        )
        failed = len(
            [
                result
                for (result, _, _) in issues
                if result.result == Result.FAILED and result.id not in suppressed_checks
            ]
        )
        cannot_run = len(
            [
                result
                for (result, _, _) in issues
                if result.result == Result.PRE_REQUISITE_CHECK_FAILED
                and result.id not in suppressed_checks
            ]
        )
        suppressed = len(
            [result for (result, _, _) in issues if result.id in suppressed_checks]
        )
        fixed = len([result for (result, _, _) in issues if result.is_fixed])
        failed_to_fix = len(
            [result for (result, _, _) in issues if result.is_fixed == False]
        )

        if self.is_json:
            self._print_json(
                issues,
                score,
                passed,
                failed,
                cannot_run,
                suppressed,
                fixed,
                failed_to_fix,
                suppressed_checks,
            )
        else:
            print()
            self._print_summary(
                score, passed, failed, cannot_run, suppressed, fixed, failed_to_fix
            )
            print()

        if self.fix:
            return failed_to_fix == 0
        else:
            return failed == 0


def cli(args=None):
    parser = argparse.ArgumentParser(
        prog="japr",
        description=(
            "A cross-language tool for rating the overall quality of open source,"
            " commercial and personal projects"
        ),
    )

    parser.add_argument("directory", help="the directory to scan")
    parser.add_argument(
        "-t",
        "--project-type",
        help="the type of project being scanned",
        choices=PROJECT_TYPES,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--profile", help="times how long each check takes to run", action="store_true"
    )
    group.add_argument(
        "-s", "--summary", help="prints results in summary form", action="store_true"
    )
    group.add_argument(
        "--fix", help="experimentally try to fix issues found", action="store_true"
    )
    group.add_argument("--json", help="output results as JSON", action="store_true")

    args = parser.parse_args(args)

    japr = Japr(
        args.summary,
        args.profile,
        args.fix,
        args.json,
    )

    if japr.check_directory(
        args.directory,
        args.project_type,
    ):
        quit(0)
    else:
        quit(1)
