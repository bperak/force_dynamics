import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from .config import config_hash
from .db import connect, init_db, insert_evaluation, insert_run, insert_sentence, insert_translation
from .methodology import get_translation, blind_evaluate, prepare_blind_labels


def load_seed_data(conn, seed_dir: str, languages: List[str]) -> None:
    for lang in languages:
        path = Path(seed_dir) / f"{lang}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Seed file not found: {path}")
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            insert_sentence(
                conn,
                language=row["language"],
                original=row["original_text"],
                human=row["translation_human"],
                google=row["translation_google"],
            )


def run_pipeline(config: Dict) -> None:
    db_path = config["database"]
    seed = int(config.get("seed", 42))
    languages = config["data"]["languages"]
    seed_dir = config["data"]["seed_dir"]

    conn = connect(db_path)
    init_db(conn)
    load_seed_data(conn, seed_dir, languages)

    cfg_hash = config_hash(config)
    translation_system = config["prompts"]["translation_system"]
    evaluation_system = config["prompts"]["evaluation_system"]

    for model_cfg in config["models"]:
        provider = model_cfg["provider"]
        model = model_cfg["name"]

        created_at = datetime.utcnow().isoformat()
        run_id = insert_run(conn, provider, model, seed, cfg_hash, created_at)
        rng = random.Random(seed + run_id)

        for lang in languages:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, original_text, translation_human, translation_google
                FROM sentences WHERE language = ? ORDER BY id
                """,
                (lang.capitalize(),),
            )
            rows = cur.fetchall()

            for row in rows:
                original = row["original_text"]
                human = row["translation_human"]
                google = row["translation_google"]

                user_prompt = (
                    f"Translate the following sentence from English to {lang.capitalize()}:\n\n{original}"
                )
                translation_gpt = get_translation(provider, model, translation_system, user_prompt)

                labels, mapping = prepare_blind_labels(rng, translation_gpt, google, human)
                evaluation = blind_evaluate(
                    provider,
                    model,
                    evaluation_system,
                    original,
                    labels["A"],
                    labels["B"],
                    labels["C"],
                )

                insert_translation(conn, run_id, int(row["id"]), translation_gpt)
                insert_evaluation(conn, run_id, int(row["id"]), json.dumps(evaluation), json.dumps(mapping))

    conn.close()
