from japr.check import Check, CheckProvider, CheckResult, Result, Severity
import japr.util
from git import InvalidGitRepositoryError
from git.repo import Repo
import os


class RustCheckProvider(CheckProvider):
    def name(self):
        return "Rust"

    def test(self, directory):
        cargo_tomls = list(japr.util.find_files_with_name(directory, "Cargo.toml"))

        try:
            repo = Repo(directory, search_parent_directories=True)
        except InvalidGitRepositoryError:
            repo = None  # Deal with later when we know what checks we're doing

        if len(cargo_tomls) != 0:
            for cargo_toml in cargo_tomls:
                # Check lock file is committed into Git
                if repo is not None:
                    lock_file = os.path.join(os.path.split(cargo_toml)[0], "Cargo.lock")
                    is_file_committed = any(
                        f.type == "blob"
                        and os.path.join(repo.working_dir, f.path) == lock_file
                        for f in repo.tree("HEAD").list_traverse()
                    )
                    yield CheckResult(
                        "RS004",
                        Result.PASSED if is_file_committed else Result.FAILED,
                        cargo_toml,
                    )
                else:
                    yield CheckResult(
                        "RS004",
                        Result.PRE_REQUISITE_CHECK_FAILED,
                        cargo_toml,
                    )
        else:
            yield CheckResult("RS004", Result.NOT_APPLICABLE)

    def checks(self):
        return [
            Check(
                "RS004",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                "Rust projects should have their Cargo lock files committed into Git",
                """When using Cargo for Rust, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed.""",
            ),
        ]
