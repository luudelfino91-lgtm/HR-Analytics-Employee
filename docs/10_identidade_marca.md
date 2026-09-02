# VELA — Identidade de Marca e Aplicação no Power BI

Referência visual completa: `brand/vela_identity.html` (documento navegável).
Este arquivo é o resumo textual e o manual de aplicação.

---

## A marca

| Elemento | Valor |
|---|---|
| Nome | **VELA** |
| Descritor (sempre acompanha o nome) | **People Analytics** |
| Lockup completo | `VELA · People Analytics` |
| Posicionamento (EN) | *Retention intelligence, before the exit interview* |
| Posicionamento (PT) | *Inteligência de retenção que enxerga a saída antes da entrevista de desligamento* |
| Nome do produto/relatório | **Retention Intelligence** (EN) · **Inteligência de Retenção** (PT) |

### Por que VELA

1. **Bilíngue sem adaptação** — "vela" é palavra real em português e lê-se igual
   em inglês. Como o projeto tem versão EN e PT, evita manter duas marcas.
2. **Significado ligado ao produto** — vela/navegação: o dashboard dá direção,
   não apenas diagnóstico. Vela é também uma constelação de navegação.
3. **Sem colisão em HR-tech** — *Kestrel* foi descartado (colisão com
   `kestrelpro.ai`, software de gestão com módulo de RH) e *Tenura* também
   (marcas ativas em outros setores). VELA está livre nesse nicho.
4. **Formato do mercado europeu de RH** — curto, uma palavra, quatro letras,
   como Personio, Sympa, Runa, Deel, HiBob.

### Por que "People Analytics" e não "Consultoria de RH"

Esta é a decisão que mais afeta o resultado no mercado-alvo. O nome sozinho não
atrai — nenhum nome atrai (Workday, Personio e Deel também não dizem nada
isoladamente). Quem atrai é o **descritor**, e ele deve conter a palavra-chave
que o recrutador realmente busca.

- **"People Analytics"** é o nome da disciplina e da família de cargos usado em
  vagas e buscas no LinkedIn. Posiciona como **produto de dados** — que é
  exatamente o que o projeto demonstra: pipeline em Python, modelo preditivo,
  explicabilidade e dashboard.
- **"Consultoria de RH"** posiciona como serviço. No mercado tech de Dublin isso
  lê como valor percebido mais baixo, e não descreve o que foi construído.

---

## Cor

Toda a paleta foi **validada por script** (faixa de luminosidade, piso de croma,
separação para protanopia/deuteranopia/tritanopia e contraste com a superfície),
nos modos claro e escuro. Seis séries aprovadas em ambos.

| Papel | Claro | Escuro | Uso |
|---|---|---|---|
| Ink | `#0F2A3D` | `#EEF3F7` (texto) | Marca primária, títulos, mastro da logo |
| Harbour | `#2A6FB8` | `#4A90E2` | Série 1 de dados, vela mestra |
| Signal | `#E8833A` | `#C4801C` | Acento da marca, série 2, atenção |
| Teal | `#1B9E8F` | `#149C8B` | Série 3, semântica positiva (risco baixo) |
| Violet | `#7B5EA7` | `#9585D6` | Série 4 |
| Crimson | `#C43A5E` | `#CE4A66` | Severidade crítica (reservada) |
| Brass | `#B8912E` | `#A88A2C` | Série 6 |
| Paper / Mist | `#FBFBF9` / `#F2F4F6` | `#0C1720` / `#12212E` | Superfícies |
| Texto secundário | `#5A6B7A` | `#9DB0C0` | Rótulos, eixos |

Os neutros têm leve viés azul em direção ao Ink — não são cinza puro.

### Escala semântica de risco

| Faixa | Cor (claro) | Cor (escuro) |
|---|---|---|
| Baixo (0-25%) | `#1B9E8F` | `#149C8B` |
| Moderado (25-50%) | `#2A6FB8` | `#4A90E2` |
| Alto (50-75%) | `#E8833A` | `#C4801C` |
| Crítico (75-100%) | `#C43A5E` | `#CE4A66` |

Quatro matizes distintos em vez de um degradê verde→vermelho: a separação
sobrevive a daltonismo, o que um degradê não faz. A cor **nunca** carrega o
significado sozinha — sempre acompanhada do rótulo da faixa.

---

## Tipografia

| Papel | Fonte | Onde |
|---|---|---|
| Display e corpo | **Archivo** (400/500/600/700) | Documentos, apresentação, site |
| Técnica / dados | **IBM Plex Mono** (400/500) | Números, hex, rótulos de eixo, código |
| Power BI | **Segoe UI** | Nativa do Windows, próxima da Archivo em peso e largura |

No Power BI não há garantia de fontes externas, por isso o tema usa Segoe UI —
a substituição está declarada no arquivo de tema, não é acidental.

---

