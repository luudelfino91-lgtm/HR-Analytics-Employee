"""Orquestrador do pipeline completo, na ordem correta de dependências:

  1. Testes estatísticos das 7 hipóteses
  2. Modelagem + SHAP out-of-fold + exportação do Star Schema em INGLÊS
  3. Tradução do modelo para PORTUGUÊS
  4. Simulação da base salarial (BRL) e do custo de turnover, aplicada aos 2 modelos

Rodar `python run_all.py` reproduz o projeto inteiro do zero, de forma
determinística (todas as sementes fixas).
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def step(title, fn):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    fn()


def main():
    from hypotheses import run_all as run_hypotheses
    from export_powerbi import build_fact_table

    step("ETAPA 1 — Testes estatísticos das 7 hipóteses", run_hypotheses)
    step("ETAPA 2-3 — Modelagem, SHAP out-of-fold e Star Schema (EN)", build_fact_table)

    def _pt():
        subprocess.run([sys.executable, str(HERE / "export_powerbi_pt.py")], check=True, cwd=HERE)
    step("ETAPA 3b — Tradução do modelo para português", _pt)

    def _fin():
        subprocess.run([sys.executable, str(HERE / "simulate_salary_base.py")], check=True, cwd=HERE)
    step("ETAPA 3c — Simulação salarial (BRL) e impacto financeiro", _fin)

    print("\nPipeline concluído. Verifique output/, powerbi_en/ e powerbi_pt/.")


if __name__ == "__main__":
    main()
