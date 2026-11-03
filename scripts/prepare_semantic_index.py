"""Baixa o modelo e prepara os vetores das receitas para busca local em CPU."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data/processed/receitas.jsonl"
MODEL_PATH = ROOT / "models/multilingual-e5-small"
INDEX_PATH = ROOT / "data/indexes/semantic.npz"
REPORT_PATH = ROOT / "reports/indice_semantico.json"
MODEL_ID = "intfloat/multilingual-e5-small"
MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
MODEL_FILES = [
    "README.md", "config.json", "model.safetensors", "modules.json",
    "1_Pooling/config.json", "sentence_bert_config.json", "sentencepiece.bpe.model",
    "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json",
]
MAX_TOKENS = 512
INDEX_VERSION = 1


def read_corpus():
    content = CORPUS_PATH.read_bytes()
    recipes = [json.loads(line) for line in content.decode("utf-8").splitlines() if line.strip()]
    if not recipes or len({recipe["id"] for recipe in recipes}) != len(recipes):
        raise ValueError("O corpus deve conter receitas com IDs únicos.")
    if any(not recipe["texto_busca"].strip() for recipe in recipes):
        raise ValueError("Há receitas sem texto de busca.")
    return recipes, hashlib.sha256(content).hexdigest()


def load_model():
    if any(not (MODEL_PATH / name).is_file() for name in MODEL_FILES):
        raise ValueError("Modelo local incompleto. Execute scripts/prepare_semantic_index.py.")
    import torch
    from sentence_transformers import SentenceTransformer

    # Limita o paralelismo para uma execução previsível em notebooks com CPU.
    torch.set_num_threads(4)
    model = SentenceTransformer(str(MODEL_PATH), device="cpu", local_files_only=True)
    model.max_seq_length = MAX_TOKENS
    return model


def main():
    parser = argparse.ArgumentParser(description="Prepara embeddings das receitas em CPU.")
    parser.add_argument("--offline", action="store_true", help="Usa somente os arquivos locais do modelo")
    parser.add_argument(
        "--permitir-truncamento", action="store_true",
        help="Autoriza cortar entradas acima de 512 tokens e registrar os casos no relatório",
    )
    args = parser.parse_args()
    try:
        recipes, corpus_hash = read_corpus()
        if not args.offline:
            from huggingface_hub import snapshot_download

            snapshot_download(
                repo_id=MODEL_ID, revision=MODEL_REVISION,
                local_dir=MODEL_PATH, allow_patterns=MODEL_FILES,
            )
        from tokenizers import Tokenizer

        tokenizer = Tokenizer.from_file(str(MODEL_PATH / "tokenizer.json"))
        tokenizer.no_truncation()
        texts = ["passage: " + recipe["texto_busca"] for recipe in recipes]
        lengths = [len(tokenizer.encode(text).ids) for text in texts]
        oversized = [
            {"id": recipe["id"], "titulo": recipe["titulo"], "tokens": length}
            for recipe, length in zip(recipes, lengths) if length > MAX_TOKENS
        ]
        print(f"{len(recipes)} receitas; {len(oversized)} excedem {MAX_TOKENS} tokens.", flush=True)
        if oversized and not args.permitir_truncamento:
            raise ValueError(
                "Indexação interrompida para evitar corte silencioso. "
                "Revise a política de textos longos antes de usar --permitir-truncamento."
            )
        import numpy as np

        model = load_model()
        embeddings = model.encode(
            texts, batch_size=16, show_progress_bar=True,
            normalize_embeddings=True, convert_to_numpy=True,
        ).astype(np.float32)
        if embeddings.shape != (len(recipes), 384) or not np.isfinite(embeddings).all():
            raise ValueError("O modelo retornou vetores inválidos.")
        metadata = {
            "index_version": INDEX_VERSION,
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "corpus_sha256": corpus_hash,
            "documents": len(recipes),
            "dimensions": embeddings.shape[1],
            "max_tokens": MAX_TOKENS,
            "document_prefix": "passage: ",
            "query_prefix": "query: ",
            "normalized": True,
            "long_text_policy": "truncate" if args.permitir_truncamento else "reject",
            "oversized_documents": oversized,
        }
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = INDEX_PATH.with_suffix(".tmp")
        with temporary.open("wb") as output:
            np.savez_compressed(
                output, embeddings=embeddings,
                ids=np.array([recipe["id"] for recipe in recipes]),
                metadata=np.array(json.dumps(metadata, ensure_ascii=False)),
            )
        temporary.replace(INDEX_PATH)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Índice salvo: {INDEX_PATH}\nRelatório: {REPORT_PATH}")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
