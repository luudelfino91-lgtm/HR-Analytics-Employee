# Benchmark Externo — Achados Adicionais Incorporados (H6 e H7)

## Metodologia

Após a entrega inicial (H1-H5), foi conduzida uma pesquisa deliberada em análises
públicas independentes desta mesma base (`HR_comma_sep.csv` / `anshika2301/hr-analytics-dataset`,
14.999 registros) — kernels, artigos e relatórios acadêmicos publicados por terceiros —
para identificar padrões relevantes que a matriz de hipóteses original não havia
capturado explicitamente.

**Regra de incorporação:** nenhum achado de terceiros foi aceito por citação. Cada um
foi re-testado do zero contra os dados desta base, com testes estatísticos formais
(qui-quadrado, KMeans + silhouette score, odds ratio). Só o que se confirmou
numericamente foi promovido a hipótese formal (H6, H7) e incorporado ao pipeline de
features/modelo/Power BI. Um achado citado por uma fonte e não confirmado (ver
"Achado avaliado e não confirmado" abaixo) foi descartado.

Fontes consultadas incluem, entre outras: análises hospedadas em RStudio Pubs, um
projeto de grupo INSEAD Data Analytics, e artigos técnicos no Medium/blogs
especializados sobre este dataset específico.

---

## H6 — Taxonomia dos Desligados (clustering não supervisionado)

**Achado de terceiros:** múltiplas análises independentes reportam que, ao plotar
`satisfaction_level` × `last_evaluation` **apenas para quem saiu** (`left=1`), emergem
visualmente 3 grupos nitidamente separados — um padrão citado com nomes variados
("Winners/Frustrated/Bad match", "Underperforming/Ambitious/Burned-out" etc.), mas
sempre com a mesma estrutura geométrica.

**Verificação nos dados:** clustering KMeans (k testado de 2 a 5, padronização via
StandardScaler) confirmou que **k=3 é o número ótimo real** (maior silhouette score,
0.795 — muito acima de k=2, k=4 ou k=5), não uma escolha arbitrária. Os 3 clusters:

| Arquétipo | % dos desligados | Satisfação média | Avaliação média | Horas/mês | Projetos | Tenure |
|---|---|---|---|---|---|---|
| Baixo Engajamento / Mau Encaixe | 46.7% | 0.41 | 0.52 | 151h | 2.2 | 3.1 anos |
| **Talento Disputado pelo Mercado** | 27.0% | 0.81 (alta) | 0.92 (excelente) | 242h | 4.5 | 5.1 anos |
| Burnout Extremo | 26.3% | 0.11 (piso) | 0.87 (excelente) | 272h | 6.1 | 4.1 anos |

**Por que isso importa para o negócio:** o cluster "Talento Disputado pelo Mercado" (27% de todos os
desligamentos) está satisfeito E bem avaliado quando sai. Qualquer estratégia de
retenção baseada em monitorar pesquisas de clima/satisfação é **estruturalmente cega**
a esse grupo — ele só é endereçável com competitividade salarial e trilha de carreira
proativa, não com "conversas de retenção" reativas disparadas por baixa satisfação.

**Incorporação:** feature `exit_archetype` — o modelo de clustering é treinado
apenas nos desligados, e depois usado para classificar **todos os colaboradores
ativos** por semelhança de perfil, permitindo ao RH visualizar hoje quantos
colaboradores ativos "parecem" com cada arquétipo de risco. Nova dimensão
`dExitArchetype` no Star Schema.

---

## H7 — Efeito Protetor de Acidente de Trabalho + Formato em U/J de `number_project`

**Achado de terceiros:** "employees with work accidents do not display higher
likelihood to leave" — e mais especificamente, o efeito é na direção oposta à intuição.
Também reportado: o risco de saída não é monotônico com o número de projetos —
tanto poucos quanto muitos projetos elevam o churn.

**Verificação nos dados:**

- `Work_accident`: churn de **7.8%** entre quem sofreu acidente vs. **26.5%** entre
  quem não sofreu. Qui-quadrado p = 9.6×10⁻⁸⁰ (associação extremamente forte,
  a mais significante estatisticamente de toda a análise). Odds ratio = 0.23 →
  a chance de sair é ~4.3x menor após um acidente de trabalho registrado.
- `number_project`: formato em J extremamente acentuado (**Cramér's V = 0.599**,
  a associação mais forte de toda a matriz de hipóteses, superando até o tenure
  de H3): 2 projetos → 65.6% de churn; 3 projetos → apenas 1.8% (ponto ótimo);
  subindo progressivamente até 7 projetos → **100% de churn** (nenhum dos 256
  colaboradores com 7 projetos permaneceu).
- Achado adicional confirmado no mesmo teste: **nenhum colaborador com ≥300
  horas/mês permaneceu na empresa** (170 de 170 saíram) — um teto absoluto de
  saída certa.

**Interpretação de negócio para o efeito do acidente:** contraintuitivo à primeira
vista, mas plausível — colaboradores com mais tempo de casa acumulam mais exposição
a acidentes de trabalho E, simultaneamente, mais vínculo/estabilidade com a empresa
(efeito de confusão por tenure, não necessariamente causal). Recomenda-se ao RH não
tratar isso como "acidentes retêm pessoas" (o que seria uma leitura perigosa), mas
como um sinal de que a variável está capturando tenure/vínculo institucional por
outra via — mantida no modelo por seu poder preditivo real, com essa ressalva
explícita.

**Incorporação:** features `is_project_extreme` (flag para 2, 6 ou 7 projetos) e
`is_hours_ceiling` (≥280h/mês). Após reincorporação, `is_project_extreme` tornou-se a
**3ª feature mais importante do modelo por SHAP** (|SHAP| médio 0,850, atrás
apenas de `satisfaction_level` com 1,143 e do índice composto `risk_score_raw`
com 0,880) — ou seja, a variável original de maior peso depois da satisfação,
confirmando ganho real de poder preditivo, não um artefato cosmético.
*(Valores conforme a atribuição SHAP out-of-fold — ver `09_auditoria.md`.)*

---

## Achado avaliado e não incorporado

Uma fonte descreveu um "perfil de colaborador valioso" (avaliação ≥0.72, tenure ≥3
anos, >4 projetos) afirmando que ele representaria "mais da metade" dos desligados.
Testado nos dados: esse perfil tem 2.503 colaboradores, churn de 57.7%, e representa
**40.5%** dos desligados totais — direcionalmente correto (é de fato um segmento de
risco relevante e substancial), mas o número exato da fonte não se confirmou
("mais da metade" → 40.5%). Por isso este achado foi tratado como **direcionalmente
válido mas não promovido a hipótese própria**: ele já está coberto, com precisão
correta, pela combinação de H6 ("Talento Disputado pelo Mercado") e H2 ("estrela infeliz").
