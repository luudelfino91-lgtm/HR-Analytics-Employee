# Modelagem Dimensional — Star Schema (Power BI)

> Este diagrama e estas regras de relacionamento são **idênticos** para os dois
> modelos entregues — `powerbi_en/` (inglês) e `powerbi_pt/` (português). Os
> nomes abaixo estão em inglês; use o mapa de tradução em
> `06_modelagem_e_nomenclatura.md` para a versão em português
> (`fRotatividadeColaboradores`, `dDepartamento`, `dFaixaSalarial`,
> `dTempoDeCasa`, `dClusterComportamental`, `dArquetipoSaida`).

## Visão geral

```
                    dDepartment (10 linhas)
                          |
                          | department_key
                          |
dSalaryRange (3) --- salary_key --- fEmployeeTurnover --- tenure_bucket_key --- dTenureBucket (4)
                                     |          |
                     performance_cluster_key    exit_archetype_key
                                     |          |
                       dPerformanceCluster (5)   dExitArchetype (3)
```

> `dExitArchetype` foi adicionada após o benchmark externo (H6, ver `docs/05_benchmark_externo.md`):
> os 3 arquétipos de desligamento (Baixo Engajamento/Mau Encaixe, Talento Disputado pelo Mercado, Burnout
> Extremo), identificados via clustering nos colaboradores que já saíram e aplicados a
> **toda a base** (inclusive ativos) por semelhança de perfil.

Todos os relacionamentos são **1:N** (dimensão → fato), filtro **único direcionado da dimensão para o fato** (cross-filter direction = Single), sem relacionamentos bidirecionais — evita ambiguidade e ciclos de filtro.

> **Nota sobre dimensão calendário:** o dataset é um *snapshot transversal* (não há datas de contratação/desligamento), portanto **não existe uma `dCalendar` nativa**. Se o RH tiver a data de admissão/desligamento real, ela deve ser incorporada em uma extração futura para permitir análises de tendência temporal (hoje o dashboard é uma foto do momento, não uma série temporal).

## Tabela Fato: `fEmployeeTurnover`

Arquivo: `output/fEmployeeTurnover.csv` (14.999 linhas, 1 linha = 1 colaborador).

| Coluna | Tipo | Descrição |
|---|---|---|
| `employee_id` | Int (PK) | Chave surrogate do colaborador |
| `department_key`, `salary_key`, `tenure_bucket_key`, `performance_cluster_key`, `exit_archetype_key` | Int (FK) | Chaves para as dimensões |
| `satisfaction_level`, `last_evaluation` | Decimal 0-1 | Métricas originais |
| `number_project`, `average_montly_hours`, `time_spend_company` | Int | Métricas originais |
| `Work_accident`, `left`, `promotion_last_5years` | Int (0/1) | Flags originais — `left` é o alvo real (histórico) |
| `workload_intensity_idx` | Decimal | Índice composto de intensidade de carga (H1) |
| `is_overworked`, `is_underutilized` | Int (0/1) | Flags de bimodalidade de carga (H1) |
| `hours_per_project` | Decimal | Eficiência aparente de alocação |
| `eval_satisfaction_gap` | Decimal | `last_evaluation - satisfaction_level` (H2) |
| `is_unhappy_star`, `is_comfortable_underperformer` | Int (0/1) | Flags de descompasso (H2) |
| `is_critical_tenure_window`, `stagnation_flag` | Int (0/1) | Flags de carreira (H3) |
| `risk_score_raw` | Decimal | Score de risco heurístico (pré-ML), combinação ponderada de H1+H3 |
| `low_exit_barrier_flag` | Int (0/1) | Alto risco + salário baixo (H5) |
| `satisfaction_x_evaluation` | Decimal | Termo de interação nãolinear |
| `is_project_extreme` | Int (0/1) | 2, 6 ou 7 projetos — formato em J de churn (H7, benchmark externo) |
| `is_hours_ceiling` | Int (0/1) | `average_montly_hours >= 280` — zona de saída quase certa (H7) |
| **`churn_probability`** | Decimal 0-1 | **Probabilidade preditiva de saída**, saída do modelo XGBoost (Etapa 2) |
| `risk_band` | Texto | Faixa categórica da probabilidade (Baixo/Moderado/Alto/Crítico) |
| `is_flight_risk` | Int (0/1) | `churn_probability >= 0.5` |
| `is_high_performer` | Int (0/1) | `last_evaluation >= 0.70` |
| `risk_quadrant` | Texto | Cruzamento risco preditivo × valor do talento (Q1-Q4) |
| `behavior_cluster` | Texto | Cluster comportamental (Burnout / Ocioso / Estrela Insatisfeita / Confortável / Padrão) |
| **`shap_main_driver_feature`** | Texto | Feature com maior `|SHAP value|` para aquele colaborador |
| `shap_main_driver_value` | Decimal | Valor SHAP do driver principal (sinal = direção do efeito) |
| `shap_driver_direction` | Texto | "Aumenta risco de saída" / "Reduz risco de saída" |

## Dimensões

**`dDepartment`** (`output/dDepartment.csv`): `department_key` (PK), `department_name`.

**`dSalaryRange`** (`output/dSalaryRange.csv`): `salary_key` (PK), `salary_range` (Low/Medium/High), `salary_rank` (0/1/2 — ordenação correta no Power BI via *Sort by Column*).

**`dTenureBucket`** (`output/dTenureBucket.csv`): `tenure_bucket_key` (PK), `tenure_bucket_label` (0-2 anos / 3 anos / 4-6 anos crítico / 7+ veterano). Ordenar por chave, não alfabeticamente.

**`dPerformanceCluster`** (`output/dPerformanceCluster.csv`): `performance_cluster_key` (PK), `cluster_name` (os 5 clusters comportamentais de H1/H2, baseados em carga de trabalho).

**`dExitArchetype`** (`output/dExitArchetype.csv`): `exit_archetype_key` (PK), `archetype_name` (os 3 arquétipos de H6: Baixo Engajamento/Mau Encaixe, Talento Disputado pelo Mercado, Burnout Extremo — baseados em satisfação × avaliação, treinados nos desligados e aplicados a toda a base).

## Passos de ingestão no Power BI

1. Power Query → Obter Dados → Pasta/CSV → importar os 6 arquivos de `output/` (fato + 5 dimensões).
2. Marcar `fEmployeeTurnover` como **Tabela Fato** (Model View → Mark as Date Table não se aplica aqui, mas use "Manage Relationships").
3. Criar relacionamentos 1:N conforme diagrama acima, cardinalidade "Um para Muitos", filtro único sentido dimensão→fato.
4. Ocultar as colunas de chave (`*_key`) da visualização de campos após o relacionamento estar criado.
5. Aplicar *Sort by Column*: `salary_range` por `salary_rank`; `tenure_bucket_label` por `tenure_bucket_key`.
6. Formatar `churn_probability` como percentual; `satisfaction_level`/`last_evaluation` como percentual (0-100%).
