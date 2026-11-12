from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from app import web
from app.runner import ExecutionStatus, PipelineResult
from app.validation import ValidationError


class UploadedBytes(BytesIO):
    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name
        self.size = len(content)


def test_dashboard_exposes_real_idle_state() -> None:
    entrypoint = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(entrypoint).run(timeout=10)

    assert not app.exception
    assert app.selectbox[0].value == "CPU — recomendado"
    assert app.button[0].disabled is True
    assert "3. Resultado" in [subheader.value for subheader in app.subheader]


def test_process_submission_updates_state_and_cleans_uploads(
    tmp_path: Path,
) -> None:
    session_dir = tmp_path / "work" / "session"
    input_path = session_dir / "entrada.mp4"
    model_path = session_dir / "modelo.pt"
    expected = PipelineResult(
        status=ExecutionStatus.COMPLETED,
        elapsed_seconds=1.25,
        output_path=tmp_path / "resultado.mp4",
    )
    state: dict[str, object] = {}

    with (
        patch("app.web.st.session_state", state),
        patch(
            "app.web.save_uploaded_file", side_effect=[input_path, model_path]
        ),
        patch("app.web.PipelineRunner.execute", return_value=expected),
        patch("app.web.remove_temporary_file") as cleanup,
    ):
        result = web._process_submission(
            UploadedBytes(b"video", "partida.mp4"),
            UploadedBytes(b"modelo", "modelo.pt"),
            "cpu",
            session_dir,
        )

    assert result is expected
    assert state["status"] == ExecutionStatus.COMPLETED
    assert state["result"] is expected
    cleanup.assert_any_call(input_path, session_dir)
    cleanup.assert_any_call(model_path, session_dir)


def test_invalid_upload_becomes_failed_state_without_running_pipeline(
    tmp_path: Path,
) -> None:
    state: dict[str, object] = {}

    with (
        patch("app.web.st.session_state", state),
        patch(
            "app.web.save_uploaded_file",
            side_effect=ValidationError("O arquivo não pôde ser aberto como vídeo."),
        ),
        patch("app.web.PipelineRunner.execute") as execute,
        patch("app.web.remove_temporary_file"),
    ):
        result = web._process_submission(
            UploadedBytes(b"invalido", "partida.mp4"),
            UploadedBytes(b"modelo", "modelo.pt"),
            "cpu",
            tmp_path / "session",
        )

    assert result.status == ExecutionStatus.FAILED
    assert result.message == "O arquivo não pôde ser aberto como vídeo."
    assert state["status"] == ExecutionStatus.FAILED
    execute.assert_not_called()


def test_process_submission_accepts_default_local_model(tmp_path: Path) -> None:
    session_dir = tmp_path / "work" / "session"
    input_path = session_dir / "entrada.mp4"
    copied_model_path = session_dir / "modelo.pt"
    default_model_path = tmp_path / "models" / "yolov8n.pt"
    default_model_path.parent.mkdir()
    default_model_path.write_bytes(b"modelo")
    expected = PipelineResult(
        status=ExecutionStatus.COMPLETED,
        elapsed_seconds=0.5,
        output_path=tmp_path / "resultado.mp4",
    )
    state: dict[str, object] = {}

    with (
        patch("app.web.st.session_state", state),
        patch(
            "app.web.save_uploaded_file",
            side_effect=[input_path, copied_model_path],
        ) as save_upload,
        patch("app.web.PipelineRunner.execute", return_value=expected),
        patch("app.web.remove_temporary_file"),
    ):
        result = web._process_submission(
            UploadedBytes(b"video", "partida.mp4"),
            None,
            "cpu",
            session_dir,
            default_model_path,
        )

    assert result is expected
    assert save_upload.call_count == 2


def test_format_bytes_uses_measured_units() -> None:
    assert web._format_bytes(512) == "512 B"
    assert web._format_bytes(2048) == "2.0 KB"
    assert web._format_bytes(2 * 1024 * 1024) == "2.0 MB"
