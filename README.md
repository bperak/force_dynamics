# Force Dynamics Translation Evaluation

End-to-end pipeline for translation, blind evaluation, and analysis of Force Dynamics (FD) relations across languages.

## What this repo does
- Loads seed data from `data/seed/*.csv`
- Generates model translations (OpenAI + Gemini)
- Runs blind evaluation with explicit FD framework
- Stores all outputs in SQLite (`data/forcedynamics.sqlite`)
- Generates paper-ready tables and figures

## Quick start

1) Create a virtual environment and install requirements:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2) Set API keys:
- Copy `.env.example` to `.env`
- Fill in `OPENAI_API_KEY` and `GEMINI_API_KEY`

3) Optional config changes:
- Edit `configs/config.yaml` to switch models, adjust temperatures, or change the SQLite path

4) Run the pipeline:
```
python scripts\run_pipeline.py --config configs\config.yaml
```

5) Generate tables/figures:
```
python scripts\generate_tables.py --config configs\config.yaml
python scripts\generate_figures.py --config configs\config.yaml
```

## Data
Seed CSVs live in `data/seed/`:
- `finnish.csv`
- `polish.csv`
- `croatian.csv`

Each CSV has columns:
- `id`
- `language`
- `original_text`
- `translation_human`
- `translation_google`

## Outputs
- SQLite DB: `data/forcedynamics.sqlite`
- Tables: `outputs/tables/`
- Figures: `outputs/figures/`

## Notes
- This repo is public. Do not commit secrets.
- The pipeline uses deterministic seeds for reproducible shuffling.
- Results are exploratory; small sample sizes require cautious interpretation.
