# Questões abertas

Este registro distingue o que ainda precisa ser decidido do que já tem evidência. IDs `Q-...` são persistentes; ao resolver uma questão, preserve a entrada e aponte para a evidência e a decisão correspondentes. Status possíveis: `OPEN`, `UNDER_TEST`, `RESOLVED`, `DEFERRED`.

## Q-001 · Qual é a unidade de uma linha e como ela se vincula a um ciclone?

- **Status:** `RESOLVED`
- **Resposta atual:** a unidade de análise é o ciclone, identificado por `track_id`; há 1.781 ciclones distintos. Uma linha armazena um ponto de grade associado a um ciclone e instante. A chave mínima (`track_id`, `time`, `lat`, `lon`) não tem duplicatas no conjunto atual.
- **Evidência:** [`COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`](../data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md), verificação direta do arquivo e [D-002](decisions.md#d-002--usar-o-ciclone-como-unidade-de-análise).

## Q-002 · Como foram gerados `wind_speed` e os indicadores de excedência?

- **Status:** `RESOLVED`
- **Resposta atual:** `wind_speed` é calculado como `sqrt(u10² + v10²)` a partir do ERA5 single-levels na grade nativa de 0,25°. Os percentis locais usam todos os 16.072 campos de 6 h entre 2010-01-01 00:00 e 2020-12-31 18:00 UTC, ou seja, **11 anos civis completos**, sem estratificação e sem máscara terra/oceano. `numpy.percentile` foi usado ponto a ponto com o método padrão `linear`.
- **Seleção das linhas:** um ponto é emitido quando `distance_km <= 1100` e `wind_speed > min(15,6; q90_local)`. As seis flags são calculadas depois da seleção, sempre com comparação estrita `>`.
- **Explicação das 13.404 linhas com `exceeded_q90 = false`:** elas entram pelo limiar fixo de 15,6 m/s em locais onde `q90_local > 15,6`; no arquivo local, todas têm `15,6 < wind_speed <= q90_local`.
- **Evidência:** reconstrução do fluxo e referências de código em [`solicitacao_agente_q002_q003.md`](solicitacao_agente_q002_q003.md#q-002--como-foram-gerados-wind_speed-e-os-indicadores-de-excedência), acompanhada de verificação das contagens no arquivo local.
- **Ressalvas de proveniência:** a versão/reprocessamento exato do ERA5 (`expver`) e uma versão formal do `local_percentiles.nc` não foram recuperados. Essas lacunas limitam a identificação exata dos insumos, mas não deixam a regra de cálculo ou seleção desconhecida.

## Q-003 · Quais são as convenções espaciais e temporais usadas neste arquivo?

- **Status:** `RESOLVED`
- **Centro e tempo:** `lat_center` e `lon_center` vêm das colunas `lat vor` e `lon vor` do catálogo de tracks. A posição não é interpolada; cada hora de track é associada ao campo ERA5 de 6 h mais próximo, com diferença máxima de 3 h, mantendo uma posição por (`track_id`, instante ERA5).
- **Distância e domínio:** `distance_km` usa haversine sobre esfera com raio de 6.371 km. O domínio regular de 0,25° vai de 10°S a 65°S e de 85°W a 15°W. O círculo de 1.100 km é truncado nas bordas sem sinalização em coluna.
- **Quadrante fixo:** os códigos 1–4 são NO, NE, SE e SO, calculados pelos sinais de `Δlat` e `Δlon`. Os eixos pertencem ao norte e ao leste; o ponto coincidente com o centro cai em NE.
- **Quadrante relativo ao movimento:** a direção usa diferença centrada entre centros vizinhos na série de 6 h, intervalo nominal de 12 h; nas pontas usa diferença simples de 6 h. O vetor é normalizado após corrigir longitude por `cos(lat)`. Deslocamento nulo usa fallback para leste. Os códigos são frente-esquerda, frente-direita, trás-direita e trás-esquerda.
- **Evidência:** fórmulas, pseudocódigo e referências em [`solicitacao_agente_q002_q003.md`](solicitacao_agente_q002_q003.md#q-003--quais-convenções-espaciais-e-temporais-foram-usadas), além das verificações locais de 0 chaves duplicadas, 1.833 estados com centro fora do domínio e 414.124 pontos-hora associados a mais de um ciclone.
- **Limitações conhecidas:** a justificativa metodológica original do raio de 1.100 km não foi localizada e o número de casos que usou fallback de direção exige reprocessar o catálogo. Essas lacunas não deixam a convenção de cálculo desconhecida.

## Q-004 · Como foram produzidas e como devem ser tratadas as fases?

- **Status:** `OPEN`
- **Fatos confirmados:** `phase` é copiada da coluna `period` do catálogo de tracks; não é calculada pelo pipeline de vento. O sufixo `2` identifica um segundo ciclo dentro da mesma track. As 509.788 linhas sem fase propagam horas que já estavam sem `period` no catálogo, em geral no início ou fim das trajetórias; 677 ciclones possuem alguma linha sem fase e 2 têm todas as linhas sem fase.
- **Uso atual:** a análise exploratória agrupa as categorias com sufixo `2` às fases principais apenas para apresentação, conforme [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias). Ausências permanecem como categoria separada e seu volume deve ser informado em análises por fase.
- **Por que permanece aberta:** não foi localizada a definição operacional de `incipient`, `intensification`, `mature`, `decay` e `residual`, nem a regra que inicia um segundo ciclo. Essa evidência pertence ao processo que gerou o catálogo externo.
- **Evidência necessária:** código ou referência metodológica da classificação `period` no catálogo `tracks_SAt_filtered_with_periods.csv`.
