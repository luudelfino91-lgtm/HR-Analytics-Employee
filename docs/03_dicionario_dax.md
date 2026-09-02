# Dicionário de Medidas DAX — Modelo em Inglês (`powerbi_en/`)

> **Gerado automaticamente** por `scripts/gen_dax_docs.py` a partir de
> `scripts/build_pbip.py` — a mesma fonte que constrói o modelo. Editar este
> arquivo à mão faz a doc divergir do modelo; edite o build e rode o gerador.

> Este é o modelo em **inglês** (medidas, colunas e categorias em inglês, valores
> em EUR com benchmarks irlandeses). O equivalente em português está em
> `07_dicionario_dax_pt.md`. Ver `06_modelagem_e_nomenclatura.md` para o mapa de
> tradução e `10_identidade_marca.md` para a aplicação da marca.

Tabela fato: **`fEmployeeTurnover`** · Tabela de medidas: **`_Measures`**
Parâmetros what-if: **`Cost Adjustment`** (0,5 a 2,0; padrão 1,0) e
**`Retention Success`** (0 a 1; padrão 0,35) — criados como tabelas calculadas
com `GENERATESERIES`, já incluídas no modelo.


---


## 01. Rates

| Medida | Formato |
|---|---|
| `Total Employees` | #,0 |
| `Total Exits (Actual)` | #,0 |
| `Actual Turnover Rate` | 0.0% |
| `Employees at Risk (Predicted)` | #,0 |
| `Predicted Risk Rate` | 0.0% |
| `Average Churn Probability` | 0.0% |
| `Actual vs Predicted Gap` | 0.0% |

```dax
Total Employees =
    COUNTROWS ( fEmployeeTurnover )

Total Exits (Actual) =
    CALCULATE ( COUNTROWS ( fEmployeeTurnover ), fEmployeeTurnover[left] = 1 )

Actual Turnover Rate =
    DIVIDE ( [Total Exits (Actual)], [Total Employees], 0 )

Employees at Risk (Predicted) =
    CALCULATE ( COUNTROWS ( fEmployeeTurnover ), fEmployeeTurnover[is_flight_risk] = 1 )

Predicted Risk Rate =
    DIVIDE ( [Employees at Risk (Predicted)], [Total Employees], 0 )

Average Churn Probability =
    AVERAGE ( fEmployeeTurnover[churn_probability] )

Actual vs Predicted Gap =
    [Predicted Risk Rate] - [Actual Turnover Rate]

```

## 02. Financial

| Medida | Formato |
|---|---|
| `Replacement Cost Adjustment Factor` | 0.00 |
| `Retention Success Rate` | 0% |
| `Estimated Loss (Actual)` | "€"#,0;-"€"#,0;"€"#,0 |
| `Estimated Loss (Projected)` | "€"#,0;-"€"#,0;"€"#,0 |
| `Required Retention Investment` | "€"#,0;-"€"#,0;"€"#,0 |
| `Average Replacement Cost per At-Risk Employee` | "€"#,0;-"€"#,0;"€"#,0 |
| `Expected Avoided Exits` | #,0 |
| `Expected Retention Saving` | "€"#,0;-"€"#,0;"€"#,0 |
| `Potential Retention ROI` | 0.00 |

```dax
Replacement Cost Adjustment Factor =
    SELECTEDVALUE ( 'Cost Adjustment'[Cost Adjustment], 1 )

Retention Success Rate =
    SELECTEDVALUE ( 'Retention Success'[Retention Success], 0.35 )

Estimated Loss (Actual) =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[left] = 1 ), fEmployeeTurnover[simulated_replacement_cost_eur] ) * [Replacement Cost Adjustment Factor]

Estimated Loss (Projected) =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[is_flight_risk] = 1 ), fEmployeeTurnover[simulated_replacement_cost_eur] ) * [Replacement Cost Adjustment Factor]

Required Retention Investment =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[is_flight_risk] = 1 ), fEmployeeTurnover[simulated_retention_action_cost_eur] )

Average Replacement Cost per At-Risk Employee =
    DIVIDE ( [Estimated Loss (Projected)], [Employees at Risk (Predicted)], 0 )

Expected Avoided Exits =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[is_flight_risk] = 1 ), fEmployeeTurnover[churn_probability] ) * [Retention Success Rate]

Expected Retention Saving =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[is_flight_risk] = 1 ), fEmployeeTurnover[simulated_replacement_cost_eur] * fEmployeeTurnover[churn_probability] ) * [Retention Success Rate] * [Replacement Cost Adjustment Factor]

Potential Retention ROI =
    DIVIDE ( [Expected Retention Saving] - [Required Retention Investment], [Required Retention Investment], 0 )

```

