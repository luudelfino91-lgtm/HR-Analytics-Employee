"""
ETAPA 3: Engenharia de dados para Power BI — exporta a Tabela Fato enriquecida
e as tabelas de Dimensão que compõem o Star Schema.
"""
import numpy as np
import pandas as pd

from hr_pipeline import load_data, OUTPUT_DIR

# Destino do modelo dimensional em inglês (o Power BI lê daqui, não de output/).
PBI_EN_DIR = OUTPUT_DIR.parent / "powerbi_en"
PBI_EN_DIR.mkdir(exist_ok=True, parents=True)
from features import engineer_features
from modeling import train_and_evaluate, run_shap


def risk_quadrant(row):
    """Quadrante de risco cruzando churn_probability (preditivo) x last_evaluation (valor do talento)."""
    high_risk = row["churn_probability"] >= 0.5
    high_value = row["last_evaluation"] >= 0.70
    if high_risk and high_value:
        return "Q1 - Critical Risk / High Performer"
    elif high_risk and not high_value:
        return "Q2 - High Risk / Standard Performer"
    elif not high_risk and high_value:
        return "Q3 - Stable / High Performer"
    else:
        return "Q4 - Stable / Standard Performer"


def cluster_by_workload(row):
    """Cluster comportamental simplificado, alinhado ao achado H1 (bimodalidade)."""
    if row["is_overworked"] == 1:
        return "Overworked (Burnout)"
    elif row["is_underutilized"] == 1:
        return "Underutilised (Idle)"
    elif row["is_unhappy_star"] == 1:
        return "Unhappy Star"
    elif row["is_comfortable_underperformer"] == 1:
        return "Comfortable / Low Performer"
    else:
        return "Standard / Balanced"


def build_fact_table():
    result = train_and_evaluate()
    shap_result = run_shap(result)

    df_fe = result["df_fe"]
    shap_export = shap_result["shap_export"]

    fact = df_fe.merge(shap_export, on="employee_id", how="left")

    fact["risk_quadrant"] = fact.apply(risk_quadrant, axis=1)
    fact["behavior_cluster"] = fact.apply(cluster_by_workload, axis=1)
    fact["risk_band"] = pd.cut(
        fact["churn_probability"],
        bins=[-0.01, 0.25, 0.5, 0.75, 1.0],
        labels=["Low (0-25%)", "Moderate (25-50%)", "High (50-75%)", "Critical (75-100%)"],
    )
    fact["is_flight_risk"] = (fact["churn_probability"] >= 0.5).astype(int)
    fact["is_high_performer"] = (fact["last_evaluation"] >= 0.70).astype(int)

    # chaves de dimensão (surrogate keys simples e determinísticas)
    fact["department_key"] = fact["department"].astype("category").cat.codes + 1
    fact["salary_key"] = fact["salary"].map({"low": 1, "medium": 2, "high": 3})
    fact["tenure_bucket_key"] = fact["tenure_bucket"].astype("category").cat.codes + 1
    fact["performance_cluster_key"] = fact["behavior_cluster"].astype("category").cat.codes + 1
    fact["exit_archetype_key"] = fact["exit_archetype"].astype("category").cat.codes + 1

    fact_cols = [
        "employee_id", "department_key", "salary_key", "tenure_bucket_key", "performance_cluster_key",
        "exit_archetype_key",
        "satisfaction_level", "last_evaluation", "number_project", "average_montly_hours",
        "time_spend_company", "Work_accident", "left", "promotion_last_5years",
        "workload_intensity_idx", "is_overworked", "is_underutilized", "hours_per_project",
        "eval_satisfaction_gap", "is_unhappy_star", "is_comfortable_underperformer",
        "is_critical_tenure_window", "stagnation_flag", "risk_score_raw", "low_exit_barrier_flag",
        "satisfaction_x_evaluation", "is_project_extreme", "is_hours_ceiling",
        "churn_probability", "risk_band", "is_flight_risk", "is_high_performer",
        "risk_quadrant", "behavior_cluster",
        "shap_main_driver_feature", "shap_main_driver_value", "shap_driver_direction",
    ]
    fact_table = fact[fact_cols].copy()
    fact_table.to_csv(PBI_EN_DIR / "fEmployeeTurnover.csv", index=False)

    # ------------------------------------------------------------------
    # Dimensões
    # ------------------------------------------------------------------
    d_department = (
        fact[["department_key", "department"]]
        .drop_duplicates()
        .sort_values("department_key")
        .rename(columns={"department": "department_name"})
    )
    d_department.to_csv(PBI_EN_DIR / "dDepartment.csv", index=False)

    d_salary = pd.DataFrame({
        "salary_key": [1, 2, 3],
        "salary_range": ["Low", "Medium", "High"],
        "salary_rank": [0, 1, 2],
    })
    d_salary.to_csv(PBI_EN_DIR / "dSalaryRange.csv", index=False)

    d_tenure = (
        fact[["tenure_bucket_key", "tenure_bucket"]]
        .drop_duplicates()
        .sort_values("tenure_bucket_key")
        .rename(columns={"tenure_bucket": "tenure_bucket_label"})
    )
    d_tenure.to_csv(PBI_EN_DIR / "dTenureBucket.csv", index=False)

    d_performance_cluster = (
        fact[["performance_cluster_key", "behavior_cluster"]]
        .drop_duplicates()
        .sort_values("performance_cluster_key")
        .rename(columns={"behavior_cluster": "cluster_name"})
    )
    d_performance_cluster.to_csv(PBI_EN_DIR / "dPerformanceCluster.csv", index=False)

    d_exit_archetype = (
        fact[["exit_archetype_key", "exit_archetype"]]
        .drop_duplicates()
        .sort_values("exit_archetype_key")
        .rename(columns={"exit_archetype": "archetype_name"})
    )
    d_exit_archetype.to_csv(PBI_EN_DIR / "dExitArchetype.csv", index=False)

    # Dimensão calendário fictícia não se aplica (dataset é transversal/snapshot, sem datas) —
    # documentado explicitamente na doc de star schema.

    print("Tabela fato:", fact_table.shape)
    print("dDepartment:", d_department.shape)
    print("dSalaryRange:", d_salary.shape)
    print("dTenureBucket:", d_tenure.shape)
    print("dPerformanceCluster:", d_performance_cluster.shape)
    print("dExitArchetype:", d_exit_archetype.shape)
    print("\nDistribuição risk_quadrant:")
    print(fact_table["risk_quadrant"].value_counts())
    print("\nDistribuição behavior_cluster:")
    print(fact_table["behavior_cluster"].value_counts())
    print("\nDistribuição exit_archetype (H6, aplicada a toda a base):")
    print(fact["exit_archetype"].value_counts())

    return fact_table, d_department, d_salary, d_tenure, d_performance_cluster, d_exit_archetype


if __name__ == "__main__":
    build_fact_table()
