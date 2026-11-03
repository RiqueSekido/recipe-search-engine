# Consultas de avaliação da busca de receitas

**Versão 1.0 · Fixada em 3 de novembro de 2026, antes da execução das consultas de avaliação.** Os identificadores, textos, grupos e critérios desta versão são a referência da avaliação. Registre eventuais revisões em outra versão.

Julgue cada par consulta–receita pela leitura dos ingredientes e do preparo completos. Atribua a mesma nota ao mesmo documento quando ele aparecer nos dois métodos. Receitas diferentes da mesma página recebem julgamentos individuais.

- **2 (completo)** — há evidência para todas as condições do critério na tabela. Aceite equivalências de vocabulário em todos os grupos.
- **1 (parcial)** — a receita cumpre uma parte central do pedido, mas falta um elemento requerido. Por exemplo, peixe frito sem revestimento atende parcialmente ao pedido de peixe com casquinha.
- **0 (irrelevante)** — a receita não atende a um elemento central do pedido. Uma palavra incidental, como “farinha” em um bolo recuperado para a consulta de peixe, é insuficiente.

Use somente a nota 2 como relevante para Precision@5 e os três graus para nDCG@5. Em caso de dúvida, cite o trecho que sustenta a nota. Uma mesma receita pode atender a várias consultas, e cada consulta admite várias respostas corretas.

| ID | Consulta | Tipo | Critério para nota 2 |
|---|---|---|---|
| Q01 | Quero fazer macarrão ao alho e óleo | Termos diretos | O prato é macarrão temperado principalmente com alho e óleo ou azeite. |
| Q02 | Como preparo sopa de espinafre com ricota? | Termos diretos | O resultado é uma sopa e incorpora espinafre e ricota. |
| Q03 | Procuro um biscoito de aveia | Termos diretos | A receita ensina a fazer biscoitos com aveia na massa. |
| Q04 | Quero fazer arroz com ervilhas | Termos diretos | O arroz é a base do prato e as ervilhas são incorporadas a ele. |
| Q05 | Como fazer doce de casca de maracujá? | Termos diretos | A casca do maracujá é preparada como parte comestível do doce. |
| Q06 | Quero preparar um bolo de banana | Termos diretos | A receita produz um bolo com banana na massa, recheio ou cobertura. |
| Q07 | Quero uma berinjela assada | Termos diretos | A berinjela é um dos elementos principais e é assada no forno. |
| Q08 | Como preparo creme de milho verde? | Termos diretos | O milho verde é o ingrediente principal de um creme salgado, como prato ou acompanhamento. |
| Q09 | Queria uma sopa de jerimum | Sinônimo ou paráfrase | A receita produz uma sopa cuja base é jerimum ou abóbora. |
| Q10 | Como faço gelado de morango? | Sinônimo ou paráfrase | O resultado é um gelado ou sorvete de morango, preparado por congelamento. |
| Q11 | Procuro bolachas de coco | Sinônimo ou paráfrase | A receita produz bolachas ou biscoitos com coco na composição. |
| Q12 | Queria um croquete de carne picada | Sinônimo ou paráfrase | O preparo usa carne moída ou finamente picada para formar croquetes. |
| Q13 | Como preparar curgete recheada? | Sinônimo ou paráfrase | A curgete ou abobrinha recebe um recheio e é servida recheada. |
| Q14 | Como faço pão de batata-baroa? | Sinônimo ou paráfrase | A massa do pão leva batata-baroa, também chamada mandioquinha. |
| Q15 | Procuro um gelado de mexerica | Sinônimo ou paráfrase | A receita ensina a fazer sorvete com mexerica, tangerina ou bergamota como sabor principal. |
| Q16 | Queria uma pasta de salsicha para passar no pão | Sinônimo ou paráfrase | A receita transforma a salsicha em uma pasta ou patê que pode ser espalhado sobre pão. |
| Q17 | Tenho talos de espinafre e queria aproveitá-los no almoço | Descritiva | O preparo utiliza os talos como parte comestível de um prato salgado. |
| Q18 | Quero servir um legume com nozes por dentro | Descritiva | Um legume serve de recipiente para um recheio que inclui nozes. |
| Q19 | Queria um doce de festa de coco que eu possa enrolar em bolinhas | Descritiva | O doce leva coco e o preparo orienta enrolar ou modelar porções individuais em forma de bola. |
| Q20 | Quero bater a massa de um pão no liquidificador | Descritiva | O preparo usa o liquidificador na mistura da massa e o produto final é pão. |
| Q21 | Quero uma bebida que combine café com uma bola de sorvete | Descritiva | Café e sorvete compõem a mesma bebida servida, e não apenas sugestões separadas de acompanhamento. |
| Q22 | Tenho arroz e queria servir uma travessa que vai ao forno | Descritiva | O arroz é a base de uma preparação montada em recipiente e levada ao forno. |
| Q23 | Quero servir peixe com uma casquinha frita por fora | Descritiva | O peixe é revestido antes de fritar, por exemplo com farinha, massa ou empanado. |
| Q24 | Queria assar um pão doce com banana por dentro | Descritiva | O resultado é pão doce assado e a banana entra como recheio. |
