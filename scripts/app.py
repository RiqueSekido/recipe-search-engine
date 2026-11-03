"""Interface local da feira. Execute com streamlit run scripts/app.py."""

from time import perf_counter

import streamlit as st

from search_bm25 import BM25Index
from search_semantic import SemanticIndex


@st.cache_resource(show_spinner="Preparando as receitas e o modelo para a primeira busca…")
def load_indexes():
    semantic = SemanticIndex()
    return BM25Index(semantic.recipes), semantic


def show_results(title, description, results):
    st.subheader(title)
    st.caption(description)
    if not results:
        st.info("Nenhuma receita contém as palavras pesquisadas.")
    for position, (recipe, _) in enumerate(results, 1):
        with st.container(border=True):
            st.markdown(f"**{position}. {recipe['titulo']}**")
            ingredients = recipe["ingredientes"]
            st.write(" · ".join(ingredients[:3]) + ("…" if len(ingredients) > 3 else ""))
            with st.expander("Ver receita"):
                st.markdown("**Ingredientes**")
                for ingredient in ingredients:
                    st.write(f"• {ingredient}")
                st.markdown("**Modo de preparo**")
                for step, instruction in enumerate(recipe["preparo"], 1):
                    st.write(f"{step}. {instruction}")
                for url in dict.fromkeys(source["fonte_url"] for source in recipe["fontes"]):
                    st.markdown(f"[Página de origem no Wikilivros]({url})")


def choose_example(query):
    st.session_state.consulta = query


def main():
    st.set_page_config(page_title="Busca de receitas", page_icon="🍲", layout="wide")
    st.caption("FEIRA DE RECUPERAÇÃO DA INFORMAÇÃO")
    st.title("Busca de receitas")
    st.write("Descreva um prato ou ingrediente e compare duas maneiras de encontrar receitas.")
    try:
        lexical, semantic = load_indexes()
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        st.error(f"Não foi possível preparar a busca. {error}")
        st.stop()

    st.caption("Experimente uma consulta")
    examples = ("bolo de cenoura", "suco de ananás", "lanche salgado para comer com as mãos")
    example_clicked = False
    for column, example in zip(st.columns(3), examples):
        if column.button(example, on_click=choose_example, args=(example,)):
            example_clicked = True
    with st.form("busca"):
        query = st.text_input("O que você quer preparar?", key="consulta",
                              placeholder="Digite uma consulta em português")
        submitted = st.form_submit_button("Buscar receitas", type="primary")

    if submitted or example_clicked:
        try:
            with st.spinner("Buscando receitas…"):
                start = perf_counter()
                lexical_hits = lexical.search(query)
                semantic_hits = semantic.search(query)
                elapsed = perf_counter() - start
                st.session_state.results = (query, lexical_hits, semantic_hits, elapsed)
        except (ValueError, RuntimeError) as error:
            st.session_state.pop("results", None)
            st.warning(str(error))
    if "results" in st.session_state:
        query, lexical_hits, semantic_hits, elapsed = st.session_state.results
        st.divider()
        st.caption(f'Resultados para “{query}” · duas buscas em {elapsed:.2f} s')
        left, right = st.columns(2)
        with left:
            show_results("Por palavras", "BM25 · considera as palavras presentes na receita.", lexical_hits)
        with right:
            show_results("Por significado", "Embeddings · aproxima consultas e receitas pelo sentido do texto.", semantic_hits)
    st.caption("Receitas dos colaboradores do Wikilivros · CC BY-SA 3.0")


if __name__ == "__main__":
    main()
