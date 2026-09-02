"""
HR Analytics — Pipeline Analítico/Preditivo de ponta a ponta
================================================================
Dataset: anshika2301/hr-analytics-dataset (14.999 registros, alvo `left`)

Estrutura:
  1. Carga e sanity checks
  2. Testes estatísticos das 5 hipóteses investigativas
  3. Engenharia de atributos
  4. Modelagem (baseline Logistic Regression vs Gradient Boosting/XGBoost)
  5. Threshold tuning por custo/benefício
  6. Explicabilidade SHAP (global + local)
  7. Exportação da tabela fato + dimensões para Power BI (Star Schema)

Autor: Pipeline gerado por Claude — Principal Analytics Engineer / People Analytics Lead
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 0. CONFIG
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "HR_comma_sep.csv"
OUTPUT_DIR = ROOT / "output"
DOCS_DIR = ROOT / "docs"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
DOCS_DIR.mkdir(exist_ok=True, parents=True)

RANDOM_STATE = 42
ALPHA = 0.05  # nível de significância

# Custo assumido de um Falso Negativo (perder um colaborador de risco sem agir)
# vs. Falso Positivo (investir retenção em quem não sairia).
# Premissa de negócio, documentada e ajustável no Power BI.
COST_FN = 4.0   # ex.: custo de reposição ~ 4x uma ação de retenção
COST_FP = 1.0   # custo de uma ação de retenção "desperdiçada"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns={"sales": "department"})
    # id estável do "colaborador" (o dataset não traz PK nativa)
    df.insert(0, "employee_id", range(1, len(df) + 1))
    assert df.shape[0] == 14999, f"Esperado 14999 linhas, obtido {df.shape[0]}"
    assert df["left"].isin([0, 1]).all()
    return df


if __name__ == "__main__":
    df = load_data()
    print(df.shape)
    print(df.dtypes)
    print(df.isna().sum())
    print(df["department"].value_counts())
    print(df["salary"].value_counts())
