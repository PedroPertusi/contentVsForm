# Notebook Guide

Run these notebooks in order to recreate the pipeline. Paths are relative to the repo root.

## Recommended Order
1) `src/data_preproc.ipynb` (original mode) — clean the PERSUADE essays, compute style metrics (TAALED/TAACO/TAASSC), and generate BERT embeddings for model training. Copy/rename the saved outputs to the locations expected by the training notebooks (`../data/full/` and `../embeddings/`) or adjust the notebook paths.  
2) `src/hyperparam_tuning.ipynb` (optional) — tune baseline XGBoost hyperparameters on the full dataset before training SES-specific models.  
3) `src/low_ses_scorer.ipynb` and `src/high_ses_scorer.ipynb` — train SES-specific XGBoost regressors (multiple feature sets), save fold models and out-of-fold predictions.  
4) `src/prompt.ipynb` — generate six GPT rewrites per essay (uses Azure OpenAI + prompts), save raw and cleaned rewrites.  
5) `src/data_preproc.ipynb` (rewrites mode) — run the same style metrics and embeddings on the cleaned rewrites and align CV folds with the trained models.  
6) `src/scorer.ipynb` — score originals and rewrites with the saved models to create the main `data_sat_scored.csv` dataset.  
7) `src/descriptive_statistics.ipynb` (optional) — basic summary stats on the full dataset.  
8) `src/measuring_redundency.ipynb` — quantify redundancy between style and embedding features, save figures.  
9) `src/decomp_bootstraping.ipynb` — fixed-effects decomposition of SES score gaps with bootstrap CIs, export tables.  
10) `src/images.ipynb` — generate all figures for the paper/tables from scored data, embeddings, and decomposition outputs.

## Notebook Inputs, Outputs, and Purpose
- `src/data_preproc.ipynb`  
  - Purpose: clean text, run TAALED/TAACO/TAASSC, and compute BERT [CLS] embeddings. Supports `MODE="original"` (raw essays) or `MODE="rewrites"` (GPT outputs).  
  - Inputs: original essays `data/persuade/persuade_2.0_human_scores_demo_id_github.csv` (for `original` mode); cleaned rewrites `data/rewrites/sat_full/rew_sat_{1..6}.csv`; model CV files `model/run_01/data_high_scored.csv` and `data_low_scored.csv` for fold alignment when processing rewrites.  
  - Outputs: preprocessed CSVs (`data/processed/sat_full/original_full.csv`, `_low_SES.csv`, `_high_SES.csv` or `rewrite_{1..6}.csv` plus `original.csv` aligned to rewrites) and embeddings (`embeddings/sat_full/embeddings_original_full.npy`, `_low.npy`, `_high.npy`, `embeddings_original.npy`, `embeddings_rewrite_{1..6}.npy`). Copy/rename to `data/full/data_full*.csv` and `embeddings/embeddings_*.npy` if you keep downstream paths unchanged.

- `src/hyperparam_tuning.ipynb` (optional)  
  - Purpose: randomized search for XGBoost baseline hyperparameters.  
  - Inputs: `data/full/data_full.csv`, `embeddings/embeddings_full.npy`.  
  - Outputs: best params JSON `model/xgb_baseline_best_params.json`.

- `src/low_ses_scorer.ipynb`  
  - Purpose: train 5-fold XGBoost regressors for low-SES essays across feature sets (full/style/embedding/TAALED/TAACO/TAASSC), record OOF metrics.  
  - Inputs: `data/full/data_full_low.csv`, `embeddings/embeddings_low.npy`.  
  - Outputs: fold models under `model/run_01/low/x_*/*.json`, feature metadata `model/run_01/low/feature_meta.json`, scored training data `model/run_01/data_low_scored.csv` (includes OOF preds and `cv_fold`).

- `src/high_ses_scorer.ipynb`  
  - Purpose: same training as above for high-SES essays.  
  - Inputs: `data/full/data_full_high.csv`, `embeddings/embeddings_high.npy`.  
  - Outputs: fold models under `model/run_01/high/x_*/*.json`, feature metadata `model/run_01/high/feature_meta.json`, scored training data `model/run_01/data_high_scored.csv`.

