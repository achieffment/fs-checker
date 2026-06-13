"""Тесты журнала .fs-log (checker.log): создание, дополнение, формат."""
from datetime import datetime
from pathlib import Path

from checker import FS_LOG, write_fs_log


def test_write_fs_log_creates_file(tmp_path: Path) -> None:
    when = datetime(2026, 6, 14, 9, 0, 0)
    lpath = write_fs_log(tmp_path, ["Activities/Web/Projects"], when=when)
    assert lpath == tmp_path / FS_LOG
    text = lpath.read_text(encoding="utf-8")
    assert "2026-06-14 09:00:00" in text
    assert "  Activities/Web/Projects" in text


def test_write_fs_log_empty_marks_no_violations(tmp_path: Path) -> None:
    when = datetime(2026, 6, 14, 9, 5, 0)
    lpath = write_fs_log(tmp_path, [], when=when)
    text = lpath.read_text(encoding="utf-8")
    assert "2026-06-14 09:05:00" in text
    assert "(нарушений нет)" in text


def test_write_fs_log_appends(tmp_path: Path) -> None:
    write_fs_log(tmp_path, ["a"], when=datetime(2026, 6, 14, 9, 0, 0))
    lpath = write_fs_log(tmp_path, ["b"], when=datetime(2026, 6, 14, 10, 0, 0))
    text = lpath.read_text(encoding="utf-8")
    # Оба блока сохранены (дополнение, а не перезапись):
    assert "2026-06-14 09:00:00" in text
    assert "2026-06-14 10:00:00" in text
    assert "  a" in text
    assert "  b" in text
