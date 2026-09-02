"""
ETAPA 3c — Simulação de Base Salarial e Impacto Financeiro, LOCALIZADA POR MERCADO.

O dataset original só tem `salary` como categórico (low/medium/high), sem valor
monetário. Este script cria uma BASE FICTÍCIA de salário, ancorada em benchmarks
externos verificáveis, e a aplica aos dois modelos — cada um na moeda e nos
parâmetros do seu mercado:

  powerbi_en/  ->  EUR, benchmarks do mercado irlandês (12 salários/ano)
  powerbi_pt/  ->  BRL, benchmarks do mercado brasileiro (13,33 salários/ano: 13º + 1/3 férias)

A metodologia é idêntica nos dois; muda apenas a âncora salarial, a convenção
de pagamento anual e o piso legal.

ÂNCORAS EXTERNAS
1. Nível salarial por departamento
   - Irlanda: faixas de mercado 2026 para analistas e tecnologia (entry €35-45k,
     mid €50-65k, experiente €70k+, arquiteto sênior €140-160k+).
   - Brasil: ordenação de mercado corporativo, corroborada pelos próprios dados
     (o departamento `management` já tem 35,7% na faixa "high", contra 6-9% nos demais).
2. Custo de turnover como % do salário anual: benchmark SHRM/mercado de 50% a 213%.

TUDO aqui é SIMULADO. Colunas levam `simulated_`/`simulado` no nome. Ver
docs/08_simulacao_financeira.md. Determinístico (seed fixa) e idempotente.
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "powerbi_en"
PT_DIR = ROOT / "powerbi_pt"
SEED = 42

# ---------------------------------------------------------------------------
# Parâmetros por mercado
# ---------------------------------------------------------------------------
MARKETS = {
    "EUR": {
        # Salário ANUAL base (faixa "medium"), mercado irlandês 2026.
        "dept_base_annual": {
            "management": 95000, "IT": 72000, "RandD": 66000, "product_mng": 64000,
            "technical": 58000, "marketing": 52000, "accounting": 49000,
            "sales": 46000, "hr": 44000, "support": 36000,
        },
        # Irlanda não tem 13º salário nem 1/3 de férias: ano = 12 meses.
        "months_per_year": 12.0,
        # Piso: salário mínimo nacional 2026 (€14,15/h) em tempo integral (39h × 52 sem).
        "annual_floor": 28700,
        "symbol": "€",
    },
    "BRL": {
        # Salário MENSAL base (faixa "medium") × 13,33 pagamentos/ano = anual base.
        # (No Brasil o salário contratado é mensal e são pagos 12 meses + 13º + 1/3 de férias.)
        "dept_base_annual": {
            "management": 14000 * 13.33, "IT": 9500 * 13.33, "RandD": 8800 * 13.33,
            "product_mng": 8500 * 13.33, "technical": 8000 * 13.33, "marketing": 7200 * 13.33,
            "accounting": 6800 * 13.33, "sales": 6200 * 13.33, "hr": 5800 * 13.33,
            "support": 4600 * 13.33,
        },
        # CLT: 13º salário + 1/3 de férias.
        "months_per_year": 13.33,
        "annual_floor": 1900 * 13.33,
        "symbol": "R$",
    },
}

BAND_MULTIPLIER = {"low": 0.68, "medium": 1.00, "high": 1.60}

# Custo de reposição como % do salário anual — benchmark de mercado (50%-213%)
REPLACEMENT_COST_PCT_BY_BAND = {"low": 0.55, "medium": 0.95, "high": 1.60}
HIGH_PERFORMER_SURCHARGE_PCT = 0.20   # perder alta performance custa mais
REPLACEMENT_COST_PCT_CAP = 2.00       # teto no limite do benchmark SHRM
RETENTION_ACTION_COST_PCT = 0.12      # reajuste/bônus/plano de carreira típico


def simulate(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    cfg = MARKETS[currency]
    rng = np.random.default_rng(SEED)  # mesma semente -> estrutura comparável entre moedas
    df = df.copy()

    base_annual = df["department"].map(cfg["dept_base_annual"])
    band_mult = df["salary"].map(BAND_MULTIPLIER)
    # bônus de senioridade: +1,8% ao ano de casa, satura em 6 anos
    tenure_bonus = 1 + np.minimum(df["time_spend_company"], 6) * 0.018
    # ruído idiossincrático (±20%), evita "degraus" artificiais dentro da mesma faixa
    jitter = rng.normal(loc=1.0, scale=0.06, size=len(df)).clip(0.8, 1.2)

    annual = (base_annual * band_mult * tenure_bonus * jitter).clip(lower=cfg["annual_floor"]).round(2)
    monthly = (annual / cfg["months_per_year"]).round(2)

    repl_pct = df["salary"].map(REPLACEMENT_COST_PCT_BY_BAND)
    repl_pct = repl_pct + np.where(df["last_evaluation"] >= 0.70, HIGH_PERFORMER_SURCHARGE_PCT, 0.0)
    repl_pct = repl_pct.clip(upper=REPLACEMENT_COST_PCT_CAP)

    cur = currency.lower()
    return pd.DataFrame({
        "employee_id": df["employee_id"].values,
        f"simulated_monthly_salary_{cur}": monthly.values,
        f"simulated_annual_salary_{cur}": annual.values,
        "simulated_replacement_cost_pct": repl_pct.round(3).values,
        f"simulated_replacement_cost_{cur}": (annual * repl_pct).round(2).values,
        f"simulated_retention_action_cost_{cur}": (annual * RETENTION_ACTION_COST_PCT).round(2).values,
    })


PT_RENAME = {
    "employee_id": "id_colaborador",
    "simulated_monthly_salary_brl": "salario_mensal_simulado_brl",
    "simulated_annual_salary_brl": "salario_anual_simulado_brl",
    "simulated_replacement_cost_pct": "percentual_custo_reposicao_simulado",
    "simulated_replacement_cost_brl": "custo_reposicao_simulado_brl",
    "simulated_retention_action_cost_brl": "custo_acao_retencao_simulado_brl",
}


def attach(fact_path: Path, sim: pd.DataFrame, id_col: str):
    """Anexa as colunas simuladas à tabela fato de forma idempotente.

    Remove QUALQUER coluna de simulação salarial pré-existente — inclusive de
    outra moeda — antes de anexar. Sem isso, trocar a moeda de um modelo deixaria
    as colunas antigas para trás e a tabela ficaria com duas moedas ao mesmo tempo.
    """
    fact = pd.read_csv(fact_path)
    stale = [c for c in fact.columns
             if c.startswith(("simulated_monthly_salary", "simulated_annual_salary",
                              "simulated_replacement_cost", "simulated_retention_action_cost",
                              "salario_mensal_simulado", "salario_anual_simulado",
                              "percentual_custo_reposicao_simulado",
                              "custo_reposicao_simulado", "custo_acao_retencao_simulado"))]
    new_cols = [c for c in sim.columns if c != id_col]
    fact = fact.drop(columns=list(set(stale) | set(new_cols)), errors="ignore")
    fact = fact.merge(sim, on=id_col, how="left")
    assert fact[new_cols].notna().all().all(), f"merge deixou nulos em {fact_path.name}"
    assert len(fact) == 14999, f"{fact_path.name} mudou de tamanho"
    fact.to_csv(fact_path, index=False)
    return fact


def sanity_report(raw, sim, currency):
    cfg = MARKETS[currency]; cur = currency.lower(); sym = cfg["symbol"]
    m = raw.merge(sim, on="employee_id")
    print(f"\n--- {currency} · salário ANUAL simulado por departamento (faixa medium) ---")
    med = m[m.salary == "medium"].groupby("department")[f"simulated_annual_salary_{cur}"].mean().sort_values(ascending=False)
    for k, v in med.items():
        print(f"    {k:14s} {sym}{v:>12,.0f}")
    s = m[f"simulated_annual_salary_{cur}"]
    print(f"    faixa geral: min {sym}{s.min():,.0f} | mediana {sym}{s.median():,.0f} | max {sym}{s.max():,.0f}")
    left = m[m["left"] == 1]
    tot = left[f"simulated_replacement_cost_{cur}"].sum()
    print(f"    custo das {len(left)} saídas reais: {sym}{tot:,.0f} (média {sym}{left[f'simulated_replacement_cost_{cur}'].mean():,.0f})")


if __name__ == "__main__":
    from hr_pipeline import load_data
    raw = load_data()

    sim_eur = simulate(raw, "EUR")
    sanity_report(raw, sim_eur, "EUR")
    attach(EN_DIR / "fEmployeeTurnover.csv", sim_eur, "employee_id")
    print(f"\n  powerbi_en/fEmployeeTurnover.csv  <- {[c for c in sim_eur.columns if c!='employee_id']}")

    sim_brl = simulate(raw, "BRL")
    sanity_report(raw, sim_brl, "BRL")
    sim_brl_pt = sim_brl.rename(columns=PT_RENAME)
    attach(PT_DIR / "fRotatividadeColaboradores.csv", sim_brl_pt, "id_colaborador")
    print(f"\n  powerbi_pt/fRotatividadeColaboradores.csv  <- {[c for c in sim_brl_pt.columns if c!='id_colaborador']}")
