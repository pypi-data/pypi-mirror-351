from japr.check import Check, CheckProvider, CheckResult, Result, Severity
import os


class LicenseCheckProvider(CheckProvider):
    def name(self):
        return "License"

    def test(self, directory):
        yield CheckResult(
            "LI001",
            (
                Result.PASSED
                if any(
                    [
                        os.path.isfile(os.path.join(directory, "LICENSE.md")),
                        os.path.isfile(os.path.join(directory, "LICENSE")),
                        os.path.isfile(os.path.join(directory, "LICENSE.txt")),
                        os.path.isfile(os.path.join(directory, "LICENSE.rst")),
                    ]
                )
                else Result.FAILED
            ),
        )

    def checks(self):
        return [
            Check(
                "LI001",
                Severity.MEDIUM,
                ["open-source", "personal"],
                (
                    "Projects should have a LICENSE.md file describing how the project"
                    " can be used"
                ),
                """Create a LICENSE.md file in the root of the project and add content to describe to other users how this project can be used

If you are not familiar with the different licenses available to you, try https://choosealicense.com which guides you through the choice.""",
            )
        ]
