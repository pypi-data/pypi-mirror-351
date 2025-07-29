import pytest
import yaml
from unittest.mock import patch
from pathlib import Path
from builder.render import tex_esc, get_jinja_env, build_template, TEMPLATE_FNAME
from builder.render import latex_render

def test_tex_esc_escapes_latex_chars():
    assert tex_esc("test123%&$") == "test123\\%\\&\\$"
    assert tex_esc("{test 123}") == "\\{test 123\\}"
    assert tex_esc("test 123") == "test 123"

def test_get_jinja_env(tmp_path):
    env = get_jinja_env(tmp_path)
    assert env.variable_start_string == "{{"
    assert env.variable_end_string == "}}"
    assert env.block_start_string == "{%"
    assert env.block_end_string == "%}"

def test_build_template(tmp_path):
    profile_path = tmp_path / "profile.yaml"
    template_dir = tmp_path / "template"
    tex_path = tmp_path / "output.tex"

    profile_path.write_text("name: Jane\nemail: jane@example.com")

    template_dir.mkdir()
    template_file = template_dir / TEMPLATE_FNAME
    template_file.write_text("Name: {{ name }}\nEmail: {{ email }}")

    build_template(profile_path, template_dir, tex_path)

    assert tex_path.exists()
    content = tex_path.read_text()
    assert "Name: Jane" in content
    assert "Email: jane@example.com" in content

def test_latex_render_calls_latexmk(tmp_path):
    resume = tmp_path / "resume.tex"
    resume.write_text("empty")

    with patch("builder.render.system") as mock_sys, patch("builder.render.chdir") as mock_chdir:
        latex_render(tmp_path)

        mock_chdir.assert_any_call(tmp_path)
        mock_sys.assert_called_once()
        assert "latexmk" in mock_sys.call_args[0][0]