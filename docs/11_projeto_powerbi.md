# Projeto Power BI — Construção, Estrutura e Como Abrir

Os dois relatórios foram **construídos programaticamente** e estão em `pbip/`,
no formato **PBIP** (Power BI Project) — o formato de projeto baseado em texto
que o Power BI Desktop abre nativamente.

```
pbip/
  VELA Retention Intelligence EN/     modelo em inglês · EUR · benchmarks irlandeses
  VELA Retention Intelligence PT/     modelo em português · BRL · benchmarks brasileiros
```

---

## Como abrir

1. Abra o **Power BI Desktop** (versão recente; PBIP é suportado desde 2023).
2. Se for a primeira vez com PBIP: *Arquivo → Opções → Recursos de visualização*
   e marque **"Formato de arquivo de projeto do Power BI (.pbip)"**. Reinicie.
3. *Arquivo → Abrir* → selecione
   `pbip/VELA Retention Intelligence EN/VELA Retention Intelligence EN.pbip`
   (ou a versão PT).
4. Ao abrir, o Power BI carrega os CSVs de `powerbi_en/` (ou `powerbi_pt/`) por
   caminho absoluto. Se você mover a pasta do projeto, ajuste o caminho em
   *Transformar dados → Configurações da fonte de dados*, ou regenere com
   `python scripts/build_pbip.py` após editar `DATA_ROOT_ON_DEVICE` no topo do script.
5. Clique em **Atualizar** para carregar os 14.999 registros.

> O tema visual não está embutido no relatório de propósito — uma referência de
> tema malformada pode impedir o arquivo de abrir. As cores da marca já estão
> aplicadas visual a visual. Para o acabamento completo (fundo de página,
> cabeçalhos, eixos), aplique o tema uma vez em
> *Exibição → Temas → Procurar temas* → `brand/VELA_Theme_EN.json` (ou `_PT`).

---

## O que já está construído

### Modelo semântico (validado no motor do Power BI)

| Item | Quantidade |
|---|---|
| Tabelas | 9 |
| Medidas DAX | 26 (em 5 pastas de exibição) |
| Colunas | 56 |
| Relacionamentos | 5 (todos *Muitos-para-Um*, filtro unidirecional, ativos) |
| Parâmetros what-if | 2 (`Cost Adjustment`, `Retention Success`) |

Tudo isto foi **verificado carregando o modelo no motor tabular do Power BI**
(via MCP, modo offline) e conferindo tabelas, medidas, pastas e relacionamentos
— não é só geração de texto sem validação.

Também já vêm configurados:

- **Chaves ocultas** (`*_key` / `chave_*`) — invisíveis no painel de campos.
- **Sort by column** — faixa salarial e faixa de tempo de casa ordenam pela
  chave, não alfabeticamente.
- **Formatação** — probabilidade, satisfação e avaliação como percentual;
  custos com o símbolo da moeda do modelo (€ ou R$).
- **Tipos explícitos** no Power Query, coluna a coluna (sem inferência).

### Relatório — 3 páginas, 39 visuais cada

**Página 1 · Diagnóstico Estratégico** (executivo)
5 cartões de KPI (taxa real, em risco, perda projetada, risco crítico/alto
desempenho, ROI) · turnover por departamento · custo de reposição por
departamento · distribuição por faixa de risco · distribuição por quadrante ·
segmentadores de departamento e tempo de casa.

**Página 2 · Deep Dive Comportamental** (analítico)
Linha de churn por tempo de casa (H3) · colunas de churn por número de projetos
(H7) · dispersão satisfação × avaliação colorida por saída (H2) · churn por
arquétipo de desligamento (H6) · churn por faixa salarial (H5).

**Página 3 · Cockpit Prescritivo** (operacional)
3 KPIs de retenção · 2 segmentadores what-if (fator de custo e taxa de sucesso)
· tabela acionável com colaborador, departamento, quadrante, driver SHAP,
direção e probabilidade · ranking de drivers · distribuição por cluster
comportamental.

Todas as páginas trazem a faixa de marca VELA no topo.

---

## Como foi construído (e como reconstruir)

```bash
cd scripts
python run_all.py        # dados: hipóteses -> modelo/SHAP -> star schema EN -> PT -> financeiro
python build_pbip.py     # gera os dois projetos PBIP em pbip/
python gen_dax_docs.py   # regenera docs/03 e docs/07 a partir do MESMO código do build
```

`scripts/build_pbip.py` é a fonte única: gera o TMDL do modelo, as 26 medidas,
os relacionamentos, os parâmetros what-if e o `report.json` com os visuais
posicionados. `scripts/gen_dax_docs.py` emite os dicionários DAX a partir da
mesma função `measures_for()` — por isso documentação e modelo **não podem
divergir**: se uma medida mudar no build, a doc muda junto.

---

## Localização: cada modelo é nativo no seu idioma

Não é só a nomenclatura de colunas. Nos dois modelos, **os valores das
categorias também são traduzidos**:

| Elemento | Modelo EN | Modelo PT |
|---|---|---|
| Quadrante | `Q1 - Critical Risk / High Performer` | `Q1 - Risco Crítico / Alto Desempenho` |
| Faixa de risco | `Critical (75-100%)` | `Crítico (75-100%)` |
| Cluster | `Overworked (Burnout)` | `Sobrecarregado (Burnout)` |
| Arquétipo | `Market-Poached Talent` | `Talento Disputado pelo Mercado` |
| Tempo de casa | `4-6 yrs (critical)` | `4-6 anos (crítico)` |
| Direção SHAP | `Increases exit risk` | `Aumenta risco de saída` |
| Medidas | `Actual Turnover Rate` | `Taxa Real de Rotatividade` |
| Moeda | EUR | BRL |

O modelo em inglês é a **fonte**; o português é gerado por tradução
(`export_powerbi_pt.py`), o que garante que os números sejam idênticos e só a
camada de rótulos mude.

---

## Ajustes finais sugeridos (5 minutos no Desktop)

O que a construção programática deliberadamente deixa para o acabamento manual,
por serem escolhas visuais que dependem de ver na tela:

1. **Aplicar o tema** (`brand/VELA_Theme_*.json`) — um clique.
2. **Inserir o logo** `brand/vela_logo_lockup.svg` sobre a faixa branca do topo
   de cada página (*Inserir → Imagem*), altura ~28 px, alinhado à esquerda.
3. **Formatação condicional** das quatro faixas de risco, com as cores da escala
   semântica em `10_identidade_marca.md` (teal → azul → âmbar → carmim).
4. **Ordenar** o gráfico de departamento por valor decrescente (menu do visual).
5. **Filtro padrão** da tabela do Cockpit: faixa de risco = Crítico.
