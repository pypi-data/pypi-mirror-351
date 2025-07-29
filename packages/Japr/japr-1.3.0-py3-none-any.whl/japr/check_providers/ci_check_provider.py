from japr.check import Check, CheckProvider, CheckResult, Result, Severity
import os


CI_PATHS = [
    ".gitlab-ci.yml",
    ".travis.yml",
    "appveyor.yml",
    ".appveyor.yml",
    "circle.yml",
    ".circleci/config.yml",
    "Jenkinsfile",
    ".drone.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    ".buildkite/pipeline.yml",
]


class CiCheckProvider(CheckProvider):
    def name(self):
        return "CI"

    def test(self, directory):
        ci_path = None

        for path in CI_PATHS:
            if os.path.isfile(os.path.join(directory, path)):
                ci_path = os.path.join(directory, path)
        if os.path.isdir(os.path.join(directory, ".github/workflows/")):
            ci_path = os.path.join(directory, ".github/workflows/")

        yield CheckResult(
            "CI001", Result.PASSED if ci_path is not None else Result.FAILED
        )

    def checks(self):
        return [
            Check(
                "CI001",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                (
                    "Projects should define a CI/CD pipeline to ensure code builds and"
                    " works correctly"
                ),
                """Consider creating a CI/CD pipeine for this project using a tool like GitHub Actions. A typical CI/CD pipeline should:
- Lint the code
- Build the code
- Run all tests
- Deploy any artifacts like NuGet packages/PyPI packages

If you are using GitHub and would like to get started with it, you can learn how to use it here: https://docs.github.com/en/actions/quickstart""",
            )
        ]
