from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_assets_path() -> Path:
    return get_project_root() / "assets"


def get_images_path() -> Path:
    return get_assets_path() / "images"
