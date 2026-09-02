# Relatório de Auditoria Técnica

Auditoria completa executada sobre todo o projeto antes da liberação para uso
comercial. Objetivo: garantir que nenhum número apresentado possa ser
derrubado sob escrutínio técnico.

**Resultado: 4 problemas encontrados e corrigidos. Todos os demais números
foram verificados e conferem exatamente.**

---

## Problemas encontrados e corrigidos

### 1. CRÍTICO — `churn_probability` era in-sample (vazamento de dados)

**O que estava errado.** O modelo que gerava a probabilidade de saída de cada
colaborador era treinado no dataset **completo** e depois usado para pontuar
esses mesmos 14.999 colaboradores. Ou seja: cada pessoa era pontuada por um
modelo que já tinha visto o próprio rótulo dela.

**Como isso aparecia.** O AUC aparente da coluna gravada era **0,9992**,
contra 0,9938 medido em holdout — inflado. Pior: a "Taxa Preditiva de Risco"
dava 23,77% contra uma "Taxa Real" de 23,81%, uma diferença de apenas 6
pessoas em 14.999. Numa apresentação comercial, um interlocutor técnico
perguntaria — com razão — se o modelo não estava apenas decorando os rótulos.

**Correção.** A `churn_probability` e os valores SHAP por colaborador passaram
a ser gerados **out-of-fold**, via `StratifiedKFold` de 5 dobras: cada
colaborador é pontuado por um modelo treinado sem a sua própria linha
(`modeling.py`, função `run_shap`). O AUC out-of-fold resultante é **0,9945**,
praticamente idêntico ao holdout de 0,9938 — como deve ser. Os números agora
são honestos e defensáveis.

### 2. CRÍTICO — bug de pipeline: a tabela fato não estava sendo regenerada

**O que estava errado.** Quando o projeto foi reorganizado em duas pastas
(`powerbi_en/` e `powerbi_pt/`), o script `export_powerbi.py` continuou
gravando o Star Schema em `output/`. Os arquivos que o Power BI efetivamente
lê (`powerbi_en/`) tinham sido copiados manualmente uma única vez e **nunca
mais eram atualizados** por novas execuções do pipeline.

**Consequência.** Qualquer correção no modelo (inclusive a do item 1) não
chegava aos arquivos de entrega. A auditoria detectou isso porque, mesmo após
implementar o out-of-fold, a tabela fato continuava exibindo o AUC antigo de
0,9992.

**Correção.** `export_powerbi.py` passou a gravar diretamente em
`powerbi_en/`, e `run_all.py` foi reescrito para orquestrar as quatro etapas
na ordem correta de dependência (hipóteses → modelo/SHAP/Star Schema EN →
tradução PT → simulação financeira). Rodar `python run_all.py` agora reproduz
o projeto inteiro de forma determinística, sem passos manuais.

### 3. Vazamento de alvo em `exit_archetype` como preditor

**O que estava errado.** O atributo `exit_archetype` (H6) vem de um KMeans
ajustado **apenas sobre quem já saiu** (`left == 1`) — portanto carrega
informação do alvo. Usá-lo como variável preditora do próprio alvo é
vazamento.

**Correção.** Removido do conjunto de features do modelo. Permanece na tabela
fato e como dimensão no Power BI, onde seu papel é **descritivo/segmentação**
(que é legítimo e é onde está seu valor de negócio). O impacto na performance
foi nulo — o atributo sequer aparecia entre as 20 variáveis mais relevantes
por SHAP.

### 4. Afirmação factualmente incorreta na documentação

**O que estava errado.** `docs/01_matriz_hipoteses.md` afirmava que a janela
crítica de carreira (H3) era "o efeito isolado mais forte do dataset". Falso:
`number_project` (H7) tem Cramér's V de **0,599** contra **0,357** do tenure.

**Correção.** Texto ajustado para "o efeito mais forte entre as cinco
hipóteses originais", com o ranking completo verificado adicionado ao
documento.

### 5. Fragilidade na medida DAX de economia de retenção

**O que estava errado.** A medida `Economia Esperada com Retenção` usava
`TOPN` sobre os colaboradores de maior probabilidade. Dois problemas:
(a) tratava cada colaborador sinalizado como uma saída certa, superestimando
o benefício — estar em risco não é sair; (b) `TOPN` em DAX retorna **todas**
as linhas empatadas no ponto de corte, e existem ~1,7 mil valores de
`churn_probability` repetidos na base, o que poderia inflar a economia
silenciosamente conforme o parâmetro escolhido.

**Correção.** Substituída pela formulação de **valor esperado**: cada
colaborador contribui com o seu custo de reposição ponderado pela sua própria
probabilidade de saída. Estatisticamente correta, imune a empates, e mais
fácil de defender. Aplicada nas duas versões do dicionário DAX.

---

## Verificações que passaram sem ressalva

