# Plano científico

## Finalidade desta página

Este plano mantém separadas a ambição científica, a evidência já produzida e as possibilidades futuras. Um item proposto não deve ser descrito como metodologia executada. Os estados usados aqui são:

- **PROPOSTO:** direção ou pergunta ainda sem protocolo completo;
- **EM TESTE:** experimento em execução, sem conclusão;
- **ADOTADO:** escolha sustentada pela evidência registrada;
- **REJEITADO:** alternativa testada e incompatível com o critério definido;
- **INCONCLUSIVO:** evidência insuficiente ou ambígua;
- **AINDA NÃO TESTADO:** possibilidade que ainda não entrou em experimento.
- **DESCRITO:** padrão observado exploratoriamente, ainda sem teste de hipótese.

## Pergunta central

Como representar onde ventos extremos tendem a ocorrer em relação a um ciclone extratropical, que geometria formam e que magnitude alcançam ao longo de seu ciclo de vida, sem confundir esse padrão relativo à tempestade com hazard em posições geográficas fixas?

## Ideia de trabalho

O referencial *storm-relative* expressa cada posição pela distância e direção em relação ao centro do ciclone. Uma variante *motion-relative* orienta essas posições pelo deslocamento da tempestade, distinguindo frente, trás, esquerda e direita. A ideia é que alinhar eventos dessa forma possa revelar organização espacial que seria diluída em latitude e longitude absolutas.

E-001 testou essa hipótese e encontrou evidência mista: o referencial relativo ao movimento concentrou o núcleo A50, mas aumentou A75, A90 e RMS. A escolha da orientação permanece **INCONCLUSIVA**; também não foi demonstrado que as fases expliquem diferenças além da seleção da amostra ou que um modelo específico seja adequado.

## Perguntas científicas e estado

| Pergunta | Estado | O que já existe | Evidência ainda necessária |
| --- | --- | --- | --- |
| Quais dados de track e lifecycle sustentam a amostra? | **ADOTADO** | Zenodo 18133432 como fonte operacional; correspondência exata com o recorte atual. | Reavaliar somente se surgir nova versão ou fonte oficial substituta. |
| Como construir estados compatíveis com ERA5 de 6 h? | **ADOTADO** | Associação ao horário mais próximo, tolerância de 3 h e desempate documentado. | Testes futuros podem avaliar sensibilidade, mas a regra atual está validada contra o dado existente. |
| Como interpretar as fases do lifecycle? | **INCONCLUSIVO** | Origem dos rótulos e semântica geral conhecidas. | Versão, parâmetros, configuração e artefatos da execução original do CycloPhaser. |
| Onde aparecem diferenças descritivas entre fases e quadrantes? | **DESCRITO** | A fase madura tem os maiores quantis pontuais no recorte; quadrantes têm medianas próximas. | Inferência por ciclone, controle da seleção e avaliação de incerteza. |
| O que constitui um extremo e um evento espacial? | **PROPOSTO** | q95 foi controle preregistrado de E-001, não definição final; também existem flags fixas, q90 e q99. | Justificativa científica do limiar, unidade de evento, denominador e análise de sensibilidade. |
| A orientação pelo movimento organiza melhor as excedências? | **INCONCLUSIVO** | E-001 comparou 1.784 ciclones; A50 melhorou, A75, A90 e RMS pioraram, e a entropia foi incerta. | Novo protocolo que isole uma explicação por vez, sem ajuste retrospectivo. |
| Como estimar ocorrência e geometria relativas ao ciclone? | **AINDA NÃO TESTADO** | E-001 comparou uma distribuição normalizada de ocorrências, não uma coverage probability. | Definição do estimando, validação entre ciclones e diagnósticos. |
| Como estimar magnitude condicionada à ocorrência? | **AINDA NÃO TESTADO** | Velocidade do vento está disponível nos pontos selecionados. | Definição da distribuição-alvo, tratamento da seleção e validação. |
| Como traduzir o padrão relativo para hazard geográfico? | **AINDA NÃO TESTADO** | Apenas direção conceitual. | Frequência de eventos, trajetórias, duração, ocorrência e magnitude validadas. |

## Fluxo de trabalho científico

O fluxograma resume a ordem lógica do projeto. Verde indica infraestrutura ou análise concluída; amarelo marca uma pendência ativa; azul identifica o próximo teste que precisa ser protocolado; cinza indica etapas futuras que ainda não devem ser descritas como metodologia executada.

