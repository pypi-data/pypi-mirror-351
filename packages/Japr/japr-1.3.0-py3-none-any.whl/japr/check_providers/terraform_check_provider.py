from japr.check import Check, CheckProvider, CheckResult, Result, Severity
import japr.util
from git import InvalidGitRepositoryError
from git.repo import Repo
import os


def _is_subdir(path, directory):
    path = os.path.realpath(path)
    directory = os.path.realpath(directory)

    relative = os.path.relpath(path, directory)

    if relative.startswith(os.pardir):
        return False
    else:
        return True


class TerraformCheckProvider(CheckProvider):
    def name(self):
        return "Terraform"

    def test(self, directory):
        terraform_locks = list(
            japr.util.find_files_with_name(directory, ".terraform.lock.hcl")
        )

        try:
            repo = Repo(directory, search_parent_directories=True)
        except InvalidGitRepositoryError:
            repo = None  # Deal with later when we know what checks we're doing

        if len(terraform_locks) != 0:
            for terraform_lock in terraform_locks:
                # Check lock file is committed into Git
                if repo is not None:
                    is_file_committed = any(
                        f.type == "blob"
                        and os.path.join(repo.working_dir, f.path) == terraform_lock
                        for f in repo.tree("HEAD").list_traverse()
                    )
                    yield CheckResult(
                        "TF004",
                        Result.PASSED if is_file_committed else Result.FAILED,
                        terraform_lock,
                    )

                    dot_terraform_dir = os.path.join(
                        os.path.dirname(terraform_lock), ".terraform"
                    )
                    is_dot_terraform_dir_committed = any(
                        f.type == "tree"
                        and os.path.join(repo.working_dir, f.path) == dot_terraform_dir
                        for f in repo.tree("HEAD").list_traverse()
                    )
                    yield CheckResult(
                        "TF005",
                        (
                            Result.PASSED
                            if not is_dot_terraform_dir_committed
                            else Result.FAILED
                        ),
                        dot_terraform_dir,
                    )
                else:
                    yield CheckResult(
                        "TF004",
                        Result.PRE_REQUISITE_CHECK_FAILED,
                        terraform_lock,
                    )
                    yield CheckResult(
                        "TF005",
                        Result.PRE_REQUISITE_CHECK_FAILED,
                        terraform_lock,
                    )
        else:
            yield CheckResult("TF004", Result.NOT_APPLICABLE)
            yield CheckResult("TF005", Result.NOT_APPLICABLE)

        terraform_state_files = list(
            japr.util.find_files_with_extension(directory, ".tfstate")
        )
        if len(terraform_state_files) != 0:
            for terraform_state_file in terraform_state_files:
                # Check state file is not committed into Git
                if repo is not None:
                    is_file_committed = any(
                        f.type == "blob"
                        and os.path.join(repo.working_dir, f.path)
                        == terraform_state_file
                        for f in repo.tree("HEAD").list_traverse()
                    )
                    yield CheckResult(
                        "TF006",
                        Result.PASSED if not is_file_committed else Result.FAILED,
                        terraform_state_file,
                    )
                else:
                    yield CheckResult(
                        "TF006",
                        Result.PRE_REQUISITE_CHECK_FAILED,
                        terraform_state_file,
                    )
        else:
            yield CheckResult("TF006", Result.NOT_APPLICABLE)

        terraform_files = list(japr.util.find_files_with_extension(directory, ".tf"))
        terraform_dirs = set(
            [os.path.dirname(terraform_file) for terraform_file in terraform_files]
        )
        if len(terraform_dirs) != 0:
            for terraform_dir in terraform_dirs:
                # Check required files are present
                has_main_file = (
                    os.path.join(terraform_dir, "main.tf") in terraform_files
                )
                yield CheckResult(
                    "TF007",
                    Result.PASSED if has_main_file else Result.FAILED,
                    terraform_dir,
                )
                has_outputs_file = (
                    os.path.join(terraform_dir, "outputs.tf") in terraform_files
                )
                yield CheckResult(
                    "TF008",
                    Result.PASSED if has_outputs_file else Result.FAILED,
                    terraform_dir,
                )
                has_variables_file = (
                    os.path.join(terraform_dir, "variables.tf") in terraform_files
                )
                yield CheckResult(
                    "TF009",
                    Result.PASSED if has_variables_file else Result.FAILED,
                    terraform_dir,
                )

                # If we're a subdir of any other directory there should be a /modules/ directory between us
                # Find closest parent from the other dirs
                closest_parent = None
                for other_dir in terraform_dirs:
                    if terraform_dir != other_dir and _is_subdir(
                        terraform_dir, other_dir
                    ):
                        if closest_parent is None or _is_subdir(
                            closest_parent, other_dir
                        ):
                            closest_parent = other_dir

                if closest_parent is not None:
                    is_in_modules_dir = os.path.join(
                        closest_parent, "modules"
                    ) == os.path.dirname(terraform_dir)

                    yield CheckResult(
                        "TF010",
                        Result.PASSED if is_in_modules_dir else Result.FAILED,
                        terraform_dir,
                    )
                else:
                    yield CheckResult("TF010", Result.NOT_APPLICABLE, terraform_dir)

        else:
            yield CheckResult("TF007", Result.NOT_APPLICABLE)
            yield CheckResult("TF008", Result.NOT_APPLICABLE)
            yield CheckResult("TF009", Result.NOT_APPLICABLE)
            yield CheckResult("TF010", Result.NOT_APPLICABLE)

    def checks(self):
        return [
            Check(
                "TF004",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform projects should have their Terraform lock files committed into Git",
                """When using Terraform, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed.""",
            ),
            Check(
                "TF005",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform projects should not have their .terraform directory committed into Git",
                """The .terraform directory contains binaries, thrid party modules and other things that are generated during a terraform init. This folder should not be committed into git.""",
            ),
            Check(
                "TF006",
                Severity.HIGH,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform state files should not be committed into git",
                """Terraform state files can contain secrets and are stored unencrypted. These secrets can be easily leaked when stored in git. Additionally, terraform state in git does not provide a single source of truth nor state locking and so can cause major issues when used in teams.

Instead of storing state in git, use another terraform backend

See https://developer.hashicorp.com/terraform/language/settings/backends/configuration""",
            ),
            Check(
                "TF007",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform modules should contain a main.tf file",
                """When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.

See https://developer.hashicorp.com/terraform/language/modules/develop/structure""",
            ),
            Check(
                "TF008",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform modules should contain an outputs.tf file",
                """When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.

See https://developer.hashicorp.com/terraform/language/modules/develop/structure""",
            ),
            Check(
                "TF009",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform modules should contain a variables.tf file",
                """When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.

See https://developer.hashicorp.com/terraform/language/modules/develop/structure""",
            ),
            Check(
                "TF010",
                Severity.LOW,
                ["open-source", "inner-source", "team", "personal"],
                "Terraform submodules should be contained in a 'modules' directory",
                """When creating submodules in a terraform module or project the submodules should be contained in a 'modules' directory. For example:
root/
|- modules/
|  '- my-submodule/
|     |-main.tf
|     |-outputs.tf
|     '-variables.tf
|-main.tf
|-outputs.tf
'-variables.tf

See https://developer.hashicorp.com/terraform/language/modules/develop/structure""",
            ),
        ]
