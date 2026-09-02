# Matriz de Hipóteses — HR Analytics Turnover

Base: 14.999 colaboradores · Alvo `left` (taxa base de churn = 23.81%)
Todos os números abaixo vêm de `output/hypothesis_test_results.json`, gerado por `scripts/hypotheses.py`.

> **Nota:** H1-H5 compõem a matriz original. H6 e H7 foram adicionadas após um
> benchmark deliberado contra análises públicas independentes desta mesma base —
> cada achado de terceiros foi re-testado do zero nos dados antes de ser incorporado.
> Ver `docs/05_benchmark_externo.md` para a metodologia completa e o que foi
> descartado por não se confirmar.

---

## H1 — Sobrecarga (burnout) vs. Subutilização (ociosidade)

**Pergunta:** o churn é puxado por excesso de carga ou por desengajamento em quem trabalha pouco?

**Testes:** Mann-Whitney U (distribuições não-normais) em `average_montly_hours` e `number_project`; segmentação por faixas de horas para localizar pontos de inflexão.

- Horas mensais: p = 1.28e-08 (diferença significativa entre quem sai e quem fica), Cohen's d = 0.168 (efeito pequeno em magnitude agregada — mas isso esconde bimodalidade).
- Projetos: p = 0.017, d = 0.056.
- Taxa de churn por faixa de horas mostra dois picos: **(130-160h] com churn de 37-39%** e **(260-320h] com churn de 43.1%**, com um "vale" de baixíssimo risco em (160-230h] (2.6% a 9.4%).
- Entre quem sai: 28.6% tem perfil de baixa carga (subutilizado) e 21.8% tem perfil de sobrecarga extrema (burnout); os 49.7% restantes saem em faixas intermediárias por outros motivos (ex.: descompasso avaliação/satisfação — ver H2).

**Veredito:** hipótese confirmada como **bimodal, não excludente**. Existem duas populações de risco distintas com o mesmo desfecho (`left=1`), mas mecanismos opostos — o que exige tratamento e ações de retenção diferentes por segmento, não uma política única de "reduzir carga".

---

## H2 — Descompasso Desempenho × Sentimento

**Pergunta:** avaliação alta (`last_evaluation`) sempre acompanha satisfação alta (`satisfaction_level`)?

**Testes:** correlação de Pearson e Spearman entre as duas variáveis; comparação de subgrupos extremos; teste t para o gap avaliação-satisfação entre quem sai e quem fica.

- Correlação Pearson r = 0.105 (praticamente nula) — **as duas métricas não andam juntas**.
- Subgrupo "estrela insatisfeita" (avaliação ≥ 0.75 e satisfação ≤ 0.25): **n = 1.271 colaboradores**, churn de **70.7%** vs. 23.8% da base — risco relativo de **2.97x**.
- Subgrupo "confortável de baixo desempenho" (avaliação ≤ 0.45 e satisfação ≥ 0.70): churn muito abaixo da média (grupo pequeno e estável).

**Veredito:** confirmada. O maior risco de perda de **talento de alta performance** está exatamente no subgrupo onde avaliação e satisfação divergem — não nos extremos "óbvios" de baixa avaliação.

---

## H3 — Janelas Críticas de Carreira

**Pergunta:** em que tempo de casa a retenção colapsa, e como promoção/salário moderam esse efeito?

