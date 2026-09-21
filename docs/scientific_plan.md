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

E-001 testou essa hipótese e encontrou evidência mista: o referencial relativo ao movimento concentrou o núcleo A50, mas aumentou A75, A90 e RMS. E-002 mostrou que esse conflito é **ROBUSTO AO WEIGHTING** por estado versus por ciclone. A escolha da orientação permanece **INCONCLUSIVA**; os dois weightings são mantidos para estimandos diferentes, e ainda não foi demonstrado que as fases expliquem diferenças além da intensidade ou que um modelo específico seja adequado.

## Perguntas científicas e estado

| Pergunta | Estado | O que já existe | Evidência ainda necessária |
| --- | --- | --- | --- |
| Quais dados de track e lifecycle sustentam a amostra? | **ADOTADO** | Zenodo 18133432 como fonte operacional; correspondência exata com o recorte atual. | Reavaliar somente se surgir nova versão ou fonte oficial substituta. |
| Como construir estados compatíveis com ERA5 de 6 h? | **ADOTADO** | Associação ao horário mais próximo, tolerância de 3 h e desempate documentado. | Testes futuros podem avaliar sensibilidade, mas a regra atual está validada contra o dado existente. |
| Como interpretar as fases do lifecycle? | **INCONCLUSIVO** | Origem dos rótulos e semântica geral conhecidas. | Versão, parâmetros, configuração e artefatos da execução original do CycloPhaser. |
| Onde aparecem diferenças descritivas entre fases e quadrantes? | **DESCRITO** | A fase madura tem os maiores quantis pontuais no recorte; quadrantes têm medianas próximas. | Inferência por ciclone, controle da seleção e avaliação de incerteza. |
| O que constitui um extremo e um evento espacial? | **PROPOSTO** | q95 foi controle preregistrado de E-001, não definição final; também existem flags fixas, q90 e q99. | Justificativa científica do limiar, unidade de evento, denominador e análise de sensibilidade. |
| A orientação pelo movimento organiza melhor as excedências? | **INCONCLUSIVO** | E-001 comparou 1.784 ciclones; A50 melhorou, A75, A90 e RMS pioraram, e a entropia foi incerta. | Novo protocolo que isole uma explicação por vez, sem ajuste retrospectivo. |
| O conflito de orientação depende do weighting? | **ADOTADO: ROBUSTO** | E-002 reproduziu E-001 e manteve o conflito núcleo–cauda sob peso igual por ciclone. | Reavaliar apenas se outro estimando ou população for declarado. |
| Lifecycle acrescenta informação além da intensidade? | **AINDA NÃO TESTADO** | Contrastes descritivos e estratos de E-001/E-002 não controlaram intensidade. | Experimento futuro com intensidade explicitamente controlada. |
| Os padrões generalizam entre ciclones? | **AINDA NÃO TESTADO** | Bootstrap interno quantificou incerteza local em E-001/E-002. | Influência, remoção de ciclones e validação fora da amostra ou por grupos. |
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
    <li class="flow-step completed">
      <span class="flow-marker" aria-hidden="true">✓</span>
      <div class="flow-content"><span class="flow-status">Concluído · inconclusivo</span><h3><a href="e001_orientation.md">E-001 — orientação pelo movimento</a></h3><p>O protocolo pareado foi executado; núcleo, cauda e fases não concordaram, portanto nenhuma representação foi adotada.</p></div>
    </li>
    <li class="flow-step completed">
      <span class="flow-marker" aria-hidden="true">✓</span>
      <div class="flow-content"><span class="flow-status">Concluído · robusto</span><h3><a href="e002_weighting.md">E-002 — weighting</a></h3><p>Peso igual por ciclone alterou detalhes quantitativos, mas preservou o conflito núcleo–cauda de E-001.</p></div>
    </li>
    <li class="flow-step next">
      <span class="flow-marker" aria-hidden="true">→</span>
      <div class="flow-content"><span class="flow-status">Próximo · proposto</span><h3>Sensibilidade ao threshold</h3><p>Comparar q90, q95, q99 e thresholds físicos sem escolher o limiar por aparência.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">1</span>
      <div class="flow-content"><span class="flow-status">Futuro · proposto</span><h3>Lifecycle versus intensidade</h3><p>Testar se a fase acrescenta informação depois de controlar a intensidade do ciclone.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">2</span>
      <div class="flow-content"><span class="flow-status">Futuro · proposto</span><h3>Estabilidade e generalização</h3><p>Avaliar influência, remoção de ciclones e desempenho em eventos ou grupos não usados na construção.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">3</span>
      <div class="flow-content"><span class="flow-status">Futuro · ainda não testado</span><h3>Modelo probabilístico de ocorrência</h3><p>Comparar uma arquitetura candidata a benchmarks simples e validar por ciclones não usados no ajuste.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">4</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Magnitude condicional</h3><p>Modelar a intensidade quando há ocorrência, como componente separado.</p></div>
    </li>
    <li class="flow-step future">
      <span class="flow-marker" aria-hidden="true">5</span>
      <div class="flow-content"><span class="flow-status">Futuro</span><h3>Integração e hazard geográfico</h3><p>Combinar componentes validados com frequência, trajetórias e duração em coordenadas fixas.</p></div>
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

