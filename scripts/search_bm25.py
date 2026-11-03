"""Busca lexical BM25 no corpus preparado, usando apenas a biblioteca padrão."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import unicodedata


CORPUS_PATH = Path(__file__).resolve().parents[1] / "data/processed/receitas.jsonl"
K1 = 1.2
B = 0.75


def tokenize(text: str) -> list[str]:
    """Separa palavras/números, preservando acentos e normalizando maiúsculas."""
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFC", text).lower())


class BM25Index:
    def __init__(self, recipes: list[dict]):
        if not recipes:
            raise ValueError("O corpus está vazio. Execute scripts/prepare_corpus.py.")
        self.recipes = recipes
        self.frequencies = [Counter(tokenize(recipe["texto_busca"])) for recipe in recipes]
        self.lengths = [sum(frequency.values()) for frequency in self.frequencies]
        self.average_length = sum(self.lengths) / len(recipes)
        if self.average_length == 0:
            raise ValueError("O corpus não contém palavras pesquisáveis.")

        document_frequency = Counter()
        for frequency in self.frequencies:
            document_frequency.update(frequency.keys())
        # Variante de IDF positiva: termos comuns têm peso baixo, nunca negativo.
        self.idf = {
            term: math.log1p((len(recipes) - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }

    def search(self, query: str, limit: int = 5) -> list[tuple[dict, float]]:
        if limit < 1:
            raise ValueError("A quantidade de resultados deve ser maior que zero.")
        terms = list(dict.fromkeys(tokenize(query)))
        if not terms:
            raise ValueError("Digite uma consulta com pelo menos uma palavra ou número.")
        terms = [term for term in terms if term in self.idf]
        if not terms:
            return []

        results = []
        for recipe, frequency, length in zip(self.recipes, self.frequencies, self.lengths):
            score = 0.0
            length_adjustment = K1 * (1 - B + B * length / self.average_length)
            for term in terms:
                occurrences = frequency[term]
                if occurrences:
                    score += self.idf[term] * (
                        occurrences * (K1 + 1) / (occurrences + length_adjustment)
                    )
            # Não preenche o ranking com documentos sem correspondência lexical.
            if score > 0:
                results.append((recipe, score))
        results.sort(key=lambda result: (-result[1], result[0]["id"]))
        return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="Busca receitas usando BM25.")
    parser.add_argument("consulta", help='Consulta, por exemplo: "bolo de cenoura"')
    parser.add_argument("-k", type=int, default=5, help="Quantidade máxima de resultados (padrão: 5)")
    args = parser.parse_args()
    if not tokenize(args.consulta):
        parser.error("Digite uma consulta com pelo menos uma palavra ou número.")
    if args.k < 1:
        parser.error("A quantidade de resultados deve ser maior que zero.")

    try:
        with CORPUS_PATH.open(encoding="utf-8") as corpus:
            recipes = [json.loads(line) for line in corpus if line.strip()]
        results = BM25Index(recipes).search(args.consulta, args.k)
    except FileNotFoundError:
        parser.error("Corpus não encontrado. Execute python scripts/prepare_corpus.py.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(f"Não foi possível pesquisar no corpus: {error}")

    if not results:
        print("Nenhuma receita contém os termos pesquisados.")
        return
    print(f"Consulta: {args.consulta}\n")
    for position, (recipe, score) in enumerate(results, 1):
        print(f"{position}. {recipe['titulo']} | BM25: {score:.4f}")
        ingredients = recipe["ingredientes"]
        preview = "; ".join(ingredients[:3])
        print(f"   Ingredientes: {preview}{'…' if len(ingredients) > 3 else ''}")
        for url in dict.fromkeys(source["fonte_url"] for source in recipe["fontes"]):
            print(f"   Fonte: {url}")


if __name__ == "__main__":
    main()