| Verificação | Resultado |
|---|---|
| Linhas nas tabelas fato (EN e PT) | 14.999 em ambas |
| Chaves `employee_id`/`id_colaborador` únicas e idênticas entre EN e PT | OK |
| Valores nulos | 0 em ambos os modelos |
| Colunas duplicadas (`_x`/`_y` de merge) | nenhuma |
| Alinhamento linha a linha com o dataset original (6 colunas-chave) | OK |
| Paridade numérica EN ↔ PT (6 colunas críticas, incluindo financeiras) | OK |
| Integridade referencial: chaves órfãs nas 5 dimensões (EN e PT) | 0 órfãs |
| `is_flight_risk` == (`churn_probability` ≥ 0,5) | OK |
| `is_high_performer` == (`last_evaluation` ≥ 0,70) | OK |
| Q1 + Q2 == total em risco; Alto + Crítico == total em risco | OK (3.539) |
| `risk_band` soma 14.999 | OK |
| Fórmula salário anual = mensal × 13,33 (13º + 1/3 férias) | OK |
| Fórmula custo reposição = salário anual × % | OK |
| Fórmula custo retenção = salário anual × 12% | OK |
| % de reposição dentro do benchmark SHRM (50%–213%) | OK (mín. 0,55 · máx. 1,80) |
| % de reposição segue exatamente a regra documentada por faixa | OK |
| Ordenação salarial High > Medium > Low em todos os 10 departamentos | OK (0 quebras) |
| H2: n = 1.271 · churn 70,7% · risco relativo 2,97x · Pearson r = 0,105 | Confere |
| H5: n = 1.658 (11,1% da base) · retenção 44,0% | Confere |
| H6: clusters 46,7% / 27,0% / 26,3% · soma 3.571 | Confere |
| H7: 3 projetos = 1,8% · 7 projetos = 100% · acidente 7,8% vs 26,5% | Confere |
| H1: cluster burnout — 98,1% com satisfação ≤ 0,2 e avaliação ≥ 0,75 | Confere |

---

## Números oficiais após a correção

Estes são os valores válidos para a apresentação. Qualquer material anterior
a esta auditoria deve ser descartado.

### Modelo preditivo

| Métrica | Valor |
|---|---|
| ROC-AUC (holdout 25%) | 0,9938 |
| PR-AUC (holdout 25%) | 0,9889 |
| ROC-AUC (out-of-fold, 5 dobras) | **0,9945** |
| PR-AUC (out-of-fold, 5 dobras) | **0,9895** |
| Baseline Regressão Logística (ROC-AUC / PR-AUC) | 0,9493 / 0,8065 |

### Segmentação de risco

| Indicador | Valor |
|---|---|
| Saídas reais na base | 3.571 (23,81%) |
| Colaboradores em risco (preditivo, ≥ 50%) | 3.539 (23,59%) |
| Q1 — Risco Crítico / Alto Desempenho | 1.890 (12,6%) |
| Faixa de risco Crítica (75-100%) | 3.404 (22,7%) |

### Impacto financeiro (valores simulados em BRL)

| Indicador | Valor |
|---|---|
| Custo das saídas já realizadas | R$ 261.385.878 |
| Custo médio por saída | R$ 73.197 |
| Custo projetado do risco atual | R$ 258.970.519 |
| Investimento necessário em retenção | R$ 34.953.612 |
| Saídas evitadas esperadas (valor esperado, 35% de sucesso) | 1.207 |
| Economia esperada | R$ 88.190.302 |
| **ROI potencial de retenção** | **1,52x** |

### Top 5 fatores por SHAP (out-of-fold)

| # | Fator | \|SHAP\| médio |
|---|---|---|
| 1 | `satisfaction_level` | 1,143 |
| 2 | `risk_score_raw` (índice composto) | 0,880 |
| 3 | `is_project_extreme` (H7) | 0,850 |
| 4 | `time_spend_company` | 0,467 |
| 5 | `satisfaction_x_evaluation` | 0,416 |

---

## Ressalvas honestas que devem acompanhar a apresentação

Estas não são erros — são limitações inerentes ao dataset, e declará-las
proativamente fortalece a credibilidade da entrega:

1. **Os valores em reais são simulados.** A base original não contém nenhum
   dado monetário. A metodologia é ancorada em benchmark de mercado e está
   documentada em `08_simulacao_financeira.md`, mas não são valores reais de
   folha de pagamento.
2. **O dataset é uma foto estática, não uma série temporal.** Não há datas de
   admissão ou desligamento, então não é possível medir tendência de turnover
   ao longo do tempo nem fazer análise de sobrevivência. Por isso o modelo
   dimensional não tem tabela calendário.
3. **Não há distinção entre saída voluntária e involuntária.** O alvo `left`
   agrega demissões e pedidos de desligamento, que têm causas e ações de
   mitigação diferentes.
4. **AUC de 0,99 é excepcionalmente alto para People Analytics real.** Isso
   reflete a natureza deste dataset público (amplamente reconhecido como
   parcialmente sintético, com padrões muito nítidos — por exemplo, 100% dos
   colaboradores com 7 projetos saíram). Em dados reais de RH, um AUC entre
   0,75 e 0,85 já seria um bom resultado. Vale apresentar o número, mas
   contextualizando que a base favorece a separabilidade.
5. **O efeito protetor de acidente de trabalho não é causal.** É muito
   provavelmente um proxy de vínculo e tempo de casa. Não deve ser lido como
   recomendação de política de segurança.
