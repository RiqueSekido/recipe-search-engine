"""Pesquisa receitas por similaridade de cosseno, usando modelo e índice locais."""

import argparse
import json

from prepare_semantic_index import (
    INDEX_PATH, INDEX_VERSION, MAX_TOKENS, MODEL_ID, MODEL_REVISION,
    load_model, read_corpus,
)


def search(query: str, limit: int = 5) -> list[tuple[dict, float]]:
    if not any(character.isalnum() for character in query):
        raise ValueError("Digite uma consulta com pelo menos uma palavra ou número.")
    if limit < 1:
        raise ValueError("A quantidade de resultados deve ser maior que zero.")
    if not INDEX_PATH.is_file():
        raise ValueError("Índice não encontrado. Execute scripts/prepare_semantic_index.py.")
    import numpy as np

    recipes, corpus_hash = read_corpus()
    with np.load(INDEX_PATH, allow_pickle=False) as saved:
        embeddings = saved["embeddings"]
        ids = saved["ids"].tolist()
        metadata = json.loads(saved["metadata"].item())
    if (
        metadata["index_version"] != INDEX_VERSION
        or metadata["model_id"] != MODEL_ID
        or metadata["model_revision"] != MODEL_REVISION
        or metadata["corpus_sha256"] != corpus_hash
        or ids != [recipe["id"] for recipe in recipes]
    ):
        raise ValueError("Índice desatualizado. Execute scripts/prepare_semantic_index.py novamente.")
    if embeddings.shape != (len(recipes), 384) or not np.isfinite(embeddings).all():
        raise ValueError("Índice inválido. Refaça a indexação.")

    model = load_model()
    text = "query: " + query.strip()
    length = len(model.tokenizer(text, truncation=False)["input_ids"])
    if length > MAX_TOKENS:
        raise ValueError(f"Consulta com {length} tokens; reduza para até {MAX_TOKENS}, incluindo o prefixo.")
    vector = model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
    # Com vetores normalizados, produto escalar e similaridade de cosseno coincidem.
    scores = embeddings @ vector
    order = sorted(range(len(recipes)), key=lambda i: (-float(scores[i]), recipes[i]["id"]))
    return [(recipes[i], float(scores[i])) for i in order[:limit]]


def main():
    parser = argparse.ArgumentParser(description="Busca semântica de receitas em CPU, sem acesso à rede.")
    parser.add_argument("consulta", help='Consulta, por exemplo: "bolo de cenoura"')
    parser.add_argument("-k", type=int, default=5, help="Quantidade máxima de resultados (padrão: 5)")
    args = parser.parse_args()
    try:
        results = search(args.consulta, args.k)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        parser.error(str(error))
    print(f"Consulta: {args.consulta}\n")
    for position, (recipe, score) in enumerate(results, 1):
        print(f"{position}. {recipe['titulo']} | Cosseno: {score:.4f}")
        ingredients = recipe["ingredientes"]
        preview = "; ".join(ingredients[:3])
        print(f"   Ingredientes: {preview}{'…' if len(ingredients) > 3 else ''}")
        for url in dict.fromkeys(source["fonte_url"] for source in recipe["fontes"]):
            print(f"   Fonte: {url}")


if __name__ == "__main__":
    main()
