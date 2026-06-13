"""Тесты CLI: коды возврата и сообщения (checker.cli)."""
from collections.abc import Callable, Iterable
from pathlib import Path

import pytest

from checker import cli


def _run(monkeypatch: pytest.MonkeyPatch, target: str) -> int:
    monkeypatch.setattr(cli, "pick_directory", lambda: target)
    return cli.main([])


def test_no_directory_selected(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code = _run(monkeypatch, "")
    assert code == 1
    assert "Каталог не выбран" in capsys.readouterr().err


def test_directory_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = _run(monkeypatch, str(tmp_path / "missing"))
    assert code == 1
    assert "каталог не найден" in capsys.readouterr().err


def test_not_a_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    code = _run(monkeypatch, str(file_path))
    assert code == 1
    assert "не является каталогом" in capsys.readouterr().err


def test_missing_fs_rule(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = _run(monkeypatch, str(tmp_path))
    assert code == 1
    assert ".fs-rule" in capsys.readouterr().err


def test_no_violations_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    make_tree: Callable[[Iterable[str]], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = make_tree(["Activities/Web/Projects/"])
    (root / ".fs-rule").write_text("/Activities/Web/Projects\n", encoding="utf-8")
    code = _run(monkeypatch, str(root))
    out = capsys.readouterr().out
    assert code == 0
    assert "Все требуемые пути на месте." in out


def test_violations_return_two(
    monkeypatch: pytest.MonkeyPatch,
    make_tree: Callable[[Iterable[str]], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = make_tree(["Activities/Web/"])
    (root / ".fs-rule").write_text("/Activities/Web/Projects\n", encoding="utf-8")
    code = _run(monkeypatch, str(root))
    out = capsys.readouterr().out
    assert code == 2
    assert "Отсутствуют пути (1):" in out
    assert "Activities/Web/Projects" in out
    assert "Проверено правил: 1." in out
