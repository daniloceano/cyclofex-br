# Padrão permanente da documentação

## Instrução obrigatória

**Todo agente ou colaborador deve ler este documento antes de criar ou modificar documentação científica do cyclofex-br.** O objetivo é manter o dashboard como um relatório científico vivo, autossuficiente e auditável por humanos, e não como um índice da implementação.

## Objetivo e público

A documentação científica deve permitir que pesquisadores, orientadores, colaboradores, avaliadores e revisores compreendam o problema, os dados, a construção da amostra, as perguntas, os métodos, os resultados, as interpretações, os limites e o estado do projeto sem abrir o código.

A documentação técnica atende à reprodução computacional, manutenção, scripts, comandos, dependências, diretórios, cache e arquitetura. Ela fica em `docs/internal/` ou na página de proveniência. Rastreabilidade é obrigatória, mas detalhes de implementação não devem interromper a narrativa científica.

## Princípios

1. **Contexto autossuficiente:** cada página e seção reintroduz os conceitos indispensáveis; não depende da memória de outra página.
2. **Raciocínio linear:** contexto → problema → pergunta → dados → método → resultado → interpretação → limitações → consequência.
3. **Ciência separada da implementação:** nomes de arquivos e scripts aparecem em reprodutibilidade ou na camada técnica.
4. **Terminologia definida:** na primeira ocorrência relevante de cada página, explique termos científicos em linguagem simples.
5. **Resultado separado de interpretação:** observação, significado e conclusão não permitida devem ser distinguíveis.
6. **Limitações explícitas:** dados, seleção, suporte, viés, dependência e testes ausentes ficam visíveis.
7. **Rastreabilidade:** análises apontam para dados, versão, configuração, produtos, código, decisões e experimentos.
8. **Força proporcional à evidência:** associação descritiva não vira causalidade, inferência ou hazard.
9. **Fonte canônica única:** Markdown é canônico; HTML é gerado.
10. **Estado explícito:** diferencie `PROPOSTO`, `EM TESTE`, `ADOTADO`, `REJEITADO`, `INCONCLUSIVO` e `AINDA NÃO TESTADO`.

## Estrutura recomendada para uma análise

Adapte os títulos à pergunta, preservando o raciocínio:

1. motivação e pergunta;
2. população, período, unidade de análise e seleção;
3. variáveis e representações, com definições;
4. método descritivo ou inferencial e justificativa;
5. resultados com tabelas e figuras contextualizadas;
6. interpretação cientificamente permitida;
7. limitações e conclusões não permitidas;
8. síntese do aprendizado e consequência para o projeto;
9. bloco discreto de reprodutibilidade.

Não organize a página pela ordem de funções de um script.

## Estrutura obrigatória para experimentos

Cada experimento `E-XXX` deve conter: contexto; pergunta; hipótese; explicações concorrentes quando pertinentes; motivação; dados e critérios de inclusão/exclusão; representação e variáveis; método; métricas; critério de decisão registrado antes do resultado; resultado; interpretação; robustez e diagnósticos; limitações; conclusão; consequência para o projeto; reprodutibilidade; status, datas e vínculos a questões e decisões.