**Testes:** taxa de churn por ano de casa; qui-quadrado (tenure agrupado × `left`, Cramér's V); comparação de churn dentro da janela crítica por status de promoção e faixa salarial.

| Tenure (anos) | Churn rate | N |
|---|---|---|
| 2 | 1.6% | — |
| 3 | 24.6% | — |
| 4 | 34.8% | — |
| **5** | **56.6%** (pico) | — |
| 6 | 29.1% | — |
| 7+ | 0.0% (sobrevivência) | — |

- Qui-quadrado tenure×left: p ≈ 0 · Cramér's V = 0.357 (associação **moderada-forte**).
- Dentro da janela crítica (4-6 anos), ausência de promoção e salário baixo/médio amplificam o risco; salário alto e promoção recente amortecem fortemente.

**Veredito:** confirmada. É o efeito mais forte **entre as cinco hipóteses originais** — mas não do dataset inteiro: o benchmark externo (H7) revelou depois que `number_project` tem associação ainda mais forte (Cramér's V = 0.599 vs. 0.357 do tenure). A retenção não é linear: há uma "lua de mel" (0-2 anos), um colapso agudo entre 3-6 anos (pico em 5), e um efeito de sobrevivência após 6-7 anos — quem supera a janela crítica tende a ficar.

> **Ranking de força dos efeitos (Cramér's V), verificado em auditoria:**
> `number_project` 0.599 (H7) › tenure 0.357 (H3) › salary 0.159 › `Work_accident` 0.154 (H7) › departamento 0.076 (H4).

---

## H4 — Heterogeneidade Departamental

**Pergunta:** o turnover tem dinâmica comum entre áreas, ou departamentos técnicos e comerciais respondem a fatores completamente diferentes?

**Testes:** qui-quadrado departamento×left com Cramér's V; correlação ponto-bisserial satisfação↔saída e horas↔saída, calculada separadamente por departamento.

- Qui-quadrado: p < 0.001, mas Cramér's V = **0.076 (fraco)** — muito mais fraco que o efeito de tenure (H3).
- Ranking de churn: HR (29.1%) e Accounting (26.6%) no topo; Management (14.4%) e R&D (15.4%) no piso.
- As correlações satisfação↔saída (negativas) e horas↔saída (positivas) mantêm sinal e magnitude semelhantes na maioria dos departamentos, técnicos e comerciais.

**Veredito:** **parcialmente confirmada, mas na direção oposta à hipótese de dinâmicas completamente distintas.** Departamento explica principalmente o *nível* (intensidade) do problema — não o *mecanismo*. O driver estrutural (satisfação baixa + sobrecarga/subutilização + tenure crítico) é compartilhado; áreas de RH e Contabilidade simplesmente concentram mais colaboradores nesses perfis de risco.

---

## H5 — Retenção Inelástica (quem fica apesar do alto risco)

**Pergunta:** existem perfis de alto risco estatístico que mesmo assim permanecem? O que atua como barreira de saída?

**Testes:** definição de perfil de alto risco (satisfação ≤ 0.3 combinada com sobrecarga extrema ou tenure na janela crítica); comparação da composição de quem fica vs. quem sai dentro desse grupo; qui-quadrado salário×saída dentro do subgrupo de risco.

- **1.658 colaboradores (11.1% da base)** têm esse perfil de alto risco.
- Mesmo assim, **44.0% permanecem** na empresa.
- Composição salarial dentro do grupo de risco: entre os que **ficam**, 45.3% ganham salário baixo e 10.3% salário alto; entre os que **saem**, 59.5% ganham salário baixo e apenas 1.7% salário alto (qui-quadrado p = 1.5e-16 — associação forte).
- Acidente de trabalho (`Work_accident`) também é mais comum entre quem fica (19.6%) do que entre quem sai (5.0%) — possível proxy de vínculo/estabilidade ou de menor mobilidade percebida.

**Veredito:** confirmada. Existe uma barreira de saída real, e ela é majoritariamente **econômica**: dentro do grupo de altíssimo risco declarado (baixa satisfação), salário alto reduz drasticamente a chance de saída. Isso implica que **insatisfação é necessária mas não suficiente** para prever churn — o modelo preditivo (Etapa 2) precisa capturar essa interação satisfação×salário, não tratar satisfação isoladamente.

---

## H6 — Taxonomia dos Desligados (benchmark externo, clustering)

**Pergunta:** entre quem sai, existe um único "perfil de churn" ou múltiplos arquétipos com mecanismos diferentes?

**Testes:** KMeans (k=2 a 5) em `satisfaction_level` × `last_evaluation`, padronizado, treinado apenas em `left=1`; seleção de k por silhouette score (evita assumir k=3 a priori).

- k=3 é o número ótimo real (silhouette = 0.795, muito acima de k=2/4/5).
- **Baixo Engajamento / Mau Encaixe** (46.7% dos desligados): satisfação e avaliação medianas-baixas, tenure curto (3.1 anos), poucos projetos (2.2).
- **Talento Disputado pelo Mercado** (27.0%): satisfação 0.81 e avaliação 0.92 — **ambas altas**, mesmo assim saiu. Tenure 5.1 anos, 242h/mês.
- **Burnout Extremo** (26.3%): satisfação 0.11 (piso absoluto), avaliação 0.87 (excelente), 272h/mês, 6.1 projetos.

**Veredito:** confirmada com validação estatística formal (não apenas inspeção visual). O achado mais acionável: quase 1 em cada 3 desligamentos é de gente satisfeita e bem avaliada — **invisível a qualquer sistema de alerta baseado em satisfação declarada**, exigindo resposta de competitividade externa (comp & career), não de clima organizacional.

---

## H7 — Acidente de Trabalho (efeito protetor) e Formato em U de Projetos (benchmark externo)

**Pergunta:** `Work_accident` aumenta o risco de saída (intuição ingênua) ou o efeito é outro? `number_project` tem relação linear com o churn?

**Testes:** qui-quadrado + odds ratio para `Work_accident`×`left`; qui-quadrado + Cramér's V para `number_project`×`left`; checagem de teto absoluto em `average_montly_hours`.

- `Work_accident`: churn de 7.8% (com acidente) vs. 26.5% (sem acidente). p = 9.6e-80, odds ratio = 0.23 — a associação mais significante estatisticamente de toda a análise.
- `number_project`: Cramér's V = **0.599** — a associação mais forte de toda a matriz. Formato em J: 2 projetos = 65.6% churn, 3 projetos = 1.8% (ponto ótimo), 7 projetos = 100% churn.
- ≥300h/mês: 170 de 170 colaboradores saíram — teto absoluto de saída certa.

**Veredito:** confirmada. `number_project` linear (como tratado inicialmente em H1) **subestimava** drasticamente o efeito real — a relação correta é não-linear em J, e é o driver categórico isolado mais forte do dataset. O efeito protetor de acidente é real nos dados, mas deve ser lido como proxy de vínculo/tenure institucional, não como recomendação literal de política de segurança.

---

## Síntese para a modelagem

1. Sobrecarga e subutilização precisam de **flags distintos** (não apenas uma variável contínua de "horas").
2. O gap avaliação-satisfação é um **feature de alto valor preditivo e de negócio** (retenção de alta performance).
3. Tenure deve entrar como **bucket categórico não-linear**, não apenas como contínua — o efeito não é monotônico.
4. Departamento deve entrar no modelo, mas como controle de nível, não como driver causal isolado.
5. Salário (e sua interação com risco/satisfação) é a variável de **barreira de saída** mais forte identificada — crítica para o threshold de custo-benefício das ações de retenção.
6. `exit_archetype` (H6) deve entrar como feature categórica e como dimensão própria no Power BI — é o único achado capaz de segmentar "Talento Disputado pelo Mercado" (satisfeito mas sai) de forma acionável.
7. `number_project` deve entrar tanto contínuo quanto como flag `is_project_extreme` (H7) — o efeito não-linear em J é forte demais para ser capturado só pela variável contínua.
