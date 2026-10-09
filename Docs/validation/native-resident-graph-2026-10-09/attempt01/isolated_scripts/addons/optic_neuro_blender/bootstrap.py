"""Verify the installed package and immutable bundled source closure."""
import hashlib
from pathlib import Path
import sys

from .runtime import read_json

PACKAGE = Path(__file__).resolve().parent


def verify_bundle():
    manifest = read_json(PACKAGE / 'package_manifest.json', 2**20)
    if manifest.get('schema') != 'optic_neuro_blender.package.v1':
        raise ValueError('Manifiesto de instalación incompatible')
    for name, expected in manifest['files'].items():
        path = (PACKAGE / name).resolve()
        if not path.is_relative_to(PACKAGE) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('La instalación no coincide con su manifiesto: ' + name)
    # Namespace isolation is also checked when reusing a Python interpreter.
    for name, module in list(sys.modules.items()):
        if name.startswith('optic_neuro_blender._vendor.') and getattr(module, '__file__', None):
            if not Path(module.__file__).resolve().is_relative_to(PACKAGE / '_vendor'):
                raise ValueError('Conflicto con otra instalación del núcleo')
    return manifest
