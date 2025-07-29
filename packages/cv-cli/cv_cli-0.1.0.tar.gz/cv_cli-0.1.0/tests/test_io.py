import pytest
import yaml
from pathlib import Path
from builder.io import move_pdf, init_template, init_build
from builder.constants import OUTPUT_DIR

def test_move_pdf_fail(tmp_path: Path, capfd: pytest.CaptureFixture):
    src = tmp_path / "fake.pdf"
    dest = tmp_path / "dest.pdf"
    move_pdf(src, dest)
    out, _ = capfd.readouterr()
    assert "PDF not found" in out
    assert not dest.exists()

def test_move_pdf(tmp_path: Path):
    src = tmp_path / "resume.pdf"
    dest = tmp_path / "dest.pdf"
    src.write_text("PDF content")
    move_pdf(src, dest)
    assert dest.read_text() == "PDF content"

def test_init_template(tmp_path: Path):
    TEST_INCLUDES = ("test1.tex", "test2.tex")
    TEST_CONTENTS = ("test1", "test2")
    TEST_CONFIG = {"include_files": [*TEST_INCLUDES]}

    template_dir = tmp_path / "template"
    profile_build_dir = tmp_path / "profile"
    template_dir.mkdir()
    profile_build_dir.mkdir()
    
    config = yaml.dump(TEST_CONFIG)
    (template_dir / "config.yaml").write_text(config)
    for path, content in zip(TEST_INCLUDES, TEST_CONTENTS):
        (template_dir / path).write_text(content)
    
    init_template(template_dir, profile_build_dir)

    for path, content in zip(TEST_INCLUDES, TEST_CONTENTS):
        assert (template_dir / path).read_text() == content

def test_init_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("builder.io.OUTPUT_DIR", str(tmp_path / "output"))
    TEST_CONFIG = {"include_files": []}

    template_dir = tmp_path / "template"
    build_dir = tmp_path / "build"
    template_dir.mkdir()
    (template_dir / "config.yaml").write_text(yaml.dump(TEST_CONFIG))

    init_build(build_dir, template_dir)

    assert (tmp_path / "output").exists()
    assert build_dir.exists()