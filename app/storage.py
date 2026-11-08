"""Armazenamento local controlado para uploads e resultados."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.validation import ValidationError

CHUNK_SIZE = 1024 * 1024


def save_uploaded_file(
    uploaded_file: BinaryIO,
    original_name: str,
    destination_dir: Path,
    allowed_extensions: frozenset[str],
    reported_size: int | None = None,
) -> Path:
    """Salva um upload em blocos com nome gerado pelo sistema."""

    suffix = Path(original_name).suffix.lower()
    if suffix not in allowed_extensions:
        extensions = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"Extensão não permitida. Use: {extensions}.")
    if reported_size is not None and reported_size <= 0:
        raise ValidationError("O arquivo enviado está vazio.")

    destination_dir.mkdir(parents=True, exist_ok=True)
    if reported_size is not None:
        free_bytes = shutil.disk_usage(destination_dir).free
        if reported_size >= free_bytes:
            raise ValidationError("Não há espaço livre para salvar o arquivo enviado.")

    destination = destination_dir / f"{uuid4().hex}{suffix}"
    bytes_written = 0
    try:
        uploaded_file.seek(0)
        with destination.open("xb") as target:
            while chunk := uploaded_file.read(CHUNK_SIZE):
                target.write(chunk)
                bytes_written += len(chunk)
    except (OSError, ValueError) as exc:
        destination.unlink(missing_ok=True)
        raise ValidationError("Não foi possível salvar o arquivo enviado.") from exc

    if bytes_written == 0:
        destination.unlink(missing_ok=True)
        raise ValidationError("O arquivo enviado está vazio.")
    return destination.resolve()


def remove_temporary_file(path: Path | None, controlled_dir: Path) -> None:
    """Remove somente um arquivo contido no diretório temporário informado."""

    if path is None:
        return
    resolved = path.resolve()
    root = controlled_dir.resolve()
    if resolved.is_relative_to(root) and resolved.is_file():
        resolved.unlink(missing_ok=True)

