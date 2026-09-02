"""
ETAPA 4 — Construção do projeto Power BI (formato PBIP).

Gera dois projetos Power BI completos e abríveis no Power BI Desktop:

  pbip/VELA Retention Intelligence EN/   (modelo em inglês, EUR)
  pbip/VELA Retention Intelligence PT/   (modelo em português, BRL)

Cada projeto contém:
  <nome>.pbip                 ponteiro do projeto
  <nome>.SemanticModel/       modelo semântico em TMDL (tabelas, relações, medidas)
  <nome>.Report/              relatório com as 3 páginas e todos os visuais

O modelo é gerado em TMDL (texto), e o relatório em report.json (formato PBIR
legado), ambos os formatos oficiais que o Power BI Desktop abre nativamente.
As tabelas leem os CSVs por caminho absoluto na máquina do usuário — ajustável
no topo deste arquivo (DATA_ROOT_ON_DEVICE).
"""
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PBIP_DIR = ROOT / "pbip"

# Caminho das pastas de dados NA MÁQUINA DO USUÁRIO (usado pelo Power Query).
DATA_ROOT_ON_DEVICE = r"C:\Users\lucas\Desktop\Portfolio\HR Analytics\archive (1)"

THEME_NAME = "VELA People Analytics"

# ---------------------------------------------------------------------------
# Mapeamento de tipos pandas -> TMDL
# ---------------------------------------------------------------------------
def tmdl_type(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "int64"
    if pd.api.types.is_float_dtype(dtype):
        return "double"
    return "string"


def pq_type(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "Int64.Type"
    if pd.api.types.is_float_dtype(dtype):
        return "type number"
    return "type text"


def esc_m(s: str) -> str:
    """Escapa uma string para literal do Power Query M."""
    return s.replace('"', '""')


# ---------------------------------------------------------------------------
# Configuração dos dois modelos
# ---------------------------------------------------------------------------
def config_en():
    return {
        "key": "EN",
        "project": "VELA Retention Intelligence EN",
        "data_folder": "powerbi_en",
        "culture": "en-US",
        "currency": "EUR",
        "currency_fmt": '"€"#,0;-"€"#,0;"€"#,0',
        "fact": "fEmployeeTurnover",
        "fact_file": "fEmployeeTurnover.csv",
        "dims": [
            ("dDepartment", "dDepartment.csv", "department_key"),
            ("dSalaryRange", "dSalaryRange.csv", "salary_key"),
            ("dTenureBucket", "dTenureBucket.csv", "tenure_bucket_key"),
            ("dPerformanceCluster", "dPerformanceCluster.csv", "performance_cluster_key"),
            ("dExitArchetype", "dExitArchetype.csv", "exit_archetype_key"),
        ],
        "sort_by": [("dSalaryRange", "salary_range", "salary_key"),
                    ("dTenureBucket", "tenure_bucket_label", "tenure_bucket_key")],
        "pages": [
            ("Strategic Diagnosis", "Retention Intelligence · Strategic Diagnosis"),
            ("Behavioural Deep Dive", "Retention Intelligence · Behavioural Deep Dive"),
            ("Prescriptive Cockpit", "Retention Intelligence · Prescriptive Cockpit"),
        ],
        "cols": {
            "left": "left", "risk": "is_flight_risk", "prob": "churn_probability",
            "band": "risk_band", "quad": "risk_quadrant", "cluster": "behavior_cluster",
            "repl": "simulated_replacement_cost_eur", "reten": "simulated_retention_action_cost_eur",
            "sat": "satisfaction_level", "eval": "last_evaluation", "hours": "average_montly_hours",
            "tenure": "time_spend_company", "proj": "number_project", "id": "employee_id",
            "driver": "shap_main_driver_feature", "dir": "shap_driver_direction",
            "gap": "eval_satisfaction_gap", "accident": "Work_accident",
        },
        "dim_cols": {"dept": ("dDepartment", "department_name"),
                     "sal": ("dSalaryRange", "salary_range"),
                     "ten": ("dTenureBucket", "tenure_bucket_label"),
                     "clu": ("dPerformanceCluster", "cluster_name"),
                     "arc": ("dExitArchetype", "archetype_name")},
        "labels": {
            "kpi_actual": "Actual Turnover Rate", "kpi_pred": "Predicted Risk Rate",
            "kpi_atrisk": "Employees at Risk", "kpi_loss": "Projected Loss",
            "kpi_roi": "Retention ROI", "kpi_q1": "Critical Risk · High Performer",
            "by_dept": "Turnover rate by department", "by_band": "Headcount by risk band",
            "cost_dept": "Projected replacement cost by department",
            "quad_dist": "Headcount by risk quadrant",
            "hours": "Churn rate by monthly hours band",
            "tenure": "Churn rate by years at company",
            "proj": "Churn rate by number of projects",
            "scatter": "Satisfaction × Evaluation (colour = left)",
            "arche": "Turnover rate by exit archetype",
            "salary": "Churn rate by salary band",
            "table": "Employees at critical risk — action list",
            "driver": "Top predictive driver (SHAP)",
            "cluster": "Headcount by behavioural cluster",
        },
        "measures_folder": "_Measures",
    }


def config_pt():
    c = config_en()
    c.update({
        "key": "PT",
        "project": "VELA Retention Intelligence PT",
        "data_folder": "powerbi_pt",
        "culture": "pt-BR",
        "currency": "BRL",
        "currency_fmt": '"R$"#,0;-"R$"#,0;"R$"#,0',
        "fact": "fRotatividadeColaboradores",
        "fact_file": "fRotatividadeColaboradores.csv",
        "dims": [
            ("dDepartamento", "dDepartamento.csv", "chave_departamento"),
            ("dFaixaSalarial", "dFaixaSalarial.csv", "chave_faixa_salarial"),
            ("dTempoDeCasa", "dTempoDeCasa.csv", "chave_tempo_casa"),
            ("dClusterComportamental", "dClusterComportamental.csv", "chave_cluster_comportamental"),
            ("dArquetipoSaida", "dArquetipoSaida.csv", "chave_arquetipo_saida"),
        ],
        "sort_by": [("dFaixaSalarial", "faixa_salarial", "chave_faixa_salarial"),
                    ("dTempoDeCasa", "faixa_tempo_casa", "chave_tempo_casa")],
        "pages": [
            ("Diagnóstico Estratégico", "Inteligência de Retenção · Diagnóstico Estratégico"),
            ("Deep Dive Comportamental", "Inteligência de Retenção · Deep Dive Comportamental"),
            ("Cockpit Prescritivo", "Inteligência de Retenção · Cockpit Prescritivo"),
        ],
        "cols": {
            "left": "saiu_da_empresa", "risk": "flag_risco_iminente", "prob": "probabilidade_saida",
            "band": "faixa_de_risco", "quad": "quadrante_risco", "cluster": "cluster_comportamental",
            "repl": "custo_reposicao_simulado_brl", "reten": "custo_acao_retencao_simulado_brl",
            "sat": "nivel_satisfacao", "eval": "ultima_avaliacao", "hours": "horas_mensais_medias",
            "tenure": "tempo_de_casa_anos", "proj": "numero_projetos", "id": "id_colaborador",
            "driver": "fator_principal_shap", "dir": "direcao_fator_shap",
            "gap": "gap_avaliacao_satisfacao", "accident": "sofreu_acidente_trabalho",
        },
        "dim_cols": {"dept": ("dDepartamento", "nome_departamento"),
                     "sal": ("dFaixaSalarial", "faixa_salarial"),
                     "ten": ("dTempoDeCasa", "faixa_tempo_casa"),
                     "clu": ("dClusterComportamental", "nome_cluster"),
                     "arc": ("dArquetipoSaida", "nome_arquetipo")},
        "labels": {
            "kpi_actual": "Taxa Real de Rotatividade", "kpi_pred": "Taxa Preditiva de Risco",
            "kpi_atrisk": "Colaboradores em Risco", "kpi_loss": "Perda Projetada",
            "kpi_roi": "ROI de Retenção", "kpi_q1": "Risco Crítico · Alto Desempenho",
            "by_dept": "Taxa de rotatividade por departamento", "by_band": "Colaboradores por faixa de risco",
            "cost_dept": "Custo de reposição projetado por departamento",
            "quad_dist": "Colaboradores por quadrante de risco",
            "hours": "Taxa de saída por faixa de horas mensais",
            "tenure": "Taxa de saída por tempo de casa",
            "proj": "Taxa de saída por número de projetos",
            "scatter": "Satisfação × Avaliação (cor = saiu)",
            "arche": "Taxa de saída por arquétipo de desligamento",
            "salary": "Taxa de saída por faixa salarial",
            "table": "Colaboradores em risco crítico — lista de ação",
            "driver": "Principal fator preditivo (SHAP)",
            "cluster": "Colaboradores por cluster comportamental",
        },
        "measures_folder": "_Medidas",
    })
    return c


# ---------------------------------------------------------------------------
# MEDIDAS DAX  (nome, expressão, pasta de exibição, formato)
# ---------------------------------------------------------------------------
# Nomes de medida por idioma. As páginas referenciam pela CHAVE, nunca pelo texto,
# para que EN e PT fiquem consistentes sem duplicar a lógica dos visuais.
MEASURE_NAMES = {
    "total":     {"EN": "Total Employees",                    "PT": "Total de Colaboradores"},
    "exits":     {"EN": "Total Exits (Actual)",               "PT": "Total de Saídas (Real)"},
    "rate":      {"EN": "Actual Turnover Rate",               "PT": "Taxa Real de Rotatividade"},
    "atrisk":    {"EN": "Employees at Risk (Predicted)",      "PT": "Total em Risco (Preditivo)"},
    "prate":     {"EN": "Predicted Risk Rate",                "PT": "Taxa Preditiva de Risco"},
    "avgprob":   {"EN": "Average Churn Probability",          "PT": "Probabilidade Média de Saída"},
    "gap":       {"EN": "Actual vs Predicted Gap",            "PT": "Gap Real vs Preditivo"},
    "factor":    {"EN": "Replacement Cost Adjustment Factor", "PT": "Fator de Ajuste do Custo de Reposição"},
    "success":   {"EN": "Retention Success Rate",             "PT": "Taxa de Sucesso da Ação de Retenção"},
    "lossR":     {"EN": "Estimated Loss (Actual)",            "PT": "Custo Estimado de Perda (Realizado)"},
    "lossP":     {"EN": "Estimated Loss (Projected)",         "PT": "Custo Estimado de Perda (Projetado)"},
    "invest":    {"EN": "Required Retention Investment",      "PT": "Investimento Necessário em Retenção"},
    "avgcost":   {"EN": "Average Replacement Cost per At-Risk Employee",
                  "PT": "Custo Médio de Reposição por Colaborador em Risco"},
    "avoid":     {"EN": "Expected Avoided Exits",             "PT": "Saídas Evitadas Esperadas"},
    "save":      {"EN": "Expected Retention Saving",          "PT": "Economia Esperada com Retenção"},
    "roi":       {"EN": "Potential Retention ROI",            "PT": "ROI Potencial de Retenção"},
    "q1":        {"EN": "Critical Risk High Performer (Count)", "PT": "Risco Crítico Alto Desempenho (Qtd)"},
    "q1pct":     {"EN": "Critical Risk High Performer (%)",   "PT": "Risco Crítico Alto Desempenho (%)"},
    "q1cost":    {"EN": "High Performer Loss Cost at Risk",   "PT": "Custo de Perda de Alto Desempenho em Risco"},
    "avgsat":    {"EN": "Average Satisfaction",               "PT": "Satisfação Média"},
    "avgeval":   {"EN": "Average Evaluation",                 "PT": "Avaliação Média"},
    "avghours":  {"EN": "Average Monthly Hours",              "PT": "Horas Médias Mensais"},
    "rank":      {"EN": "Department Turnover Rank",           "PT": "Ranking Departamento por Rotatividade"},
    "extreme":   {"EN": "Employees in Extreme Project Zone",  "PT": "Colaboradores em Zona de Projeto Extremo"},
    "driver":    {"EN": "Most Frequent Main Driver",          "PT": "Fator Principal Mais Frequente"},
    "accuracy":  {"EN": "Model Accuracy (Info)",              "PT": "Precisão do Modelo (Informativo)"},
}

FOLDERS = {
    "g1": {"EN": "01. Rates",          "PT": "01. Taxas"},
    "g2": {"EN": "02. Financial",      "PT": "02. Financeiro"},
    "g3": {"EN": "03. Critical Risk",  "PT": "03. Risco Crítico"},
    "g4": {"EN": "04. Segmentation",   "PT": "04. Segmentação"},
    "g5": {"EN": "05. Explainability", "PT": "05. Explicabilidade"},
}


def MN(cfg, key):
    """Nome da medida no idioma do modelo."""
    return MEASURE_NAMES[key][cfg["key"]]


def measures_for(cfg):
    F, C = cfg["fact"], cfg["cols"]
    cur = cfg["currency_fmt"]
    k = cfg["key"]
    n = lambda key: MEASURE_NAMES[key][k]
    g = lambda key: FOLDERS[key][k]
    extreme_col = "flag_projeto_extremo" if k == "PT" else "is_project_extreme"
    q1 = "Q1 - Risco Crítico / Alto Desempenho" if k == "PT" else "Q1 - Critical Risk / High Performer"

    M = []
    add = lambda key, e, f, fmt=None: M.append(
        {"name": n(key), "expr": e, "folder": g(f), "format": fmt})

    add("total",   f"COUNTROWS ( {F} )", "g1", "#,0")
    add("exits",   f"CALCULATE ( COUNTROWS ( {F} ), {F}[{C['left']}] = 1 )", "g1", "#,0")
    add("rate",    f"DIVIDE ( [{n('exits')}], [{n('total')}], 0 )", "g1", "0.0%")
    add("atrisk",  f"CALCULATE ( COUNTROWS ( {F} ), {F}[{C['risk']}] = 1 )", "g1", "#,0")
    add("prate",   f"DIVIDE ( [{n('atrisk')}], [{n('total')}], 0 )", "g1", "0.0%")
    add("avgprob", f"AVERAGE ( {F}[{C['prob']}] )", "g1", "0.0%")
    add("gap",     f"[{n('prate')}] - [{n('rate')}]", "g1", "0.0%")

    add("factor",  "SELECTEDVALUE ( 'Cost Adjustment'[Cost Adjustment], 1 )", "g2", "0.00")
    add("success", "SELECTEDVALUE ( 'Retention Success'[Retention Success], 0.35 )", "g2", "0%")
    add("lossR",   f"SUMX ( FILTER ( {F}, {F}[{C['left']}] = 1 ), {F}[{C['repl']}] ) * [{n('factor')}]", "g2", cur)
    add("lossP",   f"SUMX ( FILTER ( {F}, {F}[{C['risk']}] = 1 ), {F}[{C['repl']}] ) * [{n('factor')}]", "g2", cur)
    add("invest",  f"SUMX ( FILTER ( {F}, {F}[{C['risk']}] = 1 ), {F}[{C['reten']}] )", "g2", cur)
    add("avgcost", f"DIVIDE ( [{n('lossP')}], [{n('atrisk')}], 0 )", "g2", cur)
    add("avoid",   f"SUMX ( FILTER ( {F}, {F}[{C['risk']}] = 1 ), {F}[{C['prob']}] ) * [{n('success')}]", "g2", "#,0")
    add("save",    f"SUMX ( FILTER ( {F}, {F}[{C['risk']}] = 1 ), {F}[{C['repl']}] * {F}[{C['prob']}] ) * [{n('success')}] * [{n('factor')}]", "g2", cur)
    add("roi",     f"DIVIDE ( [{n('save')}] - [{n('invest')}], [{n('invest')}], 0 )", "g2", "0.00")

    add("q1",     f'CALCULATE ( COUNTROWS ( {F} ), {F}[{C["quad"]}] = "{q1}" )', "g3", "#,0")
    add("q1pct",  f"DIVIDE ( [{n('q1')}], [{n('total')}], 0 )", "g3", "0.0%")
    add("q1cost", f'SUMX ( FILTER ( {F}, {F}[{C["quad"]}] = "{q1}" ), {F}[{C["repl"]}] ) * [{n("factor")}]', "g3", cur)

    add("avgsat",   f"AVERAGE ( {F}[{C['sat']}] )", "g4", "0.0%")
    add("avgeval",  f"AVERAGE ( {F}[{C['eval']}] )", "g4", "0.0%")
    add("avghours", f"AVERAGE ( {F}[{C['hours']}] )", "g4", "#,0")
    dept_t, dept_c = cfg["dim_cols"]["dept"]
    add("rank",     f"RANKX ( ALL ( {dept_t}[{dept_c}] ), CALCULATE ( [{n('rate')}] ),, DESC )", "g4", "0")
    add("extreme",  f"CALCULATE ( COUNTROWS ( {F} ), {F}[{extreme_col}] = 1 )", "g4", "#,0")

    add("driver", f"VAR T = TOPN ( 1, VALUES ( {F}[{C['driver']}] ), CALCULATE ( COUNTROWS ( {F} ) ), DESC )\n"
                  f"RETURN CONCATENATEX ( T, {F}[{C['driver']}], \", \" )", "g5")
    add("accuracy", '"ROC-AUC 0.994 | PR-AUC 0.989 (XGBoost, 25% holdout) — out-of-fold scoring (5 folds)"'
                    if k == "EN" else
                    '"ROC-AUC 0,994 | PR-AUC 0,989 (XGBoost, holdout 25%) — scoring out-of-fold (5 dobras)"', "g5")
    return M


# ---------------------------------------------------------------------------
# TMDL
# ---------------------------------------------------------------------------
def m_partition(csv_path: str, df: pd.DataFrame) -> str:
    """Expressão Power Query M que lê o CSV com tipos explícitos."""
    types = ", ".join(f'{{"{c}", {pq_type(df[c].dtype)}}}' for c in df.columns)
    return (
        'let\n'
        f'    Source = Csv.Document(File.Contents("{esc_m(csv_path)}"), '
        '[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'    Typed = Table.TransformColumnTypes(Promoted, {{{types}}})\n'
        'in\n'
        '    Typed'
    )


def indent(text: str, n: int) -> str:
    pad = "\t" * n
    return "\n".join(pad + ln if ln.strip() else ln for ln in text.split("\n"))


def table_tmdl(name: str, df: pd.DataFrame, csv_path: str, *, hidden_cols=None,
               sort_by=None, fmt_map=None) -> str:
    hidden_cols = hidden_cols or set()
    sort_by = sort_by or {}
    fmt_map = fmt_map or {}
    L = [f"table {name}", ""]
    for c in df.columns:
        L.append(f"\tcolumn '{c}'")
        L.append(f"\t\tdataType: {tmdl_type(df[c].dtype)}")
        L.append(f"\t\tsourceColumn: {c}")
        L.append("\t\tsummarizeBy: none")
        if c in fmt_map:
            L.append(f'\t\tformatString: {fmt_map[c]}')
        if c in hidden_cols:
            L.append("\t\tisHidden")
        if c in sort_by:
            L.append(f"\t\tsortByColumn: {sort_by[c]}")
        L.append("")
    L.append(f"\tpartition {name} = m")
    L.append("\t\tmode: import")
    L.append("\t\tsource =")
    L.append(indent(m_partition(csv_path, df), 3))
    L.append("")
    return "\n".join(L)


def measures_table_tmdl(folder_name: str, measures) -> str:
    L = [f"table {folder_name}", ""]
    L.append("\tcolumn _dummy")
    L.append("\t\tdataType: int64")
    L.append("\t\tisHidden")
    L.append("\t\tsummarizeBy: none")
    L.append("\t\tsourceColumn: [Value]")
    L.append("")
    for m in measures:
        L.append(f"\tmeasure '{m['name']}' =")
        L.append(indent(m["expr"], 3))
        if m.get("format"):
            L.append(f'\t\tformatString: {m["format"]}')
        L.append(f'\t\tdisplayFolder: {m["folder"]}')
        L.append("")
    L.append(f"\tpartition {folder_name} = calculated")
    L.append("\t\tmode: import")
    L.append("\t\tsource = {BLANK()}")
    L.append("")
    return "\n".join(L)


def param_table_tmdl(name: str, col: str, lo, hi, step, default) -> str:
    return (
        f"table '{name}'\n\n"
        f"\tcolumn '{col}'\n"
        f"\t\tdataType: double\n"
        f"\t\tsummarizeBy: none\n"
        f"\t\tsourceColumn: [Value]\n"
        f"\t\tformatString: 0.00\n\n"
        f"\tpartition '{name}' = calculated\n"
        f"\t\tmode: import\n"
        f"\t\tsource = GENERATESERIES({lo}, {hi}, {step})\n"
    )


def relationships_tmdl(cfg) -> str:
    L = []
    for i, (dim, _f, key) in enumerate(cfg["dims"], start=1):
        L.append(f"relationship rel_{dim}")
        L.append("\tfromColumn: %s.%s" % (cfg["fact"], key))
        L.append("\ttoColumn: %s.%s" % (dim, key))
        L.append("\tcrossFilteringBehavior: oneDirection")
        L.append("")
    return "\n".join(L)


def model_tmdl(cfg) -> str:
    refs = [cfg["fact"]] + [d[0] for d in cfg["dims"]] + \
           [cfg["measures_folder"], "Cost Adjustment", "Retention Success"]
    L = ["model Model", f"\tculture: {cfg['culture']}", "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
         "\tdiscourageImplicitMeasures", "\tsourceQueryCulture: " + cfg["culture"], ""]
    for r in refs:
        L.append(f"ref table '{r}'" if " " in r else f"ref table {r}")
    L.append("")
    L.append("ref cultureInfo " + cfg["culture"])
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# REPORT (PBIR legado)
# ---------------------------------------------------------------------------
PAL = ["#2A6FB8", "#E8833A", "#1B9E8F", "#7B5EA7", "#C43A5E", "#B8912E", "#4A7C8C", "#8C5E3C"]
INK, MUTED, RULE = "#0F2A3D", "#5A6B7A", "#E4E8EC"
CANVAS_W, CANVAS_H = 1280, 720
_uid = {"n": 0}


def nid(prefix="v"):
    _uid["n"] += 1
    return f"{prefix}{_uid['n']:04d}"


def col_ref(table, column):
    return {"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": column}}


def _query(entities, selects):
    """entities: list of (alias, entity). selects: list of dicts already shaped."""
    return {"Version": 2,
            "From": [{"Name": a, "Entity": e, "Type": 0} for a, e in entities],
            "Select": selects}


def sel_measure(alias, table, name):
    return {"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": name},
            "Name": f"{table}.{name}", "NativeReferenceName": name}


