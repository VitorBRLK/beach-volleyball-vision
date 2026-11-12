"""Interface Streamlit local do Beach Volleyball Vision."""

from __future__ import annotations

import logging
from html import escape
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
DEFAULT_MODEL_PATH = REPOSITORY_ROOT / "models" / "yolov8n.pt"
LOGGER = logging.getLogger(__name__)

PAGE_STYLES = """
<style>
  :root { color-scheme: dark; }
  .bvv-hero {
    padding: 1.75rem;
    margin-bottom: 1rem;
    border: 1px solid #2A3546;
    border-radius: 16px;
    background:
      radial-gradient(circle at 92% 18%, rgba(87, 227, 170, 0.16), transparent 28%),
      linear-gradient(135deg, #151E2C 0%, #0F1724 100%);
  }
  .bvv-kicker {
    color: #57E3AA;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin: 0 0 0.55rem;
    text-transform: uppercase;
  }
  .bvv-hero h1 {
    color: #E8EEF7;
    font-size: clamp(1.65rem, 4vw, 2.35rem);
    line-height: 1.15;
    margin: 0;
  }
  .bvv-hero p {
    color: #A7B7CA;
    margin: 0.65rem 0 0;
    max-width: 44rem;
  }
  .bvv-dashboard {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 0.25rem 0 1.5rem;
  }
  .bvv-status-card {
    background: #151E2C;
    border: 1px solid #2A3546;
    border-radius: 12px;
    min-height: 96px;
    padding: 1rem;
  }
  .bvv-status-card span {
    color: #A7B7CA;
    display: block;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
  }
  .bvv-status-card strong {
    color: #E8EEF7;
    display: block;
    font-size: 1rem;
  }
  .bvv-status-card small {
    color: #A7B7CA;
    display: block;
    font-size: 0.78rem;
    margin-top: 0.3rem;
  }
  .bvv-indicator {
    border-radius: 999px;
    display: inline-block;
    height: 0.55rem;
    margin-right: 0.4rem;
    width: 0.55rem;
  }
  .bvv-indicator--ok { background: #57E3AA; }
  .bvv-indicator--warning { background: #FFC57C; }
  .bvv-steps {
    align-items: center;
    color: #A7B7CA;
    display: flex;
    flex-wrap: wrap;
    font-size: 0.82rem;
    gap: 0.55rem;
    margin: 0.25rem 0 1.25rem;
  }
  .bvv-step {
    align-items: center;
    display: inline-flex;
    gap: 0.4rem;
  }
  .bvv-step b {
    align-items: center;
    background: #1E2B3C;
    border: 1px solid #2A3546;
    border-radius: 999px;
    color: #57E3AA;
    display: inline-flex;
    height: 1.65rem;
    justify-content: center;
    width: 1.65rem;
  }
  .bvv-arrow { color: #617187; }
  .bvv-file-summary {
    background: #111A27;
    border: 1px solid #2A3546;
    border-radius: 8px;
    color: #A7B7CA;
    font-size: 0.82rem;
    margin: -0.35rem 0 0.85rem;
    padding: 0.65rem 0.75rem;
  }
  .bvv-file-summary strong { color: #E8EEF7; }
  .bvv-result-empty {
    border: 1px dashed #3A485C;
    border-radius: 12px;
    color: #A7B7CA;
    padding: 1.25rem;
    text-align: center;
  }
  a:focus-visible, button:focus-visible, input:focus-visible,
  [role="button"]:focus-visible, [tabindex]:focus-visible {
    outline: 3px solid #57E3AA !important;
    outline-offset: 3px !important;
  }
  @media (max-width: 780px) {
    .bvv-hero { padding: 1.25rem; }
    .bvv-dashboard { grid-template-columns: 1fr; }
    .bvv-arrow { display: none; }
    .bvv-steps { align-items: flex-start; flex-direction: column; }
  }
</style>
"""


class UploadedFile(Protocol):
    """Parte do contrato de upload usada pela aplicação."""

    name: str
    size: int

    def read(self, size: int = -1) -> bytes: ...


