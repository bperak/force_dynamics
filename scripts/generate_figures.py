import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.config import load_config


def main():
    parser = argparse.ArgumentParser(description='Generate figures')
    parser.add_argument('--config', default='configs/config.yaml', help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config)
    tables_dir = Path(config['output']['tables_dir'])
    figures_dir = Path(config['output']['figures_dir'])
    figures_dir.mkdir(parents=True, exist_ok=True)

    table_path = tables_dir / 'table3_scores.csv'
    if not table_path.exists():
        raise SystemExit(f'Missing table: {table_path}')

    df = pd.read_csv(table_path)

    # Simple bar chart: GPT self-score by language and model
    fig, ax = plt.subplots(figsize=(8, 4))
    for model in df['model'].unique():
        subset = df[df['model'] == model]
        ax.plot(subset['language'], subset['gpt_self_score'], marker='o', label=model)

    ax.set_title('GPT Self-Score by Language and Model')
    ax.set_xlabel('Language')
    ax.set_ylabel('Average Self-Score')
    ax.legend()

    out_path = figures_dir / 'gpt_self_score_by_language.png'
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    main()