def sel_column(alias, table, name):
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": name},
            "Name": f"{table}.{name}", "NativeReferenceName": name}


def sel_agg(alias, table, name, fn=0, native=None):
    """fn: 0=Sum 1=Avg 2=Min 3=Max 5=Count"""
    label = {0: "Sum", 1: "Average", 2: "Min", 3: "Max", 5: "Count"}[fn]
    return {"Aggregation": {"Expression": {"Column": {
                "Expression": {"SourceRef": {"Source": alias}}, "Property": name}}, "Function": fn},
            "Name": f"{label}({table}.{name})", "NativeReferenceName": native or name}


def container(x, y, w, h, cfg_obj, z=0):
    cfg_obj.setdefault("layouts", [{"id": 0, "position": {"x": x, "y": y, "z": z,
                                                          "width": w, "height": h}}])
    return {"x": x, "y": y, "z": z, "width": w, "height": h,
            "config": json.dumps(cfg_obj, ensure_ascii=False)}


def _title(text, size=11, color=INK):
    return {"title": [{"properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "text": {"expr": {"Literal": {"Value": f"'{text}'"}}},
        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{color}'"}}}}},
        "fontSize": {"expr": {"Literal": {"Value": f"{size}D"}}},
        "alignment": {"expr": {"Literal": {"Value": "'left'"}}},
    }}]}


