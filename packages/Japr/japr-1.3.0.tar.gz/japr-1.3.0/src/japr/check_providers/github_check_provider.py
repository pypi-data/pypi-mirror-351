from japr.check import Check, CheckProvider, CheckFix, CheckResult, Result, Severity
from git import InvalidGitRepositoryError
from git.repo import Repo
import japr.template_util
import japr.util
import os
import yaml


class AddIssueTemplateFix(CheckFix):
    def fix(self, directory, _):
        os.makedirs(os.path.join(directory, ".github/ISSUE_TEMPLATE"), exist_ok=True)
        with open(os.path.join(directory, ".github/ISSUE_TEMPLATE/bug.md"), "w") as f:
            f.write(
                japr.template_util.template("bug_report_issue_template.md", directory)
            )
        with open(
            os.path.join(directory, ".github/ISSUE_TEMPLATE/feature_request.md"), "w"
        ) as f:
            f.write(
                japr.template_util.template(
                    "feature_request_issue_template.md", directory
                )
            )
        return True

    @property
    def success_message(self):
        return (
            "Created issue templates at .github/ISSUE_TEMPLATE/bug_report.md and"
            " .github/ISSUE_TEMPLATE/feature_request.md from a template. You should add"
            " your own content to it."
        )

    @property
    def failure_message(self):
        return (
            "Tried to create an issue template at .github/ISSUE_TEMPLATE/bug_report.md"
            " and .github/ISSUE_TEMPLATE/feature_request.md but was unable to."
        )


class AddPullRequestTemplateFix(CheckFix):
    def fix(self, directory, _):
        os.makedirs(os.path.join(directory, ".github"), exist_ok=True)
        with open(
            os.path.join(directory, ".github/pull_request_template.md"), "w"
        ) as f:
            f.write(japr.template_util.template("pull_request_template.md", directory))
        return True

    @property
    def success_message(self):
        return (
            "Created an issue template at .github/pull_request_template.md from a"
            " template. You should add your own content to it."
        )

    @property
    def failure_message(self):
        return (
            "Tried to create an issue template at .github/pull_request_template.md but"
            " was unable to."
        )


class GitHubCheckProvider(CheckProvider):
    def name(self):
        return "GitHub"

    def test(self, directory):
        try:
            repo = Repo(directory, search_parent_directories=True)
            github_is_origin = (
                "origin" in repo.remotes and "github" in repo.remote("origin").url
            )
        except InvalidGitRepositoryError:
            github_is_origin = False

        if not github_is_origin:
            yield CheckResult("GH001", Result.NOT_APPLICABLE)
            yield CheckResult("GH002", Result.NOT_APPLICABLE)
            return

        # https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates
        has_issue_template = any(
            [
                os.path.isfile(os.path.join(directory, "issue_template")),
                os.path.isfile(os.path.join(directory, "issue_template.md")),
                os.path.isfile(os.path.join(directory, "issue_template.yml")),
                os.path.isfile(os.path.join(directory, "docs/issue_template")),
                os.path.isfile(os.path.join(directory, "docs/issue_template.md")),
                os.path.isfile(os.path.join(directory, "docs/issue_template.yml")),
                os.path.isfile(os.path.join(directory, ".github/issue_template")),
                os.path.isfile(os.path.join(directory, ".github/issue_template.md")),
                os.path.isfile(os.path.join(directory, ".github/issue_template.yml")),
                os.path.isdir(os.path.join(directory, "issue_template")),
                os.path.isdir(os.path.join(directory, "docs/issue_template")),
                os.path.isdir(os.path.join(directory, ".github/issue_template")),
            ]
        )
        # https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
        has_pull_request_template = any(
            [
                os.path.isfile(os.path.join(directory, "pull_request_template")),
                os.path.isfile(os.path.join(directory, "pull_request_template.md")),
                os.path.isfile(os.path.join(directory, "docs/pull_request_template")),
                os.path.isfile(
                    os.path.join(directory, "docs/pull_request_template.md")
                ),
                os.path.isfile(
                    os.path.join(directory, ".github/pull_request_template")
                ),
                os.path.isfile(
                    os.path.join(directory, ".github/pull_request_template.md")
                ),
                os.path.isdir(os.path.join(directory, "pull_request_template")),
                os.path.isdir(os.path.join(directory, "docs/pull_request_template")),
                os.path.isdir(os.path.join(directory, ".github/pull_request_template")),
            ]
        )

        yield CheckResult(
            "GH001",
            Result.PASSED if has_issue_template else Result.FAILED,
            fix=AddIssueTemplateFix(),
        )
        yield CheckResult(
            "GH002",
            Result.PASSED if has_pull_request_template else Result.FAILED,
            fix=AddPullRequestTemplateFix(),
        )

        has_workflow_job = False
        if os.path.isdir(os.path.join(directory, ".github", "workflows")):
            workflows = list(
                japr.util.find_files_with_extension(
                    os.path.join(directory, ".github", "workflows"), "yaml"
                )
            )
            workflows.extend(
                japr.util.find_files_with_extension(
                    os.path.join(directory, ".github", "workflows"), "yml"
                )
            )

            for workflow in workflows:
                with open(workflow, "r") as f:
                    workflow_yaml = yaml.load(f, yaml.SafeLoader)

                    jobs = workflow_yaml.get("jobs", [])
                    if len(jobs) > 0:
                        has_workflow_job = True

                    has_job_timeouts = all(
                        "timeout-minutes" in jobs[job] for job in jobs
                    )

                    yield CheckResult(
                        "GH003",
                        Result.PASSED if has_job_timeouts else Result.FAILED,
                        file_path=workflow,
                    )

        if not has_workflow_job:
            yield CheckResult("GH003", Result.NOT_APPLICABLE)

    def checks(self):
        return [
            Check(
                "GH001",
                Severity.LOW,
                ["open-source", "inner-source"],
                "GitHub projects should have an issue template",
                """To help users create issues that are useful for you an issue template is recommended.

Create a .github/issue_template.md file and fill it with a template for users to use when filing issues.
See https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates""",
            ),
            Check(
                "GH002",
                Severity.LOW,
                ["open-source", "inner-source"],
                "GitHub projects should have a pull request template",
                """To help users create pull requests that are useful for you a pull request template is recommended.

Create a .github/pull_request_template.md file and fill it with a template for users to use when filing pull requests
See https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository""",
            ),
            Check(
                "GH003",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                "GitHub Actions workflows should have timeouts set",
                """Workflows for GitHub Actions must have timeouts set to avoid hefty charges getting incurred by stuck jobs. By default, the timeout is 6h which is lmost always unecessary

                Add the timeout-minutes property to your job
                See https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes""",
            ),
        ]
