import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main


def test_build_download_command_includes_youtube_runtime_and_extractor_args():
    command = main.build_download_command(
        "https://youtu.be/yaFFcH5apoI?feature=shared",
        "mp4",
        "best",
        "/tmp/downloads",
        "/usr/bin",
    )

    assert "--js-runtimes" in command
    assert "--extractor-args" in command
    assert "youtube:player_client=android" in command
