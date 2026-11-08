from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from app.runner import (
    ConcurrentExecutionError,
    ExecutionStatus,
    PipelineRequest,
    PipelineRunner,
)


def _request(repository: Path) -> PipelineRequest:
    work = repository / "data" / "work" / "session"
    output = repository / "data" / "outputs" / "resultado.mp4"
    work.mkdir(parents=True)
    (repository / "run.py").write_text("# CLI simulada", encoding="utf-8")
    input_path = work / "entrada com espaco.mp4"
    model_path = work / "modelo.pt"
    input_path.write_bytes(b"video")
    model_path.write_bytes(b"modelo")
    return PipelineRequest(input_path, output, model_path)


def test_build_command_preserves_paths_with_spaces(tmp_path: Path) -> None:
    request = _request(tmp_path)
    command = PipelineRunner(tmp_path).build_command(request)

    assert str(request.input_path.resolve()) in command
    assert command[command.index("--device") + 1] == "cpu"
    assert len(command) == 9


def test_success_requires_created_readable_output(tmp_path: Path) -> None:
    request = _request(tmp_path)

    def run_pipeline(
        *_args: object, **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        request.output_path.parent.mkdir(parents=True, exist_ok=True)
        request.output_path.write_bytes(b"video anotado")
        return subprocess.CompletedProcess([], 0, "ok", "")

    with (
        patch("app.runner.probe_video"),
        patch("app.runner.subprocess.run", side_effect=run_pipeline) as run_mock,
    ):
        result = PipelineRunner(tmp_path).execute(request)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.output_path == request.output_path.resolve()
    assert run_mock.call_args.kwargs["shell"] is False


def test_nonzero_exit_is_failure(tmp_path: Path) -> None:
    request = _request(tmp_path)
    completed = subprocess.CompletedProcess([], 2, "", "erro controlado")

    with (
        patch("app.runner.probe_video"),
        patch("app.runner.subprocess.run", return_value=completed),
    ):
        result = PipelineRunner(tmp_path).execute(request)

    assert result.status == ExecutionStatus.FAILED
    assert "encerrou com erro" in (result.message or "")


def test_missing_output_is_failure(tmp_path: Path) -> None:
    request = _request(tmp_path)
    completed = subprocess.CompletedProcess([], 0, "ok", "")

    with (
        patch("app.runner.probe_video"),
        patch("app.runner.subprocess.run", return_value=completed),
    ):
        result = PipelineRunner(tmp_path).execute(request)

    assert result.status == ExecutionStatus.FAILED
    assert "sem criar" in (result.message or "")


def test_invalid_device_does_not_start_subprocess(tmp_path: Path) -> None:
    request = _request(tmp_path)
    invalid = PipelineRequest(
        request.input_path, request.output_path, request.model_path, "gpu"
    )

    with (
        patch("app.runner.probe_video"),
        patch("app.runner.subprocess.run") as run_mock,
    ):
        result = PipelineRunner(tmp_path).execute(invalid)

    assert result.status == ExecutionStatus.FAILED
    run_mock.assert_not_called()


def test_missing_cli_does_not_start_subprocess(tmp_path: Path) -> None:
    work = tmp_path / "data" / "work" / "session"
    work.mkdir(parents=True)
    request = PipelineRequest(
        work / "entrada.mp4",
        tmp_path / "data" / "outputs" / "resultado.mp4",
        work / "modelo.pt",
    )

    with patch("app.runner.subprocess.run") as run_mock:
        result = PipelineRunner(tmp_path).execute(request)

    assert result.status == ExecutionStatus.FAILED
    assert "run.py" in (result.message or "")
    run_mock.assert_not_called()


def test_concurrent_execution_does_not_start_subprocess(tmp_path: Path) -> None:
    request = _request(tmp_path)

    with (
        patch("app.runner.probe_video"),
        patch(
            "app.runner.ExecutionLock.__enter__",
            side_effect=ConcurrentExecutionError(
                "Já existe um processamento em andamento."
            ),
        ),
        patch("app.runner.subprocess.run") as run_mock,
    ):
        result = PipelineRunner(tmp_path).execute(request)

    assert result.status == ExecutionStatus.FAILED
    assert "andamento" in (result.message or "")
    run_mock.assert_not_called()

