# Blueprint do Dashboard — Power BI (3 abas)

## Aba 1 — Diagnóstico Estratégico (Visão Executiva / C-Level)

**Objetivo:** resposta em 10 segundos para "quão grave é o problema e quanto custa".

- **Faixa de KPIs (cards no topo):** Taxa Real de Turnover · Taxa Preditiva de Risco · Total em Risco (Preditivo) · Custo Estimado de Perda (Projetado) · ROI Potencial de Retenção.
- **Slicers de what-if:** Custo Médio de Reposição, Custo de Ação de Retenção, Taxa de Sucesso — permitem ao C-level simular cenários ao vivo.
- **Gráfico de barras horizontais:** Taxa Real de Turnover por Departamento (via `dDepartment`), ordenado desc, com linha de referência da média geral (23.8%).
- **Gráfico de rosca (donut):** distribuição da base por `risk_band` (Baixo/Moderado/Alto/Crítico).
- **Ranking (tabela compacta):** Top 5 departamentos por `Custo de Perda de Alto Desempenho em Risco`.
- **Card destacado:** `Risco Crítico Alto Desempenho (Qtd)` com ícone de alerta — a métrica mais acionável para o CHRO.
- Filtros globais na página: Departamento, Faixa Salarial, Faixa de Tenure.

## Aba 2 — Deep Dive Comportamental (Investigação & Causa-Raiz)

**Objetivo:** validar visualmente as 5 hipóteses para audiências analíticas (RH BP, People Analytics).

- **Scatter plot 3D-simulado (bubble chart):** eixo X = `average_montly_hours`, eixo Y = `last_evaluation`, tamanho da bolha = contagem, cor = `satisfaction_level` (escala sequencial) — replica visualmente o achado H1/H2 (clusters de burnout e estrela insatisfeita ficam visualmente isolados).
- **Gráfico de linha:** Taxa Real de Turnover por `time_spend_company` (1 a 10 anos) — evidencia o colapso em H3 (pico em 5 anos). Adicionar marcador/anotação manual no ponto de pico.
- **Gráfico de barras agrupadas:** churn dentro da janela crítica (4-6 anos) cruzando `promotion_last_5years` × `salary_range` — mostra o efeito amortecedor.
- **Small multiples (matriz de gráficos):** correlação satisfação↔saída por departamento, para visualizar a heterogeneidade de nível vs. mecanismo comum (H4).
- **Gráfico de dispersão:** `eval_satisfaction_gap` no eixo X, `churn_probability` no eixo Y, colorido por `behavior_cluster` — visão unificada dos 5 clusters comportamentais.
- **Segmentação de tempo de casa:** visual de árvore de decomposição (Decomposition Tree) nativo do Power BI, com `left` como métrica analisada e `satisfaction_level`, `time_spend_company`, `salary_range`, `average_montly_hours` como campos explicativos — permite navegação exploratória ad-hoc pelos analistas.
- **Gráfico de barras (H6, benchmark externo):** Turnover Real por `dExitArchetype[archetype_name]`, com anotação textual fixa explicando que "Talento Disputado pelo Mercado" está satisfeito e bem avaliado no momento da saída — a visualização que mais frequentemente surpreende stakeholders na primeira leitura.
- **Gráfico de linha em J (H7, benchmark externo):** Taxa Real de Turnover por `number_project` (2 a 7) — evidencia visualmente o formato não-linear, com anotação no ponto de mínimo (3 projetos) e no ponto de máximo (7 projetos, 100% churn).

## Aba 3 — Cockpit Prescritivo / Gestão Ativa (Operação de RH)

**Objetivo:** lista de ação para gestores e RH Business Partners — "quem eu preciso conversar esta semana".

- **Tabela/Matriz acionável (visual principal):** filtrada por padrão em `risk_band = "Crítico"`, colunas: `employee_id`, `department_name`, `salary_range`, `churn_probability` (barra de dados condicional), `shap_main_driver_feature`, `shap_driver_direction`, `risk_quadrant`. Ordenação padrão por `churn_probability` desc.
- **Explicabilidade individual simplificada:** ao selecionar uma linha (via *drillthrough* para página de detalhe do colaborador), exibir um gráfico de barras horizontais com os top 5 valores SHAP daquele colaborador especificamente (requer exportação complementar `shap_employee_level.csv` já disponível, ou tabela wide por feature se granularidade individual for necessária).
- **Matriz de quadrantes (scatter 2x2):** eixo X = `churn_probability`, eixo Y = `last_evaluation`, quadrantes rotulados conforme `risk_quadrant` (Q1 a Q4), com linhas de referência em 50% e 70% — visual de priorização direta para o RH: **Q1 é a fila de intervenção prioritária**.
- **Cards de contagem por cluster comportamental** (`behavior_cluster`) com formatação condicional por severidade, permitindo direcionar a ação certa por segmento (ex.: "Sobrecarregado" → redistribuição de carga; "Estrela Insatisfeita" → conversa de carreira/remuneração; "Subutilizado" → engajamento/novos desafios).
- **Card/slicer adicional por `dExitArchetype` (H6):** ação diferenciada por arquétipo — "Talento Disputado pelo Mercado" recebe oferta de trilha de carreira/revisão salarial proativa (não pesquisa de clima, que não captura esse grupo); "Burnout Extremo" recebe redistribuição de carga imediata; "Baixo Engajamento/Mau Encaixe" recebe conversa de expectativas/onboarding reforçado.
- **Botão de exportação (Export data)** habilitado na tabela principal, para o RH baixar a lista de ação em Excel/CSV para uso em campanhas de retenção.

## Diretrizes gerais de storytelling

1. Cores de risco padronizadas em todas as 3 abas (ex.: cinza=Baixo, amarelo=Moderado, laranja=Alto, vermelho=Crítico) — nunca reatribuir a paleta entre páginas.
2. Todas as métricas financeiras (`Custo Estimado de Perda`, `ROI Potencial`) carregam tooltip explicando a premissa (`Custo Médio de Reposição`) para não gerar desconfiança executiva sobre "de onde veio o número".
3. Página 1 = decisão em 30 segundos. Página 2 = investigação analítica. Página 3 = ação operacional. Essa progressão deve ficar explícita na navegação (ícones/breadcrumb no topo).
4. Nenhum visual usa `left` (rótulo histórico) e `churn_probability`/`is_flight_risk` (predição) na mesma métrica sem rotular claramente qual é "Real" e qual é "Preditivo" — confusão entre as duas é o erro mais comum em dashboards de turnover.