## Aplicação no Power BI — passo a passo

1. Abrir o `.pbix` correspondente (`powerbi_en/` ou `powerbi_pt/`).
2. **Exibição → Temas → Procurar temas** → selecionar
   `brand/VELA_Theme_EN.json` (modelo em inglês) ou
   `brand/VELA_Theme_PT.json` (modelo em português).
3. Inserir `brand/vela_logo_lockup.svg` no canto superior esquerdo das três
   abas (Inserir → Imagem), altura de 28-32 px.
4. Título de cada aba ao lado do logo, separado por uma linha vertical fina:
   - EN: `Retention Intelligence · Strategic Diagnosis` / `Behavioural Deep Dive` / `Prescriptive Cockpit`
   - PT: `Inteligência de Retenção · Diagnóstico Estratégico` / `Deep Dive Comportamental` / `Cockpit Prescritivo`
5. Nas medidas de faixa de risco, aplicar formatação condicional com as quatro
   cores da escala semântica acima (o tema já traz `good`/`neutral`/`bad`, mas a
   escala de quatro faixas precisa ser mapeada manualmente na formatação
   condicional do visual).

### O que o tema já resolve automaticamente

- 8 cores de série na ordem validada (nunca cicladas)
- Fundo de cartão branco sobre plano de página `#F2F4F6`, borda `#E4E8EC`, raio 8px
- Título de visual alinhado à esquerda, Segoe UI Semibold 12px
- Eixo de categoria sem linhas de grade; eixo de valor com grade `#EDEFF1` de 1px
- Legenda no topo à esquerda, sem título, 9px
- Cartões de KPI com número em Segoe UI Light 30px
- Cores semânticas: `good` = Teal, `bad` = Crimson, `neutral` = cinza-azulado

Qualquer visual novo já nasce dentro da identidade, sem formatação manual.

---

## Por que esta identidade funciona para o mercado irlandês

Nenhum elemento é temático da Irlanda — sem verde, sem trevo, sem referência
celta. As escolhas respondem a sinais concretos do mercado de Dublin em 2026:

| Sinal do mercado | Resposta da identidade |
|---|---|
| Portfólio pesa mais que diploma; processos com várias rodadas práticas | Marca própria e tema aplicado fazem o projeto parecer produto entregue, não exercício acadêmico |
| SQL + Python + Power BI é o stack que empregadores pedem | O projeto entrega os três; o descritor "People Analytics" os ancora numa disciplina reconhecível |
| Governança e conformidade viraram pauta de board (NIS2, DORA, GDPR) | Auditoria documentada, ressalvas explícitas e rótulo de dado simulado sinalizam maturidade de governança |
| "Job hugging" — 64% dos profissionais permanecem no emprego, apertando a oferta de talento | Retenção é o tema mais quente do RH irlandês agora; o posicionamento cai no timing certo |
| Salários em euro, faixas de €35k a €160k+ | Versão EN em EUR com benchmarks irlandeses; versão PT em BRL para o mercado brasileiro |

A linguagem visual é a do B2B europeu de dados — azul-marinho profundo, um único
acento quente, régua tipográfica precisa, muito espaço em branco. É o registro
que um recrutador de Dublin reconhece como software sério.

---

## Arquivos

```
brand/
  vela_identity.html       Documento navegável da identidade (referência visual)
  vela_logo.svg            Marca isolada (favicon, ícone)
  vela_logo_lockup.svg     Marca + wordmark + descritor (cabeçalho do dashboard)
  VELA_Theme_EN.json       Tema do Power BI — modelo em inglês
  VELA_Theme_PT.json       Tema do Power BI — modelo em português
```


---

## Variação "Night Harbour" (modo escuro do relatório Power BI)

O relatório Power BI entregue usa a variação escura da identidade — padrão em
dashboards executivos premium (referência de mercado: estilo Xperiun /
campeonatos de data viz). Tokens:

| Papel | Hex |
|---|---|
| Fundo de página | `#0D1B28` |
| Cartão | `#14293C` |
| Borda de cartão / divisórias | `#22405A` |
| Barra lateral | `#0A1622` |
| Texto primário | `#F2F7FA` |
| Texto secundário | `#9FB3C2` |
| Texto terciário / eixos | `#6E8598` |
| Acento de UI (estado ativo) | `#F2A25C` |

Paleta de séries recalibrada para o fundo escuro e **revalidada** com o
validador CVD (todos os checks PASS sobre `#14293C`):
`#3E82CC · #DE7024 · #1B9E8F · #8E71BC · #D25275 · #AD8322`.

Elementos de identidade de RH no relatório: ícones de linha (pessoas, saída,
custo, meta, medidor, tendência) gerados em `scripts/gen_icons.py` e embutidos
como recursos do relatório; sublinha de contexto metodológico sob cada KPI;
barra lateral com marca VELA e indicador de página.