def visual(vtype, x, y, w, h, projections, query, *, title=None, objects=None, z=0):
    obj = dict(objects or {})
    vc = {}
    if title:
        vc.update(_title(title))
    sv = {"visualType": vtype, "projections": projections, "prototypeQuery": query,
          "drillFilterOtherVisuals": True}
    if obj:
        sv["objects"] = obj
    if vc:
        sv["vcObjects"] = vc
    return container(x, y, w, h, {"name": nid(), "singleVisual": sv}, z)


def textbox(x, y, w, h, runs, *, z=0, align="left"):
    paragraphs = [{"textRuns": runs, "horizontalTextAlignment": align}]
    cfg = {"name": nid("t"), "singleVisual": {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
        "drillFilterOtherVisuals": True}}
    return container(x, y, w, h, cfg, z)


def shape_rect(x, y, w, h, color, *, z=0):
    cfg = {"name": nid("s"), "singleVisual": {
        "visualType": "shape",
        "objects": {
            "shape": [{"properties": {"tileShape": {"expr": {"Literal": {"Value": "'rectangle'"}}}}}],
            "fill": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{color}'"}}}}}}}],
            "outline": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
        },
        "drillFilterOtherVisuals": True}}
    return container(x, y, w, h, cfg, z)


# ---------------------------------------------------------------------------
# Construtores de visual de alto nível
# ---------------------------------------------------------------------------
def kpi_card(x, y, w, h, mtable, mname, label, *, color=INK, size=34):
    q = _query([("m", mtable)], [sel_measure("m", mtable, mname)])
    proj = {"Values": [{"queryRef": f"{mtable}.{mname}"}]}
    objects = {
        "labels": [{"properties": {
            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{color}'"}}}}},
            "fontSize": {"expr": {"Literal": {"Value": f"{size}D"}}},
            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Light'"}}}}}],
        "categoryLabels": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "false"}}}}}],
    }
    return visual("card", x, y, w, h, proj, q, title=label, objects=objects)