### 4. E-002 — weighting por estado versus por ciclone — concluído e robusto

E-002 alterou somente o weighting. Os 10% de ciclones com mais estados positivos recebiam 22,52% da massa *equal-state*, mas dar massa total igual a cada ciclone preservou o conflito de E-001: *motion-relative* reduziu A50 e aumentou A75, A90 e RMS. O [relatório E-002](e002_weighting.md) adota a conclusão de robustez, não uma orientação universal nem um weighting universal.

### 5. Sensibilidade ao threshold — próximo e proposto

O próximo experimento deverá verificar se estrutura, orientação e efeito do weighting persistem sob q90, q95, q99 e thresholds físicos existentes. A lista é de candidatos: protocolo, threshold final e conclusão ainda não foram fixados.

### 6. Lifecycle versus intensidade — futuro e proposto

A pergunta é se diferenças atribuídas à fase permanecem depois de controlar intensidade. Estratificações atuais não respondem a isso, e nenhum efeito independente do lifecycle foi adotado.

### 7. Estabilidade e generalização por ciclone — futuro e proposto

Esta etapa deverá combinar bootstrap mais abrangente, influência ou remoção de ciclones, *leave-one-cyclone-out* ou validação por grupos e estabilidade das superfícies e métricas. Os bootstraps de E-001 e E-002 são quantificação local de incerteza e não substituem validação fora da amostra.

### 8. Modelo probabilístico completo de ocorrência — futuro e ainda não testado

A direção candidata inclui posição *storm-relative*, lifecycle, intensidade, velocidade de translação, tamanho e heterogeneidade entre ciclones somente se dados e evidência justificarem. Família estatística, GAM/GAMM, efeito obrigatório de lifecycle e conjunto final de covariáveis não foram adotados. O modelo deverá superar benchmarks simples e ser validado por ciclones não usados no ajuste.

### 9. Magnitude condicional — futura e separada

A magnitude do vento quando há ocorrência responde a uma pergunta diferente da probabilidade de ocorrência. Ela será modelada depois que o componente de ocorrência estiver definido e validado.

### 10. Integração e hazard geográfico — futuro

Um *footprint* relativo ao ciclone não é, por si só, hazard. A tradução exigirá incorporar a frequência dos ciclones, suas trajetórias, duração dos estados e distribuições condicionais. Nenhuma dessas combinações foi executada.

Esta ordem é a sequência atualmente pretendida e pode ser revisada quando novas evidências forem produzidas; etapas futuras não são decisões irrevogáveis.

## Critério permanente de avanço

Uma etapa só muda de **PROPOSTO** para **EM TESTE** quando seu protocolo identifica dados e versão, unidade de análise, variáveis, método, métricas e critério de decisão. Ela só passa a **ADOTADO**, **REJEITADO** ou **INCONCLUSIVO** depois que resultados, diagnósticos, limitações e consequência para o projeto forem registrados.
