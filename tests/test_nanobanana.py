"""Unit tests for the nanobanana script. No network, no API key."""

import base64
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PNG = b"\x89PNG\r\n\x1a\nfake"


def image_response(data=PNG, mime="image/png"):
    part = SimpleNamespace(inline_data=SimpleNamespace(data=data, mime_type=mime))
    return SimpleNamespace(parts=[part])


class FakeClient:
    """Stands in for genai.Client and records every generate_content call."""

    def __init__(self, response=None, error=None):
        self.calls = []
        self.response = response if response is not None else image_response()
        self.error = error
        self.models = self

    def generate_content(self, model, contents, config):
        self.calls.append(
            SimpleNamespace(model=model, contents=contents, config=config)
        )
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def fake_client(nb, monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(nb, "get_client", lambda: client)
    return client


def run_cli(nb, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["nanobanana", *argv])
    nb.main()


# --- helpers -----------------------------------------------------------------


def test_get_api_key_prefers_nanobanana_var(nb, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini")
    monkeypatch.setenv("NANOBANANA_API_KEY", "preferred")
    assert nb.get_api_key() == "preferred"


def test_get_api_key_falls_back(nb, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google")
    assert nb.get_api_key() == "google"


def test_get_api_key_missing_exits(nb):
    with pytest.raises(SystemExit, match="No API key found"):
        nb.get_api_key()


def test_model_name_default_and_override(nb, monkeypatch):
    assert nb.model_name() == nb.DEFAULT_MODEL
    monkeypatch.setenv("NANOBANANA_MODEL", "other-model")
    assert nb.model_name() == "other-model"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("A Cat, on the Moon!", "a_cat_on_the_moon"),
        ("   ", "generated_image"),
        ("!!!", "generated_image"),
        ("story_step1_seed grows", "story_step1_seed_grows"),
        ("x" * 50, "x" * 32),
    ],
)
def test_slugify(nb, text, expected):
    assert nb.slugify(text) == expected


def test_unique_path_increments(nb):
    first = nb.unique_path("cat")
    assert first == nb.OUTPUT_DIR / "cat.png"
    first.write_bytes(b"x")
    assert nb.unique_path("cat") == nb.OUTPUT_DIR / "cat_1.png"


def test_find_input_searches_dirs(nb, tmp_path, monkeypatch):
    images = tmp_path / "images"
    images.mkdir()
    (images / "photo.jpg").write_bytes(b"x")
    monkeypatch.setattr(nb, "SEARCH_DIRS", [tmp_path, images])
    assert nb.find_input("photo.jpg") == images / "photo.jpg"


def test_find_input_missing_exits(nb, tmp_path, monkeypatch):
    monkeypatch.setattr(nb, "SEARCH_DIRS", [tmp_path])
    with pytest.raises(SystemExit, match="not found"):
        nb.find_input("missing.png")


def test_csv_parsers(nb):
    assert nb.csv_str(" a, b ,,c ") == ["a", "b", "c"]
    assert nb.csv_int("16, 32,64") == [16, 32, 64]


# --- response parsing ----------------------------------------------------------


def test_extract_images_bytes_and_mime(nb):
    assert nb.extract_images(image_response(PNG, "image/JPEG")) == [(PNG, "jpg")]


def test_extract_images_base64_string(nb):
    encoded = base64.b64encode(PNG).decode()
    assert nb.extract_images(image_response(encoded)) == [(PNG, "png")]


def test_extract_images_from_candidates(nb):
    part = SimpleNamespace(
        inline_data=SimpleNamespace(data=PNG, mime_type="image/webp")
    )
    response = SimpleNamespace(
        parts=None,
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))],
    )
    assert nb.extract_images(response) == [(PNG, "webp")]


def test_extract_images_skips_text_parts(nb):
    response = SimpleNamespace(parts=[SimpleNamespace(inline_data=None, text="hi")])
    assert nb.extract_images(response) == []


# --- prompt and config builders --------------------------------------------------


def test_build_batch_prompts_count(nb):
    assert nb.build_batch_prompts("cat", 3, None, None) == ["cat"] * 3


def test_build_batch_prompts_styles_and_variations(nb):
    prompts = nb.build_batch_prompts("cat", 0, ["anime"], ["lighting"])
    assert prompts == [
        "cat, anime style, dramatic lighting",
        "cat, anime style, soft lighting",
    ]


def test_build_batch_prompts_truncates_to_count(nb):
    assert len(nb.build_batch_prompts("cat", 2, ["a", "b", "c"], None)) == 2


