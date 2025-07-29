from japr.check import Check, CheckProvider, CheckResult, Result, Severity
from git import InvalidGitRepositoryError
from git.repo import Repo
import os

IDE_DIRECTORIES = [".vs", ".idea", ".settings"]  # Visual Studio  # Intellij  # Eclipse

IDE_FILES = [".classpath", ".project"]  # Eclipse

IDE_FILE_EXTENSIONS = ["swp", "iml", "iws", "ipr"]  # Vim  # Intellij


class GitCheckProvider(CheckProvider):
    def name(self):
        return "Git"

    def test(self, directory):
        try:
            repo = Repo(directory, search_parent_directories=True)
            yield CheckResult("GI001", Result.PASSED)

            yield CheckResult(
                "GI002", Result.PASSED if "origin" in repo.remotes else Result.FAILED
            )
            yield CheckResult(
                "GI003", Result.PASSED if "master" not in repo.heads else Result.FAILED
            )
            yield CheckResult(
                "GI004",
                (
                    Result.PASSED
                    if os.path.isfile(os.path.join(directory, ".gitignore"))
                    else Result.FAILED
                ),
            )

            ds_store_paths = [
                f.path
                for f in repo.tree("HEAD").list_traverse()
                if f.type == "blob" and f.name == ".DS_Store"
            ]
            if len(ds_store_paths) != 0:
                for ds_store_path in ds_store_paths:
                    yield CheckResult("GI005", Result.FAILED, ds_store_path)
            else:
                yield CheckResult("GI005", Result.PASSED)

            ide_paths = [
                f.path
                for f in repo.tree("HEAD").list_traverse()
                if (f.type == "tree" and f.name in IDE_DIRECTORIES)
                or (f.type == "blob" and f.name in IDE_FILES)
                or (
                    f.type == "blob"
                    and os.path.splitext(f.name)[1] in IDE_FILE_EXTENSIONS
                )
            ]
            if len(ide_paths) != 0:
                for ide_path in ide_paths:
                    yield CheckResult("GI006", Result.FAILED, ide_path)
            else:
                yield CheckResult("GI006", Result.PASSED)

        except InvalidGitRepositoryError:
            yield CheckResult("GI001", Result.FAILED)
            yield CheckResult("GI002", Result.PRE_REQUISITE_CHECK_FAILED)
            yield CheckResult("GI003", Result.PRE_REQUISITE_CHECK_FAILED)
            yield CheckResult("GI004", Result.PRE_REQUISITE_CHECK_FAILED)
            yield CheckResult("GI005", Result.PRE_REQUISITE_CHECK_FAILED)
            yield CheckResult("GI006", Result.PRE_REQUISITE_CHECK_FAILED)

    def checks(self):
        return [
            Check(
                "GI001",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                "Projects should be tracked in Git version control",
                """All projects, even the smallest personal projects benefit from being tracked in Git as it provides branch management, backups and history to your project.

Run `git init` in this project to setup Git and then make a commit.""",
            ),
            Check(
                "GI002",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                "Projects in Git should have a remote copy in origin",
                """This project does not have a Git remote named 'origin' which suggests there is no backup copy of the project should it be lost.

Setup a Git repository on your favourite Git service (e.g. GitHub) and follow the instructions to add a remote to an existing project. The instructions will likely look like:

git remote add origin <your repository url>
git push origin main""",
            ),
            Check(
                "GI003",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                (
                    "Projects in Git should switch from a 'master' branch to a 'main'"
                    " branch"
                ),
                """This project has a branch named 'master' however it is now recommended to use a branch named 'main' to avoid culturally inappropriate language.

The following guide does a good job or describing the process and providing solutions to any issues you may have with this: https://www.git-tower.com/learn/git/faq/git-rename-master-to-main""",
            ),
            Check(
                "GI004",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "Projects in Git should have a .gitignore file",
                """.gitignore files help you avoid committing unwanted files into Git such as binaries or build artifacts. You should create a .gitignore file for this project.

You can find comprehensive examples for your chosen language here: https://github.com/github/gitignore""",
            ),
            Check(
                "GI005",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                "Avoid committing .DS_store files",
                """.DS_store files are OSX metadata files in a proprietary binary format. When committed to Git repositories they cause unnecessary changes and provide no value as they differ per machine.

You can tell git to ignore them from commits by adding them to your .gitignore.

You can also all them to your global .gitignore to avoid ever committing them in any repository. Configure a global .gitignore using the following:
git config --global core.excludesfile ~/.gitignore

To remove one from the current repository you can use:
git rm --cached ./path/to/.DS_Store""",
            ),
            Check(
                "GI006",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                "Avoid committing IDE related files/directories",
                """Many IDEs store IDE specific files with your project. When committed to Git repositories they cause unnecessary changes and provide no value as they differ per machine.

You can tell git to ignore them from commits by adding them to your .gitignore.

You can also all them to your global .gitignore to avoid ever committing them in any repository. Configure a global .gitignore using the following:
git config --global core.excludesfile ~/.gitignore

To remove one from the current repository you can use:
git rm --cached /path/to/file""",
            ),
        ]