- `src/prompt.ipynb`  
  - Purpose: generate six rewrites per essay at different style levels using Azure OpenAI; optionally evaluate content preservation.  
  - Inputs: cleaned essays `data/persuade/persuade_full_cleaned.csv`; system/user prompts in `prompts/sat/`; evaluation prompt `prompts/evaluation/evaluation_function.txt`; Azure OpenAI credentials via environment (`API_KEY`, `API_VERSION`, `AZURE_ENDPOINT`).  
  - Outputs: raw rewrites `data/rewrites/sat_full/raw_rew_sat_{1..6}.csv`; cleaned rewrites with short/invalid rows removed `data/rewrites/sat_full/rew_sat_{1..6}.csv`.

- `src/data_preproc.ipynb` (rewrites mode)  
  - Purpose: apply the same style metrics and embeddings to GPT rewrites, attach `cv_fold` from the training data for consistent scoring splits.  
  - Inputs: cleaned rewrites from `prompt.ipynb`; scored training files `model/run_01/data_high_scored.csv` and `data_low_scored.csv`.  
  - Outputs: processed rewrites `data/processed/sat_full/rewrite_{1..6}.csv`, aligned original reference `data/processed/sat_full/original.csv`, and embeddings `embeddings/sat_full/embeddings_rewrite_{1..6}.npy` + `embeddings_original.npy`.

- `src/scorer.ipynb`  
  - Purpose: load trained fold models, score originals and all rewrites for both SES-specific models across feature groups, and collect predictions.  
  - Inputs: processed rewrites + aligned original CSVs in `data/processed/sat_full/`; embeddings in `embeddings/sat_full/`; trained models and `feature_meta.json` from `model/run_01/high` and `model/run_01/low`.  
  - Outputs: scored dataset `data/results/sat_full/data_sat_scored.csv` (and cleaned variant `data_sat_scored_cleaned.csv`) with predictions for each feature group, SES model, and rewrite index `k`.

- `src/descriptive_statistics.ipynb` (optional)  
  - Purpose: compute group-level descriptive stats (SES, demographics, prompts) for the full dataset.  
  - Inputs: `data/full/data_full.csv`.  
  - Outputs: `descriptive_statistics_summary.csv`.

- `src/measuring_redundency.ipynb`  
  - Purpose: assess redundancy/unique information between style and embedding features via R² comparisons and PID; plot results.  
  - Inputs: `model/run_01/data_low_scored.csv`, `model/run_01/data_high_scored.csv`.  
  - Outputs: figures saved to `tables/sat_final/` (e.g., `redundency.png`, `pid_decomposition.png` and SES variants).

- `src/decomp_bootstraping.ipynb`  
  - Purpose: fixed-effects regression to decompose SES score gaps into content/style/other; cluster bootstrap for CIs; produce summary tables.  
  - Inputs: `data/results/sat_full/data_sat_scored.csv`.  
  - Outputs: augmented FE rows `data/results/sat_full/decomp_rows_with_fe.csv`; bootstrap tables in `tables/sat_final/tables/` (`decomposition_bootstrap_summary_*.csv` and `.tex`).

- `src/images.ipynb`  
  - Purpose: generate all publication figures (distributions, scatterplots, t-SNE, rewrite comparisons, FE/variance charts).  
  - Inputs: `data/persuade/persuade_full_cleaned.csv`; embeddings `embeddings/embeddings_full.npy`, `embeddings_low.npy`, `embeddings_high.npy`; scored training data `model/run_01/data_low_scored.csv`, `data_high_scored.csv`; scored rewrites `data/results/sat_full/data_sat_scored.csv`; decomposition rows `data/results/sat_full/decomp_rows_with_fe.csv`.  
  - Outputs: numerous PNGs and LaTeX tables under `tables/sat_final/` and `tables/sat_final/tables/` (e.g., `real_scores.png`, `explained_variability.png`, `decomp_shares_tables.csv`/`.tex`, rewrite distribution plots, FE/style distributions).
