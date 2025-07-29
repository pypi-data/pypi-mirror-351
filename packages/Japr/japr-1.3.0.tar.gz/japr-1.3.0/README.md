# Jamie's Awesome Project Rater
A cross-language tool for rating and enforcing the overall quality of projects by looking at tool & language setup

It's a linter that makes sure you install linters (and some other stuff)

![Screenshot of a report](/screenshot.png)

## Installation
Using pip:
```bash
pip install japr
```

Using [pipx](https://github.com/pypa/pipx) which will get you the latest, bleeding edge version:
```bash
pipx install git+https://github.com/JamJar00/japr
```

Or you can use Docker:
```bash
docker run --rm -v $(pwd):/app jamoyjamie/japr:v1.0.1
```

## Usage
```bash
japr <directory> -t <project-type>
```

For more options:
```bash
japr <directory> [--summary] [--project-type <open-source|inner-source|team|personal>]
```

#### Project Type
To run a check you need to tell Japr about the audience of your projects so it can select a good set of rules to apply. Most personal projects don't need a pull request template for example!

Select one of the following project types and pass on the command line via `-t`/`--project-type` or in the configuration file as in the section below.
| Project Type | Description                                                                                                                                                    |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| open-source  | A comprehensive ruleset for open source projects that are for anyone and everyone that might stumble upon the code                                             |
| inner-source | A comprehensive ruleset for projects that are accessible across an organisation and may be used by other teams (often referred to as 'inner source' projects   |
| team         | A balanced ruleset designed for projects that belong to a single team                                                                                          |
| personal     | A lightweight ruleset designed to tidy up personal projects                                                                                                    |

![Animation of a report and a fix](/animation.gif)

### Configuration
Configuration is done mostly through a `.japr.yaml` file in the root of your repository.
```yaml
# .japr.yaml
projectType: open-source
```
The most useful thing to put in there is the project type so it doesn't need to be specified on the command line each time

#### Suppressing Checks
If you need to suppress a check then you can add an `overrides` second to your configuration file like so:
```yaml
# .japr.yaml
override:
  - id: CI001
    suppress: true
```
Be aware that the project's score is always calculated against the full ruleset no matter what you suppress so that the score is comparable across projects of the same type.

## Score
Japr produces a score for each project between 0 and 5 stars. A project with a 5 star score is very commendable.

This score is always calculated against the full ruleset so is comparable between projects of the same type even if they have different suppressions set.

## Supported Languages
Japr will work for projects of all languages however there are additional checks for the following:
- Python
- C#
- Javascript

The following table tracks the level of support for each language. Many languages also have additional checks not listed.
|                       | Python         | C# | JS        | Rust  | Terraform |
|-----------------------|----------------|----|-----------|-------|-----------|
| Linter setup          | ✅             | ✅ | ✅        |       | ❌        |
| Lock files in Git     | ✅             | ❌ | ✅        | ✅    | ✅        |
| Dependency Managers   | Poetry, Pipenv |    | NPM, Yarn | Cargo |           |

## Experimental Automatic Fixes
Japr can automatically fix some issues when supplied the `--fix` flag. **This functionality is highly expermental**

## Development
Pull requsts are welcome. Please read [the contributing guide first](./CONTRIBUTING.md).

Building and running Japr from source should be relatively easy. Here are some of the commands you'll need:
```bash
# Get dependencies and venvs setup
poetry install

# Run Japr
poetry run japr

# Run the test suite
poetry run pytest

# Format your code
poetry run black .

# Generate rule docs (and append to readme, delete the exsting rules first though otherwise you'll still have the old docs!)
poetry generate_docs >> README.md
```

### TODO
- Support code blocks in the advice section
- Deploy to Docker Hub
- Tests, always need _more_ tests
- Allow enabling checks even when project type usually suppresses it
- Allow configuring suppressed rules only for certain files
- Fixes for more checks and stabilise
- Fix not finding git repo if repo root is a parent directory

#### Checks
- Check lock files are checked into Git
- Are linters in dev dependencies?
- No TODOs anywhere, they should be tracked in issues
- More languages
- Is it a recognised license? Appropriate for the type of project?
- Copyright headers?
- Code of Conduct file - https://bttger.github.io/contributing-gen-web/

##### Python
- Support Flit & Setuptools as other dependency managers
    https://peps.python.org/pep-0621/
- No Python 2

##### GitHub
- Pull request templates/issue templates should have YAML front matter
- Issue templates should be in the .github folder

##### Sketchy Ideas
- Has git tags for versions?
  - Versions in project files match latest git tag
    - Might need thought for cases where the version has been bumped but the tag hasn't been pushed yet
- Integrate with GitHub?

#### Tests
- Git provider
- JS/Python lock files in git

## Rules
### Readme
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| RE001 | High | open-source, inner-source, team, personal | Projects should have a README.md file describing the project and its use | Create a README.md file in the root of the project and add content to describe to other users (or just your future self) things like:</br>- Why does this project exist?</br>- How do I install it?</br>- How do I use it?</br>- What configuration can be set?</br>- How do I build the source code?</br></br>See https://www.makeareadme.com/ for further guidance |
| RE002 | Low | open-source, inner-source, team, personal | README.md should contain an Installation section | To help users (and your future self) install your project/library you should provide an installation section in your README. Add the following to your readme:</br></br>## Installation</br>1. Do this</br>2. Now do this |
| RE003 | Low | open-source, inner-source, team, personal | README.md should contain a Usage section | To help users (and your future self) use your project/library you should provide a usage section in your README. Add the following to your readme:</br></br>## Usage</br>To do this thing:</br>1. Do this</br>2. Then run this |

### License
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| LI001 | Medium | open-source, personal | Projects should have a LICENSE.md file describing how the project can be used | Create a LICENSE.md file in the root of the project and add content to describe to other users how this project can be used</br></br>If you are not familiar with the different licenses available to you, try https://choosealicense.com which guides you through the choice. |

### Git
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| GI001 | High | open-source, inner-source, team, personal | Projects should be tracked in Git version control | All projects, even the smallest personal projects benefit from being tracked in Git as it provides branch management, backups and history to your project.</br></br>Run `git init` in this project to setup Git and then make a commit. |
| GI002 | High | open-source, inner-source, team, personal | Projects in Git should have a remote copy in origin | This project does not have a Git remote named 'origin' which suggests there is no backup copy of the project should it be lost.</br></br>Setup a Git repository on your favourite Git service (e.g. GitHub) and follow the instructions to add a remote to an existing project. The instructions will likely look like:</br></br>git remote add origin <your repository url></br>git push origin main |
| GI003 | High | open-source, inner-source, team, personal | Projects in Git should switch from a 'master' branch to a 'main' branch | This project has a branch named 'master' however it is now recommended to use a branch named 'main' to avoid culturally inappropriate language.</br></br>The following guide does a good job or describing the process and providing solutions to any issues you may have with this: https://www.git-tower.com/learn/git/faq/git-rename-master-to-main |
| GI004 | Low | open-source, inner-source, team, personal | Projects in Git should have a .gitignore file | .gitignore files help you avoid committing unwanted files into Git such as binaries or build artifacts. You should create a .gitignore file for this project.</br></br>You can find comprehensive examples for your chosen language here: https://github.com/github/gitignore |
| GI005 | Medium | open-source, inner-source, team, personal | Avoid committing .DS_store files | .DS_store files are OSX metadata files in a proprietary binary format. When committed to Git repositories they cause unnecessary changes and provide no value as they differ per machine.</br></br>You can tell git to ignore them from commits by adding them to your .gitignore.</br></br>You can also all them to your global .gitignore to avoid ever committing them in any repository. Configure a global .gitignore using the following:</br>git config --global core.excludesfile ~/.gitignore</br></br>To remove one from the current repository you can use:</br>git rm --cached ./path/to/.DS_Store |
| GI006 | Medium | open-source, inner-source, team, personal | Avoid committing IDE related files/directories | Many IDEs store IDE specific files with your project. When committed to Git repositories they cause unnecessary changes and provide no value as they differ per machine.</br></br>You can tell git to ignore them from commits by adding them to your .gitignore.</br></br>You can also all them to your global .gitignore to avoid ever committing them in any repository. Configure a global .gitignore using the following:</br>git config --global core.excludesfile ~/.gitignore</br></br>To remove one from the current repository you can use:</br>git rm --cached /path/to/file |

### CI
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| CI001 | Medium | open-source, inner-source, team, personal | Projects should define a CI/CD pipeline to ensure code builds and works correctly | Consider creating a CI/CD pipeine for this project using a tool like GitHub Actions. A typical CI/CD pipeline should:</br>- Lint the code</br>- Build the code</br>- Run all tests</br>- Deploy any artifacts like NuGet packages/PyPI packages</br></br>If you are using GitHub and would like to get started with it, you can learn how to use it here: https://docs.github.com/en/actions/quickstart |

### Python
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| PY001 | Medium | open-source, inner-source, team, personal | Python projects should prefer a build system to a requirements.txt | Python is moving towards using more intelligent build systems like Poetry or pipenv to manage dependencies. Consider switching from a requirements.txt file to one of these tools. |
| PY002 | Medium | open-source, inner-source, team | Python projects should have a linter configured | Python projects should have a comprehensive linter configured such as Pylama in order to ensure a consistent code style is used across all files and by all contributors.</br></br>Having a consistent style helps ensure readability and ease of understanding for any outsider looking into the project's code. Linters can also improve the stability of the code by catching mistakes before the code is published. |
| PY003 | Medium | open-source, inner-source, team, personal | Python projects should prefer a build system to setup.py/setup.cfg | Python is moving towards using more intelligent build systems like Poetry or pipenv to manage dependencies. Consider switching from a setup.py or setup.cfg file to one of these tools. |
| PY004 | Medium | open-source, inner-source, team, personal | Python projects using a dependency manager should have their lock files committed into Git | When using a dependency manager for Python such as Poetry, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed. |

### GitHub
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| GH001 | Low | open-source, inner-source | GitHub projects should have an issue template | To help users create issues that are useful for you an issue template is recommended.</br></br>Create a .github/issue_template.md file and fill it with a template for users to use when filing issues.</br>See https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates |
| GH002 | Low | open-source, inner-source | GitHub projects should have a pull request template | To help users create pull requests that are useful for you a pull request template is recommended.</br></br>Create a .github/pull_request_template.md file and fill it with a template for users to use when filing pull requests</br>See https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository |
| GH003 | High | open-source, inner-source, team, personal | GitHub Actions workflows should have timeouts set | Workflows for GitHub Actions must have timeouts set to avoid hefty charges getting incurred by stuck jobs. By default, the timeout is 6h which is lmost always unecessary</br></br>                Add the timeout-minutes property to your job</br>                See https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes |

### C#
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| CS002 | Medium | open-source, inner-source, team | C# projects should have a linter configured | C# projects should have a comprehensive linter configured such as StyleCop in order to ensure a consistent code style is used across all files and by all contributors.</br></br>Having a consistent style helps ensure readability and ease of understanding for any outsider looking into the project's code. Linters can also improve the stability of the code by catching mistakes before the code is published. |
| CS003 | Medium | open-source, inner-source, team | C# projects should have nullable reference types enabled | C# projects should have nullable reference types enabled to avoid hard to detect null reference exceptions from appearing during runtime.</br></br>Nullable reference types were introduced in C#8 and can be enabled by adding the following into your csproj file:</br>    <PropertyGroup></br>      <Nullable>enable</Nullable></br>    </PropertyGroup></br></br>See https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references |
| CS004 | Medium | open-source, inner-source, team | C# projects should have treat warnings as errors enabled | C# projects should have treat warnings as errors enabled to avoid warnings being ignored. This will cause warnings to fail the build and stop compilation</br></br>Warnings can be set to fail the build using:</br>    <PropertyGroup></br>      <TreatWarningsAsErrors>enable</TreatWarningsAsErrors></br>    </PropertyGroup></br> |

### Contributing
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| CT001 | Medium | open-source | Projects should have a CONTRIBUTING.md file describing how to contribute to the project | Create a CONTRIBUTING.md file in the root of the project and add content to describe to other users how they can contribute to the project in the most helpful way</br></br>A good contributing guide should:</br>- Explain how people can best ask questions</br>- Explain how people can best report bugs or suggest enhancements</br>- Explain how people can donate</br>- Explain what the process is for making a pull request (e.g. does an issue need to exist before a pull request can be opened?)</br>- Explain the standards expected of any pull requests</br>- Explain any subtleties to contributing to the documentation</br>- Explain how people can join your team or help contribute in a grander way</br> |

### Javascript
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| JS002 | Medium | open-source, inner-source, team | Javascript projects should have a linter configured | Javascript projects should have a comprehensive linter configured such as ESLint in order to ensure a consistent code style is used across all files and by all contributors.</br></br>Having a consistent style helps ensure readability and ease of understanding for any outsider looking into the project's code. Linters can also improve the stability of the code by catching mistakes before the code is published. |
| JS004 | Medium | open-source, inner-source, team, personal | Javascript projects should have their lock files committed into Git | When using a dependency manager for Javascript such as npm, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed. |

### Rust
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| RS004 | Medium | open-source, inner-source, team, personal | Rust projects should have their Cargo lock files committed into Git | When using Cargo for Rust, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed. |

### Terraform
| ID | Severity | Enabled for Project Types | Description | Advice |
|----|----------|---------------------------|-------------|--------|
| TF004 | Medium | open-source, inner-source, team, personal | Terraform projects should have their Terraform lock files committed into Git | When using Terraform, the lock files should be comitted into Git. This ensures that all dependencies of packages are installed at the same version no matter when and on what machine the project is installed. |
| TF005 | Medium | open-source, inner-source, team, personal | Terraform projects should not have their .terraform directory committed into Git | The .terraform directory contains binaries, thrid party modules and other things that are generated during a terraform init. This folder should not be committed into git. |
| TF006 | High | open-source, inner-source, team, personal | Terraform state files should not be committed into git | Terraform state files can contain secrets and are stored unencrypted. These secrets can be easily leaked when stored in git. Additionally, terraform state in git does not provide a single source of truth nor state locking and so can cause major issues when used in teams.</br></br>Instead of storing state in git, use another terraform backend</br></br>See https://developer.hashicorp.com/terraform/language/settings/backends/configuration |
| TF007 | Low | open-source, inner-source, team, personal | Terraform modules should contain a main.tf file | When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.</br></br>See https://developer.hashicorp.com/terraform/language/modules/develop/structure |
| TF008 | Low | open-source, inner-source, team, personal | Terraform modules should contain an outputs.tf file | When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.</br></br>See https://developer.hashicorp.com/terraform/language/modules/develop/structure |
| TF009 | Low | open-source, inner-source, team, personal | Terraform modules should contain a variables.tf file | When creating terraform modules (or using terraform in general) each module should contain a minimum of a main.tf, outputs.tf and a variables.tf file, even if these are empty.</br></br>See https://developer.hashicorp.com/terraform/language/modules/develop/structure |
| TF010 | Low | open-source, inner-source, team, personal | Terraform submodules should be contained in a 'modules' directory | When creating submodules in a terraform module or project the submodules should be contained in a 'modules' directory. For example:</br>root/</br>|- modules/</br>|  '- my-submodule/</br>|     |-main.tf</br>|     |-outputs.tf</br>|     '-variables.tf</br>|-main.tf</br>|-outputs.tf</br>'-variables.tf</br></br>See https://developer.hashicorp.com/terraform/language/modules/develop/structure |