def bar_by_dim(x, y, w, h, dim_t, dim_c, mtable, mname, title, *, vtype="barChart",
               series_color=PAL[0], data_labels=True):
    q = _query([("s", dim_t), ("m", mtable)],
               [sel_column("s", dim_t, dim_c), sel_measure("m", mtable, mname)])
    proj = {"Category": [{"queryRef": f"{dim_t}.{dim_c}"}],
            "Y": [{"queryRef": f"{mtable}.{mname}"}]}
    objects = {
        "dataPoint": [{"properties": {"fill": {"solid": {"color": {
            "expr": {"Literal": {"Value": f"'{series_color}'"}}}}}}}],
        "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": str(data_labels).lower()}}},
                                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
        "categoryAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
        "valueAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
    }
    return visual(vtype, x, y, w, h, proj, q, title=title, objects=objects)


def bar_by_fact_col(x, y, w, h, fact, colname, mtable, mname, title, *,
                    vtype="columnChart", series_color=PAL[0]):
    q = _query([("s", fact), ("m", mtable)],
               [sel_column("s", fact, colname), sel_measure("m", mtable, mname)])
    proj = {"Category": [{"queryRef": f"{fact}.{colname}"}],
            "Y": [{"queryRef": f"{mtable}.{mname}"}]}
    objects = {
        "dataPoint": [{"properties": {"fill": {"solid": {"color": {
            "expr": {"Literal": {"Value": f"'{series_color}'"}}}}}}}],
        "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
        "categoryAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
        "valueAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
    }
    return visual(vtype, x, y, w, h, proj, q, title=title, objects=objects)


