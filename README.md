# VELA · People Analytics — Retention Intelligence

> *Inteligência de retenção que enxerga a saída antes da entrevista de desligamento.*

Investigação analítica ponta a ponta sobre o dataset `anshika2301/hr-analytics-dataset`
(14.999 colaboradores, alvo `left`, taxa base de churn 23.81%), entregue como produto
de dados sob a marca **VELA People Analytics** — identidade calibrada para o mercado
irlandês (ver `docs/10_identidade_marca.md`).

## Estrutura

```
data/                    HR_comma_sep.csv (dataset original, 14.999 linhas)
scripts/
  hr_pipeline.py          Config, carga e sanity checks
  hypotheses.py           Testes estatísticos das 7 hipóteses (ETAPA 1 + benchmark externo)
  features.py             Engenharia de atributos, incl. arquétipos H6 e flags H7 (ETAPA 2)
  modeling.py             Baseline vs XGBoost, threshold tuning, SHAP (ETAPA 2)
  export_powerbi.py       Tabela fato + dimensões em INGLÊS -> powerbi_en/ (ETAPA 3)
  export_powerbi_pt.py    Tradução do modelo para PORTUGUÊS -> powerbi_pt/ (ETAPA 3b)
  simulate_salary_base.py Base salarial simulada (EUR p/ EN, BRL p/ PT) + custo de turnover (ETAPA 3c)
  run_all.py              Orquestrador — roda o pipeline de dados (as 4 etapas, EN e PT)
  build_pbip.py           CONSTRÓI os 2 projetos Power BI (modelo TMDL + 3 páginas de visuais)
  gen_theme.py            Tema escuro "Night Harbour" (paleta validada p/ CVD sobre fundo escuro)
  gen_icons.py            Ícones de RH (PNG) embutidos nos cartões KPI do relatório
  gen_dax_docs.py         Gera docs/03 e docs/07 a partir do mesmo código do build
docs/
  01_matriz_hipoteses.md          Matriz de hipóteses (H1-H7) com resultados estatísticos reais
  02_star_schema.md               Modelagem dimensional — Star Schema (válido para os 2 modelos)
  03_dicionario_dax.md            Medidas DAX — modelo em INGLÊS
  04_blueprint_dashboard.md       Blueprint das 3 abas do relatório
  05_benchmark_externo.md         Metodologia e achados de terceiros verificados/incorporados (H6, H7)
  06_modelagem_e_nomenclatura.md  Convenções de nomenclatura e mapa de tradução EN <-> PT
  07_dicionario_dax_pt.md         Medidas DAX — modelo em PORTUGUÊS
  08_simulacao_financeira.md      Metodologia da base salarial simulada (EUR/BRL) e do custo de turnover
  09_auditoria.md                 RELATÓRIO DE AUDITORIA — problemas corrigidos e números oficiais
  10_identidade_marca.md          Marca VELA: nome, paleta validada, tipografia e aplicação no Power BI
  11_projeto_powerbi.md           COMO ABRIR os relatórios PBIP, o que já está construído e como reconstruir
brand/
  vela_identity.html              Documento navegável da identidade visual
  vela_logo.svg / _lockup.svg     Marca em vetor (ícone e lockup completo)
  VELA_Theme_EN.json              Tema do Power BI — modelo em inglês
  VELA_Theme_PT.json              Tema do Power BI — modelo em português
output/
  storyboard.html                 Storyboard visual (1 gráfico por hipótese) — planejamento das páginas do PBI
  hypothesis_test_results.json    Resultados brutos dos testes estatísticos (H1-H7)
  model_metrics.json              Métricas comparativas dos modelos + threshold ótimo
  model_comparison_curves.png     ROC e Precision-Recall (baseline vs XGBoost)
  shap_global_importance.csv      Top 20 features por importância SHAP média
  shap_summary_plot.png           SHAP summary plot (beeswarm)
  shap_employee_level.csv         Probabilidade + driver SHAP por colaborador
powerbi_en/                       DADOS do modelo em INGLÊS — fEmployeeTurnover.csv + 5 dimensões
powerbi_pt/                       DADOS do modelo em PORTUGUÊS — fRotatividadeColaboradores.csv + 5 dimensões
pbip/
  VELA Retention Intelligence EN/  RELATÓRIO POWER BI pronto (abrir o .pbip) — inglês, EUR
  VELA Retention Intelligence PT/  RELATÓRIO POWER BI pronto (abrir o .pbip) — português, BRL
```

## Como reproduzir

```bash
pip install -r requirements.txt
cd scripts
python run_all.py        # dados: hipóteses -> modelo/SHAP -> Star Schema EN -> tradução PT -> financeiro
python gen_theme.py      # regenera os temas VELA (modo escuro)
python gen_icons.py      # regenera os ícones de RH
python build_pbip.py     # constrói os 2 projetos Power BI em pbip/
python gen_dax_docs.py   # regenera os dicionários DAX a partir do mesmo código do build
```

O pipeline é determinístico (sementes fixas) e idempotente — rodar duas vezes produz exatamente os mesmos arquivos.

## Resumo dos principais achados (ver `docs/01_matriz_hipoteses.md` para detalhe estatístico completo)

