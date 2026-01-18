import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.config import load_config


def parse_scores(evaluation_json: str, mapping_json: str) -> dict:
    eval_data = json.loads(evaluation_json)
    mapping = json.loads(mapping_json)

    scores = {
        'GPT': None,
        'Google': None,
        'Human': None,
    }

    score_map = {
        'A': eval_data.get('translation_A_score'),
        'B': eval_data.get('translation_B_score'),
        'C': eval_data.get('translation_C_score'),
    }

    for label, target in mapping.items():
        if target in scores:
            scores[target] = score_map.get(label)

    return scores


def main():
    parser = argparse.ArgumentParser(description='Generate summary tables')
    parser.add_argument('--config', default='configs/config.yaml', help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config)
    db_path = config['database']
    out_dir = Path(config['output']['tables_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.id, r.provider, r.model, s.language, e.evaluation_json, e.mapping_json
        FROM evaluations e
        JOIN runs r ON e.run_id = r.id
        JOIN sentences s ON e.sentence_id = s.id
        ORDER BY r.id, s.language, s.id
        """
    )

    accum = defaultdict(lambda: {'GPT': [], 'Google': [], 'Human': []})
    for run_id, provider, model, language, evaluation_json, mapping_json in cur.fetchall():
        scores = parse_scores(evaluation_json, mapping_json)
        key = (run_id, provider, model, language)
        for k, v in scores.items():
            if v is not None:
                accum[key][k].append(float(v))

    rows = []
    for (run_id, provider, model, language), vals in accum.items():
        gpt = sum(vals['GPT']) / len(vals['GPT']) if vals['GPT'] else None
        google = sum(vals['Google']) / len(vals['Google']) if vals['Google'] else None
        human = sum(vals['Human']) / len(vals['Human']) if vals['Human'] else None
        bias = None
        if gpt is not None and human is not None:
            bias = gpt - human
        rows.append({
            'run_id': run_id,
            'provider': provider,
            'model': model,
            'language': language,
            'gpt_self_score': gpt,
            'google_score': google,
            'human_score': human,
            'bias_self_minus_human': bias,
        })

    df = pd.DataFrame(rows)
    out_path = out_dir / 'table3_scores.csv'
    df.to_csv(out_path, index=False)
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    main()
