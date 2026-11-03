# recipe-search-engine

Buscador de receitas em linguagem natural, com scripts de busca lexical BM25 e semântica pelo terminal.

## Ambiente para busca semântica

O ambiente local usa Python 3.12.10 de 64 bits e uma `.venv` exclusiva do projeto, com PyTorch para CPU. As versões das dependências estão fixadas em `requirements.txt`.

Para recriar o ambiente no Windows, após instalar Python 3.12 para o usuário:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install "torch==2.15.0+cpu" --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

O PyTorch é instalado primeiro a partir do índice oficial para CPU; as demais dependências vêm do PyPI. Os comandos usam diretamente o Python da `.venv`, sem precisar ativá-la ou alterar a política de execução do PowerShell.

Para executar a busca existente nesse ambiente:

```powershell
.\.venv\Scripts\python.exe scripts/search_bm25.py "bolo de cenoura"
```

A `.venv`, os arquivos baixados do modelo, os índices locais e os caches de bytecode são ignorados pelo Git.

## Corpus

- `data/raw/receitas_wikilivros.jsonl`: cópia original, sem alterações.
- `data/processed/receitas.jsonl`: documentos preparados para busca.
- `reports/preparacao_corpus.json`: origem, hash do original, consolidações e casos para revisão.

Fonte: [denisevitoriano/tech_challenge_fase_04](https://github.com/denisevitoriano/tech_challenge_fase_04/tree/9f5ac844fea4c889d1115abe6e6f00191dfb83fd), versão `9f5ac844fea4c889d1115abe6e6f00191dfb83fd`.
As receitas são atribuídas aos colaboradores do Wikilivros; as páginas de origem ficam preservadas em `fontes` de cada documento.
O repositório de origem declara o corpus sob [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); essa indicação é mantida para os dados derivados. A preparação acrescenta metadados e consolida repetições, preservando os textos.

## Reproduzir a preparação

Com Python 3.9 ou superior, sem instalar dependências:

```sh
python scripts/prepare_corpus.py
```

O script lê a cópia local, verifica seu SHA-256 e recria o corpus preparado e o relatório. Não acessa a rede.

Cada receita recebe um ID SHA-256 calculado a partir das listas de ingredientes e preparo. O ID independe da posição no arquivo; alterações nessas listas produzem outro ID.
Somente listas exatamente iguais são consolidadas. O primeiro registro fornece o título e a categoria principais; todos os títulos, categorias e links originais são preservados em `fontes`, e os títulos diferentes também ficam em `titulos_alternativos`.

O campo `texto_busca` reúne título, títulos alternativos, ingredientes e preparo, separados por quebras de linha. Os dois métodos de busca poderão usar esse mesmo conteúdo.

A preparação mantém variações reais e receitas curtas. O relatório registra resíduos de marcação e o caso de preparo incompleto observado na auditoria; não constitui uma revisão manual completa. Tempo de preparo não é um campo estruturado, e algumas subseções de ingredientes aparecem dentro do preparo. Filtros ainda dependem de revisão adicional.

## Buscar receitas com BM25

Na pasta do projeto, com Python 3.9 ou superior:

```sh
python scripts/search_bm25.py "bolo de cenoura"
python scripts/search_bm25.py "arroz com frango" -k 3
```

A busca usa apenas a biblioteca padrão e exibe até cinco receitas por padrão, com título, pontuação e fontes. O índice é construído em memória a cada execução, a partir de `texto_busca`.

Receitas e consultas passam pela mesma tokenização: normalização Unicode NFC, minúsculas e separação em palavras/números, preservando acentos. Não há remoção de palavras comuns, redução de palavras ao radical ou expansão de sinônimos. Cada termo distinto da consulta contribui uma vez para a pontuação; basta haver correspondência com algum termo para uma receita participar do ranking.

A implementação usa BM25 com `k1 = 1.2`, `b = 0.75` e IDF positiva:

```text
IDF(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
score(d, q) = soma de IDF(t) * f(t,d) * (k1 + 1)
                         / (f(t,d) + k1 * (1 - b + b * tamanho(d) / tamanho_médio))
```

`N` é o total de documentos, `df(t)` conta os documentos com o termo e `f(t,d)` conta suas ocorrências na receita. O tamanho é medido em tokens. Empates são resolvidos pelo ID da receita. A pontuação serve para ordenar resultados; não é uma probabilidade de relevância.

Consultas vazias ou compostas somente de pontuação são rejeitadas. Se nenhum termo existir no corpus, a busca informa que não houve correspondência. Documentos sem correspondência não são usados para completar a quantidade solicitada.

## Busca semântica

Modelo: [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small), revisão `614241f622f53c4eeff9890bdc4f31cfecc418b3`, executado em CPU. O índice contém vetores normalizados de 384 dimensões. As receitas recebem o prefixo `passage: ` e as consultas, `query: `, conforme o treinamento do modelo.

Para baixar o modelo e verificar o tamanho dos textos:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_semantic_index.py
```

O modelo limita a entrada a 512 tokens, incluindo prefixo e tokens especiais. Na versão atual do corpus, 32 das 2.502 receitas ultrapassam esse limite; a maior tem 982 tokens. A política escolhida para esta primeira versão é o truncamento documentado. Por padrão, o script ainda interrompe antes de gerar vetores se houver textos longos; para aplicar a política escolhida, use:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_semantic_index.py --permitir-truncamento
```

Essa opção permite que o modelo use o início dos textos até seu limite. O corpus original e o preparado continuam completos; o relatório `reports/indice_semantico.json` lista todos os documentos afetados. Nesses casos, o BM25 tem acesso a mais conteúdo que a busca semântica, limitação que precisa acompanhar a avaliação. Acrescente `--offline` à preparação para usar o modelo já baixado sem acesso à rede.

Após a geração do índice:

```powershell
.\.venv\Scripts\python.exe scripts/search_semantic.py "bolo de cenoura"
.\.venv\Scripts\python.exe scripts/search_semantic.py "comida com aipim" -k 3
```

A consulta usa somente os arquivos locais. Os vetores das receitas ficam em `data/indexes/semantic.npz`; cada busca calcula apenas o vetor da consulta. O produto escalar de vetores normalizados equivale à similaridade de cosseno. Empates são resolvidos pelo ID da receita, como no BM25.

O índice guarda os IDs na mesma ordem dos vetores, a revisão do modelo e o SHA-256 do corpus. Se o corpus ou a versão esperada do índice/modelo mudar, a busca exige nova indexação. Consultas vazias, quantidade inválida de resultados e consultas acima do limite são rejeitadas.

A similaridade semântica não exige palavras em comum: sempre retorna os documentos mais próximos, até a quantidade solicitada, mesmo que sejam pouco relevantes. Não há limiar de relevância calibrado nesta versão. A pontuação não é uma probabilidade e não deve ser comparada numericamente à pontuação BM25.
