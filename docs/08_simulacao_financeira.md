# Simulação de Base Salarial e Impacto Financeiro — Metodologia

> **Localizado por mercado.** Cada modelo usa a moeda e os parâmetros do seu
> mercado-alvo, a partir da mesma metodologia:
>
> | Modelo | Moeda | Âncora salarial | Pagamentos/ano | Piso |
> |---|---|---|---|---|
> | `powerbi_en/` | **EUR** | mercado irlandês 2026 | 12 | €28.700 (salário mínimo nacional em tempo integral, €14,15/h) |
> | `powerbi_pt/` | **BRL** | mercado brasileiro | 13,33 (13º + 1/3 férias) | R$ 1.900/mês |
>
> A régua de custo de turnover (% do salário anual) é **idêntica** nos dois —
> muda apenas a âncora salarial e a convenção de pagamento anual.

> ⚠️ **Aviso obrigatório:** os valores monetários descritos aqui são
> **inteiramente simulados/fictícios**, gerados pelo script
> `scripts/simulate_salary_base.py` para permitir análises de impacto
> financeiro diferenciado por colaborador. O dataset original
> (`HR_comma_sep.csv`) não contém nenhum valor monetário — só a faixa
> categórica `salary` (low/medium/high). **Não usar estes números como
> substituto de dados reais de folha de pagamento.** Toda coluna gerada por
> esta simulação leva o prefixo `simulated_` (modelo EN) ou `simulado` no
> nome (modelo PT), justamente para que nunca sejam confundidas com dado real.

## Por que simular, e por que isso é defensável

A pergunta original era se dava para atribuir impacto financeiro sem
precisar de várias rodadas de ajuste até "parecer certo". A resposta é sim,
porque a simulação não foi arbitrada às cegas — foi ancorada em **dois
pontos de referência externos, verificáveis e documentados**, e o resultado
foi validado com uma checagem de sanidade única (não houve iteração/calibração):

### 1. Nível salarial por departamento (ordenação, não os valores exatos)

A ordenação relativa entre departamentos (liderança e tecnologia no topo,
suporte/operação na base) é corroborada pelos **próprios dados originais**: no
dataset, o departamento `management` já tem 35,7% dos seus colaboradores na
faixa "high", contra apenas 6-9% em todos os demais. Isso ancora a ordenação,
que não foi inventada.

Os **níveis absolutos** vêm de benchmarks de cada mercado:

- **Irlanda (EUR):** faixas de mercado 2026 para analistas e tecnologia —
  entry €35–45k, mid €50–65k, experiente €70k+, arquiteto sênior €140–160k+.
  A simulação reproduz essa escala: Support na faixa média fica em €38k,
  Technical em €62k, IT em €76k e Management em €101k (chegando a €162k na
  faixa alta, dentro do intervalo de arquiteto sênior).
- **Brasil (BRL):** ordenação do mercado corporativo brasileiro, com base
  mensal (Diretoria R$ 14.000, TI R$ 9.500 … Suporte R$ 4.600 na faixa média).

Ambas as tabelas estão em `MARKETS` no script `scripts/simulate_salary_base.py`.

### 2. Custo de turnover como % do salário anual (benchmark de mercado)

