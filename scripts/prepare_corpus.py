"""Prepara a cópia local do corpus, sem dependências externas nem acesso à rede."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/receitas_wikilivros.jsonl"
OUTPUT_PATH = ROOT / "data/processed/receitas.jsonl"
REPORT_PATH = ROOT / "reports/preparacao_corpus.json"
COMMIT = "9f5ac844fea4c889d1115abe6e6f00191dfb83fd"
EXPECTED_SHA256 = "a1b7380c14ae72ac21d0cd39bb3cee0e811b77d7b6c50dc1be04f68ba4c1f158"
SOURCE_URL = (
    "https://raw.githubusercontent.com/denisevitoriano/tech_challenge_fase_04/"
    f"{COMMIT}/data/processed/receitas.jsonl"
)


def main():
    raw_bytes = RAW_PATH.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("O arquivo original difere da versão auditada. Revise a origem.")

    recipes = {}
    review = []
    original_count = 0
    for line_number, line in enumerate(raw_bytes.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        original = json.loads(line)
        original_count += 1
        # A ordem, a grafia e a separação das listas fazem parte da identidade.
        content = json.dumps(
            [original["ingredientes"], original["preparo"]],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        recipe_id = "receita_" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        if recipe_id not in recipes:
            recipes[recipe_id] = {
                "id": recipe_id,
                "titulo": original["titulo"],
                "categoria": original["categoria"],
                "ingredientes": original["ingredientes"],
                "preparo": original["preparo"],
                "titulos_alternativos": [],
                "fontes": [],
            }
        recipe = recipes[recipe_id]
        if original["titulo"] != recipe["titulo"]:
            if original["titulo"] not in recipe["titulos_alternativos"]:
                recipe["titulos_alternativos"].append(original["titulo"])
        recipe["fontes"].append({
            "linha_original": line_number,
            "titulo": original["titulo"],
            "categoria": original["categoria"],
            "fonte_titulo": original["fonte_titulo"],
            "fonte_url": original["fonte_url"],
        })

        text = "\n".join([original["titulo"], *original["ingredientes"], *original["preparo"]])
        if re.search(r"\[\[|\]\]|\{\{|\}\}|<[^>]+>|&[a-zA-Z]+;|={2,}", text):
            review.append({
                "id": recipe_id,
                "linha_original": line_number,
                "titulo": original["titulo"],
                "motivo": "Possível resíduo de marcação; revisar separação das subseções.",
            })
        if line_number == 2367:
            review.append({
                "id": recipe_id,
                "linha_original": line_number,
                "titulo": original["titulo"],
                "motivo": "Caso observado na auditoria: preparo contém apenas uma observação.",
            })

    for recipe in recipes.values():
        recipe["texto_busca"] = "\n".join([
            recipe["titulo"],
            *recipe["titulos_alternativos"],
            *recipe["ingredientes"],
            *recipe["preparo"],
        ])

    report = {
        "origem": {
            "url": SOURCE_URL,
            "commit": COMMIT,
            "sha256": digest,
            "licenca_declarada_no_readme_da_origem": "CC BY-SA 3.0",
        },
        "registros_originais": original_count,
        "documentos_preparados": len(recipes),
        "registros_consolidados": original_count - len(recipes),
        "criterio_duplicata": "Ingredientes e preparo exatamente iguais, incluindo ordem e maiúsculas.",
        "grupos_consolidados": [
            {"id": recipe["id"], "fontes": recipe["fontes"]}
            for recipe in recipes.values() if len(recipe["fontes"]) > 1
        ],
        "revisao_pendente": review,
        "limite_da_revisao": "Não é revisão manual completa nem detecção de todas as receitas quase iguais.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        "".join(json.dumps(recipe, ensure_ascii=False) + "\n" for recipe in recipes.values()),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{original_count} registros -> {len(recipes)} documentos; {len(review)} casos para revisão.")


if __name__ == "__main__":
    main()
