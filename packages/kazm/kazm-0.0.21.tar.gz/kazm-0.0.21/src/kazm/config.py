from configparser import ConfigParser
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

_settings = ConfigParser()
_settings.read(Path(__file__).parent / "settings.ini")

def get_secret(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise KeyError(f"Missing required environment variable: {key}")
    return value

def get_setting(section: str) -> str:
    if section not in _settings:
        raise ValueError(f"Setting section {section} not found")
    return dict(_settings[section])

if __name__ == '__main__':
    assert get_setting("AI")
    assert get_secret("GROQ_API_KEY")