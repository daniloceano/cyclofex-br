> Este arquivo descreve o Parquet **condicionado** de vento, não o catálogo completo de estados. Uma linha existe somente quando `distance_km <= 1100` e `wind_speed > min(15,6; q90_local)`. O catálogo completo e os estados sem linha estão em [`cyclone_states_era5_6h_1979_2020.parquet`](cyclone_states_era5_6h_1979_2020.parquet); detalhes e limites constam no [dicionário de dados](../docs/data_dictionary.md).

| Coluna | Tipo | Descrição | Peso no arquivo |
|---|---|---|---|
| `track_id` | int64 | Identificador do ciclone no catálogo (1.781 distintos) | 0,06 MB |
| `time` | timestamp | Instante do campo ERA5, passo de 6 h (UTC) | 0,10 MB |
| `phase` | string | Fase calculada previamente com o CycloPhaser; sufixos numéricos indicam ocorrências repetidas da fase | 0,06 MB |
| `lat_center` | float32 | Latitude do centro do ciclone (vorticidade da track) | 0,15 MB |
| `lon_center` | float32 | Longitude do centro | 0,15 MB |
| `lat` | float32 | Latitude do ponto de grade que excedeu | 1,41 MB |
| `lon` | float32 | Longitude do ponto de grade | 3,42 MB |
| `wind_speed` | float32 | Vento a 10 m no ponto (m/s), 1,39 a 34,85 | 94,14 MB |
| `distance_km` | float32 | Distância do ponto ao centro (0,5 a 1.100 km) | 97,71 MB |
| `fixed_quadrant` | int8 | Quadrante geográfico: 1=NO, 2=NE, 3=SE, 4=SO | 0,80 MB |
| `rotated_quadrant` | int8 | Quadrante relativo ao deslocamento: 1=frente-esq, 2=frente-dir, 3=trás-dir, 4=trás-esq | 0,95 MB |
| `exceeded_15_6` | bool | Vento > 15,6 m/s — 32,06% | 0,62 MB |
| `exceeded_20_0` | bool | Vento > 20,0 m/s — 1,68% | 0,08 MB |
| `exceeded_25_0` | bool | Vento > 25,0 m/s — 0,03% | 0,01 MB |
| `exceeded_q90` | bool | Vento > p90 local do ponto — 99,92% | 0,02 MB |
| `exceeded_q95` | bool | Vento > p95 local — 53,30% | 1,04 MB |
| `exceeded_q99` | bool | Vento > p99 local — 12,34% | 0,43 MB |
