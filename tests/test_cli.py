"""Тесты CLI: коды возврата и сообщения (checker.cli)."""
from collections.abc import Callable, Iterable
from pathlib import Path

import pytest

from checker import FS_LOG, cli


def _run(monkeypatch: pytest.MonkeyPatch, target: str) -> int:
    monkeypatch.setattr(cli, "pick_directory", lambda: target)
    # По умолчанию глушим веб-хук, чтобы тесты не уходили в сеть.
    monkeypatch.setattr(cli, "send_webhook", lambda text: True)
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


def test_argument_bypasses_picker(
    monkeypatch: pytest.MonkeyPatch,
    make_tree: Callable[[Iterable[str]], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = make_tree(["Activities/Web/Projects/"])
    (root / ".fs-rule").write_text("/Activities/Web/Projects\n", encoding="utf-8")

    def _boom() -> str:
        raise AssertionError("pick_directory не должен вызываться при аргументе-каталоге")

    monkeypatch.setattr(cli, "pick_directory", _boom)
    monkeypatch.setattr(cli, "send_webhook", lambda text: True)
    code = cli.main([str(root)])
    assert code == 0
    assert "Все требуемые пути на месте." in capsys.readouterr().out


def test_missing_writes_log_and_sends_webhook(
    monkeypatch: pytest.MonkeyPatch,
    make_tree: Callable[[Iterable[str]], Path],
) -> None:
    root = make_tree(["Activities/Web/"])
    (root / ".fs-rule").write_text("/Activities/Web/Projects\n", encoding="utf-8")
    sent: list[str] = []
    monkeypatch.setattr(cli, "pick_directory", lambda: str(root))
    monkeypatch.setattr(cli, "send_webhook", lambda text: bool(sent.append(text)) or True)
    code = cli.main([])
    assert code == 2
    log = (root / FS_LOG).read_text(encoding="utf-8")
    assert "Activities/Web/Projects" in log
    assert len(sent) == 1
    assert "отсутствуют пути" in sent[0]


def test_no_violations_no_log_no_webhook(
    monkeypatch: pytest.MonkeyPatch,
    make_tree: Callable[[Iterable[str]], Path],
) -> None:
    root = make_tree(["Activities/Web/Projects/"])
    (root / ".fs-rule").write_text("/Activities/Web/Projects\n", encoding="utf-8")
    sent: list[str] = []
    monkeypatch.setattr(cli, "pick_directory", lambda: str(root))
    monkeypatch.setattr(cli, "send_webhook", lambda text: bool(sent.append(text)) or True)
    code = cli.main([])
    assert code == 0
    assert not (root / FS_LOG).exists()
    assert sent == []
