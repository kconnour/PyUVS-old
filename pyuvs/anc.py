from pathlib import Path
import numpy as np


def get_package_path() -> Path:
    return Path(__file__).parent.resolve()


def get_muv_template_filepath() -> Path:
    return get_package_path() / 'anc' / 'muv_templates.npy'


def load_muv_templates() -> dict:
    file_path = get_muv_template_filepath()
    return np.load(file_path, allow_pickle=True).item()


def load_no_nightglow_template() -> np.ndarray:
    return load_muv_templates()['no_nightglow']
