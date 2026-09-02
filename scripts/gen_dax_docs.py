"""
Gera a seção de medidas dos dicionários DAX a partir da MESMA fonte usada para
construir os modelos (`build_pbip.measures_for`). Assim documentação e modelo
não podem divergir — se uma medida mudar no build, a doc muda junto.

Escreve:
  docs/03_dicionario_dax.md   (modelo EN)
  docs/07_dicionario_dax_pt.md (modelo PT)
"""
from pathlib import Path

from build_pbip import config_en, config_pt, measures_for, FOLDERS

ROOT = Path(__file__).resolve().parent.parent

HEADER = {
"EN": """# Dicionário de Medidas DAX — Modelo em Inglês (`powerbi_en/`)

> **Gerado automaticamente** por `scripts/gen_dax_docs.py` a partir de
> `scripts/build_pbip.py` — a mesma fonte que constrói o modelo. Editar este
> arquivo à mão faz a doc divergir do modelo; edite o build e rode o gerador.

> Este é o modelo em **inglês** (medidas, colunas e categorias em inglês, valores
> em EUR com benchmarks irlandeses). O equivalente em português está em
> `07_dicionario_dax_pt.md`. Ver `06_modelagem_e_nomenclatura.md` para o mapa de
> tradução e `10_identidade_marca.md` para a aplicação da marca.

Tabela fato: **`fEmployeeTurnover`** · Tabela de medidas: **`_Measures`**
Parâmetros what-if: **`Cost Adjustment`** (0,5 a 2,0; padrão 1,0) e
**`Retention Success`** (0 a 1; padrão 0,35) — criados como tabelas calculadas
com `GENERATESERIES`, já incluídas no modelo.
""",
"PT": """# Dicionário de Medidas DAX — Modelo em Português (`powerbi_pt/`)

> **Gerado automaticamente** por `scripts/gen_dax_docs.py` a partir de
> `scripts/build_pbip.py` — a mesma fonte que constrói o modelo. Editar este
> arquivo à mão faz a doc divergir do modelo; edite o build e rode o gerador.

> Este é o modelo em **português** (medidas, colunas e categorias traduzidas,
> valores em BRL com benchmarks brasileiros). O equivalente em inglês está em
> `03_dicionario_dax.md`. Os valores calculados são os mesmos — muda a
> nomenclatura e a âncora salarial.

Tabela fato: **`fRotatividadeColaboradores`** · Tabela de medidas: **`_Medidas`**
Parâmetros what-if: **`Cost Adjustment`** (0,5 a 2,0; padrão 1,0) e
**`Retention Success`** (0 a 1; padrão 0,35) — criados como tabelas calculadas
com `GENERATESERIES`, já incluídas no modelo.
""",
}

NOTES = {
"g2": """
> **Nota metodológica (revisada em auditoria).** As saídas evitadas e a economia
> esperada usam a formulação de **valor esperado**: cada colaborador em risco
> contribui com o seu custo de reposição *ponderado pela sua própria
> probabilidade de saída*, não como uma saída certa. Isso corrige duas
> fragilidades da versão anterior (baseada em `TOPN`): contar cada sinalizado
> como uma saída inteira **superestimava** o benefício — estar em risco não é
> sair; e o `TOPN` do DAX devolve **todas** as linhas empatadas no corte, e há
> ~1,7 mil probabilidades repetidas na base, o que poderia inflar a economia
> silenciosamente. A versão atual é estatisticamente correta e imune a empates.
>
> Os custos por colaborador (`*_replacement_cost_*` / `custo_reposicao_*`) são
> **simulados** — ver `08_simulacao_financeira.md`.
""",
"g5": """
> `Most Frequent Main Driver` / `Fator Principal Mais Frequente` isola a tabela
> numa `VAR` e materializa o texto com `CONCATENATEX`. Envolver `TOPN` em
> `CALCULATE` — como estava antes da auditoria — gera erro no Power BI, porque
> `CALCULATE` não pode devolver uma tabela.
""",
}


def render(cfg) -> str:
    k = cfg["key"]
    parts = [HEADER[k], "\n---\n"]
    by_folder = {}
    for m in measures_for(cfg):
        by_folder.setdefault(m["folder"], []).append(m)

    order = [FOLDERS[g][k] for g in ["g1", "g2", "g3", "g4", "g5"]]
    key_of = {FOLDERS[g][k]: g for g in FOLDERS}

    for folder in order:
        ms = by_folder.get(folder, [])
        if not ms:
            continue
        parts.append(f"\n## {folder}\n")
        parts.append("| Medida | Formato |\n|---|---|")
        for m in ms:
            parts.append(f"| `{m['name']}` | {m.get('format') or '—'} |")
        parts.append("\n```dax")
        for m in ms:
            parts.append(f"{m['name']} =")
            parts.append("\n".join("    " + ln for ln in m["expr"].split("\n")))
            parts.append("")
        parts.append("```")
        note = NOTES.get(key_of[folder])
        if note:
            parts.append(note)
    parts.append("""
---

## Onde as medidas já estão aplicadas

Estas medidas **já estão criadas** no projeto Power BI correspondente em
`pbip/`, com as pastas de exibição acima e a formatação indicada. Não é preciso
colar nada à mão — o dicionário serve como referência e para revisão.
""")
    return "\n".join(parts)


if __name__ == "__main__":
    for cfg, out in [(config_en(), "docs/03_dicionario_dax.md"),
                     (config_pt(), "docs/07_dicionario_dax_pt.md")]:
        p = ROOT / out
        p.write_text(render(cfg), encoding="utf-8")
        n = len(measures_for(cfg))
        print(f"  {out}: {n} medidas documentadas")
