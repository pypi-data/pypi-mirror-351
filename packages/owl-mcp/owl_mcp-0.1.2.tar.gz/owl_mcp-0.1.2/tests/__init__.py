from pathlib import Path

THIS_DIR = Path(__file__).parent
INPUT_DIR = THIS_DIR / "input"
OUTPUT_DIR = THIS_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)
