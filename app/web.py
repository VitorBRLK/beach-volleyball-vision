"""Interface Streamlit local do Beach Volleyball Vision."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol
from uuid import uuid4

import streamlit as st

from app.runner import ExecutionStatus, PipelineRequest, PipelineResult, PipelineRunner
from app.storage import remove_temporary_file, save_uploaded_file
from app.validation import MODEL_EXTENSIONS, VIDEO_EXTENSIONS, ValidationError

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = REPOSITORY_ROOT / "data" / "work"
OUTPUT_ROOT = REPOSITORY_ROOT / "data" / "outputs"
LOGGER = logging.getLogger(__name__)


class UploadedFile(Protocol):
    """Parte do contrato de upload usada pela aplicação."""

    name: str
    size: int

    def read(self, size: int = -1) -> bytes: ...


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    st.set_page_config(page_title="Beach Volleyball Vision", page_icon="🏐")
    st.title("Beach Volleyball Vision")
    st.caption("Análise local de vídeos gravados, com CPU como padrão.")

    session_id = st.session_state.setdefault("session_id", uuid4().hex)
    session_dir = WORK_ROOT / session_id
    result: PipelineResult | None = st.session_state.get("result")
    current_status = st.session_state.setdefault("status", ExecutionStatus.IDLE)

    with st.form("pipeline_configuration"):
        video_upload = st.file_uploader(
            "Vídeo da partida",
            type=sorted(extension.removeprefix(".") for extension in VIDEO_EXTENSIONS),
            help="O original não será alterado.",
        )
        model_upload = st.file_uploader(
            "Modelo YOLO local",
            type=sorted(extension.removeprefix(".") for extension in MODEL_EXTENSIONS),
            help="Use apenas pesos de uma origem confiável. Nenhum modelo é baixado.",
        )
        device_label = st.selectbox(
            "Dispositivo", ("CPU", "CUDA (se disponível)"), index=0
        )
        submitted = st.form_submit_button(
            "Iniciar processamento",
            disabled=current_status == ExecutionStatus.RUNNING,
        )

    if submitted:
        if video_upload is None or model_upload is None:
            st.error("Selecione o vídeo e o modelo antes de iniciar.")
        else:
            _process_submission(
                video_upload=video_upload,
                model_upload=model_upload,
                device="cpu" if device_label == "CPU" else "cuda",
                session_dir=session_dir,
            )
            result = st.session_state.get("result")

    _render_result(result)


def _process_submission(
    video_upload: UploadedFile,
    model_upload: UploadedFile,
    device: str,
    session_dir: Path,
) -> None:
    input_path: Path | None = None
    model_path: Path | None = None
    result = PipelineResult(
        status=ExecutionStatus.FAILED,
        elapsed_seconds=0.0,
        message="Não foi possível concluir o processamento.",
    )
    st.session_state["status"] = ExecutionStatus.RUNNING
    st.info("Processando vídeo. Isso pode levar algum tempo neste computador.")
    try:
        input_path = save_uploaded_file(
            video_upload,  # type: ignore[arg-type]
            video_upload.name,
            session_dir,
            VIDEO_EXTENSIONS,
            getattr(video_upload, "size", None),
        )
        model_path = save_uploaded_file(
            model_upload,  # type: ignore[arg-type]
            model_upload.name,
            session_dir,
            MODEL_EXTENSIONS,
            getattr(model_upload, "size", None),
        )
        request = PipelineRequest(
            input_path=input_path,
            output_path=OUTPUT_ROOT / f"resultado_{uuid4().hex}.mp4",
            model_path=model_path,
            device=device,
        )
        result = PipelineRunner(REPOSITORY_ROOT).execute(request)
    except ValidationError as exc:
        result = PipelineResult(
            status=ExecutionStatus.FAILED,
            elapsed_seconds=0.0,
            message=str(exc),
        )
    except OSError:
        LOGGER.exception("Falha ao armazenar os arquivos enviados")
        result = PipelineResult(
            status=ExecutionStatus.FAILED,
            elapsed_seconds=0.0,
            message="Não foi possível armazenar os arquivos enviados.",
        )
    finally:
        remove_temporary_file(input_path, session_dir)
        remove_temporary_file(model_path, session_dir)

    st.session_state["result"] = result
    st.session_state["status"] = result.status


def _render_result(result: PipelineResult | None) -> None:
    if result is None:
        st.info("Selecione um vídeo para começar.")
        return
    if result.status == ExecutionStatus.FAILED:
        st.error(result.message or "Não foi possível concluir o processamento.")
        st.caption(f"Tempo decorrido: {result.elapsed_seconds:.2f} s")
        return
    if result.status != ExecutionStatus.COMPLETED or result.output_path is None:
        return

    output_path = result.output_path
    if not output_path.is_file():
        st.error("O vídeo de saída não está mais disponível.")
        return
    st.success("Processamento concluído. Confira o vídeo gerado.")
    st.caption(
        f"Tempo: {result.elapsed_seconds:.2f} s · "
        f"Tamanho: {output_path.stat().st_size / (1024 * 1024):.2f} MB"
    )
    st.video(str(output_path))
    with output_path.open("rb") as output_file:
        st.download_button(
            "Baixar vídeo anotado",
            data=output_file,
            file_name=output_path.name,
            mime="video/mp4",
        )


if __name__ == "__main__":
    main()

