"""Пакет проверки наличия папок и файлов по правилам .fs-rule (read-only).

Публичное API: импортируйте отсюда, а не из подмодулей напрямую.
"""
from __future__ import annotations

from .cli import main
from .engine import CheckResult, FsChecker
from .report import format_report
from .rule import FsRule, FsRuleError, Negation, Rule, load_fs_rule

__all__ = [
    "main",
    "FsChecker",
    "CheckResult",
    "format_report",
    "load_fs_rule",
    "FsRule",
    "Rule",
    "Negation",
    "FsRuleError",
]