- **H1 (Sobrecarga vs Subutilização):** confirmada bimodalidade — dois clusters de risco opostos (burnout ≥250h/mês+≥6 projetos vs. ociosidade <150h/mês+≤2 projetos), não um único perfil de churn.
- **H2 (Desempenho × Sentimento):** correlação avaliação-satisfação é fraca (r=0.105). O subgrupo "estrela insatisfeita" (alta avaliação, baixa satisfação) tem churn de 70.7% (2.97x a taxa base) — maior risco de perda de talento.
- **H3 (Janelas Críticas):** efeito mais forte do dataset entre as hipóteses originais (Cramér's V=0.357). Retenção colapsa entre 3-6 anos de casa, pico de 56.6% de churn em 5 anos; após 6-7 anos, efeito de sobrevivência (churn ≈ 0%).
- **H4 (Heterogeneidade Departamental):** associação estatisticamente significativa mas fraca (Cramér's V=0.076) — departamento explica nível, não mecanismo; o driver estrutural é compartilhado entre áreas.
- **H5 (Retenção Inelástica):** 11.1% da base tem perfil de altíssimo risco e mesmo assim 44% permanece — salário alto é a barreira de saída dominante (qui-quadrado p=1.5e-16).
- **H6 (Taxonomia dos Desligados, benchmark externo):** clustering (KMeans, k=3 validado por silhouette=0.795) revela 3 arquétipos entre quem saiu — 46.7% "Baixo Engajamento/Mau Encaixe", 27.0% **"Talento Disputado pelo Mercado"** (satisfeito e bem avaliado, mesmo assim saiu — invisível a pesquisas de clima), 26.3% "Burnout Extremo".
- **H7 (Acidente de Trabalho e Formato em J de Projetos, benchmark externo):** `number_project` tem a associação mais forte de toda a análise (Cramér's V=0.599, formato em J: 3 projetos=1.8% churn, 7 projetos=100% churn). `Work_accident` reduz o risco de saída em ~4.3x (odds ratio=0.23, p=9.6e-80) — efeito real mas provável proxy de tenure/vínculo, não recomendação literal de segurança.

Ver `docs/05_benchmark_externo.md` para a metodologia de pesquisa e verificação usada para incorporar H6/H7 (incluindo um achado de terceiros testado e **descartado** por não se confirmar com a precisão citada).

## Modelo preditivo

| Modelo | ROC-AUC | PR-AUC | Threshold ótimo (custo FN=4x FP) |
|---|---|---|---|
| Logistic Regression (baseline) | 0.949 | 0.807 | 0.41 |
| **XGBoost (campeão, holdout 25%)** | **0.994** | **0.989** | 0.54 |
| XGBoost — scoring **out-of-fold** (5 dobras) | **0.994** | **0.990** | — |

A `churn_probability` gravada na tabela fato é **out-of-fold**: cada colaborador foi pontuado por um modelo treinado sem a sua própria linha, de modo que os números do dashboard são honestos e comparáveis ao holdout (ver `docs/09_auditoria.md`).

SHAP (global, out-of-fold) — top drivers: `satisfaction_level` (1,14), `risk_score_raw` (0,88), `is_project_extreme` (H7, 0,85), `time_spend_company` (0,47), `satisfaction_x_evaluation` (0,42).

## Impacto financeiro (valores simulados, localizados por mercado)

O modelo em inglês usa **euros com benchmarks irlandeses**; o modelo em português usa
**reais com benchmarks brasileiros**. Mesma metodologia e mesma régua de custo de
turnover (50%-213% do salário anual) — muda apenas a âncora salarial.

| Indicador | EUR (modelo EN) | BRL (modelo PT) |
|---|---|---|
| Custo das saídas já realizadas | €145,7 mi (€40.806 por saída) | R$ 261,4 mi (R$ 73.197 por saída) |
| Custo projetado do risco atual | €144,4 mi | R$ 259,0 mi |
| Investimento necessário em retenção | €19,5 mi | R$ 35,0 mi |
| Economia esperada (35% de sucesso) | €49,2 mi | R$ 88,2 mi |
| **ROI potencial de retenção** | **1,52x** | **1,52x** |

O ROI fica em **1,52x nas duas moedas**, mas não é numericamente idêntico
(1,518x em EUR contra 1,523x em BRL). A diferença vem do piso salarial legal de
cada mercado: o piso irlandês (€28.700, salário mínimo em tempo integral) atinge
1.135 colaboradores da base, enquanto o piso brasileiro não atinge nenhum — o que
desloca levemente a distribuição relativa de custo. Metodologia e ressalvas em
`docs/08_simulacao_financeira.md`. Os valores são **simulados** — a base original
não contém dados monetários.

## Storyboard visual (planejamento das páginas)

`output/storyboard.html` traz um gráfico por hipótese (H1-H7) + explicabilidade
do modelo, já organizado pela aba do Power BI onde cada um deve viver — é o
material de apoio para decidir o storytelling antes de montar o relatório
final. Publicado também como artifact para visualização interativa.

## Uso no Power BI — dois modelos completos

Este projeto entrega **dois modelos Power BI independentes**, com os mesmos
números e o mesmo Star Schema, apenas com nomenclatura traduzida:

- **`powerbi_en/`** — modelo em inglês (`fEmployeeTurnover` + 5 dimensões). Medidas em `docs/03_dicionario_dax.md`.
- **`powerbi_pt/`** — modelo em português (`fRotatividadeColaboradores` + 5 dimensões, colunas e categorias traduzidas). Medidas em `docs/07_dicionario_dax_pt.md`.

Para qualquer um dos dois: importe os 6 CSVs da respectiva pasta, aplique o tema
(`Exibição → Temas → Procurar temas` → `brand/VELA_Theme_EN.json` ou `_PT.json`),
siga `docs/02_star_schema.md` para os relacionamentos (idênticos nos dois modelos) e
cole as medidas do dicionário DAX correspondente. `docs/06_modelagem_e_nomenclatura.md` documenta as convenções de nomenclatura e o mapa completo de tradução EN↔PT. `docs/04_blueprint_dashboard.md` traz a blueprint das 3 abas, válida para os dois idiomas.
