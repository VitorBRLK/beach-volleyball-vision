"""CLI minima de deteccao para o baseline local do Beach Volleyball Vision."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2

LOGGER = logging.getLogger(__name__)
TARGET_LABELS = frozenset({"person", "sports ball", "ball", "volleyball"})


class PipelineError(RuntimeError):
    """Erro controlado de entrada ou execucao da CLI."""


@dataclass(frozen=True, slots=True)
class ProcessingSummary:
    """Resumo verificavel produzido pela execucao."""

    frames_processed: int


def build_parser() -> argparse.ArgumentParser:
    """Cria o contrato de linha de comando consumido pelo adaptador."""

    parser = argparse.ArgumentParser(
        description="Detecta pessoas e bola em um video gravado."
    )
    parser.add_argument("video", type=Path, help="Video de entrada.")
    parser.add_argument("--out", required=True, type=Path, help="Saida MP4.")
    parser.add_argument("--model", required=True, type=Path, help="Modelo YOLO.")
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda"),
        default="cpu",
        help="Dispositivo de inferencia (padrao: cpu).",
    )
    return parser


def run_pipeline(
    input_path: Path,
    output_path: Path,
    model_path: Path,
    device: str = "cpu",
) -> ProcessingSummary:
    """Processa o video quadro a quadro sem carregar o arquivo inteiro na memoria."""

    input_path = input_path.resolve()
    output_path = output_path.resolve()
    model_path = model_path.resolve()
    _validate_paths(input_path, output_path, model_path)
    _validate_device(device)

    yolo_class = _load_yolo_class()
    model = yolo_class(str(model_path))
    target_class_ids = _target_class_ids(model.names)

    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        capture.release()
        raise PipelineError("O video de entrada nao pode ser aberto.")

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    if width <= 0 or height <= 0 or fps <= 0:
        capture.release()
        raise PipelineError("O video nao possui dimensoes ou FPS validos.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = output_path.with_name(
        f".{output_path.stem}.{uuid4().hex}.partial.mp4"
    )
    writer = cv2.VideoWriter(
        str(partial_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        writer.release()
        partial_path.unlink(missing_ok=True)
        raise PipelineError("Nao foi possivel criar o video de saida MP4.")

    try:
        frames_processed = 0
        try:
            while True:
                readable, frame = capture.read()
                if not readable:
                    break
                predictions = model.predict(
                    source=frame,
                    device=device,
                    classes=target_class_ids,
                    verbose=False,
                )
                if not predictions:
                    raise PipelineError(
                        "O modelo nao retornou resultado para um quadro."
                    )
                writer.write(predictions[0].plot())
                frames_processed += 1
        finally:
            capture.release()
            writer.release()
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise

    if frames_processed == 0:
        partial_path.unlink(missing_ok=True)
        raise PipelineError("O video nao contem quadros legiveis.")
    if not partial_path.is_file() or partial_path.stat().st_size == 0:
        partial_path.unlink(missing_ok=True)
        raise PipelineError("O processamento nao gerou um arquivo de saida valido.")

    try:
        partial_path.replace(output_path)
    except OSError as exc:
        partial_path.unlink(missing_ok=True)
        raise PipelineError("Nao foi possivel publicar o video de saida.") from exc
    return ProcessingSummary(frames_processed=frames_processed)


def _validate_paths(input_path: Path, output_path: Path, model_path: Path) -> None:
    if not input_path.is_file():
        raise PipelineError("O video de entrada nao foi encontrado.")
    if not model_path.is_file():
        raise PipelineError("O modelo YOLO nao foi encontrado.")
    if model_path.suffix.lower() not in {".pt", ".onnx"}:
        raise PipelineError("O modelo deve usar a extensao .pt ou .onnx.")
    if output_path.suffix.lower() != ".mp4":
        raise PipelineError("A saida deve usar a extensao .mp4.")
    if output_path.exists():
        raise PipelineError("O arquivo de saida ja existe e nao sera sobrescrito.")
    if input_path == output_path:
        raise PipelineError("A saida nao pode sobrescrever o video de entrada.")


def _validate_device(device: str) -> None:
    if device not in {"cpu", "cuda"}:
        raise PipelineError("O dispositivo deve ser 'cpu' ou 'cuda'.")
    if device == "cuda":
        import torch

        if not torch.cuda.is_available():
            raise PipelineError("CUDA nao esta disponivel neste ambiente.")


def _target_class_ids(names: Mapping[int, str] | Sequence[str]) -> list[int]:
    items = names.items() if isinstance(names, Mapping) else enumerate(names)
    class_ids = [
        int(class_id)
        for class_id, label in items
        if str(label).strip().casefold() in TARGET_LABELS
    ]
    if not class_ids:
        raise PipelineError(
            "O modelo nao possui classes compativeis de pessoa ou bola."
        )
    return class_ids


def _load_yolo_class() -> Any:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise PipelineError(
            "Ultralytics nao esta instalado no ambiente do projeto."
        ) from exc
    return YOLO


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        summary = run_pipeline(args.video, args.out, args.model, args.device)
    except PipelineError as exc:
        LOGGER.error("%s", exc)
        return 2
    except Exception:
        LOGGER.exception("Falha inesperada durante o processamento")
        return 1
    LOGGER.info("Processamento concluido: %s quadros.", summary.frames_processed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
