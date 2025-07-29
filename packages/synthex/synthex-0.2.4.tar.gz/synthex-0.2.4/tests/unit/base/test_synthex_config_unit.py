import pytest
from pytest import MonkeyPatch
import os

from synthex.config import Config


@pytest.mark.unit
def test_synthex_config_no_env_file(monkeypatch: MonkeyPatch):
    """
    This test ensures that the Config class can be successfully instantiated without raising
    an exception when no .env file is present. If instantiation fails, the test will fail.
    Arguments:
        monkeypatch (MonkeyPatch): pytest fixture for safely modifying environment variables.
    """
    
    # Remove .env file.
    os.remove(".env")
    # Remove all environment variables that were already picked up.
    for var in os.environ:
        monkeypatch.delenv(var, raising=False)
    
    config = Config() # type: ignore