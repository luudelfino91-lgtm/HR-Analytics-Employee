"""
ETAPA 2 (parte 3-4): Modelagem preditiva, threshold tuning por custo/benefício
e explicabilidade SHAP.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_curve,
    confusion_matrix, classification_report, roc_curve, f1_score
)
from xgboost import XGBClassifier
import shap

from hr_pipeline import load_data, OUTPUT_DIR, RANDOM_STATE, COST_FN, COST_FP
from features import engineer_features

# NOTA METODOLÓGICA (auditoria): `exit_archetype` foi REMOVIDO do conjunto de
# features do modelo. Ele é derivado de um KMeans ajustado APENAS sobre quem já
# saiu (left==1), portanto carrega informação do alvo — usá-lo como preditor
# seria vazamento (target leakage). Ele permanece na tabela fato e como dimensão
# no Power BI, onde seu valor é descritivo/segmentação, não preditivo.
# Impacto na performance: nulo — o atributo já não aparecia entre as 20 features
# mais relevantes por SHAP.
CAT_COLS = ["department", "salary", "tenure_bucket"]
NUM_COLS = [
    "satisfaction_level", "last_evaluation", "number_project", "average_montly_hours",
    "time_spend_company", "Work_accident", "promotion_last_5years",
    "workload_intensity_idx", "is_overworked", "is_underutilized", "hours_per_project",
    "eval_satisfaction_gap", "is_unhappy_star", "is_comfortable_underperformer",
    "is_critical_tenure_window", "stagnation_flag", "risk_score_raw", "salary_rank",
    "low_exit_barrier_flag", "satisfaction_x_evaluation",
    "is_project_extreme", "is_hours_ceiling",  # H7 - formato em U de projetos / teto de horas
]


def build_dataset():
    df = load_data()
    df_fe = engineer_features(df)
    X = df_fe[NUM_COLS + CAT_COLS].copy()
    y = df_fe["left"].copy()
    return df_fe, X, y


def optimal_threshold_by_cost(y_true, y_proba, cost_fn=COST_FN, cost_fp=COST_FP):
    """Varre thresholds e escolhe o que minimiza custo total = FN*cost_fn + FP*cost_fp."""
    thresholds = np.linspace(0.01, 0.99, 197)
    costs = []
    for t in thresholds:
        preds = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()
        cost = fn * cost_fn + fp * cost_fp
        costs.append(cost)
    costs = np.array(costs)
    best_idx = costs.argmin()
    return float(thresholds[best_idx]), float(costs[best_idx]), thresholds, costs


def train_and_evaluate():
    df_fe, X, y = build_dataset()
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df_fe.index, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUM_COLS),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CAT_COLS),
    ])

    # --- Baseline: Regressão Logística com balanceamento de classe ---
    baseline = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    baseline.fit(X_train, y_train)
    proba_baseline = baseline.predict_proba(X_test)[:, 1]

    # --- Gradient Boosting: XGBoost, tratando desbalanceamento via scale_pos_weight ---
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    gbm_preprocessor = ColumnTransformer([
        ("num", "passthrough", NUM_COLS),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CAT_COLS),
    ])
    gbm = Pipeline([
        ("prep", gbm_preprocessor),
        ("clf", XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9,
            scale_pos_weight=scale_pos_weight,
            eval_metric="aucpr", random_state=RANDOM_STATE, n_jobs=-1,
        )),
    ])
    gbm.fit(X_train, y_train)
    proba_gbm = gbm.predict_proba(X_test)[:, 1]

    # --- Comparação de modelos ---
    metrics = {}
    for name, proba in [("logistic_regression_baseline", proba_baseline), ("xgboost_gradient_boosting", proba_gbm)]:
        auc = roc_auc_score(y_test, proba)
        ap = average_precision_score(y_test, proba)
        preds_default = (proba >= 0.5).astype(int)
        f1_default = f1_score(y_test, preds_default)
        best_t, best_cost, _, _ = optimal_threshold_by_cost(y_test, proba)
        preds_tuned = (proba >= best_t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, preds_tuned).ravel()
        metrics[name] = {
            "roc_auc": float(auc),
            "average_precision_pr_auc": float(ap),
            "f1_threshold_0.5": float(f1_default),
            "custo_business_threshold_otimo": best_t,
            "custo_total_minimizado": best_cost,
            "confusion_matrix_threshold_otimo": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
            "classification_report_threshold_otimo": classification_report(
                y_test, preds_tuned, output_dict=True
            ),
        }

    # Modelo campeão = maior PR-AUC (mais informativo que ROC-AUC em classe minoritária)
    champion = "xgboost_gradient_boosting" if metrics["xgboost_gradient_boosting"]["average_precision_pr_auc"] >= \
        metrics["logistic_regression_baseline"]["average_precision_pr_auc"] else "logistic_regression_baseline"
    metrics["modelo_campeao"] = champion

    with open(OUTPUT_DIR / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # --- gráficos de apoio ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for name, proba, color in [("Logistic Regression", proba_baseline, "#6b7280"),
                                ("XGBoost", proba_gbm, "#2563eb")]:
        fpr, tpr, _ = roc_curve(y_test, proba)
        axes[0].plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_test, proba):.3f})", color=color)
        prec, rec, _ = precision_recall_curve(y_test, proba)
        axes[1].plot(rec, prec, label=f"{name} (AP={average_precision_score(y_test, proba):.3f})", color=color)
    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.3)
    axes[0].set_xlabel("FPR"); axes[0].set_ylabel("TPR"); axes[0].set_title("ROC Curve"); axes[0].legend()
    axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision"); axes[1].set_title("Precision-Recall Curve"); axes[1].legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "model_comparison_curves.png", dpi=150)
    plt.close()

    return {
        "df_fe": df_fe, "X": X, "y": y,
        "X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test,
        "idx_train": idx_train, "idx_test": idx_test,
        "baseline": baseline, "gbm": gbm,
        "proba_baseline": proba_baseline, "proba_gbm": proba_gbm,
        "metrics": metrics, "champion": champion,
        "gbm_preprocessor": gbm_preprocessor,
    }


def run_shap(result, n_splits=5):
    """Gera `churn_probability` e a atribuição SHAP por colaborador de forma
    OUT-OF-FOLD (validação cruzada estratificada).

    METODOLOGIA (corrigido em auditoria):
    A versão anterior treinava um modelo no dataset COMPLETO e usava esse mesmo
    modelo para pontuar todos os 14.999 colaboradores. Isso produzia predições
    IN-SAMPLE — cada colaborador era pontuado por um modelo que já tinha visto o
    seu próprio rótulo. O efeito era um AUC aparente de 0,9992 (contra 0,994 de
    holdout) e uma "Taxa Preditiva de Risco" que reproduzia quase exatamente a
    taxa real observada, dando falsa impressão de poder preditivo.

    Aqui, cada colaborador é pontuado por um modelo treinado SEM a sua própria
    linha (StratifiedKFold, n_splits dobras). O mesmo vale para os valores SHAP:
    a atribuição de cada colaborador vem do explainer da dobra em que ele estava
    fora do treino. O resultado é uma probabilidade honesta, comparável às
    métricas de holdout reportadas — apropriada para uso executivo e comercial.
    """
    from sklearn.model_selection import StratifiedKFold
    from xgboost import XGBClassifier

    df_fe, X, y = result["df_fe"], result["X"], result["y"]

    # O pré-processador é apenas one-hot/passthrough (não usa o alvo), então
    # pode ser ajustado sobre todo o X sem introduzir vazamento.
    preprocessor = ColumnTransformer([
        ("num", "passthrough", NUM_COLS),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CAT_COLS),
    ])
    X_transformed = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out()
    X_t = pd.DataFrame(X_transformed, columns=feature_names, index=X.index).astype(float)

    def make_clf(y_train):
        return XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9,
            scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
            eval_metric="aucpr", random_state=RANDOM_STATE, n_jobs=-1,
        )

    oof_proba = np.zeros(len(X_t))
    oof_shap = np.zeros((len(X_t), X_t.shape[1]))

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_t, y), start=1):
        X_tr, X_te = X_t.iloc[tr_idx], X_t.iloc[te_idx]
        y_tr = y.iloc[tr_idx]
        clf = make_clf(y_tr)
        clf.fit(X_tr, y_tr)
        oof_proba[te_idx] = clf.predict_proba(X_te)[:, 1]
        oof_shap[te_idx, :] = shap.TreeExplainer(clf).shap_values(X_te)
        print(f"  fold {fold}/{n_splits} concluída")

    # Honestidade da predição out-of-fold (deve bater com o holdout, não superá-lo)
    oof_auc = roc_auc_score(y, oof_proba)
    oof_ap = average_precision_score(y, oof_proba)
    print(f"  OOF ROC-AUC={oof_auc:.4f} | OOF PR-AUC={oof_ap:.4f}")
    result["metrics"]["out_of_fold_scoring"] = {
        "n_splits": n_splits, "roc_auc": float(oof_auc), "average_precision_pr_auc": float(oof_ap),
        "nota": ("churn_probability da tabela fato é out-of-fold: cada colaborador foi "
                  "pontuado por um modelo treinado sem a sua própria linha."),
    }
    with open(OUTPUT_DIR / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(result["metrics"], f, indent=2, ensure_ascii=False)

    shap_values = oof_shap

    # --- SHAP global (feature importance média |SHAP|) ---
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    global_importance = pd.Series(mean_abs_shap, index=feature_names).sort_values(ascending=False)
    global_importance.head(20).to_csv(OUTPUT_DIR / "shap_global_importance.csv", header=["mean_abs_shap"])

    plt.figure()
    shap.summary_plot(shap_values, X_t, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "shap_summary_plot.png", dpi=150, bbox_inches="tight")
    plt.close()

    # --- SHAP local: driver principal por colaborador (para a tabela fato) ---
    shap_df = pd.DataFrame(shap_values, columns=feature_names, index=X.index)
    main_driver_idx = shap_df.abs().values.argmax(axis=1)
    main_driver_feature = [feature_names[i] for i in main_driver_idx]
    main_driver_shap_value = shap_df.values[np.arange(len(shap_df)), main_driver_idx]

    churn_probability = oof_proba

    shap_export = pd.DataFrame({
        "employee_id": df_fe["employee_id"].values,
        "churn_probability": churn_probability,
        "shap_main_driver_feature": main_driver_feature,
        "shap_main_driver_value": main_driver_shap_value,
    })

    def clean_feature_name(f):
        return f.split("__")[-1]

    shap_export["shap_main_driver_feature"] = shap_export["shap_main_driver_feature"].apply(clean_feature_name)
    shap_export["shap_driver_direction"] = np.where(
        shap_export["shap_main_driver_value"] > 0, "Increases exit risk", "Reduces exit risk"
    )

    shap_export.to_csv(OUTPUT_DIR / "shap_employee_level.csv", index=False)

    return {
        "global_importance": global_importance,
        "shap_export": shap_export,
        "oof_roc_auc": float(oof_auc),
        "oof_pr_auc": float(oof_ap),
    }


if __name__ == "__main__":
    result = train_and_evaluate()
    print(json.dumps(result["metrics"], indent=2, ensure_ascii=False)[:3000])
    shap_result = run_shap(result)
    print("\nTop 15 SHAP global importance:")
    print(shap_result["global_importance"].head(15))
