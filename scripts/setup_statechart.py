"""Fetch the pinned TLC test dependency into ignored, checkout-local tools."""
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar'
DIGEST = '936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88'


def install():
    target = ROOT / 'work/tools/tla2tools.jar'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != DIGEST:
            raise ValueError('Existing TLC jar differs from the pin; preserve it for inspection')
        return target
    with urllib.request.urlopen(URL, timeout=90) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != DIGEST:
        raise ValueError('Downloaded TLC jar differs from the pinned SHA-256')
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
        staging = Path(temporary.name)
        temporary.write(data)
    try:
        os.replace(staging, target)
    finally:
        staging.unlink(missing_ok=True)
    return target


if __name__ == '__main__':
    print(install())
