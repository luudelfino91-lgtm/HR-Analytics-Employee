"""
ETAPA 2 (parte 2): Engenharia de Atributos
Cria features derivadas justificadas pelas hipóteses testadas em hypotheses.py,
incluindo H6 (taxonomia de desligados via KMeans) e H7 (formato em U de projetos)
identificadas em benchmark contra análises públicas independentes desta base.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from hr_pipeline import load_data, RANDOM_STATE


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- H1: intensidade de carga (burnout vs subutilização) ---
    df["workload_intensity_idx"] = (
        (df.average_montly_hours / df.average_montly_hours.max())
        + (df.number_project / df.number_project.max())
    ) / 2
    df["is_overworked"] = (
        (df.average_montly_hours >= 250) & (df.number_project >= 6)
    ).astype(int)
    df["is_underutilized"] = (
        (df.average_montly_hours < 150) & (df.number_project <= 2)
    ).astype(int)
    df["hours_per_project"] = df.average_montly_hours / df.number_project.replace(0, np.nan)
    df["hours_per_project"] = df["hours_per_project"].fillna(df["hours_per_project"].median())

    # --- H2: descompasso avaliação x satisfação ---
    df["eval_satisfaction_gap"] = df.last_evaluation - df.satisfaction_level
    df["is_unhappy_star"] = (
        (df.last_evaluation >= 0.75) & (df.satisfaction_level <= 0.25)
    ).astype(int)
    df["is_comfortable_underperformer"] = (
        (df.last_evaluation <= 0.45) & (df.satisfaction_level >= 0.70)
    ).astype(int)

    # --- H3: janela crítica de carreira / estagnação ---
    df["is_critical_tenure_window"] = df.time_spend_company.between(4, 6).astype(int)
    df["stagnation_flag"] = (
        (df.promotion_last_5years == 0) & (df.time_spend_company >= 4)
    ).astype(int)
    df["tenure_bucket"] = pd.cut(
        df.time_spend_company,
        bins=[0, 2, 3, 6, 10],
        labels=["0-2 yrs (new)", "3 yrs (transition)", "4-6 yrs (critical)", "7+ yrs (veteran)"],
    )

    # --- H5: barreira de saída / risco combinado ---
    df["risk_score_raw"] = (
        (1 - df.satisfaction_level) * 0.4
        + df.workload_intensity_idx.clip(0, 1) * 0.3
        + df.is_critical_tenure_window * 0.15
        + df.stagnation_flag * 0.15
    )
    salary_rank = {"low": 0, "medium": 1, "high": 2}
    df["salary_rank"] = df.salary.map(salary_rank)
    df["low_exit_barrier_flag"] = (
        (df.risk_score_raw >= df.risk_score_raw.quantile(0.75)) & (df.salary_rank == 0)
    ).astype(int)

    # --- interação satisfação x avaliação (não-linear, para capturar quadrantes) ---
    df["satisfaction_x_evaluation"] = df.satisfaction_level * df.last_evaluation

    # --- salário ordinal (para modelos que usam ordinalidade; manter categórica p/ Power BI) ---
    df["salary_ordinal"] = df.salary_rank

    # --- H7: formato em U/J de number_project — extremos (subutilização e sobrecarga
    # de projetos) concentram churn muito acima da faixa "ótima" (3-4 projetos) ---
    df["is_project_extreme"] = df.number_project.isin([2, 6, 7]).astype(int)
    df["is_hours_ceiling"] = (df.average_montly_hours >= 280).astype(int)  # churn ~78-100% acima desse teto

    # --- H6: arquétipo de desligamento (taxonomia de 3 clusters treinada SOMENTE em
    # quem saiu, via KMeans em satisfaction_level x last_evaluation, validada por
    # silhouette score em hypotheses.py). Aplicada a TODOS os colaboradores (ativos
    # inclusive) para indicar a qual arquétipo de risco cada um mais se assemelha,
    # caso viesse a sair — é a feature de maior valor de negócio para segmentar ações
    # de retenção diferenciadas (ver docs/05_benchmark_externo.md). ---
    leavers = df[df.left == 1]
    scaler = StandardScaler().fit(leavers[["satisfaction_level", "last_evaluation"]])
    km = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=10).fit(
        scaler.transform(leavers[["satisfaction_level", "last_evaluation"]])
    )
    # rotula cada centróide pela combinação satisfação/avaliação (mesma regra de hypotheses.py)
    centroids_original_scale = scaler.inverse_transform(km.cluster_centers_)
    archetype_labels = {}
    for i, (sat, ev) in enumerate(centroids_original_scale):
        if sat >= 0.7 and ev >= 0.8:
            archetype_labels[i] = "Market-Poached Talent"
        elif sat <= 0.3 and ev >= 0.7:
            archetype_labels[i] = "Extreme Burnout"
        else:
            archetype_labels[i] = "Low Engagement / Poor Fit"

    all_scaled = scaler.transform(df[["satisfaction_level", "last_evaluation"]])
    df["exit_archetype_cluster"] = km.predict(all_scaled)
    df["exit_archetype"] = df["exit_archetype_cluster"].map(archetype_labels)

    return df


if __name__ == "__main__":
    df = load_data()
    df_fe = engineer_features(df)
    print(df_fe.shape)
    print(df_fe.columns.tolist())
    print(df_fe[["is_overworked", "is_underutilized", "is_unhappy_star",
                  "is_comfortable_underperformer", "stagnation_flag",
                  "low_exit_barrier_flag", "is_project_extreme", "is_hours_ceiling"]].sum())
    print(df_fe["exit_archetype"].value_counts())
    print(df_fe.groupby("exit_archetype")["left"].mean())
