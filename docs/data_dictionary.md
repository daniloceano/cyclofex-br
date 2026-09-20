# Dicionário de dados

## Arquivo inspecionado

[`data/cyclone_exceedances_by_track_2010_2020_p90.parquet`](../data/cyclone_exceedances_by_track_2010_2020_p90.parquet) é o conjunto atualmente disponível para desenvolvimento. Suas colunas são documentadas em [`COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`](../data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md). A caracterização estrutural reproduzível está em [`structural_summary.json`](../outputs/01_data_overview/structural_summary.json), gerado por [`inspect_parquet.py`](../scripts/01_data_overview/inspect_parquet.py).

- **SHA-256 do arquivo de dados:** `3913a1d8ab49856212e1e5a19275b3644ae947dcf940872fb2f40a884d9efa0c`
- **Dimensão:** 17.182.983 linhas, 17 colunas e 143 grupos de linhas.
- **Ciclones:** 1.781 valores distintos de `track_id`.
- **Período dos campos:** 2010-01-02 18:00 UTC a 2020-12-31 18:00 UTC, em passos nominais de 6 h conforme a documentação fornecida.

## Unidades do conjunto

**Unidade de análise:** o ciclone, identificado por `track_id`. Contagens, separação de treino e teste, inferência e validação devem tratar os **1.781 `track_id` únicos** como as unidades fundamentais, quando aplicável. As 17.182.983 linhas não são 17 milhões de ciclones nem 17 milhões de observações independentes.

**Unidade de armazenamento de uma linha:** um ponto de grade espacial, associado a um `track_id`, um instante do campo ERA5 e o estado do ciclone nesse instante. `lat` e `lon` localizam o ponto; `lat_center` e `lon_center` localizam o centro do ciclone. As colunas `exceeded_*` são valores booleanos no ponto, de modo que um campo espacial está armazenado em formato tabular longo: várias linhas representam posições do campo de um ciclone em um instante.

O recorte não é formado exclusivamente por excedências do q90. Uma linha é armazenada quando `distance_km <= 1.100` e `wind_speed > min(15,6; q90_local)`. Por isso, 13.404 linhas entram pelo limiar fixo em locais onde `q90_local > 15,6` e têm `exceeded_q90 = false`; todas elas satisfazem `15,6 < wind_speed <= q90_local`. Dentro do círculo e do domínio, um ponto ausente não passou pelo limiar de entrada. Fora do domínio, a posição não foi avaliada. Veja [Q-002](open_questions.md#q-002--como-foram-gerados-wind_speed-e-os-indicadores-de-excedência).

## Campos observados

| Coluna | Tipo Parquet | Definição documentada | Valores observados e ausências |
| --- | --- | --- | --- |
| `track_id` | `int64` | Identificador globalmente único do ciclone no catálogo, no formato geral AAAANNNN: ano de gênese e sequência anual. | 1.781 distintos; sem nulos. Faixa observada: 20100003–20210007. O último código pertence a uma track iniciada em dezembro de 2020 e encerrada em 2021. |
| `time` | `timestamp[ms]` | Instante do campo ERA5, passo de 6 h, UTC. | 2010-01-02 18:00 a 2020-12-31 18:00; sem nulos. |
| `phase` | `string` | Cópia da coluna `period` do catálogo de tracks. O sufixo `2` marca um segundo ciclo de vida na mesma track. | `incipient`, `intensification`, `intensification 2`, `mature`, `mature 2`, `decay`, `decay 2`, `residual`; 509.788 nulos, herdados do catálogo. A definição operacional das fases permanece em Q-004. |
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

## Proveniência e limites do recorte

Os percentis locais atuais foram calculados experimentalmente ponto a ponto com os **11 anos civis completos de 2010–2020**, 16.072 campos de 6 h, usando `numpy.percentile` com interpolação `linear`. Eles serão atualizados após a incorporação das tracks completas de 1979–2020. A versão exata do ERA5 e a versão formal do arquivo de percentis não foram recuperadas; veja [Q-002](open_questions.md#q-002--como-foram-gerados-wind_speed-e-os-indicadores-de-excedência).

O mesmo ponto de grade e hora pode ser associado a ciclones simultâneos: 414.124 pontos-hora aparecem sob mais de um `track_id`, com máximo de três. Além disso, 1.833 dos 20.101 estados ciclone-tempo têm o centro fora do domínio dos percentis; nesses casos, o círculo é truncado pela grade sem uma coluna de aviso. Agregações devem manter `track_id`, e comparações entre ciclones devem considerar essa cobertura desigual.
