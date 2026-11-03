# Busca de receitas em linguagem natural

Como encontrar uma receita quando você usa um nome diferente do que aparece no livro? Nesta demonstração de Recuperação da Informação, você faz uma consulta em português e compara duas listas de até cinco resultados. Ambas pesquisam as mesmas **2.502 receitas do Wikilivros**. A coluna **Por palavras** usa BM25 para localizar termos da consulta. A coluna **Por significado** usa embeddings para aproximar textos de sentido semelhante.

## Abrir a interface da feira

**Com o projeto já preparado**, abra o PowerShell na raiz do repositório e execute:

```powershell
.\.venv\Scripts\python.exe -m streamlit run scripts/app.py --server.address 127.0.0.1 --server.port 8501
```

[Abrir a interface local](http://127.0.0.1:8501). No primeiro acesso, aguarde o carregamento do modelo. Digite o pedido e clique em **Buscar receitas**, ou escolha um dos exemplos da tela. Clique em **Ver receita** para ler os ingredientes e o preparo daquela variação. Isso ajuda a distinguir pratos com o mesmo título e o mesmo link de origem.

Mantenha o aplicativo aberto durante a feira. As consultas seguintes reutilizam o modelo e os índices em memória e funcionam sem internet. O tempo mostrado na tela mede as duas buscas após o carregamento. Para encerrar, pressione Ctrl+C no terminal.

<details>
<summary><strong>Primeira instalação no Windows</strong></summary>

Use a branch `dev`, que contém a aplicação e o corpus preparado. Com Python 3.12 de 64 bits instalado, execute na raiz do projeto. A primeira linha usa o caminho padrão de instalação para o usuário. Ajuste-o se necessário.

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install "torch==2.15.0+cpu" --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/prepare_semantic_index.py --permitir-truncamento
```

A última linha baixa o modelo e calcula um vetor por receita em CPU. Essa preparação precisa de internet no primeiro uso e pode levar alguns minutos. Os pesos ficam em `models/` e o índice em `data/indexes/semantic.npz`. Quando terminar, execute o comando de abertura da interface acima. Nas próximas sessões basta abrir o aplicativo.

</details>

## Três experiências para fazer na tela

1. **Procure `bolo de cenoura` e abra o pão.** Na coluna **Por palavras**, *Pão de cenoura light* apareceu em segundo lugar. Procure “tipo bolo inglês” no preparo. A palavra *bolo* descreve a fôrma, mas também contribui para a pontuação lexical. Na coluna **Por significado**, os cinco primeiros resultados foram bolos de cenoura.
2. **Procure `suco de ananás` e compare as bebidas no topo.** O BM25 encontrou *Licor de abacaxi*, que menciona “ananás”. A busca semântica encontrou *Refresco delicioso de abacaxi*, cuja receita usa “abacaxi”. Qual você abriria para preparar o suco?
3. **Digite `mandioca frita` e depois `macaxeira frita`.** Na primeira busca, *Mandioca frita* aparece em segundo lugar no BM25 e em primeiro na semântica. Trocando apenas o nome regional, ela sai das duas listas visíveis. O corpus contém a receita, mas nenhuma entrada usa a palavra “macaxeira”. Nesse caso, a semelhança de significado também foi insuficiente para trazê-la ao topo.

## O que a avaliação mostrou

A avaliação preliminar reuniu **24 consultas** com oito por grupo (termos diretos, sinônimos ou paráfrases, e descrições). Uma IA julgou **211 pares de consulta e receita** sem ver o método nem a posição de origem. Os resultados dependem desses julgamentos e aguardam revisão humana.

| Método | Resultados plenamente relevantes | Precision@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 30 de 120 | 25,0% | 0,676 |
| Busca semântica | 37 de 120 | 30,8% | 0,755 |

**Precision@5** mede a proporção dos cinco primeiros resultados que atenderam completamente ao pedido. **nDCG@5** também considera relevância parcial e valoriza os acertos nas primeiras posições. Neste conjunto, a precisão empatou nas consultas diretas e foi maior para a busca semântica nos outros dois grupos. [Consultas e critérios](avaliacao/consultas.md) · [Julgamentos por IA](avaliacao/julgamento_v1_ia.md) · [Resultados por grupo e consulta](avaliacao/resultados_v1_ia.md)

## Corpus e atribuição

As receitas são dos colaboradores do Wikilivros. O corpus de origem declara a licença CC BY-SA 3.0. A preparação consolidou quatro pares com ingredientes e preparo idênticos, preservou as fontes e manteve as variações reais. Cada resultado pode ser consultado na página original. [Repositório de origem](https://github.com/denisevitoriano/tech_challenge_fase_04/tree/9f5ac844fea4c889d1115abe6e6f00191dfb83fd) · [Licença](https://creativecommons.org/licenses/by-sa/3.0/) · [Relatório de preparação](reports/preparacao_corpus.json)

## Para desenvolvimento

Os dois métodos usam o campo `texto_busca`, que reúne título, títulos alternativos, ingredientes e preparo. A busca individual pelo terminal mostra posição, pontuação, prévia dos ingredientes e fontes.

```powershell
.\.venv\Scripts\python.exe scripts/search_bm25.py "bolo de cenoura" -k 5
.\.venv\Scripts\python.exe scripts/search_semantic.py "bolo de cenoura" -k 5
```

O **BM25** usa termos em minúsculas com acentos preservados, `k1 = 1.2`, `b = 0.75` e IDF positiva. Para cada termo distinto da consulta, pesa a frequência na receita (`f`), o número de receitas que contêm o termo (`df`) e o comprimento da receita em tokens (`L`).

```text
IDF = ln(1 + (N - df + 0.5) / (df + 0.5))
contribuição = IDF * f * (k1 + 1) / (f + k1 * (1 - b + b * L / L_médio))
```

A **busca semântica** usa o modelo multilingual-e5-small com os prefixos `query: ` e `passage: `. Compara o vetor da consulta aos vetores normalizados das receitas por similaridade de cosseno. O limite de 512 tokens atingiu 32 receitas. Para elas, o BM25 considera o texto integral e o modelo semântico considera o trecho inicial. [Modelo](https://huggingface.co/intfloat/multilingual-e5-small) · [Revisão do modelo e receitas truncadas](reports/indice_semantico.json)

Para recriar o corpus a partir da cópia original, use `python scripts/prepare_corpus.py`. Se o corpus mudar, gere o índice novamente. Com o modelo já baixado, acrescente `--offline` ao comando de indexação.
