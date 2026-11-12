from __future__ import annotations

from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

import pytest

import run


class FakeCapture:
    def __init__(self) -> None:
        self.frames = [object(), object()]

    def isOpened(self) -> bool:
        return True

    def get(self, property_id: int) -> float:
        values = {
            run.cv2.CAP_PROP_FRAME_WIDTH: 640,
            run.cv2.CAP_PROP_FRAME_HEIGHT: 360,
            run.cv2.CAP_PROP_FPS: 30,
        }
        return values[property_id]

    def read(self) -> tuple[bool, object | None]:
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self) -> None:
        return None


class FakeWriter:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.write_bytes(b"video")

    def isOpened(self) -> bool:
        return True

    def write(self, _frame: object) -> None:
        return None

    def release(self) -> None:
        return None


class FakePrediction:
    def plot(self) -> object:
        return object()


class FakeModel:
    names: ClassVar[dict[int, str]] = {
        0: "person",
        32: "sports ball",
        35: "baseball glove",
    }

    def __init__(self, _path: str) -> None:
        self.calls: list[dict[str, object]] = []

    def predict(self, **kwargs: object) -> list[FakePrediction]:
        self.calls.append(kwargs)
        return [FakePrediction()]


def test_pipeline_streams_frames_and_writes_output(tmp_path: Path) -> None:
    input_path = tmp_path / "entrada.mp4"
    model_path = tmp_path / "modelo.pt"
    output_path = tmp_path / "resultado.mp4"
    input_path.write_bytes(b"video")
    model_path.write_bytes(b"modelo")
    fake_model = FakeModel(str(model_path))

    with (
        patch("run._load_yolo_class", return_value=lambda _path: fake_model),
        patch("run.cv2.VideoCapture", return_value=FakeCapture()),
        patch(
            "run.cv2.VideoWriter",
            side_effect=lambda path, *_args: FakeWriter(path),
        ),
        patch("run.cv2.VideoWriter_fourcc", return_value=0),
    ):
        summary = run.run_pipeline(input_path, output_path, model_path)

    assert summary.frames_processed == 2
    assert output_path.read_bytes() == b"video"
    assert len(fake_model.calls) == 2
    assert fake_model.calls[0]["device"] == "cpu"
    assert fake_model.calls[0]["classes"] == [0, 32]


def test_pipeline_refuses_to_overwrite_output(tmp_path: Path) -> None:
    input_path = tmp_path / "entrada.mp4"
    model_path = tmp_path / "modelo.pt"
    output_path = tmp_path / "resultado.mp4"
    input_path.write_bytes(b"video")
    model_path.write_bytes(b"modelo")
    output_path.write_bytes(b"existente")

    with pytest.raises(run.PipelineError, match="nao sera sobrescrito"):
        run.run_pipeline(input_path, output_path, model_path)


def test_pipeline_removes_partial_output_after_inference_failure(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "entrada.mp4"
    model_path = tmp_path / "modelo.pt"
    output_path = tmp_path / "resultado.mp4"
    input_path.write_bytes(b"video")
    model_path.write_bytes(b"modelo")
    fake_model = FakeModel(str(model_path))

    with (
        patch("run._load_yolo_class", return_value=lambda _path: fake_model),
        patch.object(fake_model, "predict", return_value=[]),
        patch("run.cv2.VideoCapture", return_value=FakeCapture()),
        patch(
            "run.cv2.VideoWriter",
            side_effect=lambda path, *_args: FakeWriter(path),
        ),
        patch("run.cv2.VideoWriter_fourcc", return_value=0),
        pytest.raises(run.PipelineError, match="nao retornou resultado"),
    ):
        run.run_pipeline(input_path, output_path, model_path)

    assert not output_path.exists()
    assert not list(tmp_path.glob("*.partial.mp4"))


def test_model_must_expose_person_or_ball_class() -> None:
    with pytest.raises(run.PipelineError, match="classes compativeis"):
        run._target_class_ids({5: "cat"})


def test_cli_defaults_to_cpu() -> None:
    args = run.build_parser().parse_args(
        ["entrada.mp4", "--out", "saida.mp4", "--model", "modelo.pt"]
    )

    assert args.device == "cpu"
