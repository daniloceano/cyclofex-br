# Padrão permanente da documentação

## Instrução obrigatória

**Todo agente ou colaborador deve ler este documento antes de criar ou modificar documentação científica do cyclofex-br.** O objetivo é manter o dashboard como um relatório científico vivo, autossuficiente e auditável por humanos, e não como um índice da implementação.

## Objetivo e público

A documentação científica deve permitir que pesquisadores, orientadores, colaboradores, avaliadores e revisores compreendam o problema, os dados, a construção da amostra, as perguntas, os métodos, os resultados, as interpretações, os limites e o estado do projeto sem abrir o código.

A documentação técnica atende à reprodução computacional, manutenção, scripts, comandos, dependências, diretórios, cache e arquitetura. Ela fica em `docs/internal/` ou na página de proveniência. Rastreabilidade é obrigatória, mas detalhes de implementação não devem interromper a narrativa científica.

## Princípios

1. **Contexto autossuficiente:** cada página e seção reintroduz os conceitos indispensáveis; não depende da memória de outra página.
2. **Raciocínio linear:** contexto → problema → pergunta → dados → método → resultado → interpretação → limitações → consequência.
3. **Método na ordem cognitiva:** dentro do método, intuição → procedimento → formalização → exemplo → interpretação; nunca fórmula antes de ideia. Ver [como explicar metodologia](#como-explicar-metodologia).
4. **Ciência separada da implementação:** nomes de arquivos e scripts aparecem em reprodutibilidade ou na camada técnica.
5. **Terminologia definida:** na primeira ocorrência relevante de cada página, explique termos científicos em linguagem simples.
6. **Resultado separado de interpretação:** observação, significado e conclusão não permitida devem ser distinguíveis.
7. **Limitações explícitas:** dados, seleção, suporte, viés, dependência e testes ausentes ficam visíveis.
8. **Rastreabilidade:** análises apontam para dados, versão, configuração, produtos, código, decisões e experimentos.
9. **Força proporcional à evidência:** associação descritiva não vira causalidade, inferência ou hazard.
10. **Fonte canônica única:** Markdown é canônico; HTML é gerado.
11. **Estado explícito:** diferencie `PROPOSTO`, `EM TESTE`, `ADOTADO`, `REJEITADO`, `INCONCLUSIVO` e `AINDA NÃO TESTADO`.

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

A seção de método não é um bloco único: ela se organiza em **visão geral com fluxograma**, **passo a passo**, **formalização**, **exemplo concreto**, **métricas**, **incerteza** e **síntese metodológica**, conforme [como explicar metodologia](#como-explicar-metodologia). Todo experimento formal precisa de um fluxograma científico-metodológico, salvo justificativa explícita na própria página.

Se uma seção não se aplicar, explique por quê. Resultados negativos, rejeitados e inconclusivos permanecem no histórico. O template canônico está em [experimentos](experiments.md#template-obrigatório-para-novos-experimentos).

## Como explicar metodologia

As regras desta seção são **permanentes** e valem para toda descrição metodológica do projeto: experimentos formais `E-XXX`, páginas de método, preparação de dados e qualquer texto que descreva uma transformação, uma métrica ou um procedimento de incerteza. Elas não substituem o rigor: exigem o **mesmo** rigor numa sequência que um pesquisador externo consiga acompanhar sem abrir o código.

O critério de sucesso é direto: depois de ler a seção, o leitor deve conseguir reconstruir mentalmente o experimento e explicá-lo com as próprias palavras.

### Ordem cognitiva

Toda descrição metodológica segue a ordem em que um ser humano compreende um procedimento, e não a ordem em que ele é implementado:

> ideia → objeto → passo a passo → formalização → exemplo concreto → resultado da transformação → interpretação → limitações e casos especiais.

Nenhuma seção começa despejando fórmulas para explicá-las depois. O leitor precisa responder “o que estamos tentando fazer?” antes de encontrar “como fazemos isso matematicamente?”.

A mesma ordem se aplica em três níveis simultâneos, sempre nesta direção:

1. **Intuição** — o que estamos fazendo e por quê. *“Queremos impedir que estados com muitas células extremas pesem mais apenas por terem mais pixels.”*
2. **Procedimento** — como fazemos. *“Dividimos o peso total do estado igualmente entre suas células excedentes.”*
3. **Formalização** — a definição matemática, com todos os símbolos definidos.

Inverter essa ordem — matemática primeiro, intuição depois — é um defeito editorial, mesmo quando o conteúdo está correto.

### Contexto local antes do método

Toda subseção metodológica reestabelece o contexto de que precisa, mesmo que o conceito já tenha aparecido antes na página. Antes da primeira operação, deixe explícito:

- qual objeto está sendo manipulado;
- por que essa transformação é necessária;
- qual problema científico ou estatístico ela resolve;
- qual será o produto da etapa.

Não presuma que o leitor guardou a definição introduzida quinze parágrafos antes.

### Objetos antes de símbolos

Antes de qualquer equação, descreva em linguagem natural o que será calculado. Só então nomeie a variável, defina o símbolo, apresente a equação e interprete o resultado.

**Nenhum símbolo pode aparecer em texto, equação, tabela ou figura antes de ser definido.** Escrever “normalizamos por `M_i` e calculamos `p_j`” antes de dizer o que são `M_i` e `p_j` é proibido, ainda que a definição venha logo abaixo.

Para cada símbolo, registre nome, significado, unidade quando existir, natureza (física, estatística ou adimensional), domínio de valores relevante e interpretação. O checklist completo está em [regras para equações](#regras-para-equações).

No texto corrido, use nomes semânticos junto do símbolo — “o peso total do estado `M_i`”, “a proporção espacial `p_i`”, “o peso do ciclone `w_j`” — em vez de repetir apenas a letra. Isso reduz a carga de memória do leitor.

### Passo a passo: uma operação de cada vez

Não agrupe várias transformações conceituais no mesmo parágrafo nem no mesmo bloco de equações. Se o método é `A → B → C → D`, escreva um passo para cada seta, cada um respondendo, nesta ordem:

1. **O que entra?** — o objeto produzido pela etapa anterior.
2. **O que queremos obter?** — o novo objeto.
3. **Por que isso é necessário?** — o problema que a operação resolve.
4. **Como é calculado?** — explicação verbal primeiro, equações depois.
5. **O que significa cada termo?** — todos os símbolos.
6. **Exemplo concreto** — um caso numérico ou espacial pequeno.
7. **O que sai desta etapa?** — o objeto que alimenta a próxima.

Use essa lógica como estrutura de raciocínio, não como formulário mecânico: quando uma etapa for trivial, comprima-a em prosa, mas preserve a sequência. O leitor nunca deve precisar inferir qual objeto produzido por uma equação será usado na equação seguinte.

### Entrada, operação e saída

Toda transformação importante — projeção de coordenadas, heading, rotação, binning, weighting, normalização, bootstrap, cálculo de métricas — declara explicitamente seu contrato:

> **entrada** → **operação** → **saída**

Exemplo: *entrada*, coordenadas geográficas da célula e do centro do ciclone; *operação*, projeção azimutal equidistante; *saída*, posição `(x, y)` em quilômetros relativa ao centro. Sem esse contrato, o leitor não consegue encadear as etapas nem auditar o que foi preservado e o que foi descartado.

### Equações introduzidas progressivamente

Uma equação nunca deve fazer trabalho demais. Quando o resultado final depende de vários níveis, construa-o por partes — peso da célula, peso do estado, peso do ciclone, peso do bin, normalização global — e só então, se ajudar, apresente a fórmula compacta como **síntese**.

A fórmula geral é bem-vinda, mas jamais como primeiro contato. A sequência recomendada é: construção intuitiva → equações simples → exemplo → equação geral → interpretação.

Toda equação relevante é seguida de uma leitura em linguagem comum. Não assuma que a equação se explica sozinha. Depois de `M_i = Σ_j m_ij`, escreva o que ela diz: quanto peso existe no estado inteiro antes da normalização.

### Exemplos numéricos concretos

Um exemplo numérico pequeno é **obrigatório** sempre que o método envolver weighting, normalização, agregação, probabilidades, bins, transformação de coordenadas, cálculo de métricas, bootstrap, seleção, thresholds ou combinação hierárquica de estados e ciclones.

O exemplo usa números simples, mostra a aritmética e verifica a normalização. Quando existirem variantes do método, mostre o mesmo exemplo sob cada variante, para que a diferença fique visível em números e não apenas em prosa.

Exemplos abstratos não satisfazem esta regra. Um exemplo aritmético explícito é preferível a qualquer quantidade de explicação verbal adicional.

### Exemplos espaciais e esquemas

Quando o método envolver posições, use um esquema pequeno. Um diagrama em texto já resolve muitos casos:

```
Estado A          C = centro do ciclone
[ ][X][X]         X = célula que excedeu o threshold
[ ][C][X]
[ ][ ][ ]
```

Depois explique como essas células se distribuem em bins ou pesos. Não é necessário transformar todo esquema em figura elaborada: diagramas em texto, SVG ou figuras pequenas bastam. A prioridade é pedagógica.

### Hierarquia ciclone → estado → célula → bin

O projeto opera em quatro níveis encadeados:

> ciclone (`track_id`) → estado ciclone–tempo → célula espacial → bin agregado

Sempre que um método atravessar mais de um nível, declare explicitamente:

- em qual nível a operação acontece;
- qual nível recebe peso;
- qual nível é agregado;
- qual nível é a unidade inferencial.

Escreva a cadeia na ordem — “primeiro distribuímos o peso dentro de cada estado entre suas células; depois combinamos estados dentro de cada ciclone; por fim combinamos ciclones para formar a distribuição global” — em vez de saltar para a fórmula final da distribuição agregada.

Quando houver weighting hierárquico, o exemplo concreto deve percorrer a hierarquia inteira: pesos das células, peso total de cada estado, peso total de cada ciclone e contribuição final ao mapa; depois, o mesmo exemplo sob o weighting alternativo.

### Métricas

Toda métrica é documentada com sete elementos, nesta ordem:

1. **pergunta** que ela responde;
2. **intuição** do que está sendo medido;
3. **cálculo**, verbal antes de formal;
4. **definição dos símbolos**, com unidade e domínio;
5. **exemplo simples**, quando ajudar;
6. **interpretação** de valores altos e baixos, e do sinal da diferença quando houver comparação;
7. **o que a métrica não mede**.

O sétimo item é obrigatório. Uma métrica sem limite declarado convida a sobreinterpretação.

### Incerteza e bootstrap

Não basta escrever “bootstrap por ciclone com 500 réplicas”. Explique a unidade de reamostragem, mostre uma réplica concreta e justifique a escolha:

```
população:  C1  C2  C3  C4
réplica 1:  C2  C2  C4  C1     (com reposição; C3 não entrou, C2 entrou duas vezes)
```

Deixe explícito que todos os estados e células de um ciclone sorteado permanecem juntos, que a métrica é recalculada em cada réplica, que a distribuição das réplicas produz o intervalo, e **por que não se reamostram células**: células do mesmo ciclone não são observações independentes. Declare também o que o intervalo não cobre — viés de seleção, incerteza do threshold, validação fora da amostra.

### Critério de decisão

Não basta listar condições. Explique a regra de forma operacional: o que será interpretado como evidência a favor, o que como evidência contrária e o que classifica o experimento como inconclusivo. Deixe claro o comportamento quando as condições apontarem em direções conflitantes. Quando ajudar, represente a regra como um mini fluxograma.

O critério é registrado antes do resultado e não é reescrito depois dele.

### Fluxogramas metodológicos

**Todo experimento formal `E-XXX` deve possuir ao menos um fluxograma científico-metodológico**, salvo justificativa explícita registrada na própria página.

O fluxograma:

- aparece **antes** da descrição matemática detalhada, para que o leitor veja o mapa inteiro antes de percorrer cada etapa;
- representa o protocolo real do experimento, não o encadeamento de scripts;
- usa linguagem científica, nunca nomes de arquivos ou funções;
- vem acompanhado de uma seção **“Como ler o fluxo do experimento”**, que explica brevemente cada etapa;
- é atualizado se o protocolo mudar antes da execução;
- permanece congelado depois da conclusão, exceto por correções editoriais.

O fluxograma é um mapa mental e **não substitui** a descrição textual do método.

### Figuras didáticas versus figuras de resultado

Distinga os dois tipos e identifique-os como tais:

- **figura de resultado** — produto científico do experimento, sujeito às regras de observação, interpretação e limitação;
- **esquema metodológico** — figura cujo único objetivo é explicar uma transformação, um sistema de coordenadas, uma sequência de agregação, a distribuição de pesos, o funcionamento do bootstrap ou o agrupamento de células em bins.

Esquemas metodológicos são bem-vindos e frequentemente necessários. A legenda deve dizer explicitamente que a figura é um exemplo conceitual e não um resultado, e deve avisar quando a escala for esquemática e não a real.

### Componentes visuais do dashboard

Para manter leitura consistente entre páginas, o dashboard oferece componentes padronizados. Use-os apenas quando ajudarem o fluxo de leitura; caixas em excesso prejudicam mais do que ajudam.

| Componente | Classe | Uso |
| --- | --- | --- |
| Ideia | `method-box idea` | a intuição que abre uma etapa |
| Entrada → operação → saída | `method-io` | contrato de uma transformação |
| Exemplo | `method-box example` | caso numérico ou espacial concreto |
| Interpretação | `method-box reading` | leitura em linguagem comum de uma equação ou métrica |
| Atenção / limitação | `method-box caution` | o que a etapa não garante ou não mede |
| Síntese | `method-box summary` | resumo sem equações ao fim do método |

No Markdown canônico, abra o `<div>`, deixe **uma linha em branco**, escreva conteúdo Markdown normal e feche com `</div>` após outra linha em branco. O conteúdo permanece legível na fonte e é convertido normalmente.

### Síntese final da seção metodológica

Toda descrição metodológica termina com uma síntese curta, tipicamente sob o título **“Em resumo: o que este método faz?”**, em três a seis frases e **sem equações**.

A síntese consolida o raciocínio: qual objeto entra, quais transformações acontecem, o que o resultado representa e qual escolha ele permite. Ela não introduz método novo nem antecipa interpretação de resultado.

### Rigor preservado

Ser didático não autoriza omitir detalhes, evitar matemática, arredondar conceitos, esconder exceções ou converter metodologia em divulgação. Casos especiais, tolerâncias numéricas, tratamentos de borda e exclusões continuam documentados. O objetivo é apresentar o mesmo conteúdo numa sequência compreensível.

### Auditoria metodológica

Antes de considerar pronta uma página com conteúdo metodológico, confirme as quinze respostas:

1. Sei qual objeto entra no método?
2. Sei por que cada operação é necessária?
3. Consigo acompanhar cada transformação na ordem em que ocorre?
4. Todos os símbolos foram definidos antes ou imediatamente ao aparecer?
5. Entendo o significado intuitivo de cada equação?
6. Existe exemplo concreto para cada parte abstrata?
7. Consigo distinguir ciclone, estado, célula e bin em cada etapa?
8. Sei qual é a saída de cada passo?
9. Entendo como cada métrica é calculada?
10. Sei o que valores altos e baixos significam?
11. Entendo como a incerteza foi calculada e qual é a unidade de reamostragem?
12. Existe fluxograma?
13. O texto explica o fluxograma etapa por etapa?
14. Consigo explicar o método com minhas próprias palavras depois de ler?
15. Precisei abrir o código para compreender alguma etapa científica?

**Se a resposta à pergunta 15 for “sim”, a documentação metodológica está incompleta.**

## Regras para equações

Uma equação só deve aparecer quando tornar o método mais claro ou preciso. Antes ou imediatamente depois dela, documente:

- o que representa e por que é usada;
- todos os símbolos;
- unidade de cada quantidade, quando aplicável;
- domínio dos valores, quando relevante;
- interpretação intuitiva do resultado.

Nunca apresente notação isolada nem presuma que o leitor conhece a convenção.

Este checklist define **o que** documentar em cada símbolo. A **ordem** em que a equação entra no texto — depois da ideia, do objeto e do procedimento verbal, e antes do exemplo concreto — é fixada em [como explicar metodologia](#como-explicar-metodologia).

## Regras para figuras e tabelas

Antes ou imediatamente depois de cada figura científica, explique a pergunta, população, eixos, cores, painéis, unidades e como ler o elemento visual. Em seguida, separe:

- **observação:** o que é visível ou calculado;
- **interpretação:** o significado compatível com o desenho;
- **limitação:** o que o elemento não mostra.

Tabelas recebem a mesma contextualização. Legendas que apenas repetem o conteúdo não são suficientes. Texto alternativo deve descrever a informação relevante da imagem.

Esquemas metodológicos seguem regras próprias: a legenda declara que a figura é um exemplo conceitual e não um resultado, e avisa quando a escala for esquemática. Ver [figuras didáticas versus figuras de resultado](#figuras-didáticas-versus-figuras-de-resultado).

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

Em conteúdo metodológico, procure também: fórmula antes da ideia, símbolo usado antes de definido, várias transformações no mesmo parágrafo, etapa sem entrada e saída declaradas, abstração sem exemplo numérico, nível hierárquico ambíguo, métrica sem “o que não mede”, bootstrap sem unidade de reamostragem, ausência de fluxograma e ausência de síntese final. A checagem completa está em [auditoria metodológica](#auditoria-metodológica).

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

Para páginas com conteúdo metodológico, aplique também as quinze perguntas da [auditoria metodológica](#auditoria-metodológica).

Se uma resposta científica exigir abrir código-fonte, a documentação ainda não está pronta.