> **Nota metodológica (revisada em auditoria).** As saídas evitadas e a economia
> esperada usam a formulação de **valor esperado**: cada colaborador em risco
> contribui com o seu custo de reposição *ponderado pela sua própria
> probabilidade de saída*, não como uma saída certa. Isso corrige duas
> fragilidades da versão anterior (baseada em `TOPN`): contar cada sinalizado
> como uma saída inteira **superestimava** o benefício — estar em risco não é
> sair; e o `TOPN` do DAX devolve **todas** as linhas empatadas no corte, e há
> ~1,7 mil probabilidades repetidas na base, o que poderia inflar a economia
> silenciosamente. A versão atual é estatisticamente correta e imune a empates.
>
> Os custos por colaborador (`*_replacement_cost_*` / `custo_reposicao_*`) são
> **simulados** — ver `08_simulacao_financeira.md`.


## 03. Critical Risk

| Medida | Formato |
|---|---|
| `Critical Risk High Performer (Count)` | #,0 |
| `Critical Risk High Performer (%)` | 0.0% |
| `High Performer Loss Cost at Risk` | "€"#,0;-"€"#,0;"€"#,0 |

```dax
Critical Risk High Performer (Count) =
    CALCULATE ( COUNTROWS ( fEmployeeTurnover ), fEmployeeTurnover[risk_quadrant] = "Q1 - Critical Risk / High Performer" )

Critical Risk High Performer (%) =
    DIVIDE ( [Critical Risk High Performer (Count)], [Total Employees], 0 )

High Performer Loss Cost at Risk =
    SUMX ( FILTER ( fEmployeeTurnover, fEmployeeTurnover[risk_quadrant] = "Q1 - Critical Risk / High Performer" ), fEmployeeTurnover[simulated_replacement_cost_eur] ) * [Replacement Cost Adjustment Factor]

```

## 04. Segmentation

| Medida | Formato |
|---|---|
| `Average Satisfaction` | 0.0% |
| `Average Evaluation` | 0.0% |
| `Average Monthly Hours` | #,0 |
| `Department Turnover Rank` | 0 |
| `Employees in Extreme Project Zone` | #,0 |

```dax
Average Satisfaction =
    AVERAGE ( fEmployeeTurnover[satisfaction_level] )

Average Evaluation =
    AVERAGE ( fEmployeeTurnover[last_evaluation] )

Average Monthly Hours =
    AVERAGE ( fEmployeeTurnover[average_montly_hours] )

Department Turnover Rank =
    RANKX ( ALL ( dDepartment[department_name] ), CALCULATE ( [Actual Turnover Rate] ),, DESC )

Employees in Extreme Project Zone =
    CALCULATE ( COUNTROWS ( fEmployeeTurnover ), fEmployeeTurnover[is_project_extreme] = 1 )

```

## 05. Explainability

| Medida | Formato |
|---|---|
| `Most Frequent Main Driver` | — |
| `Model Accuracy (Info)` | — |

```dax
Most Frequent Main Driver =
    VAR T = TOPN ( 1, VALUES ( fEmployeeTurnover[shap_main_driver_feature] ), CALCULATE ( COUNTROWS ( fEmployeeTurnover ) ), DESC )
    RETURN CONCATENATEX ( T, fEmployeeTurnover[shap_main_driver_feature], ", " )

Model Accuracy (Info) =
    "ROC-AUC 0.994 | PR-AUC 0.989 (XGBoost, 25% holdout) — out-of-fold scoring (5 folds)"

```

> `Most Frequent Main Driver` / `Fator Principal Mais Frequente` isola a tabela
> numa `VAR` e materializa o texto com `CONCATENATEX`. Envolver `TOPN` em
> `CALCULATE` — como estava antes da auditoria — gera erro no Power BI, porque
> `CALCULATE` não pode devolver uma tabela.


---

## Onde as medidas já estão aplicadas

Estas medidas **já estão criadas** no projeto Power BI correspondente em
`pbip/`, com as pastas de exibição acima e a formatação indicada. Não é preciso
colar nada à mão — o dicionário serve como referência e para revisão.
