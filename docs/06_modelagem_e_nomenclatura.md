# Modelagem e Nomenclatura — Dois Modelos Power BI (EN e PT-BR)

Este projeto agora entrega **dois modelos Power BI completos e independentes**,
lado a lado, a partir da mesma base analítica:

```
powerbi_en/    Modelo em inglês — fEmployeeTurnover + 5 dimensões
powerbi_pt/    Modelo em português — fRotatividadeColaboradores + 5 dimensões
```

Cada pasta é autossuficiente: pode ser aberta como um relatório Power BI
separado (`.pbix`/`.pbip`), com seu próprio Star Schema, suas próprias
medidas DAX (docs `03_dicionario_dax.md` para EN e `07_dicionario_dax_pt.md`
para PT) e seu próprio conjunto de nomes visíveis ao usuário final. Os dois
carregam exatamente os mesmos números — só a camada de nomenclatura muda.

---

## Por que dois modelos, e não um modelo bilíngue com tradução dinâmica

O Power BI suporta tradução dinâmica de metadados (*Object Translations* /
*Perspectives* via Tabular Editor), mas essa abordagem exige Power BI
Premium/Fabric para expor o seletor de idioma ao usuário final e adiciona
complexidade de manutenção. Como o pedido foi por "um trabalho em inglês e
outro em português", optou-se pela abordagem mais simples e 100% portável
(funciona em Power BI Desktop/Pro padrão): **dois modelos fisicamente
separados**, gerados a partir do mesmo pipeline Python (`export_powerbi.py`
para EN, `export_powerbi_pt.py` para PT), garantindo que nunca divirjam nos
números — apenas na camada de rótulos.

---

## Convenções de nomenclatura adotadas (as mesmas nos dois idiomas)

| Elemento | Convenção | Exemplo EN | Exemplo PT |
|---|---|---|---|
| Tabela fato | prefixo `f` + PascalCase | `fEmployeeTurnover` | `fRotatividadeColaboradores` |
| Tabela dimensão | prefixo `d` + PascalCase | `dDepartment` | `dDepartamento` |
| Chave surrogate (FK/PK) | sufixo `_key` (EN) / `chave_` (PT), sempre **oculta** ao usuário final | `department_key` | `chave_departamento` |
| Coluna de atributo | snake_case, minúsculo | `satisfaction_level` | `nivel_satisfacao` |
| Flag booleana (0/1) | prefixo `is_`/sufixo claro (EN) · prefixo `flag_` (PT) | `is_overworked` | `flag_sobrecarregado` |
| Medida DAX | Nome de Negócio em Title Case, sem prefixo técnico | `Taxa Real de Turnover` | `Taxa Real de Rotatividade` |
| Termo técnico consagrado | mantido em inglês em ambos os idiomas | `SHAP`, `KMeans`, `XGBoost`, `AUC`, `ROC`, `churn_probability` (só como conceito em texto, nunca como nome de coluna PT) | idem |

**Regra de tradução aplicada:** nomes de tabela, coluna e valores de
categoria (departamento, faixa salarial, cluster, arquétipo, quadrante de
risco) foram 100% traduzidos no modelo PT. Termos estatísticos/técnicos que
identificam um método específico (SHAP, KMeans, AUC, ROC, XGBoost, Cramér's V,
p-valor) foram mantidos em inglês/notação internacional mesmo no modelo PT,
por serem nomenclatura técnica padrão sem tradução natural amplamente aceita —
aparecem apenas em documentação e tooltips explicativos, nunca como nome de
coluna do modelo.

---

## Boas práticas de modelagem aplicadas (válidas para os dois modelos)

1. **Chaves ocultas:** toda coluna `*_key` / `chave_*` deve ser marcada como
   **oculta** (Hide in Report View) após os relacionamentos serem criados —
   o usuário final nunca precisa vê-la, apenas usa os atributos da dimensão.
2. **Cross-filter direction único** (dimensão → fato) em todos os
   relacionamentos — evita ambiguidade e ciclos de filtro. Nenhum
   relacionamento bidirecional neste modelo.
3. **Sort by Column** aplicado nas dimensões ordinais: `dFaixaSalarial` /
   `dSalaryRange` ordenada pela chave (não alfabeticamente — "Alta" não pode
   vir antes de "Baixa" só porque começa com A); `dTempoDeCasa` /
   `dTenureBucket` ordenada pela chave sequencial de tempo, não pelo rótulo.
4. **Display Folders nas medidas:** todas as medidas DAX devem ser
   organizadas em pastas de exibição por tema (ver `03_dicionario_dax.md` /
   `07_dicionario_dax_pt.md`) — `01. Taxas`, `02. Financeiro`, `03. Segmentação`,
   `04. Explicabilidade` — para não poluir a lista de campos.
2. **Formatação nativa:** `probabilidade_saida`/`churn_probability`,
   `nivel_satisfacao`/`satisfaction_level`, `ultima_avaliacao`/`last_evaluation`
   devem ser formatadas como percentual (0-100%) direto na definição da
   coluna, não deixado para cada visual configurar individualmente.
