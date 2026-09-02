# Dicionário de Medidas DAX — Modelo em Português (`powerbi_pt/`)

> **Gerado automaticamente** por `scripts/gen_dax_docs.py` a partir de
> `scripts/build_pbip.py` — a mesma fonte que constrói o modelo. Editar este
> arquivo à mão faz a doc divergir do modelo; edite o build e rode o gerador.

> Este é o modelo em **português** (medidas, colunas e categorias traduzidas,
> valores em BRL com benchmarks brasileiros). O equivalente em inglês está em
> `03_dicionario_dax.md`. Os valores calculados são os mesmos — muda a
> nomenclatura e a âncora salarial.

Tabela fato: **`fRotatividadeColaboradores`** · Tabela de medidas: **`_Medidas`**
Parâmetros what-if: **`Cost Adjustment`** (0,5 a 2,0; padrão 1,0) e
**`Retention Success`** (0 a 1; padrão 0,35) — criados como tabelas calculadas
com `GENERATESERIES`, já incluídas no modelo.


---


## 01. Taxas

| Medida | Formato |
|---|---|
| `Total de Colaboradores` | #,0 |
| `Total de Saídas (Real)` | #,0 |
| `Taxa Real de Rotatividade` | 0.0% |
| `Total em Risco (Preditivo)` | #,0 |
| `Taxa Preditiva de Risco` | 0.0% |
| `Probabilidade Média de Saída` | 0.0% |
| `Gap Real vs Preditivo` | 0.0% |

```dax
Total de Colaboradores =
    COUNTROWS ( fRotatividadeColaboradores )

Total de Saídas (Real) =
    CALCULATE ( COUNTROWS ( fRotatividadeColaboradores ), fRotatividadeColaboradores[saiu_da_empresa] = 1 )

Taxa Real de Rotatividade =
    DIVIDE ( [Total de Saídas (Real)], [Total de Colaboradores], 0 )

Total em Risco (Preditivo) =
    CALCULATE ( COUNTROWS ( fRotatividadeColaboradores ), fRotatividadeColaboradores[flag_risco_iminente] = 1 )

Taxa Preditiva de Risco =
    DIVIDE ( [Total em Risco (Preditivo)], [Total de Colaboradores], 0 )

Probabilidade Média de Saída =
    AVERAGE ( fRotatividadeColaboradores[probabilidade_saida] )

Gap Real vs Preditivo =
    [Taxa Preditiva de Risco] - [Taxa Real de Rotatividade]

```

## 02. Financeiro

| Medida | Formato |
|---|---|
| `Fator de Ajuste do Custo de Reposição` | 0.00 |
| `Taxa de Sucesso da Ação de Retenção` | 0% |
| `Custo Estimado de Perda (Realizado)` | "R$"#,0;-"R$"#,0;"R$"#,0 |
| `Custo Estimado de Perda (Projetado)` | "R$"#,0;-"R$"#,0;"R$"#,0 |
| `Investimento Necessário em Retenção` | "R$"#,0;-"R$"#,0;"R$"#,0 |
| `Custo Médio de Reposição por Colaborador em Risco` | "R$"#,0;-"R$"#,0;"R$"#,0 |
| `Saídas Evitadas Esperadas` | #,0 |
| `Economia Esperada com Retenção` | "R$"#,0;-"R$"#,0;"R$"#,0 |
| `ROI Potencial de Retenção` | 0.00 |

