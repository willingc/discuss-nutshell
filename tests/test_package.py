from __future__ import annotations

import importlib.metadata

import discuss_nutshell as m


def test_version():
    """Test that the version matches."""
    assert importlib.metadata.version("discuss_nutshell") == m.__version__