Se uma seção não se aplicar, explique por quê. Resultados negativos, rejeitados e inconclusivos permanecem no histórico. O template canônico está em [experimentos](experiments.md#template-obrigatório-para-novos-experimentos).

## Regras para equações

Uma equação só deve aparecer quando tornar o método mais claro ou preciso. Antes ou imediatamente depois dela, documente:

- o que representa e por que é usada;
- todos os símbolos;
- unidade de cada quantidade, quando aplicável;
- domínio dos valores, quando relevante;
- interpretação intuitiva do resultado.

Nunca apresente notação isolada nem presuma que o leitor conhece a convenção.

## Regras para figuras e tabelas

Antes ou imediatamente depois de cada figura científica, explique a pergunta, população, eixos, cores, painéis, unidades e como ler o elemento visual. Em seguida, separe:

- **observação:** o que é visível ou calculado;
- **interpretação:** o significado compatível com o desenho;
- **limitação:** o que o elemento não mostra.

Tabelas recebem a mesma contextualização. Legendas que apenas repetem o conteúdo não são suficientes. Texto alternativo deve descrever a informação relevante da imagem.

## Regras para dados

Apresente primeiro a necessidade científica, a origem e o significado das unidades. Explique track, estado ciclone–tempo, lifecycle, vento, associação temporal, suporte espacial e distinção entre zero, ausência e não observado antes de listar arquivos ou schemas. Declare período, população, resolução, filtros e unidade de análise. Campos e tipos completos pertencem à referência técnica.

## Terminologia que exige cuidado

Defina quando aparecer pela primeira vez na página: *storm-relative*, *motion-relative*, lifecycle, *excursion set*, *coverage probability*, *footprint*, hazard, threshold, quantil local, unidade de análise e suporte espacial.

Ao comparar sistemas de referência, prefira os termos intuitivos **quadrantes fixos** (`centered`) e **quadrantes rotacionados pelo movimento** (`motion-relative`). Esclareça que “quadrantes” nomeia a orientação dos eixos: análises com coordenadas contínuas não são reduzidas a quatro categorias. Preserve `centered` e `motion_relative` como identificadores técnicos em código, tabelas e arquivos reprodutíveis.

Não use “massa” isoladamente para ponderação estatística. Prefira **peso normalizado de ocorrências** e defina `p_i` como a proporção desse peso no bin; deixe explícito que não se trata de massa física nem de magnitude do vento.

Preserve sempre:

- evento ≠ climatologia;
- *excursion set* ≠ *footprint* probabilístico;
- ocorrência ≠ magnitude;
- *footprint storm-relative* ≠ hazard geográfico;
- ausência de observação ≠ não-excedência.

## Citações e proveniência

- Use links persistentes e DOI para fontes externas quando disponíveis.
- Identifique produto, versão, período e hash na camada de reprodutibilidade.
- Não atribua método ou resultado a uma fonte que apenas fornece genealogia histórica.
- Se a versão exata for desconhecida, registre a lacuna; não escolha uma por suposição.
- Separe dados fornecidos, transformação executada no projeto e inferência do autor.

## Decisões, questões e pressupostos

- `decisions.md` é o registro formal. A narrativa explica a escolha em prosa e cita o ID discretamente.
- `open_questions.md` registra por que a questão importa, o conhecido, o desconhecido, a evidência necessária, dependências e status.
- `assumptions.md` recebe IDs `A-...` quando um pressuposto sustenta inferência, com necessidade, alcance, evidência, teste e status.
- IDs nunca são reutilizados. Substituições preservam o item anterior e apontam para o novo.

## Relação entre documentação científica e técnica

O relatório principal responde “o que, por quê, como cientificamente, o que foi encontrado e o que significa”. `docs/internal/` responde “como executar e manter”. Uma página científica pode incluir um bloco final de reprodutibilidade, mas caminhos e comandos não devem dominar sua abertura ou estruturar seus títulos.

## Atualização do dashboard

1. Edite a fonte Markdown apropriada.
2. Atualize decisões, questões, pressupostos e experimentos vinculados quando o estado científico mudar.
3. Atualize números somente a partir de produtos reproduzíveis identificados.
4. Execute `python3 dashboard/build_docs.py`.
5. Verifique links, mídia, responsividade básica e legibilidade.
6. Não edite manualmente o conteúdo dos HTML gerados.

## Revisão editorial obrigatória

Procure parágrafos sem contexto, termos indefinidos, código no meio da narrativa, força excessiva de conclusão, figuras ou tabelas sem leitura, equações sem definição, duplicação, inconsistência terminológica, unidade não explicada e fatos científicos escondidos apenas na camada técnica.

## Teste de auditoria humana

Antes de entregar, confirme que um pesquisador externo consegue responder pelo dashboard:

1. Qual é a pergunta e por que importa?
2. Quais dados, fontes, períodos e unidades são usados?
3. Como a amostra foi preparada e o que é suporte espacial?
4. Que análise foi feita e por quê?
5. O que foi encontrado, interpretado e ainda não demonstrado?
6. Quais decisões estão vigentes e quais questões permanecem abertas?
7. Qual é o próximo teste e por que ainda não começou?
8. Como reproduzir tecnicamente os resultados?

Se uma resposta científica exigir abrir código-fonte, a documentação ainda não está pronta.
