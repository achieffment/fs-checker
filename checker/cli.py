"""CLI: разбор аргументов и сценарий запуска."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import FsChecker
from .picker import pick_directory
from .report import format_report
from .rule import FsRuleError, load_fs_rule


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Проверка наличия папок и файлов по правилам .fs-rule (read-only, рекурсивно). Каталог выбирается интерактивно при запуске (диалог проводника на Windows и в WSL, диалог macOS, либо ввод пути в терминале на обычном Linux).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """0 — нарушений нет; 1 — ошибка запуска; 2 — найдены отсутствующие пути."""
    _parse_args(argv)
    targ = pick_directory()
    if not targ:
        sys.stderr.write("Каталог не выбран.\n")
        return 1
    root = Path(targ).expanduser()
    try:
        root = root.resolve(strict=True)
    except OSError:
        sys.stderr.write(f"Ошибка: каталог не найден: {targ}\n")
        return 1
    if not root.is_dir():
        sys.stderr.write(f"Ошибка: каталог не является каталогом: {root}\n")
        return 1
    try:
        fs_rule = load_fs_rule(root)
    except FsRuleError as exc:
        sys.stderr.write(f"Ошибка: {exc}\n")
        return 1
    result = FsChecker(fs_rule).check(root)
    print(format_report(root, result))
    return 2 if result.missing else 0
