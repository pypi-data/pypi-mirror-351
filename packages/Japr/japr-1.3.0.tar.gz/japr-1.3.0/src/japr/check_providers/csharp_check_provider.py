from japr.check import Check, CheckProvider, CheckResult, Result, Severity
import japr.util
import os
import xml.etree.ElementTree as ET


_linters = [
    "StyleCop.Analyzers",
    "SonarAnalyzer.CSharp",
    "Microsoft.CodeAnalysis.NetAnalyzers",
    "Roslynator.Analyzers",
    "Roslynator.CodeAnalysis.Analyzers",
    "Roslynator.Formatting.Analyzers",
]


def _extract_dependencies_from_csproj(file):
    data = ET.parse(file)

    try:
        dependencies = [
            reference.get("Include")
            for reference in data.findall("./ItemGroup/PackageReference")
        ]
    except KeyError:
        print("ERROR")
        dependencies = []

    return set(dependencies)


def _has_enabled_net_analyzers_in_csproj(file):
    data = ET.parse(file)

    try:
        # TODO this defaults to true on net5.0 and above
        # TODO consider the EnforceCodeStyleInBuild property too
        properties = data.findall("./PropertyGroup/EnableNETAnalyzers")
        return len(properties) > 0 and all(
            property.text == "true" for property in properties
        )
    except KeyError:
        return False


def _has_enabled_nullable_in_csproj(file):
    data = ET.parse(file)

    try:
        properties = data.findall("./PropertyGroup/Nullable")
        return len(properties) > 0 and all(
            property.text == "enable" for property in properties
        )
    except KeyError:
        return False


def _has_enabled_treat_warnings_as_errors(file):
    data = ET.parse(file)

    try:
        properties = data.findall("./PropertyGroup/TreatWarningsAsErrors")
        return len(properties) > 0 and all(
            property.text == "true" for property in properties
        )
    except KeyError:
        return False


class CSharpCheckProvider(CheckProvider):
    def name(self):
        return "C#"

    def test(self, directory):
        cs_projects = list(japr.util.find_files_with_extension(directory, "csproj"))

        if len(cs_projects) != 0:
            for cs_project in cs_projects:
                dependencies = _extract_dependencies_from_csproj(
                    os.path.join(directory, cs_project)
                )
                has_enabled_net_analyzers = _has_enabled_net_analyzers_in_csproj(
                    os.path.join(directory, cs_project)
                )
                yield CheckResult(
                    "CS002",
                    (
                        Result.PASSED
                        if len(set(_linters).intersection(dependencies))
                        or has_enabled_net_analyzers
                        else Result.FAILED
                    ),
                    cs_project,
                )
                has_enabled_nullable = _has_enabled_nullable_in_csproj(
                    os.path.join(directory, cs_project)
                )
                yield CheckResult(
                    "CS003",
                    Result.PASSED if has_enabled_nullable else Result.FAILED,
                    cs_project,
                )
                has_enabled_treat_warnings_as_errors = (
                    _has_enabled_treat_warnings_as_errors(
                        os.path.join(directory, cs_project)
                    )
                )
                yield CheckResult(
                    "CS004",
                    (
                        Result.PASSED
                        if has_enabled_treat_warnings_as_errors
                        else Result.FAILED
                    ),
                    cs_project,
                )
        else:
            yield CheckResult("CS002", Result.NOT_APPLICABLE)
            yield CheckResult("CS003", Result.NOT_APPLICABLE)
            yield CheckResult("CS004", Result.NOT_APPLICABLE)

    def checks(self):
        return [
            Check(
                "CS002",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team"],
                "C# projects should have a linter configured",
                """C# projects should have a comprehensive linter configured such as StyleCop in order to ensure a consistent code style is used across all files and by all contributors.

Having a consistent style helps ensure readability and ease of understanding for any outsider looking into the project's code. Linters can also improve the stability of the code by catching mistakes before the code is published.""",
            ),
            Check(
                "CS003",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team"],
                "C# projects should have nullable reference types enabled",
                """C# projects should have nullable reference types enabled to avoid hard to detect null reference exceptions from appearing during runtime.

Nullable reference types were introduced in C#8 and can be enabled by adding the following into your csproj file:
    <PropertyGroup>
      <Nullable>enable</Nullable>
    </PropertyGroup>

See https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references""",
            ),
            Check(
                "CS004",
                Severity.MEDIUM,
                ["open-source", "inner-source", "team"],
                "C# projects should have treat warnings as errors enabled",
                """C# projects should have treat warnings as errors enabled to avoid warnings being ignored. This will cause warnings to fail the build and stop compilation

Warnings can be set to fail the build using:
    <PropertyGroup>
      <TreatWarningsAsErrors>enable</TreatWarningsAsErrors>
    </PropertyGroup>
""",
            ),
        ]
