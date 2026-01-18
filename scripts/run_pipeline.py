import argparse
from pathlib import Path

from src.config import load_config
from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run end-to-end pipeline")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        raise SystemExit(f"Config not found: {cfg_path}")

    config = load_config(str(cfg_path))
    run_pipeline(config)


if __name__ == "__main__":
    main()