def test_build_image_config_none_without_options(nb):
    assert nb.build_image_config(SimpleNamespace()) is None


def test_build_image_config_sets_fields(nb):
    args = SimpleNamespace(aspect_ratio="1:1", resolution="4K", thinking="high")
    config = nb.build_image_config(args)
    assert config.image_config.aspect_ratio == "1:1"
    assert config.image_config.image_size == "4K"
    assert config.thinking_config.thinking_level.lower() == "high"


def test_build_image_config_without_thinking(nb):
    args = SimpleNamespace(aspect_ratio="16:9", resolution="2K", thinking=None)
    assert nb.build_image_config(args).thinking_config is None


def test_build_icon_prompt(nb):
    args = SimpleNamespace(
        prompt="rocket",
        style="flat",
        type="app-icon",
        corners="rounded",
        background="white",
    )
    assert nb.build_icon_prompt(args) == (
        "rocket, flat style app-icon, rounded corners, white background, "
        "clean design, high quality, professional"
    )


def test_build_pattern_prompt_seamless(nb):
    args = SimpleNamespace(
        prompt="leaves",
        style="floral",
        type="seamless",
        density="dense",
        colors="duotone",
        size="256x256",
    )
    prompt = nb.build_pattern_prompt(args)
    assert "tileable" in prompt
    assert prompt.startswith("leaves, floral style seamless pattern")


def test_build_diagram_prompt(nb):
    args = SimpleNamespace(
        prompt="login flow",
        type="sequence",
        style="clean",
        layout="vertical",
        complexity="simple",
        colors="mono",
        annotations="minimal",
    )
    assert nb.build_diagram_prompt(args).startswith("login flow, sequence diagram")


# --- commands, end to end with a fake client ----------------------------------------


def test_generate_saves_image(nb, fake_client, monkeypatch, capsys):
    run_cli(nb, monkeypatch, "generate", "a red fox", "--resolution", "1K")
    saved = Path(capsys.readouterr().out.strip())
    assert saved == nb.OUTPUT_DIR / "a_red_fox.png"
    assert saved.read_bytes() == PNG
    (call,) = fake_client.calls
    assert call.contents == ["a red fox"]
    assert call.config.image_config.image_size == "1K"


def test_generate_batch_with_count(nb, fake_client, monkeypatch, capsys):
    run_cli(nb, monkeypatch, "generate", "fox", "--count", "3")
    assert len(capsys.readouterr().out.split()) == 3
    assert len(fake_client.calls) == 3


def test_generate_fails_when_model_errors(nb, monkeypatch):
    monkeypatch.setattr(
        nb, "get_client", lambda: FakeClient(error=RuntimeError("boom"))
    )
    with pytest.raises(SystemExit, match="no images generated"):
        run_cli(nb, monkeypatch, "generate", "fox")


def test_edit_sends_input_image(nb, fake_client, tmp_path, monkeypatch, capsys):
    (tmp_path / "in.png").write_bytes(PNG)
    monkeypatch.setattr(nb, "SEARCH_DIRS", [tmp_path])
    run_cli(nb, monkeypatch, "edit", "in.png", "make it blue")
    assert Path(capsys.readouterr().out.strip()).name == "edit_make_it_blue.png"
    prompt, image_part = fake_client.calls[0].contents
    assert prompt == "make it blue"
    assert image_part.inline_data.mime_type == "image/png"


def test_icon_one_file_per_size(nb, fake_client, monkeypatch, capsys):
    run_cli(nb, monkeypatch, "icon", "rocket", "--sizes", "16,32", "--format", "jpeg")
    outputs = capsys.readouterr().out.split()
    assert [Path(p).name for p in outputs] == ["rocket_16.jpg", "rocket_32.jpg"]


def test_story_steps(nb, fake_client, monkeypatch, capsys):
    run_cli(nb, monkeypatch, "story", "seed grows", "--steps", "2", "--type", "process")
    assert len(capsys.readouterr().out.split()) == 2
    assert "step 2 of 2" in fake_client.calls[1].contents[0]
    assert "transition from previous step" in fake_client.calls[1].contents[0]


@pytest.mark.parametrize("command", ["pattern", "diagram"])
def test_single_image_commands(nb, fake_client, monkeypatch, capsys, command):
    run_cli(nb, monkeypatch, command, "test subject")
    assert Path(capsys.readouterr().out.strip()).exists()


def test_rejects_unknown_aspect_ratio(nb, monkeypatch):
    with pytest.raises(SystemExit):
        run_cli(nb, monkeypatch, "generate", "fox", "--aspect-ratio", "7:3")