def line_by_fact_col(x, y, w, h, fact, colname, mtable, mname, title, *, series_color=PAL[0]):
    q = _query([("s", fact), ("m", mtable)],
               [sel_column("s", fact, colname), sel_measure("m", mtable, mname)])
    proj = {"Category": [{"queryRef": f"{fact}.{colname}"}],
            "Y": [{"queryRef": f"{mtable}.{mname}"}]}
    objects = {
        "dataPoint": [{"properties": {"fill": {"solid": {"color": {
            "expr": {"Literal": {"Value": f"'{series_color}'"}}}}}}}],
        "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
        "categoryAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
        "valueAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "false"}}}}}],
    }
    return visual("lineChart", x, y, w, h, proj, q, title=title, objects=objects)


def scatter(x, y, w, h, fact, id_col, xcol, ycol, legend_col, title):
    q = _query([("s", fact)], [
        sel_column("s", fact, id_col),
        sel_agg("s", fact, xcol, 1),
        sel_agg("s", fact, ycol, 1),
        sel_column("s", fact, legend_col),
    ])
    proj = {"Details": [{"queryRef": f"{fact}.{id_col}"}],
            "X": [{"queryRef": f"Average({fact}.{xcol})"}],
            "Y": [{"queryRef": f"Average({fact}.{ycol})"}],
            "Series": [{"queryRef": f"{fact}.{legend_col}"}]}
    objects = {
        "categoryAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "true"}}}}}],
        "valueAxis": [{"properties": {"showAxisTitle": {"expr": {"Literal": {"Value": "true"}}}}}],
        "bubbles": [{"properties": {"bubbleSize": {"expr": {"Literal": {"Value": "-40D"}}}}}],
    }
    return visual("scatterChart", x, y, w, h, proj, q, title=title, objects=objects)


