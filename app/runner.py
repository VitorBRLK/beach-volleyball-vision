"""Adaptador seguro entre a interface Streamlit e a CLI do pipeline."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from time import perf_counter
from typing import IO, Self

from app.validation import ValidationError, probe_video, validate_model

LOGGER = logging.getLogger(__name__)
LOG_LIMIT = 8_000


class ExecutionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConcurrentExecutionError(RuntimeError):
    """Indica que outra execução mantém a trava global."""


@dataclass(frozen=True, slots=True)
class PipelineRequest:
    input_path: Path
    output_path: Path
    model_path: Path
    device: str = "cpu"


@dataclass(frozen=True, slots=True)
class PipelineResult:
    status: ExecutionStatus
    elapsed_seconds: float
    output_path: Path | None = None
    message: str | None = None
    diagnostic: str = ""


class ExecutionLock:
    """Trava de arquivo liberada pelo sistema operacional após falha do processo."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._handle: IO[bytes] | None = None

    def __enter__(self) -> Self:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+b")
        handle.seek(0)
        if handle.read(1) == b"":
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError) as exc:
            handle.close()
            raise ConcurrentExecutionError(
                "Já existe um processamento em andamento."
            ) from exc
        self._handle = handle
        return self

    def __exit__(self, *_args: object) -> None:
        if self._handle is None:
            return
        try:
            self._handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()
            self._handle = None


class PipelineRunner:
    """Valida parâmetros, executa a CLI e confirma a saída produzida."""

    def __init__(
        self,
        repository_root: Path,
        cli_path: Path | None = None,
        lock_path: Path | None = None,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.cli_path = (cli_path or self.repository_root / "run.py").resolve()
        self.lock_path = (
            lock_path or self.repository_root / "data" / ".processing.lock"
        ).resolve()

    def build_command(self, request: PipelineRequest) -> list[str]:
        """Constrói argumentos sem interpretação por shell."""

        return [
            sys.executable,
            str(self.cli_path),
            str(request.input_path.resolve()),
            "--out",
            str(request.output_path.resolve()),
            "--model",
            str(request.model_path.resolve()),
            "--device",
            request.device,
        ]

    def execute(self, request: PipelineRequest) -> PipelineResult:
        started_at = perf_counter()
        try:
            self._validate_request(request)
            with ExecutionLock(self.lock_path):
                with tempfile.TemporaryFile(mode="w+b") as process_log:
                    completed = subprocess.run(
                        self.build_command(request),
                        cwd=self.repository_root,
                        stdout=process_log,
                        stderr=subprocess.STDOUT,
                        shell=False,
                        check=False,
                    )
                    diagnostic = _read_log_tail(process_log)
                if completed.returncode != 0:
                    LOGGER.error(
                        "Pipeline finalizou com código %s: %s",
                        completed.returncode,
                        diagnostic,
                    )
                    return self._failed(
                        started_at,
                        "O pipeline encerrou com erro. Consulte o log local.",
                        diagnostic,
                    )
                if not request.output_path.is_file():
                    return self._failed(
                        started_at,
                        "O pipeline terminou sem criar o vídeo de saída.",
                        diagnostic,
                    )
                probe_video(request.output_path)
                return PipelineResult(
                    status=ExecutionStatus.COMPLETED,
                    elapsed_seconds=perf_counter() - started_at,
                    output_path=request.output_path.resolve(),
                    diagnostic=diagnostic,
                )
        except ConcurrentExecutionError as exc:
            return self._failed(started_at, str(exc))
        except ValidationError as exc:
            return self._failed(started_at, str(exc))
        except OSError as exc:
            LOGGER.exception("Falha ao iniciar ou executar o pipeline")
            return self._failed(
                started_at,
                "Não foi possível iniciar o pipeline.",
                str(exc)[:LOG_LIMIT],
            )

    def _validate_request(self, request: PipelineRequest) -> None:
        if not self.cli_path.is_file():
            raise ValidationError(
                "A CLI do pipeline (run.py) não foi encontrada no repositório."
            )
        work_root = (self.repository_root / "data" / "work").resolve()
        output_root = (self.repository_root / "data" / "outputs").resolve()
        if not request.input_path.resolve().is_relative_to(work_root):
            raise ValidationError("O vídeo deve estar no diretório de trabalho controlado.")
        if not request.model_path.resolve().is_relative_to(work_root):
            raise ValidationError("O modelo deve estar no diretório de trabalho controlado.")
        if not request.output_path.resolve().is_relative_to(output_root):
            raise ValidationError("A saída deve estar no diretório controlado de resultados.")
        if request.output_path.exists():
            raise ValidationError("O arquivo de saída já existe e não será sobrescrito.")
        probe_video(request.input_path)
        validate_model(request.model_path)
        if request.device not in {"cpu", "cuda"}:
            raise ValidationError("O dispositivo deve ser 'cpu' ou 'cuda'.")
        if request.device == "cuda":
            _validate_cuda()
        request.output_path.parent.mkdir(parents=True, exist_ok=True)
        free_bytes = shutil.disk_usage(request.output_path.parent).free
        if free_bytes <= request.input_path.stat().st_size:
            raise ValidationError(
                "O espaço livre é insuficiente para iniciar o processamento."
            )

    @staticmethod
    def _failed(
        started_at: float, message: str, diagnostic: str = ""
    ) -> PipelineResult:
        return PipelineResult(
            status=ExecutionStatus.FAILED,
            elapsed_seconds=perf_counter() - started_at,
            message=message,
            diagnostic=diagnostic,
        )


def _validate_cuda() -> None:
    try:
        import torch  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ValidationError("PyTorch com suporte a CUDA não está disponível.") from exc
    if not torch.cuda.is_available():
        raise ValidationError("CUDA não está disponível neste ambiente.")


def _read_log_tail(process_log: IO[bytes]) -> str:
    process_log.flush()
    process_log.seek(0, os.SEEK_END)
    length = process_log.tell()
    process_log.seek(max(0, length - LOG_LIMIT))
    return process_log.read(LOG_LIMIT).decode("utf-8", errors="replace").strip()