3. **Uma tabela de medidas "vazia"** (`_Medidas` / `_Measures`), sem dados
   próprios, apenas hospedando as medidas DAX — prática recomendada para
   desacoplar lógica de negócio das tabelas de dados físicas. Criar essa
   tabela manualmente no Power BI (Inserir Dados → tabela vazia) em cada
   um dos dois modelos.
4. **Nenhuma coluna calculada nativa do Power BI**: todas as features
   (flags, índices, probabilidade, cluster, quadrante) já vêm **pré-calculadas
   pelo pipeline Python** e chegam como colunas simples no CSV — evita lógica
   duplicada/divergente entre DAX e Python, e mantém o Power BI focado em
   agregação e visualização, não em engenharia de atributos.

---

## Mapa completo de tradução de tabelas e colunas

### Tabela Fato

| Coluna EN (`powerbi_en`) | Coluna PT (`powerbi_pt`) |
|---|---|
| `employee_id` | `id_colaborador` |
| `department_key` | `chave_departamento` |
| `salary_key` | `chave_faixa_salarial` |
| `tenure_bucket_key` | `chave_tempo_casa` |
| `performance_cluster_key` | `chave_cluster_comportamental` |
| `exit_archetype_key` | `chave_arquetipo_saida` |
| `satisfaction_level` | `nivel_satisfacao` |
| `last_evaluation` | `ultima_avaliacao` |
| `number_project` | `numero_projetos` |
| `average_montly_hours` | `horas_mensais_medias` |
| `time_spend_company` | `tempo_de_casa_anos` |
| `Work_accident` | `sofreu_acidente_trabalho` |
| `left` (histórico real) | `saiu_da_empresa` |
| `promotion_last_5years` | `promovido_ultimos_5_anos` |
| `workload_intensity_idx` | `indice_intensidade_carga` |
| `is_overworked` | `flag_sobrecarregado` |
| `is_underutilized` | `flag_subutilizado` |
| `hours_per_project` | `horas_por_projeto` |
| `eval_satisfaction_gap` | `gap_avaliacao_satisfacao` |
| `is_unhappy_star` | `flag_estrela_insatisfeita` |
| `is_comfortable_underperformer` | `flag_confortavel_baixo_desempenho` |
| `is_critical_tenure_window` | `flag_janela_critica_carreira` |
| `stagnation_flag` | `flag_estagnacao_sem_promocao` |
| `risk_score_raw` | `score_risco_bruto` |
| `low_exit_barrier_flag` | `flag_baixa_barreira_saida` |
| `satisfaction_x_evaluation` | `interacao_satisfacao_avaliacao` |
| `is_project_extreme` | `flag_projeto_extremo` |
| `is_hours_ceiling` | `flag_teto_horas_criticas` |
| `churn_probability` (predito) | `probabilidade_saida` |
| `risk_band` | `faixa_de_risco` |
| `is_flight_risk` | `flag_risco_iminente` |
| `is_high_performer` | `flag_alto_desempenho` |
| `risk_quadrant` | `quadrante_risco` |
| `behavior_cluster` | `cluster_comportamental` |
| `shap_main_driver_feature` | `fator_principal_shap` |
| `shap_main_driver_value` | `valor_shap_fator_principal` |
| `shap_driver_direction` | `direcao_fator_shap` |

### Dimensões

| Tabela EN | Tabela PT | Colunas EN → PT |
|---|---|---|
| `dDepartment` | `dDepartamento` | `department_key`→`chave_departamento`; `department_name`→`nome_departamento` |
| `dSalaryRange` | `dFaixaSalarial` | `salary_key`→`chave_faixa_salarial`; `salary_range`→`faixa_salarial`; `salary_rank`→`ordem_faixa_salarial` |
| `dTenureBucket` | `dTempoDeCasa` | `tenure_bucket_key`→`chave_tempo_casa`; `tenure_bucket_label`→`faixa_tempo_casa` |
| `dPerformanceCluster` | `dClusterComportamental` | `performance_cluster_key`→`chave_cluster_comportamental`; `cluster_name`→`nome_cluster` |
| `dExitArchetype` | `dArquetipoSaida` | `exit_archetype_key`→`chave_arquetipo_saida`; `archetype_name`→`nome_arquetipo` |

### Valores de categoria traduzidos

| Campo | Valor EN | Valor PT |
|---|---|---|
| Departamento | sales / technical / support / IT / product_mng / marketing / RandD / accounting / hr / management | Vendas / Técnico / Suporte / TI / Gestão de Produto / Marketing / P&D / Contabilidade / RH / Diretoria |
| Faixa salarial | low / medium / high | Baixa / Média / Alta |
| Arquétipo de saída | Talento Disputado pelo Mercado | **Talento Disputado pelo Mercado** (renomeado no PT para maior clareza executiva — "aliciado" carrega conotação negativa em português; "disputado pelo mercado" é neutro e mais preciso) |

O Star Schema (relacionamentos, cardinalidade, direção de filtro) é
**idêntico** nos dois modelos — apenas os nomes mudam. Ver `02_star_schema.md`
para o diagrama, válido para ambos com a tabela de tradução acima.
