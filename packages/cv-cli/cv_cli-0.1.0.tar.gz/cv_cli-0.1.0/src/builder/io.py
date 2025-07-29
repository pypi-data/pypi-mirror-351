import yaml
from os import path, replace, makedirs
from shutil import copy
from pathlib import Path
from .constants import OUTPUT_DIR

def move_pdf(pdf_path:str|Path, output_path:str|Path) -> None:
    """Moves specified pdf file.

    Args:
        pdf_path (str): source path
        output_path (str): destination path
    """
    if path.exists(pdf_path):
        replace(pdf_path, output_path)
        print(f"PDF moved to {output_path}")
        return
    print(f"PDF not found: {pdf_path}")

def init_template(template_dir: Path, profile_build_dir: Path) -> None:
    """Initializes template files according to template config

    Args:
        template_dir (Path): path to templates directory
        profile_build_dir (Path): path to profiles directory
    """
    conf_path = template_dir / "config.yaml"
    with open(conf_path) as f:
        conf = yaml.safe_load(f)
    
    for fpath in conf["include_files"]:
        include_path = template_dir / fpath
        copy(include_path, profile_build_dir)

def init_build(profile_build_dir: Path, template_dir: Path) -> None:
    """Initializes required directories and files.

    Args:
        profile_build_dir (str): path to profiles directory
        style_path (str): path to styles directory
    """
    makedirs(f"{OUTPUT_DIR}", exist_ok=True)
    makedirs(profile_build_dir, exist_ok=True)
    # copy(style_path, profile_build_dir)
    init_template(template_dir, profile_build_dir)