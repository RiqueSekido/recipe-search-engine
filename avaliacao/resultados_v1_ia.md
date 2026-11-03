# Avaliação dos buscadores · versão 1.0

24 consultas, cinco resultados por método e 211 julgamentos cegos por IA. Médias por consulta, com peso igual. Precision@5 conta apenas a nota 2. nDCG@5 usa ganho 2^nota − 1 e desconto log2(posição + 1). O ranking ideal ordena a união julgada dos dois top 5 da mesma consulta. Quando todos os ganhos são zero, ambos recebem nDCG zero.

| Grupo | Consultas | P@5 BM25 | P@5 semântica | nDCG@5 BM25 | nDCG@5 semântica |
|---|---:|---:|---:|---:|---:|
| Geral | 24 | 0.250 | 0.308 | 0.676 | 0.755 |
| Termos diretos | 8 | 0.375 | 0.375 | 0.921 | 0.889 |
| Sinônimo ou paráfrase | 8 | 0.075 | 0.150 | 0.462 | 0.616 |
| Descritiva | 8 | 0.300 | 0.400 | 0.643 | 0.758 |

| ID | Consulta | P@5 BM25 | P@5 semântica | nDCG@5 BM25 | nDCG@5 semântica |
|---|---|---:|---:|---:|---:|
| Q01 | Quero fazer macarrão ao alho e óleo | 0.200 | 0.200 | 1.000 | 1.000 |
| Q02 | Como preparo sopa de espinafre com ricota? | 0.200 | 0.200 | 1.000 | 1.000 |
| Q03 | Procuro um biscoito de aveia | 0.400 | 0.200 | 0.936 | 0.797 |
| Q04 | Quero fazer arroz com ervilhas | 0.200 | 0.400 | 0.797 | 0.841 |
| Q05 | Como fazer doce de casca de maracujá? | 0.200 | 0.200 | 0.862 | 0.796 |
| Q06 | Quero preparar um bolo de banana | 0.800 | 0.800 | 0.913 | 0.913 |
| Q07 | Quero uma berinjela assada | 0.400 | 0.400 | 0.861 | 0.825 |
| Q08 | Como preparo creme de milho verde? | 0.600 | 0.600 | 1.000 | 0.944 |
| Q09 | Queria uma sopa de jerimum | 0.000 | 0.000 | 0.000 | 0.000 |
| Q10 | Como faço gelado de morango? | 0.000 | 0.000 | 0.869 | 1.000 |
| Q11 | Procuro bolachas de coco | 0.000 | 0.400 | 0.223 | 0.958 |
| Q12 | Queria um croquete de carne picada | 0.400 | 0.600 | 0.663 | 0.803 |
| Q13 | Como preparar curgete recheada? | 0.000 | 0.000 | 0.387 | 0.613 |
| Q14 | Como faço pão de batata-baroa? | 0.000 | 0.000 | 0.195 | 0.805 |
| Q15 | Procuro um gelado de mexerica | 0.000 | 0.000 | 0.387 | 0.000 |
| Q16 | Queria uma pasta de salsicha para passar no pão | 0.200 | 0.200 | 0.975 | 0.752 |
| Q17 | Tenho talos de espinafre e queria aproveitá-los no almoço | 0.200 | 0.400 | 0.626 | 0.856 |
| Q18 | Quero servir um legume com nozes por dentro | 0.200 | 0.000 | 0.663 | 0.417 |
| Q19 | Queria um doce de festa de coco que eu possa enrolar em bolinhas | 0.200 | 0.600 | 0.560 | 0.865 |
| Q20 | Quero bater a massa de um pão no liquidificador | 0.400 | 0.400 | 0.565 | 0.624 |
| Q21 | Quero uma bebida que combine café com uma bola de sorvete | 0.600 | 0.400 | 0.799 | 0.585 |
| Q22 | Tenho arroz e queria servir uma travessa que vai ao forno | 0.200 | 0.600 | 0.573 | 0.887 |
| Q23 | Quero servir peixe com uma casquinha frita por fora | 0.400 | 0.600 | 0.794 | 0.830 |
| Q24 | Queria assar um pão doce com banana por dentro | 0.200 | 0.200 | 0.568 | 1.000 |