O multiplicador de custo de reposição não foi um chute — é uma faixa
amplamente citada em benchmarks de RH: **50% a 213% do salário anual**,
citando a SHRM (Society for Human Resource Management) para posições
especializadas ([fonte](https://blog.bgcbrasil.com.br/custo-do-turnover)).
A régua aplicada:

| Faixa salarial | % do salário anual aplicado | Onde cai no benchmark (50%-213%) |
|---|---|---|
| Baixa (low) | 55% (+20 p.p. se alto desempenho) | Extremo inferior — cargos operacionais, reposição mais rápida/barata |
| Média (medium) | 95% (+20 p.p. se alto desempenho) | Meio da faixa — especialização intermediária |
| Alta (high) | 160% (+20 p.p. se alto desempenho, teto 200%) | Próximo ao teto do benchmark — cargos especializados/liderança |

O acréscimo de +20 pontos percentuais para colaboradores de alto desempenho
(`last_evaluation >= 0.70`) reflete a lógica de negócio documentada nesse
mesmo benchmark: perder alguém de alta performance custa mais (perda de
conhecimento institucional, barra mais alta para repor) — mesma lógica já
usada na Aba 1 do dashboard (quadrante "Risco Crítico / Alto Desempenho").

## Fórmula completa

```
salário_anual_simulado =
    salário_anual_base_do_departamento          -- tabela do mercado (EUR ou BRL)
    × multiplicador_faixa_salarial (0,68 / 1,00 / 1,60)
    × (1 + 0,018 × min(tempo_de_casa, 6))       -- bônus de senioridade, satura em 6 anos
    × ruído (~N(1,0 ; 0,06), limitado a ±20%)   -- evita "degraus" artificiais
    , com piso legal do mercado

salário_mensal_simulado = salário_anual_simulado / pagamentos_por_ano
                          -- Irlanda: 12 · Brasil: 13,33 (13º + 1/3 de férias)

% custo de reposição = tabela acima (por faixa + bônus de alto desempenho, teto 200%)

custo_reposição_simulado    = salário_anual_simulado × % custo de reposição
custo_ação_retenção_simulado = salário_anual_simulado × 12%   -- reajuste/bônus/carreira
```

A semente aleatória é fixa (`seed=42`) — rodar o script de novo produz
exatamente os mesmos números, então o resultado é 100% reprodutível.

## Resultado da checagem de sanidade (rodada única, sem calibração)

Salário **anual** simulado na faixa "medium", por departamento:

| Departamento | EUR (Irlanda) | BRL (Brasil) |
|---|---|---|
| Diretoria | €101.389 | R$ 199.171 |
| TI | €76.490 | R$ 134.533 |
| P&D | €69.732 | R$ 123.937 |
| Gestão de Produto | €67.963 | R$ 120.321 |
| Técnico | €61.583 | R$ 113.229 |
| Marketing | €54.963 | R$ 101.445 |
| Contabilidade | €52.129 | R$ 96.433 |
| Vendas | €48.905 | R$ 87.866 |
| RH | €46.710 | R$ 82.076 |
| Suporte | €38.018 | R$ 64.755 |

- Faixa geral EUR: mínimo €28.700 · mediana €46.327 · máximo €194.223 — coerente com as faixas irlandesas de mercado, sem outliers irreais.
- Faixa geral BRL: mínimo R$ 35.343 · mediana R$ 83.011 · máximo R$ 381.535.
- % de custo de reposição médio realizado: 65,7% (baixa) · 105,7% (média) · 170,4% (alta) — todos dentro do benchmark 50%-213%, nos dois mercados.
- **Custo das 3.571 saídas já ocorridas: €145,7 milhões** (média €40.806) no modelo irlandês e **R$ 261,4 milhões** (média R$ 73.197) no brasileiro.

Nenhum desses números precisou de ajuste manual após a primeira execução —
a ordenação por departamento já saiu coerente com o observado nos dados reais,
e as percentagens de custo já caíram dentro do benchmark citado.

### Números projetados (base para o ROI do dashboard)

Calculados sobre os 3.539 colaboradores sinalizados em risco pelo modelo
(probabilidade de saída ≥ 50%, **out-of-fold** — ver `09_auditoria.md`):

| Indicador | EUR (modelo EN) | BRL (modelo PT) |
|---|---|---|
| Custo projetado do risco atual | €144.400.000 | R$ 258.970.519 |
| Investimento necessário em retenção | €19.500.000 | R$ 34.953.612 |
| Saídas evitadas esperadas (valor esperado, 35% de sucesso) | 1.207 | 1.207 |
| Economia esperada | €49.200.000 | R$ 88.190.302 |
| **ROI potencial de retenção** | **1,52x** | **1,52x** |

O ROI fica em **1,52x nas duas moedas**, mas não é numericamente idêntico:
**1,518x em EUR contra 1,523x em BRL**. A razão economia/investimento é
independente da unidade monetária, então em tese deveria bater exatamente — a
diferença de 0,005 vem do **piso salarial legal de cada mercado**, que não é uma
simples conversão de escala: o piso irlandês (€28.700) atinge 1.135 colaboradores
da base, enquanto o piso brasileiro (R$ 25.327/ano) não atinge nenhum. Isso
comprime levemente a cauda inferior da distribuição no modelo em euros e desloca
a razão na terceira casa decimal. É esperado e está documentado — não é
inconsistência de cálculo.

As "saídas evitadas" e a "economia esperada" usam **valor esperado** — cada
colaborador em risco entra ponderado pela sua própria probabilidade de saída,
não como uma saída certa. Por isso 3.539 sinalizados geram 1.207 saídas
evitáveis esperadas, e não 1.239 (que seria a contagem simples × 35%). Essa
escolha é deliberada e está detalhada em `09_auditoria.md`, item 5.

## Onde isso entra no modelo

- **Tabelas fato** ganharam 5 novas colunas cada, uma linha por colaborador, prontas para `SUMX` no Power BI:
  - `powerbi_en/`: `simulated_monthly_salary_eur`, `simulated_annual_salary_eur`, `simulated_replacement_cost_pct`, `simulated_replacement_cost_eur`, `simulated_retention_action_cost_eur`
  - `powerbi_pt/`: `salario_mensal_simulado_brl`, `salario_anual_simulado_brl`, `percentual_custo_reposicao_simulado`, `custo_reposicao_simulado_brl`, `custo_acao_retencao_simulado_brl`
- **Medidas DAX** (`03_dicionario_dax.md` seção 2 / `07_dicionario_dax_pt.md` seção 02) foram reescritas para somar o custo real linha a linha (`SUMX`) em vez de multiplicar uma contagem por um valor médio fixo — o impacto financeiro agora varia de fato por departamento, faixa salarial e desempenho, em vez de tratar todo mundo como igual.
- Mantém-se **um único parâmetro what-if** (`Fator de Ajuste do Custo de Reposição`, padrão 1,0x) para o RH testar sensibilidade (ex.: "e se o custo real for 1,3x maior que a nossa estimativa?") sem precisar rodar o pipeline Python de novo.
