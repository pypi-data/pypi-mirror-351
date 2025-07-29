from __future__ import annotations

import importlib.metadata

import deltakit as m


def test_version():
    assert importlib.metadata.version("deltakit") == m.__version__
