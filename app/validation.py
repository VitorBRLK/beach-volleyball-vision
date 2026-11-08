"""Validação de arquivos sem acoplamento com a interface web."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

VIDEO_EXTENSIONS = frozenset({".avi", ".mkv", ".mov", ".mp4", ".webm"})
MODEL_EXTENSIONS = frozenset({".onnx", ".pt"})


class ValidationError(ValueError):
    """Erro de entrada que pode ser apresentado de forma segura ao usuário."""


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Metadados confirmados pela leitura do vídeo."""

    width: int
    height: int
    frames: int
    fps: float


def validate_model(path: Path) -> Path:
    """Confirma que o modelo local existe, não está vazio e é permitido."""

    resolved = path.resolve()
    _validate_regular_file(resolved, "modelo")
    if resolved.suffix.lower() not in MODEL_EXTENSIONS:
        raise ValidationError("O modelo deve usar a extensão .pt ou .onnx.")
    if resolved.stat().st_size == 0:
        raise ValidationError("O arquivo de modelo está vazio.")
    return resolved


def probe_video(path: Path) -> VideoMetadata:
    """Abre o vídeo com OpenCV e confirma que pelo menos um quadro é legível."""

    resolved = path.resolve()
    _validate_regular_file(resolved, "vídeo")
    if resolved.suffix.lower() not in VIDEO_EXTENSIONS:
        extensions = ", ".join(sorted(VIDEO_EXTENSIONS))
        raise ValidationError(f"Formato de vídeo não permitido. Use: {extensions}.")
    if resolved.stat().st_size == 0:
        raise ValidationError("O arquivo de vídeo está vazio.")

    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ValidationError(
            "OpenCV não está instalado; não foi possível validar o vídeo."
        ) from exc

    capture: Any = cv2.VideoCapture(str(resolved))
    try:
        if not capture.isOpened():
            raise ValidationError("O arquivo não pôde ser aberto como vídeo.")
        readable, _frame = capture.read()
        if not readable:
            raise ValidationError("O vídeo não contém quadros legíveis.")
        return VideoMetadata(
            width=max(0, int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))),
            height=max(0, int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))),
            frames=max(0, int(capture.get(cv2.CAP_PROP_FRAME_COUNT))),
            fps=max(0.0, float(capture.get(cv2.CAP_PROP_FPS))),
        )
    finally:
        capture.release()


def _validate_regular_file(path: Path, description: str) -> None:
    if not path.exists():
        raise ValidationError(f"O arquivo de {description} não foi encontrado.")
    if not path.is_file():
        raise ValidationError(f"O caminho de {description} não aponta para um arquivo.")

