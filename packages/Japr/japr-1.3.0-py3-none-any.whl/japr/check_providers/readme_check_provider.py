from japr.check import Check, CheckProvider, CheckFix, CheckResult, Result, Severity
import japr.template_util
import os


class AddReadmeFix(CheckFix):
    def fix(self, directory, _):
        with open(os.path.join(directory, "README.md"), "w") as f:
            f.write(japr.template_util.template("README.md", directory))
        return True

    @property
    def success_message(self):
        return (
            "Created a README.md file in the root directory from a template. You should"
            " add your own content to it."
        )

    @property
    def failure_message(self):
        return (
            "Tried to create a README.md file in the root directory but was unable to."
        )


class ReadmeCheckProvider(CheckProvider):
    def name(self):
        return "Readme"

    def test(self, directory):
        if os.path.isfile(os.path.join(directory, "README.md")):
            readme_path = os.path.join(directory, "README.md")
        elif os.path.isfile(os.path.join(directory, "README")):
            readme_path = os.path.join(directory, "README")
        elif os.path.isfile(os.path.join(directory, "README.txt")):
            readme_path = os.path.join(directory, "README.txt")
        elif os.path.isfile(os.path.join(directory, "README.rst")):
            readme_path = os.path.join(directory, "README.rst")
        else:
            readme_path = None

        yield CheckResult(
            "RE001",
            Result.PASSED if readme_path is not None else Result.FAILED,
            fix=AddReadmeFix(),
        )

        if readme_path is not None:
            with open(readme_path, "r") as readme_file:
                content = readme_file.read()

            if readme_path.endswith(".rst"):
                yield CheckResult(
                    "RE002",
                    (
                        Result.PASSED
                        if content.find("Install\n=") != -1
                        or content.find("Setup\n=") != -1
                        or content.find("Getting Started\n=") != -1
                        or content.find("Quickstart\n=") != -1
                        else Result.FAILED
                    ),
                )
                yield CheckResult(
                    "RE003",
                    (
                        Result.PASSED
                        if content.find("Usage\n=") != -1
                        or content.find("How-to\n=") != -1
                        or content.find("API\n=") != -1
                        else Result.FAILED
                    ),
                )
            else:
                yield CheckResult(
                    "RE002",
                    (
                        Result.PASSED
                        if content.find("# Install") != -1
                        or content.find("# Setup") != -1
                        or content.find("# Getting Started") != -1
                        or content.find("# Quickstart") != -1
                        else Result.FAILED
                    ),
                )
                yield CheckResult(
                    "RE003",
                    (
                        Result.PASSED
                        if content.find("# Usage") != -1
                        or content.find("# How-to") != -1
                        or content.find("# API") != -1
                        else Result.FAILED
                    ),
                )
        else:
            yield CheckResult("RE002", Result.PRE_REQUISITE_CHECK_FAILED)
            yield CheckResult("RE003", Result.PRE_REQUISITE_CHECK_FAILED)

    def checks(self):
        return [
            Check(
                "RE001",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                (
                    "Projects should have a README.md file describing the project and"
                    " its use"
                ),
                """Create a README.md file in the root of the project and add content to describe to other users (or just your future self) things like:
- Why does this project exist?
- How do I install it?
- How do I use it?
- What configuration can be set?
- How do I build the source code?

See https://www.makeareadme.com/ for further guidance""",
            ),
            Check(
                "RE002",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "README.md should contain an Installation section",
                """To help users (and your future self) install your project/library you should provide an installation section in your README. Add the following to your readme:

## Installation
1. Do this
2. Now do this""",
            ),
            Check(
                "RE003",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "README.md should contain a Usage section",
                """To help users (and your future self) use your project/library you should provide a usage section in your README. Add the following to your readme:

## Usage
To do this thing:
1. Do this
2. Then run this""",
            ),
        ]
