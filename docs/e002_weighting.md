# E-002 — Weighting por estado versus por ciclone

- **Status:** `ADOPTED` — resultado classificado como **ROBUSTO AO WEIGHTING**.
- **Data de planejamento, execução e encerramento:** 21 de setembro de 2026.
- **Questões e decisões relacionadas:** [Q-007](open_questions.md#q-007--a-orientação-pelo-movimento-organiza-melhor-as-excedências), [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001) e [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado).
- **Experimento anterior:** [E-001](e001_orientation.md) permanece historicamente `INCONCLUSIVE` sob seu protocolo original.

## Contexto

Um ciclone é identificado por `track_id`. Um **estado ciclone–tempo** representa esse ciclone em um campo ERA5 de 6 h. Uma célula q95-positiva é uma posição observável onde a velocidade do vento a 10 m excedeu estritamente o percentil 95 local. O conjunto dessas células num estado é um *excursion set*: uma realização observada de excedências, não um *footprint* probabilístico.

E-001 comparou quadrantes fixos (`centered`), nos quais o centro do ciclone é deslocado para a origem e o norte permanece para cima, com quadrantes rotacionados pelo movimento (`motion-relative`), que também giram o campo para colocar o deslocamento do ciclone para a frente. “Quadrantes” nomeia o sistema de referência; as coordenadas usadas nas métricas são contínuas. Cada estado q95-positivo recebeu peso normalizado total um — não massa física nem magnitude do vento. Assim, ciclones com mais estados positivos participaram mais vezes do mapa agregado.

## Problema

A unidade científica fundamental do projeto é o ciclone, mas a distribuição de E-001 descreveu a população de estados. A diferença não torna E-001 incorreto: indica que dois estimandos legítimos podem responder a perguntas distintas. E-002 mede quanto a estrutura espacial e a conclusão de E-001 dependem dessa escolha, sem reinterpretar retrospectivamente seu protocolo.

## Pergunta

**Pergunta principal.** A estrutura espacial das excedências q95 muda de forma relevante quando cada ciclone recebe o mesmo peso total, em vez de cada estado q95-positivo receber o mesmo peso?

**Pergunta secundária.** A conclusão `INCONCLUSIVE` de E-001 sobre quadrantes fixos versus rotacionados permanece quando se remove a participação proporcionalmente maior dos ciclones com muitos estados positivos?

## Hipótese

A hipótese principal previa sensibilidade porque duração e número de estados q95-positivos variam entre ciclones. A hipótese de robustez previa que o conflito observado em E-001 — núcleo A50 mais concentrado, mas regiões intermediária e externa mais dispersas após a rotação — permaneceria sob peso igual por ciclone. A explicação concorrente era que poucos sistemas temporalmente longos produzissem esse conflito; nesse caso, *equal-cyclone* poderia alinhar as métricas em favor de uma representação.

## Visão geral do desenho experimental

O fluxograma resume a cadeia lógica de E-002, da pergunta à classificação de robustez. A comparação é deliberadamente estreita: toda a geometria e toda a população vêm congeladas de E-001, e a única coisa que muda entre os dois braços é **quem recebe peso igual**.

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/methodology_flow.png" alt="Fluxograma em oito etapas do experimento E-002: pergunta, protocolo herdado de E-001, auditoria de reprodução, dois weightings, quatro distribuições, avaliação por métricas, incerteza por bootstrap de ciclones e decisão sobre robustez.">
  <figcaption>Esquema metodológico, não um resultado. Os dois braços se separam apenas na etapa de weighting e voltam a ser avaliados na mesma grade, com as mesmas métricas e o mesmo bootstrap.</figcaption>
</figure>

## Como ler o fluxo do experimento

Cada caixa corresponde a uma etapa científica, não a um script.

1. **Pergunta.** A estrutura espacial das excedências q95 depende de o peso igual ser atribuído a estados ou a ciclones?
2. **Protocolo herdado.** População, threshold q95 local, suporte espacial, corte de heading em 5 km/h, transformação de coordenadas, domínio, bins de 50 km, agrupamento de fases e ausência de suavização são reutilizados literalmente de E-001.
3. **Auditoria de reprodução.** Ciclones, estados, células excedentes e exclusões são recontados. Qualquer divergência interromperia o experimento antes dos resultados.
4. **Dois weightings.** *Equal-state* dá peso total um a cada estado q95-positivo; *equal-cyclone* dá peso total um a cada ciclone q95-positivo. Esta é a **única** diferença.
5. **Quatro distribuições.** Duas orientações — quadrantes fixos e rotacionados — vezes dois weightings, todas na mesma grade.
6. **Avaliação.** Entropia, A50, A75, A90 e RMS descrevem cada distribuição; a concentração entre ciclones e a distância de variação total descrevem o efeito do próprio weighting.
7. **Incerteza.** Quinhentas réplicas reamostram `track_id` com reposição e recalculam ambos os weightings dentro de cada réplica.
8. **Decisão.** O critério preregistrado classifica o resultado como robusto, parcialmente sensível ou sensível ao weighting.

As seções seguintes percorrem essas etapas em detalhe, começando por **por que** os dois weightings não são intercambiáveis.

## Por que os dois weightings respondem a perguntas diferentes

**Equal-state** descreve a população de estados: “se um estado q95-positivo for selecionado ao acaso, onde aparecem suas excedências?”. Um ciclone com 20 estados positivos aparece 20 vezes mais que outro com um estado positivo.

**Equal-cyclone** descreve a população de ciclones q95-positivos: “se um ciclone for selecionado ao acaso e sua distribuição interna for observada, qual estrutura é típica entre ciclones?”. Cada ciclone recebe massa total um, independentemente de sua duração representada.

Portanto, *equal-cyclone* não é automaticamente mais correto por o ciclone ser a unidade inferencial. Unidade do bootstrap e estimando descritivo cumprem funções diferentes: o bootstrap por ciclone preserva a dependência; o weighting define qual população o mapa resume.

## Dados

O experimento reutilizou as três entradas de E-001, com hashes validados: catálogo operacional de tracks e **lifecycle** — ciclo de vida categorizado em fases — do Zenodo 18133432, catálogo de estados de 6 h e Parquet condicionado de vento ERA5 a 10 m. O período comparável vai de 1º de janeiro de 2010 a 31 de dezembro de 2020 UTC.

**Suporte espacial** é o conjunto de células da grade de 0,25° situadas simultaneamente no domínio 65°S–10°S, 85°W–15°W e até 1.100 km do centro. Ausência de suporte não foi convertida em não-excedência. E-002 preservou q95 local, seleção, suporte completo ou parcial, transformação azimutal equidistante, corte de heading de 5 km/h, domínio relativo de −1.100 a +1.100 km, bins de 50 km, fases agrupadas e ausência de suavização.

## População reproduzida de E-001

O pipeline interromperia antes dos resultados se qualquer contagem divergisse. A validação reproduziu exatamente:

| Auditoria | Contagem |
| --- | ---: |
| Ciclones elegíveis | 1.784 |
| Estados comparáveis | 23.050 |
| Estados com ao menos uma excedência q95 | 16.921 |
| Células q95 excedentes | 9.090.570 |
| Estados com suporte excluídos por heading < 5 km/h | 284 |
| Ciclones com ao menos um estado q95-positivo | 1.757 |

Vinte e sete ciclones elegíveis não tiveram estado q95-positivo: permaneceram na auditoria e no bootstrap da população elegível, mas não receberam massa em uma distribuição condicionada à ocorrência.

## Como o peso desce de ciclone para célula

<div class="method-box idea">

O mapa final é construído somando contribuições de milhares de estados. Antes de somar, é preciso decidir **quanto** cada um pode contribuir. Essa decisão não é técnica: ela define qual população o mapa descreve. Dar o mesmo peso a cada estado descreve a população de estados; dar o mesmo peso a cada ciclone descreve a população de ciclones. E-002 constrói as duas e compara.

</div>

<ul class="method-io">
<li>células q95 de cada estado, já posicionadas em bins de 50 km pela geometria de E-001</li>
<li>atribuição de peso total a estados ou a ciclones, e repartição desse peso entre as células</li>
<li>duas distribuições espaciais normalizadas sobre a mesma grade, uma por weighting</li>
</ul>

O peso percorre quatro níveis encadeados, sempre de cima para baixo:

> ciclone (`track_id`) → estado ciclone–tempo → célula q95 → bin de 50 km

Neste relatório, *massa* é usada como sinônimo abreviado de **peso normalizado de ocorrências**: não é massa física nem magnitude do vento. A diferença entre os dois esquemas está inteiramente em **qual nível recebe uma unidade de peso**: o estado ou o ciclone.

Sejam, em todo o restante da seção:

- `j` — índice do ciclone;
- `t` — índice de um estado q95-positivo do ciclone `j`;
- `m_jt` — número de células excedentes no estado `t` do ciclone `j`, adimensional, com `m_jt ≥ 1`;
- `n_j` — número de estados q95-positivos do ciclone `j`, adimensional, com `n_j ≥ 1`.

Posições têm unidade de quilômetro e áreas têm km², mas pesos e proporções espaciais são adimensionais.

### Equal-state

**O que entra.** Os estados q95-positivos, cada um com suas `m_jt` células.

**O que queremos obter.** Um peso por célula tal que cada estado contribua com exatamente uma unidade.

**Como é calculado.** O estado recebe uma unidade de peso e a divide igualmente entre suas células excedentes. Em *equal-state*, cada célula recebe peso

$$
w_{jt\mathrm{cell}} = \frac{1}{m_{jt}}.
$$

Aqui, $w_{jt\mathrm{cell}}$ é o peso adimensional de uma célula excedente. As células de cada estado somam uma unidade de peso; a soma dos bins é depois normalizada para um.

<div class="method-box reading">

Em outras palavras, o número de células excedentes controla apenas o **detalhe** com que o peso do estado se espalha, nunca o **total** que ele contribui. Um estado que cobriu uma área enorme e outro que cobriu poucos pixels entram no mapa com a mesma importância. O que ainda não é neutralizado é a duração: um ciclone com muitos estados positivos entra muitas vezes.

</div>

**O que sai.** Um peso por célula; o peso total de cada ciclone `j` fica igual a `n_j`.

### Equal-cyclone

**O que entra.** Os mesmos estados e as mesmas células, mais a contagem `n_j` de estados positivos por ciclone.

**O que queremos obter.** Um peso por célula tal que cada **ciclone** contribua com exatamente uma unidade, independentemente de quantos estados positivos tenha.

**Como é calculado.** O ciclone recebe uma unidade, reparte-a igualmente entre seus `n_j` estados positivos, e cada estado reparte a sua parte entre suas células. Se $n_j$ é o número adimensional de estados q95-positivos do ciclone $j$, cada célula recebe

$$
w_{jt\mathrm{cell}} = \frac{1}{n_j m_{jt}}.
$$

As células de cada estado somam $1/n_j$, e todos os estados do ciclone somam uma unidade. A distribuição agregada é normalizada entre os 1.757 ciclones q95-positivos. Dentro de cada fase, $n_j$ conta apenas estados positivos daquela fase; assim, a análise estratificada também compara ciclones com peso total igual no estrato.

<div class="method-box reading">

A fórmula é a de *equal-state* dividida por `n_j`. Esse único fator é toda a diferença entre os dois experimentos: ele remove a vantagem de participação que um ciclone longo tinha por aparecer muitas vezes.

</div>

**O que sai.** Um peso por célula; o peso total de cada ciclone é um, por construção.

### Exemplo concreto: a mesma população sob os dois weightings

<div class="method-box example">

Considere uma população reduzida a dois ciclones:

- **Ciclone A** — estado `A1` com 4 células q95 e estado `A2` com 2 células q95, portanto `n_A = 2`;
- **Ciclone B** — estado `B1` com 3 células q95, portanto `n_B = 1`.

**Sob *equal-state*,** cada estado vale um. As células de `A1` recebem `1/4 = 0,25`; as de `A2` recebem `1/2 = 0,50`; as de `B1` recebem `1/3 ≈ 0,3333`. Os pesos totais ficam `A = 1 + 1 = 2` e `B = 1`. Sobre o total de 3, o ciclone A contribui com **66,7%** do mapa e o ciclone B com **33,3%**.

**Sob *equal-cyclone*,** cada ciclone vale um. Os dois estados de A dividem essa unidade, então `A1` vale `1/2` e `A2` vale `1/2`; suas células recebem `0,5/4 = 0,125` e `0,5/2 = 0,25`. O ciclone B tem um único estado positivo, que continua valendo um, com células de `1/3 ≈ 0,3333`. Os pesos totais ficam `A = 1` e `B = 1`, e cada ciclone contribui com **50%** do mapa.

Verificação: em ambos os esquemas, as células de um mesmo estado somam o peso daquele estado, e os pesos dos estados somam o peso do ciclone. Só a repartição **entre** ciclones muda.

</div>

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/weighting_hierarchy_example.png" alt="Esquema didático com dois painéis: à esquerda, equal-state, em que o ciclone A com dois estados positivos contribui com 66,7% do mapa; à direita, equal-cyclone, em que ambos os ciclones contribuem com 50%. Cada célula mostra seu peso numérico.">
  <figcaption>Esquema metodológico, não um resultado de E-002. Os números são do exemplo reduzido acima, não da amostra real. Os pesos das células mudam entre os painéis, mas dentro de cada estado eles continuam iguais entre si: o weighting altera o total de cada ciclone, não o equilíbrio interno de um estado.</figcaption>
</figure>

<div class="method-box caution">

O exemplo mostra o mecanismo, não a magnitude. Na amostra real, nenhum ciclone isolado chega perto de 66,7%: o maior recebe 0,21% da massa *equal-state*. O efeito observado é agregado — os 10% de ciclones com mais estados positivos reúnem 22,52% da massa —, e é essa concentração agregada, não um evento dominante, que E-002 mede.

</div>

## Diagnóstico de contribuição dos ciclones

<div class="method-box idea">

O exemplo anterior mostrou o **mecanismo** do weighting em dois ciclones. Falta saber qual é a sua magnitude na amostra real: os 1.757 ciclones q95-positivos participam de forma parecida do mapa *equal-state*, ou uma minoria de sistemas longos concentra boa parte da massa? Esta seção mede essa desigualdade antes de qualquer resultado espacial, porque ela determina o quanto o weighting **pode** mudar.

</div>

Para cada `track_id`, o produto reprodutível registra estados elegíveis, estados q95-positivos, duração representada em blocos de 6 h, intervalo entre primeiro e último estado e fração de massa nos dois weightings. A duração de observação é o número de estados multiplicado por 6 h; o intervalo temporal também é fornecido porque uma sequência pode conter lacunas de elegibilidade.

Entre os ciclones positivos, a mediana foi 8 estados; P25 = 5, P75 = 13, P90 = 18, P95 = 20, P99 = 26 e o máximo = 35. O ciclone de maior peso recebeu 0,2068% da massa *equal-state*, contra 0,0569% sob peso igual.

| Grupo ordenado por contribuição *equal-state* | Ciclones | Massa *equal-state* | Massa *equal-cyclone* |
| --- | ---: | ---: | ---: |
| 1% superior | 18 | 3,19% | 1,02% |
| 5% superior | 88 | 12,69% | 5,01% |
| 10% superior | 176 | 22,52% | 10,02% |

### Concentração entre ciclones: HHI e número efetivo

**Pergunta que respondem.** A massa do mapa está repartida entre muitos ciclones ou concentrada em poucos?

**Intuição.** A tabela acima responde por faixas — quanto cabe aos 1%, 5% e 10% maiores —, mas não resume a desigualdade inteira num número. Somar os **quadrados** das frações faz isso: elevar ao quadrado penaliza contribuições grandes muito mais do que pequenas, de modo que a soma cresce quando poucos ciclones dominam. Como esse valor é difícil de ler diretamente, ele é invertido e passa a responder a uma pergunta concreta: *quantos ciclones de peso idêntico produziriam essa mesma concentração?*

**Cálculo verbal.** Para cada ciclone, calcula-se a fração da massa global que ele recebeu; essas frações são elevadas ao quadrado e somadas, produzindo o índice de Herfindahl. O número efetivo é o inverso dessa soma.

**Formalização.** Seja $a_j$ a fração adimensional da massa global recebida pelo ciclone $j$, com $\sum_j a_j=1$ e $n$ ciclones q95-positivos. Então

$$
HHI=\sum_j a_j^2, \qquad N_{eff}=\frac{1}{HHI}.
$$

`HHI` é adimensional e varia entre $1/n$ — todos os ciclones com a mesma fração — e $1$ — um único ciclone com toda a massa. `N_eff` é adimensional, tem unidade conceitual de “número de ciclones” e varia entre $1$ e $n$; ele não precisa ser inteiro.

<div class="method-box example">

Retomando a população reduzida de dois ciclones da seção anterior, sob *equal-state* o ciclone A recebeu `2/3` da massa e o ciclone B, `1/3`:

$$HHI=\left(\tfrac{2}{3}\right)^2+\left(\tfrac{1}{3}\right)^2=\tfrac{5}{9}=0{,}5556, \qquad N_{eff}=\frac{1}{0{,}5556}=1{,}8.$$

Ou seja, dois ciclones desiguais concentram a massa como se fossem apenas 1,8 ciclones iguais. Sob *equal-cyclone*, cada um recebe `0,5`:

$$HHI=0{,}25+0{,}25=0{,}50, \qquad N_{eff}=2{,}0,$$

exatamente o número de ciclones da população — o valor teórico máximo, alcançado por construção quando todos têm peso igual.

</div>

**Valores observados.** *Equal-state* teve HHI = 0,0007759 e $N_{eff}=1.288,8$; *equal-cyclone*, HHI = 0,0005692 e $N_{eff}=1.757$, seu valor teórico. Para os grupos superiores, 1%, 5% e 10% foram convertidos em número de ciclones pelo teto, resultando em 18, 88 e 176 eventos.

**Como interpretar.** `N_eff` próximo do número de ciclones positivos indica participação quase equilibrada; valores muito menores indicam que a massa se comporta como se viesse de uma população menor do que a realmente observada. A queda de 1.757 para 1.288,8 significa que o estimando por estado se apoia efetivamente em cerca de 73% dos ciclones disponíveis.

**O que não medem.** `HHI` e `N_eff` descrevem apenas como o peso se reparte **entre** ciclones. Não dizem **onde**, no espaço, esse peso cai; não medem a influência de um ciclone sobre uma métrica específica — isso exigiria remoção ou *leave-one-cyclone-out*, não executados aqui; e não distinguem duração física de participação, já que o número de estados positivos combina duração, suporte, heading e ocorrência q95.

### Participação temporal e contribuição acumulada

A figura pergunta se poucos ciclones dominam pela quantidade de estados positivos. O eixo horizontal mostra estados por ciclone; o vertical, número de ciclones, e a linha marca a mediana.

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/positive_states_per_cyclone.png" alt="Histograma do número de estados q95-positivos por ciclone, com mediana de oito estados e cauda até 35.">
  <figcaption>Participação temporal dos 1.757 ciclones q95-positivos. A maioria possui poucos estados, mas existe uma cauda de sistemas que participa muitas vezes do estimando por estado.</figcaption>
</figure>

**Observação:** a distribuição é assimétrica, mas o maior ciclone isolado responde por apenas 0,21% da massa. **Interpretação:** há concentração agregada relevante, não domínio por um único evento. **Limitação:** número de estados positivos combina duração, seleção, suporte e ocorrência; não mede duração física completa do ciclone.

A próxima figura ordena os ciclones do maior para o menor peso. O eixo horizontal acumula a fração de ciclones e o vertical acumula a massa; a diagonal é o resultado *equal-cyclone*.

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/cumulative_cyclone_contribution.png" alt="Curva de contribuição acumulada mostrando que os 10% de ciclones com maior número de estados positivos recebem 22,52% da massa equal-state, ante cerca de 10% em equal-cyclone.">
  <figcaption>Concentração da massa entre ciclones. O afastamento da diagonal quantifica a participação adicional de sistemas com mais estados q95-positivos.</figcaption>
</figure>

**Observação:** os 10% superiores concentram 22,52% da massa *equal-state*. **Interpretação:** $N_{eff}$ cai 26,6% em relação aos 1.757 ciclones positivos, uma desigualdade material, porém distribuída. **Limitação:** a curva mede contribuição, não influência causal de cada ciclone sobre uma métrica específica.

## Métricas

As definições são idênticas às de E-001, incluindo o que cada métrica **não** mede; o tratamento completo de cada uma está em [métodos de avaliação e métricas de E-001](e001_orientation.md#métodos-de-avaliação-e-métricas). A entropia de Shannon $H=-\sum_i p_i\ln p_i$, em nat, resume quão espalhada está a massa entre bins; $i$ identifica um bin e $p_i$ é sua massa adimensional normalizada, com $\sum_i p_i=1$. A50, A75 e A90 são o número mínimo de bins necessários para atingir 50%, 75% e 90% da massa multiplicado por 2.500 km². RMS é a raiz da distância quadrática média ao centroide, em km. A distância do centroide ao centro, em km, e a razão entre eixos principais da covariância, adimensional, são diagnósticos de deslocamento e anisotropia; não entram na decisão principal.

Essas métricas descrevem **cada** distribuição isoladamente. E-002 precisa também de uma medida do quanto o próprio weighting mudou o mapa.

### Distância de variação total

**Pergunta que responde.** Quanto de peso teria de ser movido de um bin para outro para transformar o mapa *equal-state* no mapa *equal-cyclone*?

**Intuição.** Se os dois mapas fossem idênticos, nada precisaria ser movido. Quanto mais eles discordarem sobre onde o peso está, maior a fração que precisaria mudar de lugar.

**Cálculo.** Somam-se as diferenças bin a bin, em valor absoluto, e divide-se por dois — cada unidade movida aparece duas vezes na soma, uma vez como perda e outra como ganho. A distância de variação total entre os mapas dos dois weightings é

$$
TV=\frac{1}{2}\sum_i\left|p_i^{(ciclone)}-p_i^{(estado)}\right|,
$$

onde $i$ identifica um bin de 50 km e cada $p_i$ é sua massa adimensional normalizada. O expoente entre parênteses nomeia o weighting, não uma potência.

**Exemplo simples.** Suponha uma grade reduzida a três bins. Sob *equal-state*, as massas são `(0,50; 0,30; 0,20)`; sob *equal-cyclone*, `(0,40; 0,35; 0,25)`. As diferenças absolutas são `0,10`, `0,05` e `0,05`, de modo que

$$TV=\tfrac{1}{2}\,(0{,}10+0{,}05+0{,}05)=0{,}10.$$

O primeiro bin perdeu `0,10` de massa e os outros dois ganharam `0,05` cada; a soma bruta conta essa mesma transferência duas vezes, e por isso ela é dividida por dois. Ler o resultado como “10% da massa mudou de bin” é exatamente o que a métrica afirma. Os números são didáticos e não são um resultado de E-002.

**Interpretação.** TV varia de 0 a 1: zero representa mapas idênticos; o valor também é a fração mínima de massa que precisaria ser redistribuída para igualá-los. Um TV de 0,08 significa que cerca de 8% do peso está em bins diferentes nos dois mapas, enquanto 92% coincide.

**O que não mede.** TV não diz **para onde** a massa se moveu, não distingue um deslocamento curto de um deslocamento longo — mover peso para o bin vizinho e para o outro extremo do domínio contam igual — e não ordena qualidade científica: um TV alto não torna um weighting melhor nem pior que o outro.

## Critério de decisão

O critério foi registrado no protocolo antes da execução. E-001 seria **robusto ao weighting** se, sob *equal-cyclone*, A50 continuasse em sentido oposto a A75, A90 e RMS e as cinco métricas de concentração não favorecessem consistentemente uma representação. Seria **sensível** se todas as cinco passassem a apontar para a mesma representação, com IC95% de H e A75 excluindo zero no mesmo sentido, ou se o critério simétrico de E-001 sustentasse claramente uma representação. Situações intermediárias seriam **parcialmente sensíveis**.

**Como o critério opera.** Ele não pergunta se o weighting mudou alguma coisa — quase certamente mudou —, mas se a mudança foi suficiente para **reverter a leitura de E-001**. Se, sob *equal-cyclone*, o conflito entre núcleo e cauda persistir e nenhuma representação reunir todas as métricas a seu favor, o experimento é classificado como `ROBUST_TO_WEIGHTING`. Se as cinco métricas passarem a apontar no mesmo sentido, com os intervalos de H e A75 excluindo zero coerentemente, o experimento é classificado como sensível e a conclusão de E-001 teria de ser reaberta. Qualquer padrão intermediário — por exemplo, quatro métricas concordando e uma discordando — seria `PARTIALLY_SENSITIVE`.

Esse critério avalia a conclusão sobre orientação; ele não exige que todos os efeitos do weighting sejam numericamente pequenos. Um weighting pode deslocar muito peso e ainda assim preservar a comparação entre orientações, e é exatamente essa distinção que o critério isola.

## Resultados

As quatro distribuições principais produziram:

| Representação | Weighting | H (nat) | A50 (km²) | A75 (km²) | A90 (km²) | RMS (km) | Distância do centroide (km) | Anisotropia |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Centered | Equal-state | 7,11505 | 967.500 | 1.817.500 | 2.660.000 | 672,06 | 219,92 | 1,0375 |
| Centered | Equal-cyclone | 7,12489 | 982.500 | 1.842.500 | 2.677.500 | 713,22 | 220,14 | 1,0102 |
| Motion-relative | Equal-state | 7,11276 | 935.000 | 1.862.500 | 2.757.500 | 679,75 | 194,58 | 1,0224 |
| Motion-relative | Equal-cyclone | 7,12448 | 960.000 | 1.870.000 | 2.755.000 | 721,43 | 190,56 | 1,0360 |

As duas linhas *equal-state* reproduziram as áreas de E-001 exatamente e as métricas contínuas com diferença absoluta inferior a $10^{-6}$; os resumos bootstrap de E-001 também foram reproduzidos dentro de $10^{-6}$.

## Efeito do weighting

Diferenças abaixo são *equal-cyclone minus equal-state*. Valores positivos de H, área ou RMS representam maior dispersão sob peso igual por ciclone.

| Representação | ΔH (nat) | ΔA50 (km²) | ΔA75 (km²) | ΔA90 (km²) | ΔRMS (km) | TV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Centered | +0,00983 | +15.000 | +25.000 | +17.500 | +41,16 | 0,07920 |
| Motion-relative | +0,01171 | +25.000 | +7.500 | −2.500 | +41,68 | 0,07858 |

O mapa *centered* abaixo compara os dois estimandos na mesma escala; o terceiro painel é *equal-cyclone minus equal-state*.

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/centered_weighting_comparison.png" alt="Mapas centered sob equal-state e equal-cyclone e sua diferença, mostrando redistribuição moderada da massa espacial.">
  <figcaption>Efeito do weighting em coordenadas centered. Tons claros nos dois primeiros painéis indicam maior massa; vermelho e azul no terceiro indicam ganho e perda sob equal-cyclone.</figcaption>
</figure>

**Observação:** 7,92% da massa precisa ser redistribuída entre bins e o RMS aumenta 41,16 km. **Interpretação:** ciclones com menos estados positivos ampliam a dispersão radial média quando recebem peso igual. **Limitação:** o mapa agregado não identifica quais ciclones geram cada deslocamento.

O mapa *motion-relative* usa direita/frente como eixos e mantém a mesma leitura.

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/motion_weighting_comparison.png" alt="Mapas motion-relative sob equal-state e equal-cyclone e sua diferença, com distância de variação total de 0,0786.">
  <figcaption>Efeito do weighting após alinhar o movimento para cima. O weighting redistribui 7,86% da massa e eleva o RMS em 41,68 km.</figcaption>
</figure>

**Observação:** a magnitude global da redistribuição é quase igual à de *centered*, embora A90 diminua 2.500 km². **Interpretação:** a sensibilidade ao weighting não depende apenas da orientação. **Limitação:** TV não informa se uma redistribuição é fisicamente preferível.

## Robustez da conclusão de E-001

A comparação *motion-relative minus centered* foi:

| Weighting | ΔH (nat) | ΔA50 (km²) | ΔA75 (km²) | ΔA90 (km²) | ΔRMS (km) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Equal-state | −0,00229 | −32.500 | +45.000 | +97.500 | +7,69 |
| Equal-cyclone | −0,00041 | −22.500 | +27.500 | +77.500 | +8,21 |

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/representation_equal_cyclone.png" alt="Mapas centered e motion-relative sob equal-cyclone e a diferença motion menos centered.">
  <figcaption>Comparação de orientação quando cada ciclone recebe massa total igual. Motion-relative mantém núcleo A50 menor, mas A75, A90 e RMS maiores.</figcaption>
</figure>

**Observação:** o conflito núcleo–cauda permanece, embora as diferenças de área diminuam. **Interpretação:** a conclusão de E-001 não foi produzida pela participação desproporcional dos ciclones mais longos. **Limitação:** robustez a este weighting não implica robustez a thresholds, tamanho do ciclone ou novas amostras.

## Resultado por fase

A tabela mostra *equal-cyclone minus equal-state* dentro das quatro fases principais; valores de H, áreas e RMS têm as mesmas unidades da análise global.

| Fase | Representação | ΔH | ΔA50 | ΔA75 | ΔA90 | ΔRMS |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Incipiente | Centered | −0,01133 | −32.500 | −10.000 | −5.000 | +12,90 |
| Incipiente | Motion-relative | −0,00744 | −17.500 | −12.500 | −7.500 | +14,08 |
| Intensificação | Centered | +0,02391 | +32.500 | +55.000 | +50.000 | +35,62 |
| Intensificação | Motion-relative | +0,03036 | +47.500 | +60.000 | +62.500 | +37,97 |
| Madura | Centered | +0,00294 | −7.500 | +17.500 | +32.500 | +13,51 |
| Madura | Motion-relative | −0,00724 | −12.500 | +5.000 | +20.000 | +12,19 |
| Decaimento | Centered | −0,02905 | −57.500 | −80.000 | −65.000 | +26,25 |
| Decaimento | Motion-relative | −0,02137 | −37.500 | −95.000 | −92.500 | +28,03 |

O $N_{eff}$ *equal-state* foi 767,3 de 1.051 ciclones positivos na fase incipiente, 1.132,9 de 1.611 na intensificação, 735,8 de 923 na madura e 873,3 de 1.296 no decaimento. A perda relativa foi maior no decaimento, seguido de intensificação. O efeito espacial não foi homogêneo: peso igual aumentou áreas na intensificação, reduziu-as no decaimento e produziu sinais mistos na fase madura. Como esta estratificação é secundária e não recebeu bootstrap próprio, ela localiza heterogeneidade, mas não domina a conclusão global.

## Incerteza

<div class="method-box idea">

As diferenças acima são um número só. Falta saber se elas sobreviveriam a outra seleção de ciclones ou se dependem de quais eventos entraram na amostra. O bootstrap responde reconstruindo a amostra muitas vezes e observando quanto cada diferença varia.

</div>

<ul class="method-io">
<li>os 1.784 ciclones elegíveis, cada um com todos os seus estados e células</li>
<li>500 reamostragens com reposição no nível do ciclone, recalculando os dois weightings dentro de cada réplica</li>
<li>uma distribuição de 500 diferenças por contraste, resumida pelos percentis 2,5 e 97,5</li>
</ul>

**Qual é a unidade de reamostragem.** O sorteio é feito sobre `track_id`. Com uma população reduzida a `C1 C2 C3 C4`, uma réplica poderia ser `C2 C2 C4 C1`: `C3` fica de fora e `C2` conta em dobro, sempre com todos os seus estados e células juntos. O esquema completo está ilustrado em [E-001](e001_orientation.md#comparação-pareada-e-incerteza).

**Por que não reamostrar estados nem células.** Estados sucessivos do mesmo ciclone descrevem o mesmo sistema em instantes próximos, e células vizinhas pertencem ao mesmo campo de vento. Tratá-los como observações independentes produziria intervalos artificialmente estreitos. Em E-002 há um motivo adicional: `n_j`, o número de estados positivos do ciclone, é justamente a quantidade que distingue os dois weightings. Reamostrar estados alteraria `n_j` e destruiria o contraste sob teste.

**Por que os dois weightings são recalculados na mesma réplica.** Dentro de cada réplica, a mesma população sorteada alimenta *equal-state* e *equal-cyclone*, de modo que a variação observada reflete a troca de ciclones e não uma diferença de amostra entre os dois braços.

Foram geradas 500 réplicas com semente 20260921. Em cada uma, os 1.784 ciclones elegíveis foram reamostrados com reposição; todos os estados e células de cada seleção foram preservados, e ambos os weightings foram recalculados. A tabela apresenta estimativa observada e IC95% percentil.

| Contraste | Métrica | Estimativa | IC95% |
| --- | --- | ---: | ---: |
| Centered: ciclone − estado | H | +0,00983 | [−0,00444; +0,01156] |
|  | A50 | +15.000 | [−12.500; +20.000] |
|  | A75 | +25.000 | [−10.000; +32.500] |
|  | A90 | +17.500 | [−17.500; +28.812] |
|  | RMS | +41,16 | [+36,36; +45,80] |
| Motion: ciclone − estado | H | +0,01171 | [−0,00239; +0,01356] |
|  | A50 | +25.000 | [−7.500; +27.500] |
|  | A75 | +7.500 | [−27.500; +20.000] |
|  | A90 | −2.500 | [−30.000; +12.500] |
|  | RMS | +41,68 | [+37,14; +46,27] |
| Motion − centered: equal-cyclone | H | −0,00041 | [−0,00883; +0,00847] |
|  | A50 | −22.500 | [−42.500; −5.000] |
|  | A75 | +27.500 | [0; +52.500] |
|  | A90 | +77.500 | [+48.688; +107.500] |
|  | RMS | +8,21 | [+5,57; +11,07] |

<figure class="result-figure">
  <img src="../outputs/04_e002_weighting/metric_differences_bootstrap.png" alt="Estimativas e intervalos bootstrap para efeitos do weighting em centered e motion-relative e para motion menos centered sob equal-cyclone.">
  <figcaption>Diferenças pontuais e IC95% por ciclone. Cada painel possui sua própria unidade; a linha vertical marca ausência de diferença.</figcaption>
</figure>

**Observação:** os IC das áreas e de H para o efeito do weighting incluem zero, mas o aumento de RMS é consistente nas duas representações. Sob *equal-cyclone*, A50 favorece *motion-relative*, enquanto A90 e RMS favorecem *centered*; H inclui zero e A75 toca zero. **Interpretação:** há evidência de maior dispersão radial entre ciclones igualmente ponderados, mas não de uma mudança coerente em todas as medidas de concentração. **Limitação:** o bootstrap quantifica incerteza interna deste experimento; não substitui análise de influência, remoção de ciclones ou validação fora da amostra.

## Em resumo: o que este método faz?

E-002 congela tudo o que E-001 fixou — população, threshold, suporte, geometria e bins — e mexe em um único parâmetro: quem recebe uma unidade de peso. Sob *equal-state*, cada estado com excedência vale um, de modo que ciclones com muitos estados participam muitas vezes. Sob *equal-cyclone*, cada ciclone vale um e reparte esse valor entre seus próprios estados. As duas escolhas produzem mapas espaciais diferentes sobre exatamente a mesma grade. Comparando as métricas de concentração entre os dois mapas, o experimento mede quanto da estrutura observada em E-001 vinha da participação desigual dos ciclones mais longos; comparando as orientações dentro de cada weighting, verifica se a conclusão de E-001 depende dessa escolha.

## Interpretação

O esquema *equal-state* não foi dominado por um ciclone ou por um grupo minúsculo, mas deu influência agregada material aos sistemas com mais estados positivos: os 10% superiores receberam 22,52% da massa, e $N_{eff}$ caiu de 1.757 para 1.288,8. Remover essa desigualdade deslocou cerca de 8% da massa espacial e aumentou RMS em aproximadamente 41 km.

Essas mudanças quantitativas não alteraram a narrativa de orientação. Sob ambos os estimandos, *motion-relative* concentra A50 e dispersa A75, A90 e RMS em relação a *centered*. E-002 é, portanto, **ROBUSTO AO WEIGHTING** segundo o critério registrado.

## Limitações

- q95 permaneceu fixo; q90, q99 e thresholds físicos não foram testados.
- O produto de vento é um recorte condicionado de 2010–2020 e não uma climatologia completa.
- Duração representada não é duração física completa e também depende de suporte, heading e ocorrência q95.
- Fases foram analisadas como fornecidas e agrupadas segundo E-001; não se controlou intensidade.
- Não houve remoção de ciclones influentes, *leave-one-cyclone-out* nem validação em grupos não usados na construção.
- A análise compara distribuições condicionadas à ocorrência; não estima *coverage probability*, magnitude condicional, *footprint* probabilístico ou hazard geográfico.

## Conclusão

O weighting altera de forma mensurável a distribuição — TV próxima de 0,079 e RMS cerca de 41 km maior sob peso igual por ciclone — mas não muda qualitativamente a comparação entre orientações. A conclusão de E-001 permanece `INCONCLUSIVE` sob seu protocolo original e mostrou-se **ROBUSTA AO WEIGHTING** em E-002.

## Consequência para o projeto

Nenhum weighting foi eleito universalmente principal. Conforme [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado), *equal-state* deve ser usado quando a pergunta-alvo é sobre a população de estados q95-positivos; *equal-cyclone*, quando a pergunta é sobre a população de ciclones q95-positivos. O estimando deve ser declarado e o outro weighting deve permanecer como análise de sensibilidade quando pertinente.

Também não foi adotada uma orientação espacial superior. O próximo teste independente é a sensibilidade ao threshold; lifecycle versus intensidade, estabilidade e generalização por ciclone e o modelo probabilístico completo permanecem futuros.

## Reprodutibilidade

O protocolo congelado está em `scripts/04_e002_weighting/protocol.json`; o código e os testes, em `scripts/04_e002_weighting/`; e os produtos, em `outputs/04_e002_weighting/`. `summary.json` registra hashes das entradas, protocolo, script e resumo de E-001, além da semente. `cyclone_contributions.csv`, `metrics.csv`, `metric_comparisons.csv`, `bootstrap_differences.csv`, `spatial_distributions.csv` e `contribution_concentration_by_phase.csv` preservam os resultados tabulares. A sequência de execução está em [proveniência e reprodutibilidade](reproducibility.md#e-002--sensibilidade-ao-weighting).

## Respostas finais de E-002

1. **Ciclones com muitos estados dominavam materialmente E-001?** Havia desigualdade material agregada, mas não domínio por poucos eventos: os 10% superiores reuniam 22,52% da massa, o maior ciclone apenas 0,21%, e $N_{eff}=1.288,8$ entre 1.757 ciclones positivos.
2. **Dar peso igual a cada ciclone altera de forma cientificamente relevante a estrutura?** Sim, de forma moderada: cerca de 8% da massa foi redistribuída e RMS aumentou aproximadamente 41 km. A maior parte dos IC para H e áreas inclui zero, portanto a mudança não é coerente em todas as métricas.
3. **A conclusão de E-001 permanece robusta?** Sim. O conflito entre núcleo e cauda permanece e nenhuma orientação se torna consistentemente superior.
