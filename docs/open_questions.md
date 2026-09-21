# Questões abertas

## Como este registro funciona

Questões recebem IDs persistentes e continuam no histórico depois de resolvidas. Os status são `OPEN`, `UNDER_TEST`, `RESOLVED` e `DEFERRED`. Uma questão só é resolvida no escopo que sua resposta declara; incertezas remanescentes devem ser vinculadas a uma nova pergunta, e não ocultadas.

## Prioridades atuais

| Questão | Status | Dependência científica |
| --- | --- | --- |
| [Q-004 — reprodução das fases](#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases) | `OPEN` | Uso confirmatório do lifecycle e eventual reclassificação |
| [Q-006 — definição de extremo e objeto espacial](#q-006--qual-definição-de-extremo-e-de-objeto-espacial-será-adotada) | `OPEN` | Modelos posteriores; q95 em E-001 foi apenas uma escolha operacional preregistrada |
| [Q-007 — escolha da orientação](#q-007--a-orientação-pelo-movimento-organiza-melhor-as-excedências) | `OPEN` | E-001 foi inconclusivo; E-002 mostrou que isso é robusto ao weighting |
| [Q-009 — lifecycle além da intensidade](#q-009--o-lifecycle-acrescenta-informação-além-da-intensidade) | `DEFERRED` | Experimento posterior à sensibilidade ao threshold |
| [Q-010 — generalização por ciclone](#q-010--os-padrões-são-estáveis-e-generalizam-para-outros-ciclones) | `DEFERRED` | Validação antes do modelo probabilístico completo |
| [Q-011 — arquitetura de ocorrência](#q-011--qual-arquitetura-deve-representar-a-ocorrência-probabilística) | `DEFERRED` | Somente depois de threshold, lifecycle e generalização |

## Q-001 · Qual é a unidade de uma linha e como ela se vincula a um ciclone?

- **Status:** `RESOLVED`
- **Por que importa:** confundir pontos de grade com eventos independentes produziria pseudorreplicação e conclusões excessivamente precisas.
- **O que sabemos:** a unidade científica fundamental é o ciclone, identificado por `track_id`; há 1.781 no recorte atual. Uma linha armazena um ponto de grade associado a um ciclone e instante. A chave `track_id + time + lat + lon` não tem duplicatas.
- **O que ainda não sabemos:** análises futuras podem exigir estados ou *excursion sets* como unidade intermediária; isso deverá ser definido por pergunta, mantendo o agrupamento por ciclone.
- **Evidência que resolveu a questão:** documentação das colunas, inspeção direta das chaves e [D-002](decisions.md#d-002--usar-o-ciclone-como-unidade-de-análise).
- **Parte do projeto que depende da resposta:** contagens, desenho de treino e teste, inferência e validação.

## Q-002 · Como foram gerados `wind_speed` e os indicadores de excedência?

- **Status:** `RESOLVED` quanto à regra de cálculo e seleção; permanecem lacunas de versão dos insumos.
- **Por que importa:** a seleção do arquivo condiciona todas as distribuições, ausências e comparações exploratórias.
- **O que sabemos:** `wind_speed` é a magnitude do vento ERA5 a 10 m na grade de 0,25°. Os percentis locais usam 16.072 campos de 6 h de 2010–2020, sem estratificação ou máscara terra–oceano, com interpolação `linear` de percentis. Uma linha entra quando está a até 1.100 km e satisfaz `wind_speed > min(15,6 m/s; q90_local)`; todas as flags usam comparação estrita `>`.
- **O que ainda não sabemos:** versão/reprocessamento ERA5 (`expver`) e versão formal do arquivo de percentis. As 13.404 linhas com `exceeded_q90 = false` são explicadas pelo limiar fixo em locais onde `q90_local > 15,6`, mas a proveniência exata dos insumos continua incompleta.
- **Evidência necessária para fechar a proveniência restante:** manifesto ou arquivos originais com versão, hash e metadados do ERA5 e dos percentis.
- **Parte do projeto que depende da resposta:** reprodução literal do produto original. E-001 usou as flags existentes como entrada versionada e não apresentou o arquivo como reconstrução do ERA5 original.
- **Evidência atual:** [investigação técnica de Q-002 e Q-003](internal/q002_q003_provenance.md) e contagens verificadas no arquivo local.

## Q-003 · Quais são as convenções espaciais e temporais usadas neste arquivo?

- **Status:** `RESOLVED` quanto às convenções computacionais.
- **Por que importa:** tempo, distância, domínio e orientação determinam quais pontos pertencem a cada estado e quadrante.
- **O que sabemos:** centros vêm de `lat vor` e `lon vor`; a track é associada ao campo de 6 h mais próximo, sem interpolação e com diferença máxima de 3 h. A distância é haversine numa esfera de 6.371 km, o domínio é 65°S–10°S e 85°W–15°W, e o raio é 1.100 km. Quadrantes fixos e relativos ao movimento, inclusive desempates e fallback leste, estão reproduzidos.
- **O que ainda não sabemos:** a justificativa científica do raio. E-001 substituiu o fallback leste por um critério explícito: 284 de 23.334 estados com suporte tinham translação abaixo de 5 km/h e foram excluídos da comparação pareada.
- **Evidência necessária para avaliar adequação:** justificativa original ou análise de sensibilidade futura do raio. A confiabilidade do heading usada em E-001 está documentada no próprio experimento.
- **Parte do projeto que depende da resposta:** reconstrução do suporte está resolvida; adoção científica de raio e representação depende de [Q-006](#q-006--qual-definição-de-extremo-e-de-objeto-espacial-será-adotada).
- **Evidência atual:** [investigação técnica de Q-002 e Q-003](internal/q002_q003_provenance.md), zero chaves duplicadas, 1.833 estados presentes com centro fora do domínio e 414.124 pontos–hora ligados a mais de um ciclone.

## Q-004 · Como foram produzidas e como devem ser tratadas as fases?

- **Status:** `OPEN`
- **Por que importa:** fases delimitam comparações científicas e podem se tornar covariáveis de modelos futuros; fronteiras não reproduzíveis limitam auditoria e sensibilidade.
- **O que sabemos:** `phase` copia `period` do Zenodo 18133432. A fonte declara uso do CycloPhaser e contém `incipient`, `intensification`, `mature`, `decay`, repetições com sufixo `2`, `residual` e 50.069 horas nulas. Todos os 20.101 estados presentes correspondem exatamente ao recorte de vento. O sufixo indica repetição não contígua; [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias) permite agrupamento preregistrado por tipo físico quando os valores literais também forem preservados.
- **O que ainda não sabemos:** versão do CycloPhaser, parâmetros, suavização, filtros, configuração, ambiente e artefatos intermediários da execução original.
- **Evidência necessária:** ambiente e configuração originais ou nova classificação versionada, preservada como produto distinto e validada contra o catálogo atual.
- **Parte do projeto que depende da resposta:** análises confirmatórias por fase e qualquer substituição dos rótulos. A descrição dos rótulos fornecidos pode continuar com a limitação explícita.

## Q-005 · Qual é a fonte operacional dos estados de track e lifecycle?

- **Status:** `RESOLVED`
- **Por que importa:** o recorte condicionado perde estados inteiros e a referência histórica usa outro namespace; sem fonte canônica, o denominador temporal seria ambíguo.
- **O que sabemos:** o Zenodo 18133432 é a fonte operacional. Ele gera 631.009 horas de 6.789 tracks e 109.857 estados de 6 h. No período comparável, há 29.311 estados: 20.101 presentes, 3.233 ausentes com suporte e 5.977 sem suporte. O Mendeley V4 permanece referência histórica.
- **O que ainda não sabemos:** nada que impeça o uso operacional atual; novas versões da fonte exigirão nova validação.
- **Evidência que resolveu a questão:** [`provenance_manifest.json`](../outputs/00_data_acquisition/provenance_manifest.json), [`validation_report.json`](../outputs/00_data_acquisition/validation_report.json) e [D-004](decisions.md#d-004--adotar-o-zenodo-18133432-como-fonte-canônica-operacional-das-tracks-e-do-lifecycle).
- **Parte do projeto que depende da resposta:** preparação da amostra, suporte espacial e reprodutibilidade de todas as análises posteriores.

## Q-006 · Qual definição de extremo e de objeto espacial será adotada?

- **Status:** `OPEN`
- **Por que importa:** threshold, evento, suporte e denominador determinam o significado de ocorrência, geometria e magnitude. Sem essas definições, modelos distintos podem responder a perguntas incompatíveis.
- **O que sabemos:** o produto atual oferece limiares fixos e quantis locais, mas foi criado como recorte experimental. Células e estados ausentes podem ser classificados apenas depois de verificar suporte. Evento, *excursion set*, *footprint* e hazard são objetos diferentes.
- **O que ainda não sabemos:** threshold científico, período de referência, unidade do evento, tratamento de suporte parcial, raio adotado, estimando espacial e critério para comparar alternativas.
- **Evidência necessária:** comparação preregistrada das definições candidatas sem escolher o threshold por aparência. E-001 e E-002 fixaram q95 exclusivamente para isolar orientação e weighting e não resolveram esta pergunta mais ampla. O próximo experimento proposto considera q90, q95, q99 e thresholds físicos.
- **Parte do projeto que depende da resposta:** modelos de ocorrência, geometria, magnitude e hazard. E-001 pôde ser executado porque tratou q95 como controle fixo, não como definição final.

## Q-007 · A orientação pelo movimento organiza melhor as excedências?

- **Status:** `OPEN` após E-001 `INCONCLUSIVE`; E-002 resolveu apenas a explicação concorrente de weighting.
- **Por que importa:** uma representação principal inadequada pode borrar estrutura comum ou introduzir complexidade sem ganho global.
- **O que sabemos:** [E-001](e001_orientation.md) comparou os mesmos 1.784 ciclones, 23.050 estados, células e flags q95. *Motion-relative* reduziu A50, mas aumentou A75, A90 e RMS; a diferença de entropia incluiu zero e as fases discordaram. [E-002](e002_weighting.md) deu massa total igual aos ciclones e preservou o conflito: ΔA50 = −22.500 km², ΔA75 = +27.500 km², ΔA90 = +77.500 km² e ΔRMS = +8,21 km.
- **O que ainda não sabemos:** se outro threshold preregistrado, normalização pelo tamanho ou estratificação física explicam o conflito entre núcleo e cauda. Weighting por ciclone deixou de ser uma explicação suficiente, mas as demais hipóteses não podem ser ajustadas retrospectivamente dentro de E-001.
- **Evidência necessária:** novo protocolo que altere um fator por vez, preserve o pareamento e mantenha o ciclone como unidade de incerteza.
- **Parte do projeto que depende da resposta:** escolha de representação para modelos espaciais posteriores. Conforme [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001), nenhuma representação foi adotada como superior.

## Q-008 · A conclusão de E-001 depende do weighting por estado?

- **Status:** `RESOLVED` no escopo q95 de E-002.
- **Por que importa:** ciclones com mais estados q95-positivos recebem mais massa em *equal-state* e poderiam determinar o conflito entre núcleo e cauda.
- **O que sabemos:** [E-002](e002_weighting.md) encontrou $N_{eff}=1.288,8$ em *equal-state* e 1.757 em *equal-cyclone*. Embora aproximadamente 8% da massa tenha sido redistribuída, *motion-relative* continuou reduzindo A50 e aumentando A75, A90 e RMS.
- **Resposta:** a conclusão qualitativa de E-001 é robusta ao weighting por estado versus por ciclone. Isso não torna os mapas idênticos nem escolhe um estimando universal.
- **Evidência que resolveu a questão:** regressão exata de E-001, quatro distribuições, TV, métricas por fase e bootstrap por `track_id` em E-002.
- **Parte do projeto que depende da resposta:** [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado) separa os estimandos e mantém a escolha de orientação aberta.

## Q-009 · O lifecycle acrescenta informação além da intensidade?

- **Status:** `DEFERRED`; ainda não testado.
- **Por que importa:** diferenças entre fases podem refletir mudança física do ciclo de vida ou apenas seleção por intensidade.
- **O que sabemos:** análises descritivas e estratos de E-001/E-002 mostram heterogeneidade, mas não controlam intensidade.
- **O que ainda não sabemos:** se fase preserva informação espacial ou preditiva condicional à intensidade do ciclone.
- **Evidência necessária:** experimento independente, posterior à sensibilidade ao threshold, com intensidade explicitamente controlada e validação por ciclone.
- **Parte do projeto que depende da resposta:** seleção de covariáveis para um futuro modelo de ocorrência.

## Q-010 · Os padrões são estáveis e generalizam para outros ciclones?

- **Status:** `DEFERRED`; ainda não testado de forma abrangente.
- **Por que importa:** intervalos internos não demonstram desempenho em eventos não usados na construção.
- **O que sabemos:** E-001 e E-002 reamostraram `track_id` para incerteza local; E-002 também quantificou concentração de contribuição.
- **O que ainda não sabemos:** influência de eventos individuais, estabilidade após remoção e generalização fora da amostra.
- **Evidência necessária:** bootstrap ampliado, influência ou remoção, *leave-one-cyclone-out* ou validação por grupos e estabilidade de superfícies e métricas.
- **Parte do projeto que depende da resposta:** qualquer modelo probabilístico completo e afirmação de generalização.

## Q-011 · Qual arquitetura deve representar a ocorrência probabilística?

- **Status:** `DEFERRED`; ainda não testado.
- **Por que importa:** um modelo complexo não deve ser adotado antes de fixar estimando, threshold e estratégia de validação.
- **O que sabemos:** posição *storm-relative*, lifecycle, intensidade, translação, tamanho e heterogeneidade entre ciclones são candidatas conceituais.
- **O que ainda não sabemos:** família estatística, necessidade de GAM/GAMM, conjunto de covariáveis e ganho sobre benchmarks simples.
- **Evidência necessária:** protocolo posterior às etapas de threshold, lifecycle e generalização, com validação em ciclones não usados no ajuste.
- **Parte do projeto que depende da resposta:** ocorrência probabilística; magnitude condicional e hazard permanecem etapas separadas.
