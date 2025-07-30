from pathlib import Path
import subprocess


def main():
    app_path = Path(__file__).parent / "app.py"
    process = subprocess.Popen(["./.venv/Scripts/streamlit", "run", str(app_path)])
    process.wait()


if __name__ == "__main__":
    main()
