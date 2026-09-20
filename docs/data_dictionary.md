# Dicionário de dados

Os três produtos abaixo têm unidades de linha diferentes. O catálogo horário é a fonte canônica de centros e lifecycle; o catálogo de 6 h é a ponte temporal e espacial para o ERA5; o Parquet de vento é um recorte condicionado e não substitui nenhum dos dois catálogos.

## A. Catálogo horário canônico

- **Arquivo:** [`data/tracks_SAt_1979_2020.parquet`](../data/tracks_SAt_1979_2020.parquet)
- **Unidade da linha:** uma hora de uma track.
- **Origem:** `tracks_SAt_filtered_with_energetics.csv`, [Zenodo 18133432](https://zenodo.org/records/18133432), DOI [`10.5281/zenodo.18133432`](https://doi.org/10.5281/zenodo.18133432).
- **Dimensão e período:** 631.009 linhas, 6.789 tracks, de 1979-01-01 00:00 a 2021-01-07 00:00 UTC. O nome `1979_2020` identifica as safras de gênese; as últimas tracks iniciadas em 2020 terminam em janeiro de 2021.
- **Integridade:** 9.626.418 bytes; SHA-256 `7d8d628a8d54f9273e1c6280f22bb0082a470d4767393bd3b224a64e8a71c553`.

[`prepare_tracks.py`](../scripts/00_data_acquisition/prepare_tracks.py) lê somente sete das 31 colunas da fonte, ordena por ciclone e hora e grava Parquet com compressão Zstandard. `lon vor`, `lat vor` e `period` são renomeadas; o literal `nan` em `period` vira nulo. Não há agrupamento ou reclassificação de fases.

| Campo | Tipo Parquet | Definição |
| --- | --- | --- |
| `track_id` | `int64` | Identificador do ciclone preservado do Zenodo. |
| `date` | `timestamp[ms]` | Hora original da track; sem timezone armazenado e com semântica UTC. |
| `lon_center` | `double` | Longitude do centro, cópia em `float64` de `lon vor`. |
| `lat_center` | `double` | Latitude do centro, cópia em `float64` de `lat vor`. |
| `vor42` | `double` | Vorticidade relativa no centro da track, preservada da fonte. |
| `region` | `string` | Região de gênese: `ARG`, `LA-PLATA` ou `SE-BR`. |
| `phase` | `string` | Cópia de `period`; nove categorias literais e 50.069 linhas nulas. |

As categorias não nulas são `incipient`, `incipient 2`, `intensification`, `intensification 2`, `mature`, `mature 2`, `decay`, `decay 2` e `residual`. A chave (`track_id`, `date`) é única e cada track é horária sem lacunas internas.

## B. Catálogo de estados associados ao ERA5 de 6 h

- **Arquivo:** [`data/cyclone_states_era5_6h_1979_2020.parquet`](../data/cyclone_states_era5_6h_1979_2020.parquet)
- **Unidade da linha:** um estado único `track_id + time` associado à grade temporal de 6 h.
- **Origem:** transformação do catálogo horário A.
- **Dimensão e período:** 109.857 estados, 6.789 tracks, de 1979-01-01 00:00 a 2021-01-07 00:00 UTC.
- **Integridade:** 2.172.718 bytes; SHA-256 `4865bbc39f273d2360b5735cb26b132d9d01e7af085df94e08fdcd16ce864782`.

A associação usa o campo ERA5 de 6 h mais próximo, com diferença máxima de 3 h; empate de 3 h escolhe o campo anterior. Se mais de uma hora da mesma track for associada ao mesmo campo, permanece a de menor diferença e, em novo empate, a anterior. A geometria de suporte conta células da grade de 0,25° em latitudes −65 a −10 e longitudes −85 a −15 cuja distância haversine, com raio terrestre de 6.371 km, é `<= 1.100 km`.

| Campo | Tipo Parquet | Definição |
| --- | --- | --- |
| `track_id` | `int64` | Identificador preservado do catálogo horário. |
| `track_time_original` | `timestamp[ms]` | Hora da track selecionada para representar o estado. |
| `time` | `timestamp[ms]` | Hora do campo ERA5 de 6 h; chave com `track_id`. |
| `lat_center`, `lon_center` | `double` | Centro na hora original selecionada. |
| `phase` | `string` | Lifecycle original nessa hora; pode ser nulo. |
| `vor42` | `double` | Vorticidade central nessa hora. |
| `region` | `string` | Região de gênese da track. |
| `track_minus_era5_hours` | `int8` | `track_time_original - time`, em horas; observado de −2 a +3 h, além de zero. |
| `in_current_parquet_period` | `bool` | Indica `time` entre 2010-01-01 00:00 e 2020-12-31 18:00 UTC, período de comparação com C. |
| `has_parquet_rows` | `bool` | Há ao menos uma linha do estado no Parquet C. Fora do período comparável, `false` não deve ser interpretado como ausência avaliada. |
| `support_cell_count` | `int32` | Número geométrico de células da grade dentro de 1.100 km. Não é contagem de linhas armazenadas nem máscara de disponibilidade do ERA5. |
| `support_status` | `string` | `full_support`: disco contínuo contido no domínio; `partial_support`: há células, mas o disco é truncado; `no_support`: zero células da grade. |
| `parquet_state_status` | `string` | `present`, `absent_with_support`, `absent_no_support` ou `outside_comparison_period`; combina período, presença em C e suporte. |

No período comparável existem 29.311 estados de 1.785 tracks: 20.101 presentes em C, 3.233 ausentes com suporte e 5.977 ausentes sem suporte. `partial_support` é suporte válido, porém truncado; não equivale a `no_support`. Para os estados com suporte e sem linhas, nenhuma célula passou pelo filtro de entrada de C. Para `no_support`, não há células a classificar como zero.

## C. Parquet condicionado de vento e excedências

### Arquivo inspecionado

[`data/cyclone_exceedances_by_track_2010_2020_p90.parquet`](../data/cyclone_exceedances_by_track_2010_2020_p90.parquet) é o conjunto atualmente disponível para desenvolvimento. Suas colunas são documentadas em [`COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`](../data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md). A caracterização estrutural reproduzível está em [`structural_summary.json`](../outputs/01_data_overview/structural_summary.json), gerado por [`inspect_parquet.py`](../scripts/01_data_overview/inspect_parquet.py).

- **SHA-256 do arquivo de dados:** `3913a1d8ab49856212e1e5a19275b3644ae947dcf940872fb2f40a884d9efa0c`
- **Dimensão:** 17.182.983 linhas, 17 colunas e 143 grupos de linhas.
- **Ciclones:** 1.781 valores distintos de `track_id`.
- **Período dos campos:** 2010-01-02 18:00 UTC a 2020-12-31 18:00 UTC, em passos nominais de 6 h conforme a documentação fornecida.

### Unidades do conjunto

**Unidade de análise:** o ciclone, identificado por `track_id`. Contagens, separação de treino e teste, inferência e validação devem tratar os **1.781 `track_id` únicos** como as unidades fundamentais, quando aplicável. As 17.182.983 linhas não são 17 milhões de ciclones nem 17 milhões de observações independentes.

**Unidade de armazenamento de uma linha:** um ponto de grade espacial, associado a um `track_id`, um instante do campo ERA5 e o estado do ciclone nesse instante. `lat` e `lon` localizam o ponto; `lat_center` e `lon_center` localizam o centro do ciclone. As colunas `exceeded_*` são valores booleanos no ponto, de modo que um campo espacial está armazenado em formato tabular longo: várias linhas representam posições do campo de um ciclone em um instante.

O recorte não é formado exclusivamente por excedências do q90. Uma linha é armazenada quando `distance_km <= 1.100` e `wind_speed > min(15,6; q90_local)`. Por isso, 13.404 linhas entram pelo limiar fixo em locais onde `q90_local > 15,6` e têm `exceeded_q90 = false`; todas elas satisfazem `15,6 < wind_speed <= q90_local`. Dentro do círculo e do domínio, um ponto ausente não passou pelo limiar de entrada. Fora do domínio, a posição não foi avaliada. Veja [Q-002](open_questions.md#q-002--como-foram-gerados-wind_speed-e-os-indicadores-de-excedência).

### Campos observados

| Coluna | Tipo Parquet | Definição documentada | Valores observados e ausências |
| --- | --- | --- | --- |
| `track_id` | `int64` | Identificador globalmente único do ciclone no catálogo, no formato geral AAAANNNN: ano de gênese e sequência anual. | 1.781 distintos; sem nulos. Faixa observada: 20100003–20210007. O último código pertence a uma track iniciada em dezembro de 2020 e encerrada em 2021. |
| `time` | `timestamp[ms]` | Instante do campo ERA5, passo de 6 h, UTC. | 2010-01-02 18:00 a 2020-12-31 18:00; sem nulos. |
| `phase` | `string` | Cópia da coluna `period`, calculada com o CycloPhaser. O sufixo `2` marca a segunda ocorrência não contígua da mesma fase na track; não é outra classe física. | `incipient`, `intensification`, `intensification 2`, `mature`, `mature 2`, `decay`, `decay 2`, `residual`; 509.788 nulos, herdados do catálogo. Ver a proveniência e o tratamento em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases). |
| `lat_center` | `float32` | Latitude do centro do ciclone, proveniente da vorticidade da track. | −74,4051 a −17,6289; sem nulos. |
| `lon_center` | `float32` | Longitude do centro do ciclone. | −84,0043 a 7,08357; sem nulos. |
| `lat` | `float32` | Latitude do ponto de grade espacial associado à excedência. | −65 a −10; sem nulos. |
| `lon` | `float32` | Longitude do ponto de grade. | −85 a −15; sem nulos. |
| `wind_speed` | `float32` | Magnitude do vento a 10 m, `sqrt(u10² + v10²)`, em m/s, no campo ERA5 de 0,25°. | 1,39227 a 34,84759 m/s; sem nulos. |
| `distance_km` | `float32` | Distância great-circle pelo método haversine, com raio terrestre de 6.371 km. | 0,5254 a 1.100 km; sem nulos. O raio de inclusão usa `<= 1.100 km`. |
| `fixed_quadrant` | `int8` | Quadrante geográfico: 1=NO, 2=NE, 3=SE, 4=SO. Eixos são fechados ao norte e a leste. | Códigos 1–4; sem nulos. Ponto coincidente com o centro cai em 2. |
| `rotated_quadrant` | `int8` | Quadrante relativo ao deslocamento: 1=frente-esquerda, 2=frente-direita, 3=trás-direita, 4=trás-esquerda. Eixos são fechados à frente e à direita. | Códigos 1–4; sem nulos. Direção por diferença centrada de 12 h, 6 h nas pontas; deslocamento nulo assume leste. |
| `exceeded_15_6` | `bool` | Vento > 15,6 m/s. | `true`: 5.508.864 (32,0600%); sem nulos. |
| `exceeded_20_0` | `bool` | Vento > 20,0 m/s. | `true`: 287.930 (1,6757%); sem nulos. |
| `exceeded_25_0` | `bool` | Vento > 25,0 m/s. | `true`: 4.450 (0,0259%); sem nulos. |
| `exceeded_q90` | `bool` | Vento > percentil 90 local do ponto. | `true`: 17.169.579 (99,9220%); `false`: 13.404; sem nulos. |
| `exceeded_q95` | `bool` | Vento > percentil 95 local do ponto. | `true`: 9.158.842 (53,3018%); sem nulos. |
| `exceeded_q99` | `bool` | Vento > percentil 99 local do ponto. | `true`: 2.120.595 (12,3413%); sem nulos. |

Os percentuais foram recalculados diretamente das contagens do conjunto e concordam, após arredondamento, com o documento de colunas. Os mínimos, máximos e nulos vêm das estatísticas dos grupos de linhas; categorias e `track_id` distintos foram lidos em lotes. A chave (`track_id`, `time`, `lat`, `lon`) não possui duplicatas.

### Proveniência e limites do recorte

Os percentis locais atuais foram calculados experimentalmente ponto a ponto com os **11 anos civis completos de 2010–2020**, 16.072 campos de 6 h, usando `numpy.percentile` com interpolação `linear`. Eles serão atualizados após a incorporação das tracks completas de 1979–2020. A versão exata do ERA5 e a versão formal do arquivo de percentis não foram recuperadas; veja [Q-002](open_questions.md#q-002--como-foram-gerados-wind_speed-e-os-indicadores-de-excedência).

O mesmo ponto de grade e hora pode ser associado a ciclones simultâneos: 414.124 pontos-hora aparecem sob mais de um `track_id`, com máximo de três. Além disso, 1.833 dos 20.101 estados ciclone-tempo têm o centro fora do domínio dos percentis; nesses casos, o círculo é truncado pela grade sem uma coluna de aviso. Agregações devem manter `track_id`, e comparações entre ciclones devem considerar essa cobertura desigual.

## Relação e rastreabilidade entre os produtos

- A é derivado diretamente do CSV oficial; B é derivado somente de A e comparado a C.
- C contém apenas estados com ao menos uma célula que passou por `wind_speed > min(15,6; q90_local)`. Ele não é um catálogo completo de estados.
- Para um estado de B com `present` ou `absent_with_support`, a grade, o centro e a regra espacial permitem reconstruir o conjunto de células avaliáveis. Uma célula elegível ausente de C não passou pelo filtro de entrada e, portanto, é falsa para q90, q95, q99 e para 15,6, 20 e 25 m/s. Os zeros podem ser reconstruídos sob esse contrato sem materializar previamente centenas de milhões de linhas.
- Para `partial_support`, só as células dentro do domínio entram no denominador; a parte truncada não foi avaliada. Para `no_support`, nada entra no denominador e a ausência não é zero.
- Checksums, schemas, ambiente, regras e resultados de correspondência estão no [`provenance_manifest.json`](../outputs/00_data_acquisition/provenance_manifest.json) e no [`validation_report.json`](../outputs/00_data_acquisition/validation_report.json).