def table_visual(x, y, w, h, entities, cols, measures, title):
    """cols: list of (alias, table, column). measures: list of (alias, table, measure)."""
    selects, refs = [], []
    for a, t, c in cols:
        selects.append(sel_column(a, t, c)); refs.append({"queryRef": f"{t}.{c}"})
    for a, t, m in measures:
        selects.append(sel_measure(a, t, m)); refs.append({"queryRef": f"{t}.{m}"})
    q = _query(entities, selects)
    objects = {
        "grid": [{"properties": {"gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                                  "outlineWeight": {"expr": {"Literal": {"Value": "1D"}}}}}],
        "columnHeaders": [{"properties": {
            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{MUTED}'"}}}}},
            "fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
        "values": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}],
    }
    return visual("tableEx", x, y, w, h, {"Values": refs}, q, title=title, objects=objects)


def slicer(x, y, w, h, table, column, title):
    q = _query([("s", table)], [sel_column("s", table, column)])
    proj = {"Values": [{"queryRef": f"{table}.{column}"}]}
    objects = {"general": [{"properties": {"orientation": {"expr": {"Literal": {"Value": "1D"}}}}}]}
    return visual("slicer", x, y, w, h, proj, q, title=title, objects=objects)


def header_band(title_text, subtitle_text):
    """Faixa superior da página com a marca VELA."""
    out = [shape_rect(0, 0, CANVAS_W, 56, "#FFFFFF", z=0)]
    out.append(textbox(24, 12, 92, 32, [
        {"value": "VELA", "textStyle": {"fontSize": "17pt", "fontWeight": "bold",
                                         "color": INK, "fontFamily": "Segoe UI"}}], z=1))
    out.append(shape_rect(120, 16, 1, 24, RULE, z=1))
    out.append(textbox(132, 13, 640, 34, [
        {"value": subtitle_text, "textStyle": {"fontSize": "11pt", "color": MUTED,
                                                "fontFamily": "Segoe UI"}}], z=1))
    out.append(shape_rect(0, 56, CANVAS_W, 1, RULE, z=1))
    return out


def page1(cfg):
    F, C, L = cfg["fact"], cfg["cols"], cfg["labels"]
    MT = cfg["measures_folder"]
    dept_t, dept_c = cfg["dim_cols"]["dept"]
    ten_t, ten_c = cfg["dim_cols"]["ten"]
    M = lambda k: MN(cfg, k)
    v = header_band(cfg["pages"][0][0], cfg["pages"][0][1])

    xs, w, gap = 24, 236, 12
    v.append(kpi_card(xs + 0 * (w + gap), 72, w, 96, MT, M("rate"),   L["kpi_actual"]))
    v.append(kpi_card(xs + 1 * (w + gap), 72, w, 96, MT, M("atrisk"), L["kpi_atrisk"], color=PAL[1]))
    v.append(kpi_card(xs + 2 * (w + gap), 72, w, 96, MT, M("lossP"),  L["kpi_loss"], size=26))
    v.append(kpi_card(xs + 3 * (w + gap), 72, w, 96, MT, M("q1"),     L["kpi_q1"], color=PAL[4]))
    v.append(kpi_card(xs + 4 * (w + gap), 72, w, 96, MT, M("roi"),    L["kpi_roi"], color=PAL[2]))

    v.append(bar_by_dim(24, 184, 616, 268, dept_t, dept_c, MT, M("rate"), L["by_dept"]))
    v.append(bar_by_dim(652, 184, 604, 268, dept_t, dept_c, MT, M("lossP"),
                        L["cost_dept"], series_color=PAL[1]))

    v.append(bar_by_fact_col(24, 468, 400, 228, F, C["band"], MT, M("total"),
                             L["by_band"], vtype="columnChart", series_color=PAL[0]))
    v.append(bar_by_fact_col(436, 468, 404, 228, F, C["quad"], MT, M("total"),
                             L["quad_dist"], vtype="barChart", series_color=PAL[3]))
    v.append(slicer(852, 468, 196, 228, dept_t, dept_c,
                    "Department" if cfg["key"] == "EN" else "Departamento"))
    v.append(slicer(1060, 468, 196, 228, ten_t, ten_c,
                    "Tenure" if cfg["key"] == "EN" else "Tempo de casa"))
    return v


def page2(cfg):
    F, C, L = cfg["fact"], cfg["cols"], cfg["labels"]
    MT = cfg["measures_folder"]
    M = lambda k: MN(cfg, k)
    arc_t, arc_c = cfg["dim_cols"]["arc"]
    sal_t, sal_c = cfg["dim_cols"]["sal"]
    v = header_band(cfg["pages"][1][0], cfg["pages"][1][1])

    v.append(line_by_fact_col(24, 72, 616, 256, F, C["tenure"], MT, M("rate"), L["tenure"]))
    v.append(bar_by_fact_col(652, 72, 604, 256, F, C["proj"], MT, M("rate"), L["proj"],
                             vtype="columnChart", series_color=PAL[1]))
    v.append(scatter(24, 344, 616, 352, F, C["id"], C["sat"], C["eval"], C["left"], L["scatter"]))
    v.append(bar_by_dim(652, 344, 604, 168, arc_t, arc_c, MT, M("rate"), L["arche"],
                        series_color=PAL[2]))
    v.append(bar_by_dim(652, 528, 604, 168, sal_t, sal_c, MT, M("rate"), L["salary"],
                        series_color=PAL[5]))
    return v


def page3(cfg):
    F, C, L = cfg["fact"], cfg["cols"], cfg["labels"]
    MT = cfg["measures_folder"]
    M = lambda k: MN(cfg, k)
    en = cfg["key"] == "EN"
    clu_t, clu_c = cfg["dim_cols"]["clu"]
    dept_t, dept_c = cfg["dim_cols"]["dept"]
    v = header_band(cfg["pages"][2][0], cfg["pages"][2][1])

    v.append(kpi_card(24, 72, 236, 92, MT, M("avoid"),
                      "Expected avoided exits" if en else "Saídas evitadas esperadas", size=26))
    v.append(kpi_card(272, 72, 236, 92, MT, M("save"),
                      "Expected saving" if en else "Economia esperada", color=PAL[2], size=22))
    v.append(kpi_card(520, 72, 236, 92, MT, M("invest"),
                      "Retention investment" if en else "Investimento em retenção", size=22))
    v.append(slicer(768, 72, 240, 92, "Cost Adjustment", "Cost Adjustment",
                    "Cost adjustment factor" if en else "Fator de ajuste de custo"))
    v.append(slicer(1020, 72, 236, 92, "Retention Success", "Retention Success",
                    "Retention success rate" if en else "Taxa de sucesso da retenção"))

    v.append(table_visual(24, 180, 800, 516,
                          [("s", F), ("d", dept_t), ("m", MT)],
                          [("s", F, C["id"]), ("d", dept_t, dept_c), ("s", F, C["quad"]),
                           ("s", F, C["driver"]), ("s", F, C["dir"])],
                          [("m", MT, M("avgprob")), ("m", MT, M("lossP"))],
                          L["table"]))

    v.append(bar_by_fact_col(836, 180, 420, 256, F, C["driver"], MT, M("total"),
                             L["driver"], vtype="barChart", series_color=PAL[0]))
    v.append(bar_by_dim(836, 448, 420, 248, clu_t, clu_c, MT, M("total"), L["cluster"],
                        series_color=PAL[3]))
    return v


def build_report(cfg, theme_json):
    sections = []
    for i, (builder, (name, subtitle)) in enumerate(zip([page1, page2, page3], cfg["pages"])):
        containers = builder(cfg)
        sections.append({
            "name": f"ReportSection{i+1}",
            "displayName": name,
            "filters": "[]",
            "ordinal": i,
            "visualContainers": containers,
            "config": json.dumps({"objects": {"background": [{"properties": {
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F2F4F6'"}}}}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]}}, ensure_ascii=False),
            "displayOption": 1,
            "width": CANVAS_W,
            "height": CANVAS_H,
        })
    report = {
        "id": 0,
        "resourcePackages": [],
        "sections": sections,
        "config": json.dumps({
            "version": "5.43",
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {"useStylableVisualContainerHeader": True},
        }, ensure_ascii=False),
        "layoutOptimization": 0,
    }
    return report


# ---------------------------------------------------------------------------
# Montagem do projeto PBIP
# ---------------------------------------------------------------------------
def platform(name, kind):
    return {"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": kind, "displayName": name},
            "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000"}}


def build_project(cfg, theme_path: Path):
    proj = cfg["project"]
    base = PBIP_DIR / proj
    if base.exists():
        shutil.rmtree(base)
    sm = base / f"{proj}.SemanticModel"
    rp = base / f"{proj}.Report"
    (sm / "definition" / "tables").mkdir(parents=True, exist_ok=True)
    (rp / "StaticResources" / "SharedResources" / "BaseThemes").mkdir(parents=True, exist_ok=True)

    data_dir = ROOT / cfg["data_folder"]
    device_dir = f"{DATA_ROOT_ON_DEVICE}\\{cfg['data_folder']}"

    # ---- tabelas ----
    fact_df = pd.read_csv(data_dir / cfg["fact_file"])
    key_cols = {k for _d, _f, k in cfg["dims"]}
    fmt = {cfg["cols"]["prob"]: "0.0%", cfg["cols"]["sat"]: "0.0%",
           cfg["cols"]["eval"]: "0.0%", cfg["cols"]["repl"]: cfg["currency_fmt"],
           cfg["cols"]["reten"]: cfg["currency_fmt"]}
    for c in fact_df.columns:
        if c.endswith(("_eur", "_brl")):
            fmt.setdefault(c, cfg["currency_fmt"])
    (sm / "definition" / "tables" / f"{cfg['fact']}.tmdl").write_text(
        table_tmdl(cfg["fact"], fact_df, f"{device_dir}\\{cfg['fact_file']}",
                   hidden_cols=key_cols, fmt_map=fmt), encoding="utf-8")

    sort_map = {}
    for tbl, col, by in cfg["sort_by"]:
        sort_map.setdefault(tbl, {})[col] = by
    for dim, fname, key in cfg["dims"]:
        ddf = pd.read_csv(data_dir / fname)
        (sm / "definition" / "tables" / f"{dim}.tmdl").write_text(
            table_tmdl(dim, ddf, f"{device_dir}\\{fname}",
                       hidden_cols={key}, sort_by=sort_map.get(dim, {})), encoding="utf-8")

    # ---- medidas e parâmetros ----
    M = measures_for(cfg)
    (sm / "definition" / "tables" / f"{cfg['measures_folder']}.tmdl").write_text(
        measures_table_tmdl(cfg["measures_folder"], M), encoding="utf-8")
    (sm / "definition" / "tables" / "Cost Adjustment.tmdl").write_text(
        param_table_tmdl("Cost Adjustment", "Cost Adjustment", "0.5", "2", "0.1", "1"), encoding="utf-8")
    (sm / "definition" / "tables" / "Retention Success.tmdl").write_text(
        param_table_tmdl("Retention Success", "Retention Success", "0", "1", "0.05", "0.35"),
        encoding="utf-8")

    # ---- model / relationships / database ----
    (sm / "definition" / "model.tmdl").write_text(model_tmdl(cfg), encoding="utf-8")
    (sm / "definition" / "relationships.tmdl").write_text(relationships_tmdl(cfg), encoding="utf-8")
    (sm / "definition" / "database.tmdl").write_text(
        f"database\n\tcompatibilityLevel: 1567\n", encoding="utf-8")
    (sm / "definition" / "cultures").mkdir(exist_ok=True)
    (sm / "definition" / "cultures" / f"{cfg['culture']}.tmdl").write_text(
        f"cultureInfo {cfg['culture']}\n\n\tlinguisticMetadata =\n\t\t\t{{\n"
        f'\t\t\t  "Version": "1.0.0",\n\t\t\t  "Language": "{cfg["culture"]}"\n\t\t\t}}\n'
        "\t\tcontentType: json\n", encoding="utf-8")
    (sm / "definition.pbism").write_text(json.dumps(
        {"version": "4.0", "settings": {}}, indent=2), encoding="utf-8")
    (sm / ".platform").write_text(json.dumps(platform(proj, "SemanticModel"), indent=2), encoding="utf-8")
    (sm / "diagramLayout.json").write_text(json.dumps(
        {"version": "1.1.0", "diagrams": [{"ordinal": 0, "scrollPosition": {"x": 0, "y": 0},
         "nodes": [], "name": "All tables", "zoomValue": 100, "pinKeyFieldsToTop": False,
         "showExtraHeaderInfo": False, "hideKeyFieldsWhenCollapsed": False,
         "tablesLocked": False}], "selectedDiagram": "All tables", "defaultDiagram": "All tables"},
        indent=2), encoding="utf-8")

    # ---- report ----
    theme_json = json.loads(theme_path.read_text(encoding="utf-8"))
    (rp / "StaticResources" / "SharedResources" / "BaseThemes" / f"{THEME_NAME}.json").write_text(
        json.dumps(theme_json, ensure_ascii=False, indent=2), encoding="utf-8")
    (rp / "report.json").write_text(json.dumps(build_report(cfg, theme_json), ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    (rp / "definition.pbir").write_text(json.dumps(
        {"version": "1.0", "datasetReference": {"byPath": {"path": f"../{proj}.SemanticModel"}, "byConnection": None}},
        indent=2), encoding="utf-8")
    (rp / ".platform").write_text(json.dumps(platform(proj, "Report"), indent=2), encoding="utf-8")

    # ---- .pbip ----
    (base / f"{proj}.pbip").write_text(json.dumps(
        {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/pbip/definitionProperties/1.0.0/schema.json",
         "version": "1.0", "artifacts": [{"report": {"path": f"{proj}.Report"}}],
         "settings": {"enableAutoRecovery": True}}, indent=2), encoding="utf-8")
    return base


def main():
    PBIP_DIR.mkdir(exist_ok=True, parents=True)
    for cfg, theme in [(config_en(), ROOT / "brand" / "VELA_Theme_EN.json"),
                       (config_pt(), ROOT / "brand" / "VELA_Theme_PT.json")]:
        _uid["n"] = 0
        base = build_project(cfg, theme)
        n_files = sum(1 for _ in base.rglob("*") if _.is_file())
        rep = json.loads((base / f"{cfg['project']}.Report" / "report.json").read_text(encoding="utf-8"))
        n_vis = sum(len(s["visualContainers"]) for s in rep["sections"])
        print(f"  {cfg['project']}: {n_files} arquivos · {len(rep['sections'])} páginas · {n_vis} visuais")


if __name__ == "__main__":
    main()