def main() -> None:
    """Monta o dashboard e coordena o fluxo da interface."""

    logging.basicConfig(level=logging.INFO)
    st.set_page_config(
        page_title="Beach Volleyball Vision",
        page_icon="🏐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(PAGE_STYLES, unsafe_allow_html=True)

    session_id = st.session_state.setdefault("session_id", uuid4().hex)
    session_dir = WORK_ROOT / session_id
    result: PipelineResult | None = st.session_state.get("result")
    current_status = st.session_state.setdefault("status", ExecutionStatus.IDLE)
    pipeline_available = (REPOSITORY_ROOT / "run.py").is_file()

    _render_header()
    _render_dashboard(pipeline_available, current_status)
    _render_journey()

    configuration_column, status_column = st.columns([1.6, 1], gap="large")
    with configuration_column:
        st.subheader("1. Configure a análise")
        st.caption(
            "Escolha os arquivos locais. Eles ficam em uma área temporária "
            "controlada e o vídeo original não é alterado."
        )
        video_upload = st.file_uploader(
            "Vídeo da partida",
            type=sorted(extension.removeprefix(".") for extension in VIDEO_EXTENSIONS),
            help="Formatos aceitos: AVI, MKV, MOV, MP4 e WebM.",
        )
        if video_upload is not None:
            _render_file_summary("Vídeo selecionado", video_upload)

        default_model_available = DEFAULT_MODEL_PATH.is_file()
        if default_model_available:
            st.caption(
                "Modelo padrão local selecionado: YOLOv8n. "
                "Envie outro arquivo somente se quiser substituí-lo."
            )

        model_upload = st.file_uploader(
            (
                "Modelo YOLO personalizado (opcional)"
                if default_model_available
                else "Modelo YOLO local"
            ),
            type=sorted(extension.removeprefix(".") for extension in MODEL_EXTENSIONS),
            help="Use pesos .pt ou .onnx confiáveis.",
        )
        if model_upload is not None:
            _render_file_summary("Modelo selecionado", model_upload)

        model_ready = default_model_available or model_upload is not None
        missing_uploads = video_upload is None or not model_ready
        execution_running = current_status == ExecutionStatus.RUNNING
        execution_disabled = (
            missing_uploads or execution_running or not pipeline_available
        )

        with st.form("pipeline_configuration"):
            device_label = st.selectbox(
                "Dispositivo de processamento",
                ("CPU — recomendado", "CUDA — se disponível"),
                index=0,
                help="CUDA só será usada se o ambiente confirmar suporte.",
            )
            submitted = st.form_submit_button(
                "Iniciar processamento",
                type="primary",
                disabled=execution_disabled,
                use_container_width=True,
            )

        _render_execution_hint(
            pipeline_available=pipeline_available,
            missing_video=video_upload is None,
            model_ready=model_ready,
            execution_running=execution_running,
        )

        if submitted and video_upload is not None and model_ready:
            with st.status(
                "Processando vídeo. Isso pode levar algum tempo neste computador.",
                expanded=True,
            ) as status_box:
                result = _process_submission(
                    video_upload=video_upload,
                    model_upload=model_upload,
                    device="cpu" if device_label.startswith("CPU") else "cuda",
                    session_dir=session_dir,
                    default_model_path=(
                        DEFAULT_MODEL_PATH if model_upload is None else None
                    ),
                )
                if result.status == ExecutionStatus.COMPLETED:
                    status_box.update(
                        label="Processamento concluído.",
                        state="complete",
                        expanded=False,
                    )
                else:
                    status_box.update(
                        label="Não foi possível concluir o processamento.",
                        state="error",
                    )
            current_status = result.status

    with status_column:
        _render_processing_panel(current_status, result, pipeline_available)

    st.divider()
    st.subheader("3. Resultado")
    _render_result(result)


def _render_header() -> None:
    st.markdown(
        """
        <header class="bvv-hero">
          <p class="bvv-kicker">Análise local de vídeo</p>
          <h1>Beach Volleyball Vision</h1>
          <p>
            Configure e acompanhe o processamento de partidas gravadas em um
            fluxo seguro, local e otimizado para CPU.
          </p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def _render_dashboard(
    pipeline_available: bool, current_status: ExecutionStatus
) -> None:
    pipeline_label = "Disponível" if pipeline_available else "Indisponível"
    pipeline_detail = (
        "CLI encontrada no repositório"
        if pipeline_available
        else "run.py não foi encontrado"
    )
    indicator_class = "ok" if pipeline_available else "warning"
    state_labels = {
        ExecutionStatus.IDLE: "Aguardando configuração",
        ExecutionStatus.RUNNING: "Processamento em andamento",
        ExecutionStatus.COMPLETED: "Última execução concluída",
        ExecutionStatus.FAILED: "Última execução falhou",
    }
    st.markdown(
        f"""
        <section class="bvv-dashboard" aria-label="Resumo do ambiente">
          <div class="bvv-status-card">
            <span>Pipeline</span>
            <strong><i class="bvv-indicator bvv-indicator--{indicator_class}"></i>{pipeline_label}</strong>
            <small>{pipeline_detail}</small>
          </div>
          <div class="bvv-status-card">
            <span>Estado</span>
            <strong>{escape(state_labels[current_status])}</strong>
            <small>Baseado na execução desta sessão</small>
          </div>
          <div class="bvv-status-card">
            <span>Ambiente</span>
            <strong>Local · CPU padrão</strong>
            <small>Acesso restrito a 127.0.0.1</small>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_journey() -> None:
    st.markdown(
        """
        <nav class="bvv-steps" aria-label="Etapas da análise">
          <span class="bvv-step"><b>1</b> Configuração</span>
          <span class="bvv-arrow" aria-hidden="true">→</span>
          <span class="bvv-step"><b>2</b> Processamento</span>
          <span class="bvv-arrow" aria-hidden="true">→</span>
          <span class="bvv-step"><b>3</b> Resultado</span>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def _render_file_summary(label: str, uploaded_file: UploadedFile) -> None:
    safe_name = escape(Path(uploaded_file.name).name)
    size = _format_bytes(max(0, getattr(uploaded_file, "size", 0)))
    st.markdown(
        f'<div class="bvv-file-summary"><strong>{escape(label)}:</strong> '
        f"{safe_name} · {size}</div>",
        unsafe_allow_html=True,
    )


def _render_execution_hint(
    *,
    pipeline_available: bool,
    missing_video: bool,
    model_ready: bool,
    execution_running: bool,
) -> None:
    if not pipeline_available:
        st.warning(
            "O pipeline de análise ainda não está disponível neste ambiente. "
            "Adicione a CLI run.py para habilitar o processamento."
        )
    elif execution_running:
        st.caption("O botão permanece desabilitado enquanto a execução está ativa.")
    elif missing_video:
        st.caption("Selecione um vídeo para habilitar o processamento.")
    elif not model_ready:
        st.caption("Selecione um modelo YOLO para habilitar o processamento.")


def _render_processing_panel(
    current_status: ExecutionStatus,
    result: PipelineResult | None,
    pipeline_available: bool,
) -> None:
    st.subheader("2. Acompanhe o processamento")
    if current_status == ExecutionStatus.RUNNING:
        st.info("Processando vídeo. Isso pode levar algum tempo neste computador.")
        return
    if current_status == ExecutionStatus.COMPLETED:
        st.success("Processamento concluído e arquivo de saída verificado.")
        if result is not None:
            st.caption(f"Tempo medido: {result.elapsed_seconds:.2f} s")
        return
    if current_status == ExecutionStatus.FAILED:
        st.error("A última tentativa não foi concluída.")
        if result is not None:
            st.caption(f"Tempo medido: {result.elapsed_seconds:.2f} s")
        return
    st.info("Selecione um vídeo para começar.")
    if not pipeline_available:
        st.caption("A configuração pode ser revisada, mas a execução está indisponível.")
    else:
        st.caption("Nenhum processamento foi iniciado nesta sessão.")


def _process_submission(
    video_upload: UploadedFile,
    model_upload: UploadedFile | None,
    device: str,
    session_dir: Path,
    default_model_path: Path | None = None,
) -> PipelineResult:
    input_path: Path | None = None
    model_path: Path | None = None
    result = PipelineResult(
        status=ExecutionStatus.FAILED,
        elapsed_seconds=0.0,
        message="Não foi possível concluir o processamento.",
    )
    st.session_state["status"] = ExecutionStatus.RUNNING
    try:
        input_path = save_uploaded_file(
            video_upload,  # type: ignore[arg-type]
            video_upload.name,
            session_dir,
            VIDEO_EXTENSIONS,
            getattr(video_upload, "size", None),
        )
        if model_upload is not None:
            model_path = save_uploaded_file(
                model_upload,  # type: ignore[arg-type]
                model_upload.name,
                session_dir,
                MODEL_EXTENSIONS,
                getattr(model_upload, "size", None),
            )
        elif default_model_path is not None:
            with default_model_path.open("rb") as default_model:
                model_path = save_uploaded_file(
                    default_model,
                    default_model_path.name,
                    session_dir,
                    MODEL_EXTENSIONS,
                    default_model_path.stat().st_size,
                )
        else:
            raise ValidationError("Selecione um modelo YOLO para continuar.")
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
    return result


def _render_result(result: PipelineResult | None) -> None:
    if result is None:
        st.markdown(
            '<div class="bvv-result-empty">O vídeo processado aparecerá aqui '
            "quando uma execução for concluída.</div>",
            unsafe_allow_html=True,
        )
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
        f"Tamanho: {_format_bytes(output_path.stat().st_size)}"
    )
    st.video(str(output_path))
    with output_path.open("rb") as output_file:
        st.download_button(
            "Baixar vídeo anotado",
            data=output_file,
            file_name=output_path.name,
            mime="video/mp4",
            use_container_width=True,
        )


def _format_bytes(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


if __name__ == "__main__":
    main()
