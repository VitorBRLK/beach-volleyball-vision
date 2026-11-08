from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from app.storage import remove_temporary_file, save_uploaded_file
from app.validation import ValidationError, probe_video, validate_model


def test_rejects_missing_model(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="não foi encontrado"):
        validate_model(tmp_path / "ausente.pt")


def test_rejects_invalid_video_extension_before_opening(tmp_path: Path) -> None:
    invalid = tmp_path / "conteudo.txt"
    invalid.write_bytes(b"nao e video")

    with pytest.raises(ValidationError, match="Formato de vídeo"):
        probe_video(invalid)


def test_upload_uses_generated_name_and_ignores_traversal(tmp_path: Path) -> None:
    destination = save_uploaded_file(
        BytesIO(b"video"),
        "../../partida.mp4",
        tmp_path / "work",
        frozenset({".mp4"}),
        reported_size=5,
    )

    assert destination.parent == (tmp_path / "work").resolve()
    assert destination.name != "partida.mp4"
    assert destination.read_bytes() == b"video"


def test_cleanup_does_not_remove_file_outside_controlled_dir(tmp_path: Path) -> None:
    controlled = tmp_path / "work"
    controlled.mkdir()
    external = tmp_path / "resultado.mp4"
    external.write_bytes(b"resultado")

    remove_temporary_file(external, controlled)

    assert external.exists()

