"""
ETAPA 3b — Versão em Português (PT-BR) do modelo Star Schema para Power BI.

Lê os exports em inglês já validados (powerbi_en/) e produz um segundo modelo
completo, com nomes de tabela/coluna e valores de categoria traduzidos para
português, seguindo o guia de nomenclatura em docs/06_modelagem_e_nomenclatura.md.
Termos técnicos consagrados (SHAP, KMeans, XGBoost, id, key/chave como sufixo)
são mantidos onde a tradução prejudicaria a leitura técnica.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "powerbi_en"
PT_DIR = ROOT / "powerbi_pt"
PT_DIR.mkdir(exist_ok=True, parents=True)

# ---------------------------------------------------------------------------
# Mapas de tradução de valores de categoria
# ---------------------------------------------------------------------------
DEPARTAMENTO_MAP = {
    "sales": "Vendas", "technical": "Técnico", "support": "Suporte", "IT": "TI",
    "product_mng": "Gestão de Produto", "marketing": "Marketing", "RandD": "P&D",
    "accounting": "Contabilidade", "hr": "RH", "management": "Diretoria",
}
SALARIO_MAP = {"low": "Baixa", "medium": "Média", "high": "Alta", "Low": "Baixa", "Medium": "Média", "High": "Alta"}
TEMPO_CASA_MAP = {
    "0-2 yrs (new)": "0-2 anos (novo)",
    "3 yrs (transition)": "3 anos (transição)",
    "4-6 yrs (critical)": "4-6 anos (crítico)",
    "7+ yrs (veteran)": "7+ anos (veterano)",
}
CLUSTER_COMPORTAMENTAL_MAP = {
    "Overworked (Burnout)": "Sobrecarregado (Burnout)",
    "Underutilised (Idle)": "Subutilizado (Ocioso)",
    "Unhappy Star": "Estrela Insatisfeita",
    "Comfortable / Low Performer": "Confortável / Baixo Desempenho",
    "Standard / Balanced": "Padrão / Equilibrado",
}
ARQUETIPO_MAP = {
    "Market-Poached Talent": "Talento Disputado pelo Mercado",
    "Extreme Burnout": "Burnout Extremo",
    "Low Engagement / Poor Fit": "Baixo Engajamento / Mau Encaixe",
}
RISK_BAND_MAP = {
    "Low (0-25%)": "Baixo (0-25%)", "Moderate (25-50%)": "Moderado (25-50%)",
    "High (50-75%)": "Alto (50-75%)", "Critical (75-100%)": "Crítico (75-100%)",
}
RISK_QUADRANT_MAP = {
    "Q1 - Critical Risk / High Performer": "Q1 - Risco Crítico / Alto Desempenho",
    "Q2 - High Risk / Standard Performer": "Q2 - Risco Alto / Desempenho Regular",
    "Q3 - Stable / High Performer": "Q3 - Estável / Alto Desempenho",
    "Q4 - Stable / Standard Performer": "Q4 - Estável / Desempenho Regular",
}
SHAP_DRIVER_MAP = {
    "Increases exit risk": "Aumenta risco de saída", "Reduces exit risk": "Reduz risco de saída",
}
# Nome técnico da feature (pós one-hot, saída do pipeline) -> rótulo em português para leitura executiva
SHAP_FEATURE_MAP = {
    "satisfaction_level": "Nível de satisfação", "is_project_extreme": "Projetos em zona extrema (H7)",
    "risk_score_raw": "Score de risco composto", "time_spend_company": "Tempo de casa (anos)",
    "satisfaction_x_evaluation": "Interação satisfação × avaliação", "average_montly_hours": "Horas mensais médias",
    "last_evaluation": "Última avaliação", "workload_intensity_idx": "Índice de intensidade de carga",
    "hours_per_project": "Horas por projeto", "eval_satisfaction_gap": "Gap avaliação-satisfação",
    "salary_rank": "Faixa salarial (ordinal)", "Work_accident": "Acidente de trabalho",
    "number_project": "Número de projetos", "is_critical_tenure_window": "Janela crítica de tenure",
    "low_exit_barrier_flag": "Baixa barreira de saída", "is_overworked": "Sobrecarregado",
    "is_underutilized": "Subutilizado", "is_unhappy_star": "Estrela insatisfeita",
    "is_comfortable_underperformer": "Confortável / baixo desempenho", "is_hours_ceiling": "Teto de horas críticas",
    "stagnation_flag": "Estagnação sem promoção", "promotion_last_5years": "Promoção nos últimos 5 anos",
}


def translate_feature_col(series):
    def tr(v):
        if pd.isna(v):
            return v
        base = SHAP_FEATURE_MAP.get(v)
        if base:
            return base
        # colunas one-hot de departamento/salário/tenure/arquétipo (prefixo do ColumnTransformer)
        for prefix, mapping, pretty in [
            ("department_", DEPARTAMENTO_MAP, "Depto"), ("salary_", SALARIO_MAP, "Salário"),
            ("tenure_bucket_", {}, "Tenure"), ("exit_archetype_", ARQUETIPO_MAP, "Arquétipo"),
        ]:
            if v.startswith(prefix):
                raw = v[len(prefix):]
                mapped = mapping.get(raw, raw)
                return f"{pretty}: {mapped}"
        return v
    return series.apply(tr)


def build_pt_model():
    fact_en = pd.read_csv(EN_DIR / "fEmployeeTurnover.csv")
    d_dept_en = pd.read_csv(EN_DIR / "dDepartment.csv")
    d_sal_en = pd.read_csv(EN_DIR / "dSalaryRange.csv")
    d_ten_en = pd.read_csv(EN_DIR / "dTenureBucket.csv")
    d_perf_en = pd.read_csv(EN_DIR / "dPerformanceCluster.csv")
    d_arch_en = pd.read_csv(EN_DIR / "dExitArchetype.csv")

    # -------------------- Dimensões --------------------
    d_departamento = d_dept_en.rename(columns={"department_key": "chave_departamento", "department_name": "nome_departamento"})
    d_departamento["nome_departamento"] = d_departamento["nome_departamento"].map(DEPARTAMENTO_MAP).fillna(d_departamento["nome_departamento"])
    d_departamento.to_csv(PT_DIR / "dDepartamento.csv", index=False)

    d_faixa_salarial = d_sal_en.rename(columns={"salary_key": "chave_faixa_salarial", "salary_range": "faixa_salarial", "salary_rank": "ordem_faixa_salarial"})
    d_faixa_salarial["faixa_salarial"] = d_faixa_salarial["faixa_salarial"].map(SALARIO_MAP).fillna(d_faixa_salarial["faixa_salarial"])
    d_faixa_salarial.to_csv(PT_DIR / "dFaixaSalarial.csv", index=False)

    d_tempo_casa = d_ten_en.rename(columns={"tenure_bucket_key": "chave_tempo_casa", "tenure_bucket_label": "faixa_tempo_casa"})
    d_tempo_casa["faixa_tempo_casa"] = d_tempo_casa["faixa_tempo_casa"].map(TEMPO_CASA_MAP).fillna(d_tempo_casa["faixa_tempo_casa"])
    d_tempo_casa.to_csv(PT_DIR / "dTempoDeCasa.csv", index=False)

    d_cluster_comportamental = d_perf_en.rename(columns={"performance_cluster_key": "chave_cluster_comportamental", "cluster_name": "nome_cluster"})
    d_cluster_comportamental["nome_cluster"] = d_cluster_comportamental["nome_cluster"].map(CLUSTER_COMPORTAMENTAL_MAP).fillna(d_cluster_comportamental["nome_cluster"])
    d_cluster_comportamental.to_csv(PT_DIR / "dClusterComportamental.csv", index=False)

    d_arquetipo_saida = d_arch_en.rename(columns={"exit_archetype_key": "chave_arquetipo_saida", "archetype_name": "nome_arquetipo"})
    d_arquetipo_saida["nome_arquetipo"] = d_arquetipo_saida["nome_arquetipo"].map(ARQUETIPO_MAP).fillna(d_arquetipo_saida["nome_arquetipo"])
    d_arquetipo_saida.to_csv(PT_DIR / "dArquetipoSaida.csv", index=False)

    # -------------------- Tabela Fato --------------------
    col_map = {
        "employee_id": "id_colaborador",
        "department_key": "chave_departamento",
        "salary_key": "chave_faixa_salarial",
        "tenure_bucket_key": "chave_tempo_casa",
        "performance_cluster_key": "chave_cluster_comportamental",
        "exit_archetype_key": "chave_arquetipo_saida",
        "satisfaction_level": "nivel_satisfacao",
        "last_evaluation": "ultima_avaliacao",
        "number_project": "numero_projetos",
        "average_montly_hours": "horas_mensais_medias",
        "time_spend_company": "tempo_de_casa_anos",
        "Work_accident": "sofreu_acidente_trabalho",
        "left": "saiu_da_empresa",
        "promotion_last_5years": "promovido_ultimos_5_anos",
        "workload_intensity_idx": "indice_intensidade_carga",
        "is_overworked": "flag_sobrecarregado",
        "is_underutilized": "flag_subutilizado",
        "hours_per_project": "horas_por_projeto",
        "eval_satisfaction_gap": "gap_avaliacao_satisfacao",
        "is_unhappy_star": "flag_estrela_insatisfeita",
        "is_comfortable_underperformer": "flag_confortavel_baixo_desempenho",
        "is_critical_tenure_window": "flag_janela_critica_carreira",
        "stagnation_flag": "flag_estagnacao_sem_promocao",
        "risk_score_raw": "score_risco_bruto",
        "low_exit_barrier_flag": "flag_baixa_barreira_saida",
        "satisfaction_x_evaluation": "interacao_satisfacao_avaliacao",
        "is_project_extreme": "flag_projeto_extremo",
        "is_hours_ceiling": "flag_teto_horas_criticas",
        "churn_probability": "probabilidade_saida",
        "risk_band": "faixa_de_risco",
        "is_flight_risk": "flag_risco_iminente",
        "is_high_performer": "flag_alto_desempenho",
        "risk_quadrant": "quadrante_risco",
        "behavior_cluster": "cluster_comportamental",
        "shap_main_driver_feature": "fator_principal_shap",
        "shap_main_driver_value": "valor_shap_fator_principal",
        "shap_driver_direction": "direcao_fator_shap",
    }
    fact_pt = fact_en.rename(columns=col_map)

    fact_pt["faixa_de_risco"] = fact_pt["faixa_de_risco"].map(RISK_BAND_MAP).fillna(fact_pt["faixa_de_risco"])
    fact_pt["quadrante_risco"] = fact_pt["quadrante_risco"].map(RISK_QUADRANT_MAP).fillna(fact_pt["quadrante_risco"])
    fact_pt["cluster_comportamental"] = fact_pt["cluster_comportamental"].map(CLUSTER_COMPORTAMENTAL_MAP).fillna(fact_pt["cluster_comportamental"])
    fact_pt["direcao_fator_shap"] = fact_pt["direcao_fator_shap"].map(SHAP_DRIVER_MAP).fillna(fact_pt["direcao_fator_shap"])
    fact_pt["fator_principal_shap"] = translate_feature_col(fact_pt["fator_principal_shap"])

    fact_pt.to_csv(PT_DIR / "fRotatividadeColaboradores.csv", index=False)

    print("fRotatividadeColaboradores:", fact_pt.shape)
    print("dDepartamento:", d_departamento.shape)
    print("dFaixaSalarial:", d_faixa_salarial.shape)
    print("dTempoDeCasa:", d_tempo_casa.shape)
    print("dClusterComportamental:", d_cluster_comportamental.shape)
    print("dArquetipoSaida:", d_arquetipo_saida.shape)
    print("\nAmostra de fator_principal_shap traduzido:")
    print(fact_pt["fator_principal_shap"].value_counts().head(10))

    return fact_pt


if __name__ == "__main__":
    build_pt_model()