```dax
Fator de Ajuste do Custo de Reposição =
    SELECTEDVALUE ( 'Cost Adjustment'[Cost Adjustment], 1 )

Taxa de Sucesso da Ação de Retenção =
    SELECTEDVALUE ( 'Retention Success'[Retention Success], 0.35 )

Custo Estimado de Perda (Realizado) =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[saiu_da_empresa] = 1 ), fRotatividadeColaboradores[custo_reposicao_simulado_brl] ) * [Fator de Ajuste do Custo de Reposição]

Custo Estimado de Perda (Projetado) =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[flag_risco_iminente] = 1 ), fRotatividadeColaboradores[custo_reposicao_simulado_brl] ) * [Fator de Ajuste do Custo de Reposição]

Investimento Necessário em Retenção =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[flag_risco_iminente] = 1 ), fRotatividadeColaboradores[custo_acao_retencao_simulado_brl] )

Custo Médio de Reposição por Colaborador em Risco =
    DIVIDE ( [Custo Estimado de Perda (Projetado)], [Total em Risco (Preditivo)], 0 )

Saídas Evitadas Esperadas =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[flag_risco_iminente] = 1 ), fRotatividadeColaboradores[probabilidade_saida] ) * [Taxa de Sucesso da Ação de Retenção]

Economia Esperada com Retenção =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[flag_risco_iminente] = 1 ), fRotatividadeColaboradores[custo_reposicao_simulado_brl] * fRotatividadeColaboradores[probabilidade_saida] ) * [Taxa de Sucesso da Ação de Retenção] * [Fator de Ajuste do Custo de Reposição]

ROI Potencial de Retenção =
    DIVIDE ( [Economia Esperada com Retenção] - [Investimento Necessário em Retenção], [Investimento Necessário em Retenção], 0 )

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


## 03. Risco Crítico

| Medida | Formato |
|---|---|
| `Risco Crítico Alto Desempenho (Qtd)` | #,0 |
| `Risco Crítico Alto Desempenho (%)` | 0.0% |
| `Custo de Perda de Alto Desempenho em Risco` | "R$"#,0;-"R$"#,0;"R$"#,0 |

```dax
Risco Crítico Alto Desempenho (Qtd) =
    CALCULATE ( COUNTROWS ( fRotatividadeColaboradores ), fRotatividadeColaboradores[quadrante_risco] = "Q1 - Risco Crítico / Alto Desempenho" )

Risco Crítico Alto Desempenho (%) =
    DIVIDE ( [Risco Crítico Alto Desempenho (Qtd)], [Total de Colaboradores], 0 )

Custo de Perda de Alto Desempenho em Risco =
    SUMX ( FILTER ( fRotatividadeColaboradores, fRotatividadeColaboradores[quadrante_risco] = "Q1 - Risco Crítico / Alto Desempenho" ), fRotatividadeColaboradores[custo_reposicao_simulado_brl] ) * [Fator de Ajuste do Custo de Reposição]

```

## 04. Segmentação

| Medida | Formato |
|---|---|
| `Satisfação Média` | 0.0% |
| `Avaliação Média` | 0.0% |
| `Horas Médias Mensais` | #,0 |
| `Ranking Departamento por Rotatividade` | 0 |
| `Colaboradores em Zona de Projeto Extremo` | #,0 |

```dax
Satisfação Média =
    AVERAGE ( fRotatividadeColaboradores[nivel_satisfacao] )

Avaliação Média =
    AVERAGE ( fRotatividadeColaboradores[ultima_avaliacao] )

Horas Médias Mensais =
    AVERAGE ( fRotatividadeColaboradores[horas_mensais_medias] )

Ranking Departamento por Rotatividade =
    RANKX ( ALL ( dDepartamento[nome_departamento] ), CALCULATE ( [Taxa Real de Rotatividade] ),, DESC )

Colaboradores em Zona de Projeto Extremo =
    CALCULATE ( COUNTROWS ( fRotatividadeColaboradores ), fRotatividadeColaboradores[flag_projeto_extremo] = 1 )

```

## 05. Explicabilidade

| Medida | Formato |
|---|---|
| `Fator Principal Mais Frequente` | — |
| `Precisão do Modelo (Informativo)` | — |

```dax
Fator Principal Mais Frequente =
    VAR T = TOPN ( 1, VALUES ( fRotatividadeColaboradores[fator_principal_shap] ), CALCULATE ( COUNTROWS ( fRotatividadeColaboradores ) ), DESC )
    RETURN CONCATENATEX ( T, fRotatividadeColaboradores[fator_principal_shap], ", " )

Precisão do Modelo (Informativo) =
    "ROC-AUC 0,994 | PR-AUC 0,989 (XGBoost, holdout 25%) — scoring out-of-fold (5 dobras)"

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
