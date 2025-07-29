from abc import ABC, abstractmethod
from enum import Enum


class CheckProvider(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def test(self, directory):
        pass

    @abstractmethod
    def checks(self):
        pass


class Check:
    def __init__(self, id, severity, project_types, reason, advice):
        self.id = id
        self.severity = severity
        self.project_types = project_types
        self.reason = reason
        self.advice = advice


class CheckResult:
    def __init__(self, id, result, file_path=None, fix=None):
        self.id = id
        self.result = result
        self.file_path = file_path
        self.fix = fix
        self.is_fixed = None


class CheckFix(ABC):
    @abstractmethod
    def fix(self, directory, file_path):
        pass

    @property
    @abstractmethod
    def success_message(self):
        pass

    @property
    @abstractmethod
    def failure_message(self):
        pass


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 4


class Result(Enum):
    PASSED = 0
    FAILED = 1
    PRE_REQUISITE_CHECK_FAILED = 2
    NOT_APPLICABLE = 3
