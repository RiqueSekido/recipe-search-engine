"""Prepara a ficha cega e os rankings da avaliação v1.0."""

import hashlib
import json
import random
import re

from prepare_semantic_index import ROOT
from search_bm25 import BM25Index
from search_semantic import SemanticIndex


def main():
    directory = ROOT / "avaliacao"
    sheet = directory / "julgamento_v1.md"
    key = directory / "rankings_v1.json"
    if sheet.exists() or key.exists():
        raise SystemExit("A avaliação já possui arquivos. Preserve a ficha e suas notas.")
    source = (directory / "consultas.md").read_text(encoding="utf-8")
    queries = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in source.splitlines() if re.match(r"^\| Q\d\d \|", line)
    ]
    if [q[0] for q in queries] != [f"Q{i:02}" for i in range(1, 25)]:
        raise ValueError("Esperadas 24 consultas de Q01 a Q24.")

    semantic = SemanticIndex()
    lexical = BM25Index(semantic.recipes)
    rng = random.Random(20261103)
    record = {"versao": "1.0", "consultas_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "semente": 20261103, "consultas": {}}
    lines = ["# Ficha de julgamento · versão 1.0", "",
             "Preencha a linha **Nota** de cada item com 2 (completo), 1 (parcial) ou 0 (irrelevante). "
             "Use o critério indicado para a consulta e registre evidência em caso de dúvida. "
             "Salve esta ficha ao terminar cada consulta.", ""]
    total = 0
    for qid, query, _, criterion in queries:
        pool = {}
        rankings = {}
        for name, index in (("bm25", lexical), ("semantica", semantic)):
            hits = index.search(query, 5)
            rankings[name] = []
            for rank, (recipe, score) in enumerate(hits, 1):
                pool[recipe["id"]] = recipe
                rankings[name].append({"posicao": rank, "id": recipe["id"], "score": score})
        ids = sorted(pool)
        rng.shuffle(ids)
        items = {f"{qid}-{i:02}": rid for i, rid in enumerate(ids, 1)}
        record["consultas"][qid] = {"consulta": query, "rankings": rankings, "itens": items}
        lines += [f"## {qid} · {query}", "", f"**Critério para nota 2** — {criterion}", ""]
        for item, rid in items.items():
            recipe = pool[rid]
            lines += [f"### {item} · {recipe['titulo']}", "", "**Ingredientes**", ""]
            lines.extend(f"- {s}" for s in recipe["ingredientes"])
            lines += ["", "**Preparo**", ""]
            lines.extend(f"{i}. {s}" for i, s in enumerate(recipe["preparo"], 1))
            lines += ["", "**Nota**: ___", "", "**Evidência**: ___", ""]
        total += len(items)
    key.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sheet.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(queries)} consultas. {total} pares para julgamento.")


if __name__ == "__main__":
    main()