<div class="project-flow" role="group" aria-label="Etapas do projeto científico">
  <div class="flow-legend" aria-label="Legenda dos estados">
    <span><i class="flow-dot completed"></i>Concluído</span>
    <span><i class="flow-dot current"></i>Pendência ativa</span>
    <span><i class="flow-dot next"></i>Próximo teste</span>
    <span><i class="flow-dot future"></i>Futuro</span>
  </div>
  <ol class="flow-list">
    <li class="flow-step completed">
      <span class="flow-marker" aria-hidden="true">✓</span>
      <div class="flow-content"><span class="flow-status">Concluído</span><h3>Base observacional</h3><p>Fonte operacional, catálogo horário, associação ao ERA5 de 6 h e suporte espacial foram reconstruídos e validados.</p></div>
    </li>
    <li class="flow-step completed">
      <span class="flow-marker" aria-hidden="true">✓</span>
      <div class="flow-content"><span class="flow-status">Concluído</span><h3><a href="exploratory_analysis.md">Análise exploratória</a></h3><p>Tracks, fases, distribuições de vento, ocorrência de excedências, quadrantes e um caso individual foram descritos.</p></div>
    </li>
    <li class="flow-step current">
      <span class="flow-marker" aria-hidden="true">!</span>
      <div class="flow-content"><span class="flow-status">Pendência ativa</span><h3><a href="open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases">Proveniência do lifecycle</a></h3><p>A origem dos rótulos está confirmada; versão, parâmetros e artefatos da execução original do CycloPhaser permanecem desconhecidos.</p></div>
    </li>
    <li class="flow-step completed">
      <span class="flow-marker" aria-hidden="true">✓</span>
      <div class="flow-content"><span class="flow-status">Concluído · inconclusivo</span><h3><a href="e001_orientation.md">E-001 — orientação pelo movimento</a></h3><p>O protocolo pareado foi executado; núcleo, cauda e fases não concordaram, portanto nenhuma representação foi adotada.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">2</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Ocorrência e geometria</h3><p>Estimar onde excedências tendem a ocorrer e caracterizar seus conjuntos espaciais, com validação entre ciclones.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">3</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Magnitude condicional</h3><p>Descrever a intensidade do vento quando a excedência ocorre, sem confundi-la com probabilidade de ocorrência.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">4</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Validação e robustez</h3><p>Avaliar generalização, sensibilidade às escolhas e estabilidade dos resultados em ciclones não usados no ajuste.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">5</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Hazard geográfico</h3><p>Combinar frequência, trajetórias, duração, ocorrência e magnitude somente depois que os componentes forem validados.</p></div>
    </li>
  </ol>
</div>

## Sequência prevista

### 1. Base observacional — concluída para o estágio atual

A proveniência das tracks foi estabelecida, a ponte temporal para ERA5 foi reconstruída e o suporte espacial foi explicitado. O recorte condicionado de vento foi caracterizado e suas convenções foram recuperadas.

### 2. Exploração descritiva — concluída

A análise disponível descreveu cobertura das tracks, distribuições pontuais de vento, ocorrência de excedências por estado, contrastes por fase e quadrante e um evento individual. Ela gerou hipóteses, não testes confirmatórios.

### 3. E-001 — orientação pelo movimento — concluído e inconclusivo

O primeiro experimento fixou q95, suporte, weighting por estado, grade de 50 km, métricas e critério antes do resultado. A comparação pareada mostrou concentração maior somente no núcleo A50, acompanhada por A75, A90 e RMS maiores e efeitos discordantes por fase. O [relatório E-001](e001_orientation.md) preserva a hipótese, o resultado negativo parcial e a consequência: nenhuma orientação principal foi adotada.

### 4. Ocorrência, geometria e magnitude — ainda não testadas

A execução de E-001 não autorizou escolher uma representação principal nem ajustar modelos. *Coverage probability* significa, neste projeto, a probabilidade condicional de uma posição relativa pertencer a um conjunto de excedência; magnitude condicional responde quanto vento ocorre quando há excedência. São perguntas diferentes e devem permanecer separadas.

### 5. Hazard geográfico — futuro

Um *footprint* relativo ao ciclone não é, por si só, hazard. A tradução exigirá incorporar a frequência dos ciclones, suas trajetórias, duração dos estados e distribuições condicionais. Nenhuma dessas combinações foi executada.

## Critério permanente de avanço

Uma etapa só muda de **PROPOSTO** para **EM TESTE** quando seu protocolo identifica dados e versão, unidade de análise, variáveis, método, métricas e critério de decisão. Ela só passa a **ADOTADO**, **REJEITADO** ou **INCONCLUSIVO** depois que resultados, diagnósticos, limitações e consequência para o projeto forem registrados.
