# Solicitação de esclarecimentos sobre a geração do parquet

## Objetivo

Responder às questões Q-002 e Q-003 do projeto **cyclofex-br** usando o código, os arquivos intermediários e a documentação que efetivamente geraram:

- `data/cyclone_exceedances_by_track_2010_2020_p90.parquet`
- `data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`

Precisamos reconstruir o procedimento com precisão suficiente para reproduzi-lo e documentá-lo. Não faça inferências apenas pelos nomes das colunas. Para cada resposta, cite o arquivo, função, trecho de código, configuração ou fonte que fornece a evidência. Se algo não puder ser determinado, escreva explicitamente **NÃO LOCALIZADO** e diga o que falta.

Não faça uma nova análise científica e não altere o parquet. O objetivo é documentar como o dado existente foi construído.

> **Nota de origem (preenchida na resposta).** Os três scripts citados abaixo vivem em `$ROOT = /home/publico/vendaval-ciclone` (máquina 9, `irbrerd09`). Os caminhos `data/...` do enunciado correspondem, na origem, a `$ROOT/outputs/parquet/`. Nada no parquet foi alterado para responder a este documento; todas as contagens vêm de leitura.

## Contexto já confirmado

- A unidade de análise é o ciclone, identificado por `track_id`.
- O parquet contém 1.781 `track_id` únicos, 17.182.983 linhas e 17 colunas.
- Uma linha representa um ponto de grade espacial associado a um ciclone e instante.
- `time` é documentado como o instante do campo ERA5 em UTC, com passo de 6 h.
- `wind_speed` é documentado como vento a 10 m no ponto, em m/s.
- `exceeded_15_6`, `exceeded_20_0` e `exceeded_25_0` representam limiares fixos em m/s.
- `exceeded_q90`, `exceeded_q95` e `exceeded_q99` representam excedência de percentis locais do ponto.
- Os percentis atuais foram calculados experimentalmente com os dez anos de dados baixados para o período das tracks usadas no recorte atual. → **Correção: são onze anos civis completos, 2010–2020** (`calculate_local_percentiles.py` L33, `years = range(2010, 2021)`). Ver Q-002.2.1.
- Após o download das tracks completas de 1979–2020, os percentis serão recalculados com o período ampliado.
- O parquet observado cobre `2010-01-02 18:00` a `2020-12-31 18:00`. Confirme o intervalo exato chamado de "dez anos", pois o nome e os extremos observados atravessam os anos civis de 2010 a 2020. → **Confirmado e respondido em Q-002.2.1.** A referência dos percentis é 2010-01-01 00:00 a 2020-12-31 18:00 UTC (16.072 campos). O primeiro instante do parquet é 2010-01-02 18:00 apenas porque é a primeira hora de track com excedência, não um limite de janela.
- Há 13.404 linhas com `exceeded_q90 = false`, embora o arquivo seja descrito como um recorte p90. → **Mecanismo explicado e verificado em Q-002.4.2.**
- Há 509.788 linhas com `phase` ausente. → **Explicado no item A.**
- O maior identificador observado é `track_id = 20210007`, embora o maior `time` observado pertença a 2020. Não interprete o prefixo do ID como ano sem verificar sua regra. → **Regra verificada no item B.**

---

# Q-002 · Como foram gerados `wind_speed` e os indicadores de excedência?

## Perguntas obrigatórias

### Q-002.1 · Campo de vento

1. Qual produto, variável e versão do ERA5 foram usados?
2. `wind_speed` foi obtido diretamente ou calculado a partir de componentes como `u10` e `v10`?
3. Se foi calculado, informe a fórmula exata, unidades de entrada e tratamento de valores ausentes.
4. Houve interpolação temporal ou espacial, regrid, arredondamento ou conversão de longitude?

**Respostas**

1. Produto: CDS `reanalysis-era5-single-levels`, `product_type: ["reanalysis"]`; variáveis `10m_u_component_of_wind` e `10m_v_component_of_wind`; horários `00:00/06:00/12:00/18:00`; área `[0, -180, -90, 180]` (Hemisfério Sul inteiro); grade nativa 0,25°. Evidência: `scripts/download/download_historical.py` L15–33. Os arquivos foram entregues em GRIB e convertidos para NetCDF por `cfgrib-0.9.15.1/ecCodes-2.42.0` (atributo `history` dos `.nc`, datado de 2026-06-10). **Versão/reprocessamento do ERA5 (ERA5 x ERA5.1, `expver`): NÃO LOCALIZADO** — o atributo não está nos arquivos e não há log do pedido ao CDS guardado no repositório. Para fechar, falta o recibo do CDS (request id) ou um `grib_ls -p expver` do GRIB original, que não foi preservado.
2. Calculado a partir de `u10` e `v10`. Nunca vem pronto do produto.
3. `wind_speed = sqrt(u10² + v10²)`, entrada em m s⁻¹ (`units` das duas variáveis), saída em m s⁻¹. Evidência: `scripts/analysis/exceedances_by_track.py` L91 (parquet) e `scripts/climatology/calculate_local_percentiles.py` L98 (percentis). Valores ausentes: **não há tratamento porque não há ausência** — `u10`/`v10` são float32 densos, sem `_FillValue` efetivo no domínio (verificado: 0 NaN no campo; 0 NaN em `q90`; 0 NaN em `wind_speed` nas 17.182.983 linhas).
4. **Sem interpolação espacial e sem regrid.** O campo é usado na grade nativa; o recorte é `sel(latitude=slice(-10,-65), longitude=slice(-85,-15))` (`exceedances_by_track.py` L54), com `assert` de que a grade resultante bate 1:1 com `local_percentiles.nc` (L55). **Sem interpolação temporal do campo**: o que se aproxima é a posição da track, casada com o campo mais próximo (Q-003.1.3). Longitude: o ERA5 já vem em [−180, 179.75]; as tracks são convertidas com `((lon + 180) % 360) - 180` (L48). Arredondamento: as colunas numéricas são gravadas em float32 (L119–127) — `wind_speed` já era float32 na origem, `distance_km` é calculada em float64 e truncada para float32 na escrita.

### Q-002.2 · Amostra de referência dos percentis

1. Quais datas inicial e final entraram no cálculo atual? Informe timestamps ou anos inclusivos exatos.
2. A referência usa todos os campos de 6 h do período, apenas instantes associados a tracks ou algum outro subconjunto?
3. O percentil foi calculado separadamente em cada ponto `lat/lon`?
4. Os dados foram agrupados por mês, estação, hora UTC ou outra estratificação, ou todos os tempos foram combinados?
5. Terra e oceano receberam o mesmo tratamento?
6. Confirme como a referência futura de 1979–2020 deverá diferir da atual.

**Respostas**

1. **2010-01-01 00:00 UTC a 2020-12-31 18:00 UTC**, anos civis 2010 a 2020 **inclusive — onze anos, não dez**. Evidência: `calculate_local_percentiles.py` L33 (`years = range(2010, 2021)`) e o atributo do arquivo (`description: ... sobre o período histórico 2010-2020`). Tamanho da amostra por ponto, medido: **16.072 campos** de 6 h (1.460 por ano, 1.464 nos bissextos 2012/2016/2020).
2. **Todos os campos de 6 h do período.** Sem filtro por track, por evento, por estação ou por hora. Evidência: o laço L88–98 percorre todos os `valid_time` de cada ano antes do `np.percentile`.
3. **Sim, ponto a ponto.** `np.percentile(band_ws, p, axis=0)` com `axis=0` = tempo, preservando a grade 221 × 281 (L103–106). O domínio é lat −10 a −65 e lon −85 a −15 (L40–41), processado em faixas de 20 linhas de latitude (L29) só por memória — não muda o resultado.
4. **Nenhuma estratificação.** Todos os tempos combinados numa única série por ponto.
5. **Mesmo tratamento.** Não há máscara terra/oceano em nenhuma etapa. A diferenciação é implícita: o q90 local de um ponto continental abrigado é muito menor que o de oceano aberto (q90 observado vai de **1,04 a 17,26 m/s**, média 10,65).
6. Diferenças esperadas com 1979–2020: (a) a amostra por ponto passa de 16.072 para ~61.400 campos de 6 h (42 anos), ~3,8×; (b) os limiares mudam de valor — direção e magnitude **não medidas**, dependem de como 2010–2020 se compara ao restante do período; (c) como o critério de seleção de linha usa `min(15,6 ; q90)`, **muda também quais linhas entram no parquet**, não só as flags. Consequência operacional em C.4.

### Q-002.3 · Implementação dos quantis

1. Qual biblioteca e função calcularam q90, q95 e q99?
2. Qual método de interpolação/definição de quantil foi usado?
3. Como valores ausentes, infinitos e empates foram tratados?
4. As comparações são estritamente `wind_speed > quantil` ou usam `>=`?
5. Qual precisão numérica foi usada para thresholds e comparação?
6. Os thresholds por ponto foram persistidos em algum arquivo? Se sim, informe caminho, esquema e versão.

**Respostas**

1. `numpy.percentile` (NumPy 2.0.2), chamadas em `calculate_local_percentiles.py` L103 (q50), L104 (q90), L105 (q95), L106 (q99); `max` por `band_ws.max(axis=0)` L107.
2. **Método default do NumPy: `linear`** (interpolação linear entre ordens estatísticas; equivalente ao tipo 7 de Hyndman–Fan). O parâmetro `method=` não foi passado em nenhuma das chamadas.
3. Ausentes: não ocorrem (item Q-002.1.3) — não há `nanpercentile` no código, e não seria necessário. Infinitos: não ocorrem. Empates: irrelevantes para a definição linear. `overwrite_input=True` (L103–106) só permite reordenar o buffer de entrada; não altera resultado.
4. **Estritamente `>` em todos os seis indicadores** e também no critério de entrada: `ws > limiar_entrada` (`exceedances_by_track.py` L106), `ws_pt > 15.6 / 20.0 / 25.0` (L124–125), `ws_pt > q90[..] / q95[..] / q99[..]` (L126–127). O único `<=` do fluxo é o raio: `dist <= RADIUS_KM` (L106).
5. Campo de vento em **float32**; limiares lidos de `local_percentiles.nc` em **float64**; a comparação é promovida a float64 pelo NumPy. As colunas gravadas no parquet são float32 (vento, distância, coordenadas) e bool (flags).
6. **Sim:** `$ROOT/data/local_percentiles.nc`. Esquema: dimensões `latitude` (221, descendente, −10 → −65) × `longitude` (281, ascendente, −85 → −15); variáveis `q50`, `q90`, `q95`, `q99`, `max`, todas float64; atributos `description` e `spatial_resolution = 0.25 x 0.25 degrees`. **Versão formal: NÃO LOCALIZADO** — o arquivo não carrega campo de versão, hash nem data de geração. O que existe são dois backups datados no mesmo diretório (`local_percentiles.nc.bak.20260819`, `.bak.20260819b`) e o mtime. Para fechar, falta gravar versão/proveniência como atributo no NetCDF.

### Q-002.4 · Construção e seleção das linhas

1. Qual condição exata selecionou uma linha para o parquet final?
2. Por que há 13.404 linhas com `exceeded_q90 = false` em um arquivo descrito como recorte p90?
3. Esses casos representam arredondamento, junção espacial, borda temporal, valores ausentes de threshold, mudança de versão ou outro mecanismo?
4. Uma posição ausente do parquet significa `false`, "não avaliada" ou apenas "não selecionada"?
5. As flags de limiar fixo e quantil foram calculadas antes ou depois do recorte?
6. Há alguma condição em que as flags possam ser inconsistentes com `wind_speed` por construção?

**Respostas**

1. Condição exata, avaliada para cada ponto da grade recortada, para cada par (ciclone, instante ERA5):

   ```
   (distance_km <= 1100.0)  AND  (wind_speed > min(15.6 , q90_local_do_ponto))
   ```

   Evidência: `exceedances_by_track.py` L31 (`limiar_entrada = np.minimum(15.6, q90)`) e L106 (`m = (dist <= RADIUS_KM) & (ws > limiar_entrada)`).
2. Porque o limiar de entrada é o **mínimo** entre 15,6 m/s e o q90 local. Onde o q90 local é **maior** que 15,6, um ponto pode entrar pelo limiar fixo sem exceder o próprio percentil. Verificado nas 13.404 linhas: em **100%** delas o q90 local é > 15,6 m/s, e em **100%** o vento está no intervalo `15,6 < wind_speed <= q90_local` (mínimo 15,60, máximo 17,26 m/s — o teto é exatamente o maior q90 do domínio).
3. **Outro mecanismo: é o critério de entrada, por desenho.** Não é arredondamento, não é junção espacial, não é borda temporal, não é threshold ausente e não é mudança de versão. Em termos de área, o caso só existe nos 1.687 pontos de grade (2,7% dos 62.101 do domínio) onde q90 > 15,6 m/s.
4. **"Não selecionada"**, com uma exceção: dentro do círculo e dentro do domínio dos percentis, ausência significa que o ponto não passou do limiar de entrada — é `false` no sentido forte. **Fora do domínio** (lat > −10, lat < −65, lon < −85, lon > −15) significa **"não avaliada"**: não há grade nem percentil ali, e parte do círculo de alguns ciclones cai nessa região (Q-003.2.5).
5. **Depois do recorte**, sobre o vetor de pontos já mascarados (L110–127). É equivalente a calcular antes: as flags são funções ponto a ponto de `wind_speed` e dos limiares do mesmo ponto, sem dependência de vizinhança.
6. **Uma só, e é a do item 2:** `exceeded_q90 = false` coexistindo com a descrição "recorte p90", nas 13.404 linhas. Fora isso, as seis flags são determinísticas em `wind_speed` e nos limiares daquele `lat/lon`, calculadas no mesmo instante e com os mesmos arrays — não há caminho de código que as dessincronize. As relações de implicação valem sempre: `exceeded_25_0 ⊂ exceeded_20_0 ⊂ exceeded_15_6` e `exceeded_q99 ⊂ exceeded_q95 ⊂ exceeded_q90`.

## Resposta de Q-002

### Síntese reproduzível

Do dado bruto até as seis flags, em linha reta:

1. **Download.** `scripts/download/download_historical.py` pede ao CDS o `reanalysis-era5-single-levels`, variáveis `10m_u_component_of_wind` e `10m_v_component_of_wind`, horários 00/06/12/18 UTC, área `[0,-180,-90,180]`, 2010–2020 — um arquivo por ano em `data/era5_wind_southern_hemisphere_{ano}.nc`, grade nativa 0,25°, entregue em GRIB e convertido para NetCDF por cfgrib.
2. **Climatologia local.** `scripts/climatology/calculate_local_percentiles.py` recorta o domínio lat −10/−65 e lon −85/−15, empilha **todos** os 16.072 campos de 6 h dos 11 anos, calcula `wind_speed = sqrt(u10²+v10²)` e aplica `np.percentile(..., axis=0)` por ponto de grade, método `linear`. Salva `q50/q90/q95/q99/max` em `data/local_percentiles.nc` (221 × 281, float64). Sem estratificação, sem máscara terra/oceano.
3. **Excedências por ciclone.** `scripts/analysis/exceedances_by_track.py` percorre ano a ano, recalcula `wind_speed` do mesmo jeito, e para cada par (ciclone, instante ERA5) seleciona os pontos com `dist <= 1100 km` e `ws > min(15,6 ; q90_local)`. Para os pontos selecionados grava as seis flags por comparação estrita `>` contra 15,6 / 20,0 / 25,0 m/s e contra q90/q95/q99 daquele ponto. Saída em Parquet, zstd nível 9.

### Fórmulas e pseudocódigo

```text
# 1) campo de vento (idêntico nas duas etapas)
wind_speed(t, y, x) = sqrt( u10(t, y, x)^2 + v10(t, y, x)^2 )          # m/s, float32

# 2) climatologia local, por ponto de grade (y, x), sobre 2010-2020
serie(y, x)   = [ wind_speed(t, y, x) for t in TODOS os 16.072 campos de 6h ]
q90(y, x)     = numpy.percentile(serie(y, x), 90, method="linear")      # idem q95, q99
# persistido em data/local_percentiles.nc (float64)

# 3) limiar de entrada, por ponto de grade
limiar_entrada(y, x) = min( 15.6 , q90(y, x) )

# 4) seleção de linha, para cada (ciclone c, instante ERA5 t)
para cada ponto (y, x) do domínio:
    dist = haversine( (lat[y], lon[x]) , (lat_center(c,t), lon_center(c,t)) )   # R = 6371 km
    SE dist <= 1100.0 E wind_speed(t,y,x) > limiar_entrada(y,x):
        emite linha

# 5) flags da linha emitida (comparação estrita)
exceeded_15_6 = wind_speed >  15.6
exceeded_20_0 = wind_speed >  20.0
exceeded_25_0 = wind_speed >  25.0
exceeded_q90  = wind_speed >  q90(y, x)
exceeded_q95  = wind_speed >  q95(y, x)
exceeded_q99  = wind_speed >  q99(y, x)
```

### Evidências

| Afirmação | Arquivo/fonte | Função, linhas ou configuração |
| --- | --- | --- |
| Produto, variáveis, horários e área do ERA5 | `scripts/download/download_historical.py` | L15–33 (`dataset`, `variable`, `time`, `area`) |
| GRIB → NetCDF por cfgrib 0.9.15.1 / ecCodes 2.42.0 | `data/era5_wind_southern_hemisphere_2015.nc` | atributo global `history` |
| `wind_speed` calculado de u10/v10 | `scripts/analysis/exceedances_by_track.py` | L91 |
| Mesma fórmula na climatologia | `scripts/climatology/calculate_local_percentiles.py` | L98 |
| Período da referência = 2010–2020 (11 anos) | `scripts/climatology/calculate_local_percentiles.py` | L33 `years = range(2010, 2021)` |
| 16.072 campos de 6 h na amostra | medição sobre os 11 `.nc` | soma de `sizes["valid_time"]` |
| Percentil por ponto, sem estratificação | `scripts/climatology/calculate_local_percentiles.py` | L103–106, `axis=0` |
| Método de quantil `linear` (default NumPy 2.0.2) | mesma fonte | ausência de `method=` nas chamadas |
| Limiar de entrada `min(15,6 ; q90)` | `scripts/analysis/exceedances_by_track.py` | L31 |
| Seleção `dist <= 1100 & ws > limiar` | idem | L106 |
| Comparações estritas `>` nas seis flags | idem | L124–127 |
| 13.404 linhas com `exceeded_q90=false`, todas com q90 > 15,6 e ws ≤ q90 | leitura do parquet + `local_percentiles.nc` | verificação ponto a ponto das 13.404 |
| Domínio e grade dos percentis | `data/local_percentiles.nc` | 221 × 281, 0,25°, lat −10/−65, lon −85/−15 |

### Pontos não localizados

- **Versão do ERA5 (`expver`, ERA5 x ERA5.1) e recibo do pedido ao CDS.** Falta o GRIB original ou o log do `cdsapi`; o NetCDF convertido não preserva o campo.
- **Versionamento do `local_percentiles.nc`.** Não há atributo de versão, hash ou data de geração dentro do arquivo — só dois backups datados de 19/08/2026 e o mtime.

---

# Q-003 · Quais convenções espaciais e temporais foram usadas?

## Perguntas obrigatórias

### Q-003.1 · Centro e associação temporal

1. De qual arquivo e variável vêm `lat_center` e `lon_center`?
2. O centro é a posição original da track ou foi interpolado para os tempos do ERA5?
3. Como os timestamps da track foram associados aos campos ERA5 de 6 h?
4. Como foram tratados ciclones simultâneos, tempos duplicados e centros fora do domínio?

**Respostas**

1. `$ROOT/data/tracks_danilo/tracks_SAt_filtered_with_periods.csv`, colunas **`lat vor`** e **`lon vor`** (posição do centro pelo máximo de vorticidade; o CSV também traz `vor42`, `region`, `geometry` e `period`). Leitura em `exceedances_by_track.py` L46; gravação como `lat_center`/`lon_center` em L120.
2. **Posição original da track, sem nenhuma interpolação.** Para cada campo ERA5 escolhe-se a hora de track existente mais próxima, e usa-se a coordenada dela como está.
3. Casamento por vizinho mais próximo no tempo: `np.searchsorted` sobre os `valid_time` do ano, seguido da escolha entre o vizinho anterior e o posterior pelo menor Δt (L62–67). Depois, `drop_duplicates(["track_id","t_idx"])` sobre a tabela ordenada por Δt mantém **uma única posição por (ciclone, instante ERA5)**: a hora de track mais próxima daquele campo (L68–69). Δt máximo possível = 3 h.
4. **Ciclones simultâneos:** tratados de forma independente, cada um com seu próprio círculo. O mesmo ponto de grade na mesma hora pode pertencer a mais de um ciclone e então aparece em mais de uma linha, uma por `track_id` — medido: **414.124 pontos-hora (2,5%) pertencem a 2 ou 3 ciclones**, máximo observado 3. **Tempos duplicados:** colapsados pelo `drop_duplicates` do item 3. **Centros fora do domínio:** mantidos, sem descarte — **1.833 de 20.101 pares (ciclone, instante), 9,1%**, têm o centro fora do retângulo dos percentis e ainda assim contribuem com os pontos do círculo que caem dentro da grade. O círculo é simplesmente truncado pelo domínio.

### Q-003.2 · Distância e domínio espacial

1. Qual fórmula gera `distance_km`? Informe equação, raio da Terra, biblioteca e CRS/projeção.
2. A distância é geodésica, great-circle/haversine, euclidiana projetada ou aproximação em graus?
3. Qual regra define o raio máximo observado de 1.100 km?
4. Qual é a grade espacial original e sua resolução?
5. Como foram tratados longitude periódica, dateline, polos, bordas do domínio, terra e oceano?

**Respostas**

1. **Haversine**, implementada em NumPy puro (sem biblioteca geoespacial, sem CRS/projeção declarados — coordenadas geográficas da própria grade ERA5). `R_EARTH = 6371.0` km (`exceedances_by_track.py` L22). Equação, L102–105:

   ```
   a = sin²(Δφ/2) + cos(φ_ponto)·cos(φ_centro)·sin²(Δλ/2)
   d = 2 · 6371.0 · asin(√a)
   ```
2. **Great-circle (haversine) sobre esfera.** Não é geodésica elipsoidal, não é euclidiana projetada, não é aproximação em graus. Erro esperado ante WGS84: até ~0,3%, ou seja ~3 km em 1.100 km.
3. Constante `RADIUS_KM = 1100.0` (L21), aplicada como `dist <= RADIUS_KM` (L106). O valor foi herdado de `scripts/analysis/continuous_5year_analysis.py` (mesmo raio) para manter os dois produtos comparáveis. Por isso `distance_km` tem máximo exatamente 1100.0.
4. Grade nativa do ERA5, **0,25° × 0,25°** (regular lat/lon), recortada para **221 latitudes × 281 longitudes** — lat −10,0 a −65,0 descendente, lon −85,0 a −15,0 ascendente. O recorte é o mesmo de `local_percentiles.nc`, com `assert` de igualdade de forma (L54–55).
5. **Longitude periódica:** as tracks são normalizadas para [−180, 180) (L48); a haversine é insensível ao wrap porque usa `sin(Δλ/2)`; o cálculo de quadrante usa `((Δλ + 180) % 360) − 180` (L112). **Dateline:** não ocorre — o domínio vai de −85 a −15. **Polos:** fora do domínio (limite sul −65). **Bordas do domínio:** o círculo é truncado sem preenchimento nem reflexão; ciclone perto da borda tem menos pontos, e isso não é sinalizado em nenhuma coluna. **Terra e oceano:** sem máscara, tratamento idêntico; a diferença entra só pelo q90 local de cada ponto.

### Q-003.3 · Quadrante geográfico

1. Como `fixed_quadrant` é calculado a partir do centro e do ponto?
2. Confirme os códigos documentados: 1=NO, 2=NE, 3=SE, 4=SO.
3. Em qual quadrante caem pontos exatamente sobre os eixos norte–sul ou leste–oeste?
4. A comparação usa diferenças simples de latitude/longitude ou azimute geodésico?

**Respostas**

1. Pelos sinais de `Δlat = lat_ponto − lat_centro` e `Δlon = ((lon_ponto − lon_centro + 180) % 360) − 180`, em graus (L111–114):

   ```
   Δlat >= 0 e Δlon <  0  → 1
   Δlat >= 0 e Δlon >= 0  → 2
   Δlat <  0 e Δlon >= 0  → 3
   Δlat <  0 e Δlon <  0  → 4
   ```
2. **Confirmado:** 1 = NO, 2 = NE, 3 = SE, 4 = SO.
3. Os limites são fechados no lado norte e no lado leste: um ponto exatamente na mesma latitude do centro (`Δlat = 0`) é classificado como **norte** (1 ou 2); um ponto exatamente na mesma longitude (`Δlon = 0`) é classificado como **leste** (2 ou 3). O ponto coincidente com o centro (`Δlat = Δlon = 0`) cai em **2 (NE)**.
4. **Diferenças simples de latitude/longitude.** Não há azimute geodésico em nenhum ponto do código.

### Q-003.4 · Movimento e rotação

1. Como o vetor de deslocamento do ciclone é calculado: diferença para o passo anterior, seguinte, central ou outro método?
2. Qual intervalo temporal entra no vetor e o que ocorre quando há lacunas na track?
3. Informe a convenção angular: origem, sentido positivo, unidade e intervalo do ângulo.
4. Escreva a transformação matemática ou matriz que converte a posição do ponto para o referencial relativo ao movimento.
5. Confirme os códigos documentados: 1=frente-esquerda, 2=frente-direita, 3=trás-direita, 4=trás-esquerda.
6. Como são classificados pontos exatamente sobre os eixos rotacionados?
7. O que acontece no primeiro e último timestep da track, com velocidade nula ou muito baixa, ou quando não é possível definir direção?

**Respostas**

1. **Diferença centrada** sobre a série já reamostrada para 6 h da própria track: posição do passo seguinte menos posição do passo anterior (L73–74).
2. Intervalo nominal **12 h** no miolo da série (t−1 → t+1) e **6 h** nas pontas, onde o cálculo cai para diferença simples (L75–76). **Lacunas:** o cálculo usa os vizinhos existentes na série reamostrada, sem verificar se há buraco — se faltar um passo, o vetor atravessa a lacuna e representa um intervalo maior que 12 h, **sem nenhuma marcação**. Limitação conhecida; não há coluna que sinalize o caso.
3. **Não há coluna de ângulo no parquet** — só o quadrante já discretizado. Internamente o deslocamento é guardado como vetor unitário `(ux, uy)`, com `ux` na direção leste e `uy` na direção norte, e `Δλ` escalado por `cos(lat)` antes de normalizar (L78–81). Nenhum bearing em graus é calculado ou persistido.
4. Com `Δx = Δλ · cos((φ_ponto + φ_centro)/2)` e `Δy = Δφ` (graus), e `(ux, uy)` unitário na direção do movimento (L115–117):

   ```
   [ y' ]   [ ux   uy ] [ Δx ]        y' = componente À FRENTE   (ao longo do movimento)
   [    ] = [         ] [    ]
   [ x' ]   [ uy  -ux ] [ Δy ]        x' = componente À DIREITA  (perpendicular, olhando no sentido do movimento)
   ```

   Classificação (L118): `y' >= 0 e x' < 0 → 1` · `y' >= 0 e x' >= 0 → 2` · `y' < 0 e x' >= 0 → 3` · `y' < 0 e x' < 0 → 4`.
5. **Confirmado:** 1 = frente-esquerda, 2 = frente-direita, 3 = trás-direita, 4 = trás-esquerda.
6. Mesma convenção de fechamento do quadrante geográfico: `y' = 0` conta como **frente**, `x' = 0` conta como **direita**. Logo, ponto exatamente sobre o eixo transversal vai para 1 ou 2, e ponto exatamente sobre o eixo de movimento vai para 2 ou 3.
7. **Primeiro e último instante da track:** diferença simples de 6 h em vez de centrada. **Deslocamento nulo** (mesma posição em dois passos, magnitude zero): fallback explícito para `(ux, uy) = (1, 0)`, ou seja, **movimento assumido para leste** (L79–81) — nesse caso o quadrante rotacionado degenera para uma rotação fixa do geográfico. **Não há coluna marcando qual linha usou o fallback**, e o caso não foi contabilizado na geração. Track com um único passo no ano cairia no mesmo fallback.

## Resposta de Q-003

### Síntese reproduzível

Da track e do ponto de grade até `distance_km`, `fixed_quadrant` e `rotated_quadrant`:

1. **Catálogo.** Lê-se `tracks_SAt_filtered_with_periods.csv` (`track_id`, `date` horária, `lon vor`, `lat vor`, `period`), normalizando a longitude para [−180, 180).
2. **Reamostragem temporal.** Cada hora de track é associada ao campo ERA5 de 6 h mais próximo (Δt ≤ 3 h); mantém-se uma posição por (ciclone, campo), a de menor Δt. A posição não é interpolada.
3. **Direção do movimento.** Por ciclone, na série de 6 h: diferença centrada entre a posição anterior e a seguinte (12 h), com diferença simples de 6 h nas pontas e fallback para leste quando o deslocamento é nulo. O vetor é normalizado após escalar a longitude por `cos(lat)`.
4. **Distância.** Haversine com R = 6.371 km entre cada ponto da grade recortada e o centro do ciclone naquele instante; entram os pontos com `dist <= 1.100 km` que também passam do limiar de vento.
5. **Quadrantes.** O geográfico sai dos sinais de Δlat/Δlon; o rotacionado projeta (Δx, Δy) no referencial do movimento e classifica por frente/trás e esquerda/direita.

### Equações e pseudocódigo

```text
# reamostragem temporal (por ano)
t_idx        = índice do valid_time ERA5 mais próximo de cada hora de track   # Δt <= 3h
posição(c,t) = hora de track de menor |Δt| dentro de (track_id, t_idx)

# direção do movimento (por ciclone, série de 6h)
Δlon = lon[t+1] - lon[t-1]        (pontas: diferença simples de 6h)
Δlat = lat[t+1] - lat[t-1]
dx   = ((Δlon + 180) mod 360 - 180) * cos(lat[t]) ;  dy = Δlat
mag  = sqrt(dx² + dy²)
(ux, uy) = (dx, dy) / mag         SE mag > 0   SENÃO   (1, 0)     # fallback: leste

# distância ponto → centro
a    = sin²(Δφ/2) + cos(φ_ponto)·cos(φ_centro)·sin²(Δλ/2)
dist = 2 · 6371.0 · asin(√a)                                      # km

# quadrante geográfico
Δlon_deg = (lon_ponto - lon_centro + 180) mod 360 - 180 ; Δlat_deg = lat_ponto - lat_centro
fixed = 1 se (Δlat>=0, Δlon<0) | 2 se (Δlat>=0, Δlon>=0) | 3 se (Δlat<0, Δlon>=0) | 4 se (Δlat<0, Δlon<0)

# quadrante relativo ao movimento
Δx = Δlon_deg · cos((lat_ponto + lat_centro)/2) ;  Δy = Δlat_deg
y' = Δx·ux + Δy·uy        # frente (+) / trás (-)
x' = Δx·uy - Δy·ux        # direita (+) / esquerda (-)
rotated = 1 se (y'>=0, x'<0) | 2 se (y'>=0, x'>=0) | 3 se (y'<0, x'>=0) | 4 se (y'<0, x'<0)
```

### Evidências

| Afirmação | Arquivo/fonte | Função, linhas ou configuração |
| --- | --- | --- |
| Origem de `lat_center`/`lon_center` | `data/tracks_danilo/tracks_SAt_filtered_with_periods.csv` | colunas `lat vor`, `lon vor`; leitura em `exceedances_by_track.py` L46 |
| Normalização de longitude da track | `scripts/analysis/exceedances_by_track.py` | L48 |
| Casamento temporal por vizinho mais próximo (Δt ≤ 3 h) | idem | L62–67 |
| Uma posição por (ciclone, instante) | idem | L68–69 (`drop_duplicates`) |
| Vetor de movimento por diferença centrada + fallback leste | idem | L73–81 |
| Haversine, R = 6371 km | idem | L22, L102–105 |
| Raio de 1.100 km | idem | L21, L106 |
| Quadrante geográfico por sinais de Δlat/Δlon | idem | L111–114 |
| Projeção no referencial do movimento | idem | L115–118 |
| 2,5% dos pontos-hora em mais de um ciclone (máx. 3) | leitura do parquet | agrupamento por (`time`,`lat`,`lon`) |
| 9,1% dos pares (ciclone, instante) com centro fora do domínio | leitura do parquet | `lat_center`/`lon_center` fora de [−65,−10] × [−85,−15] |
| Chave (`track_id`,`time`,`lat`,`lon`) sem duplicata | leitura do parquet | 0 duplicatas em 17.182.983 linhas |

### Pontos não localizados

- **Quantas linhas usaram o fallback de direção** (deslocamento nulo) — não foi instrumentado na geração e não há coluna que permita reconstruir a posteriori sem reprocessar as tracks. Reprocessável, se necessário.
- **Critério que originou o raio de 1.100 km.** O valor é herdado do pipeline anterior; não há no repositório a justificativa metodológica (documento, card ou comentário) que o escolheu.

---

# Esclarecimentos adicionais necessários

Responda estes itens quando houver evidência no mesmo código ou fluxo de geração.

## A. Fases do ciclo de vida

1. Como `phase` é calculada ou importada?
2. Qual é a definição operacional de `incipient`, `intensification`, `mature`, `decay` e `residual`?
3. O que significam `intensification 2`, `mature 2` e `decay 2`?
4. Por que 509.788 linhas têm `phase` ausente?
5. Ausência de fase ocorre por ciclone, timestep, falha de junção ou regra do ciclo de vida?
6. Como esses valores devem ser tratados em análises futuras?

**Respostas**

1. **Importada, não calculada.** É a coluna `period` do próprio CSV de tracks, copiada para a linha como `phase` (`exceedances_by_track.py` L46 e L120). Nenhum código deste repositório classifica fase.
2. **NÃO LOCALIZADO.** A definição operacional está do lado do catálogo (classificação por ciclo de vida energético, LEC), não neste repositório. Falta a referência/código que gerou `..._with_periods.csv` para documentar os critérios de corte entre `incipient`, `intensification`, `mature`, `decay` e `residual`.
3. Sufixo ` 2` = **segundo ciclo dentro da mesma track** (o catálogo traz `incipient 2`, `intensification 2`, `mature 2` e `decay 2`). A definição formal do que dispara um segundo ciclo é a mesma lacuna do item 2 — **NÃO LOCALIZADO**.
4. Porque a hora de track correspondente já vem **sem classificação** no catálogo: **50.069 de 631.009 pontos horários (7,9%)** têm `period` vazio no CSV de origem. Nada é perdido na junção — a ausência é propagada.
5. **Por timestep**, não por ciclone. São trechos no início e no fim das trajetórias, antes de a primeira fase começar ou depois de a última terminar. Medido no parquet: **677 ciclones têm pelo menos uma linha sem fase** e apenas **2 têm todas as linhas sem fase**.
6. Tratar como categoria própria ("sem classificação"), nunca como zero nem como fase implícita. Em qualquer agregação por fase, filtrar explicitamente e reportar o volume excluído (3,0% das linhas do parquet).

## B. Identificador e chave dos dados

1. Como `track_id` é construído? Seu prefixo codifica ano ou outra informação?
2. Por que aparece `track_id = 20210007` quando o último `time` observado é de 2020?
3. `track_id` é único globalmente no catálogo ou apenas dentro de um arquivo/ano?
4. Qual é a chave mínima esperada de uma linha: `track_id + time + lat + lon`?
5. Duplicatas nessa chave são possíveis ou indicam erro?

**Respostas**

1. Inteiro de 8 dígitos no formato **AAAANNNN**: os 4 primeiros são o **ano de gênese** e os 4 últimos um sequencial dentro do ano. Verificado no catálogo completo: o prefixo bate com o ano da primeira data da track em **6.788 de 6.789** casos.
2. Porque é **a única exceção**, e é uma track que atravessa o ano civil: `20210007` vai de **2020-12-30 11:00 a 2021-01-05 16:00**. O catálogo a numerou como 2021; o parquet contém apenas as horas dela que caem dentro do ERA5 baixado, que termina em 2020-12-31 18:00. Não é erro de junção nem de tipo.
3. **Único globalmente no catálogo** — 6.789 identificadores distintos para 6.789 tracks. No recorte 2010–2020 do parquet aparecem 1.781.
4. **Sim: (`track_id`, `time`, `lat`, `lon`).** Verificado: **0 duplicatas** em 17.182.983 linhas.
5. Duplicata nessa chave **indica erro**. O que **não** é duplicata e não deve ser tratado como tal: a mesma tripla (`time`, `lat`, `lon`) em `track_id` diferentes — ocorre em 414.124 pontos-hora (2,5%), com até 3 ciclones no mesmo ponto. Qualquer soma sobre pontos sem agrupar por ciclone contará esses pontos mais de uma vez.

## C. Proveniência e reprodução

1. Liste, em ordem, todos os scripts e entradas que produzem o parquet.
2. Informe versões relevantes de bibliotecas, parâmetros e constantes.
3. Identifique thresholds, máscaras, domínios e caminhos atualmente codificados manualmente.
4. Informe quais produtos precisam ser regenerados quando os percentis forem recalculados para 1979–2020.
5. Indique qualquer etapa manual que impeça reprodução integral.

**Respostas**

1. Ordem de execução, com entradas:
   1. `scripts/download/download_historical.py` → `data/era5_wind_southern_hemisphere_{2010..2020}.nc` (requer `~/.cdsapirc`).
   2. `scripts/climatology/calculate_local_percentiles.py` (entrada: os 11 NetCDF) → `data/local_percentiles.nc`.
   3. `scripts/analysis/exceedances_by_track.py ANO_INI ANO_FIM SAIDA.parquet` (entradas: os 11 NetCDF, `data/local_percentiles.nc` e `data/tracks_danilo/tracks_SAt_filtered_with_periods.csv`) → `outputs/parquet/cyclone_exceedances_by_track_2010_2020_p90.parquet`.
   - O catálogo de tracks é **insumo externo**: não é produzido por nenhum script deste repositório.
2. Ambiente de execução `/home/publico/venv` na máquina 9: **Python 3.9.25, NumPy 2.0.2, pandas 2.2.3, PyArrow 21.0.0, xarray 2024.7.0**. Parquet gravado com **zstd nível 9**, sem dicionário, 14+ row groups. Constantes: `RADIUS_KM = 1100.0`, `R_EARTH = 6371.0`, limiares fixos `15.6 / 20.0 / 25.0`, `BLOCO = 120` timesteps por leitura.
3. Codificado manualmente: os caminhos absolutos `ROOT`, `TRACKS`, `PERC` (L17–20); o raio e o raio da Terra (L21–22); os três limiares fixos (L31, L124–125); o domínio lat −65/−10 e lon −85/−15 (em `calculate_local_percentiles.py` L40–41, e implicitamente em `exceedances_by_track.py` via a grade do `local_percentiles.nc`); o período 2010–2020 (`years = range(2010, 2021)`). **Não há máscara** de terra/oceano em lugar nenhum.
4. Ao recalcular os percentis para 1979–2020, regenerar **nesta ordem**: (a) `data/local_percentiles.nc`; (b) `outputs/parquet/cyclone_exceedances_by_track_*.parquet` — muda o conteúdo **e o conjunto de linhas**, porque o critério de entrada depende do q90; (c) `outputs/csv/cyclone_exceedances_5years.csv` e o parquet derivado dele; (d) `wind_spatial_field_by_phase_*` e `wind_spatial_field_all_mendeley_*`; (e) os agregados que alimentam o painel (`wind_spatial_pattern_by_phase.csv`, `wind_phase_extremes_summary.csv`, `wind_spatial_field_by_phase_grid.csv`). Observação: ampliar para 1979 exige também baixar o ERA5 desses anos — hoje só existem 2010–2020 em disco.
5. Etapas que impedem reprodução integral hoje: (a) **o projeto não está sob controle de versão** (não há `.git`), então não existe hash de código que identifique a versão que gerou o parquet; (b) o **catálogo de tracks** vem pronto de fora, sem versão declarada; (c) a conversão **GRIB → NetCDF** foi feita na entrega do CDS e o GRIB original não foi preservado; (d) o script gerador foi escrito fora da árvore do projeto e **só agora foi versionado** em `scripts/analysis/exceedances_by_track.py` — a cópia preservada é idêntica à que gerou o arquivo.

## Respostas adicionais

| Item | Resposta | Evidência | Consequência para o projeto |
| --- | --- | --- | --- |
| Fases | Importadas da coluna `period` do catálogo, não calculadas aqui; 9 valores, incluindo ciclos secundários com sufixo ` 2`; 3,0% das linhas sem fase | `exceedances_by_track.py` L46/L120; CSV de tracks com 50.069 de 631.009 horas sem `period` | Definição operacional das fases precisa vir do dono do catálogo antes de qualquer análise por fase; linhas sem fase exigem filtro explícito |
| `track_id` e chave | Formato AAAANNNN (ano de gênese + sequencial), único no catálogo; chave mínima (`track_id`,`time`,`lat`,`lon`) sem duplicatas; 20210007 é track que cruza 2020→2021 | Verificação em 6.789 tracks (6.788 com prefixo = ano de gênese); 0 duplicatas em 17.182.983 linhas | Agregações espaciais devem agrupar por ciclone: 2,5% dos pontos-hora pertencem a mais de um ciclone e seriam contados em duplicidade |
| Proveniência | 3 scripts encadeados + catálogo externo; ambiente e constantes documentados acima; sem git, sem versão no NetCDF de percentis | `download_historical.py`, `calculate_local_percentiles.py`, `exceedances_by_track.py` | Reprodução é possível hoje, mas não é rastreável: sem versionar código, percentis e catálogo, não há como provar qual versão gerou um parquet específico |

---

# Entrega esperada

## 1. Fatos confirmados

1. `wind_speed` é `sqrt(u10² + v10²)` do ERA5 single-levels 0,25°, em m/s, na grade nativa — sem regrid e sem interpolação espacial ou temporal do campo.
2. A referência dos percentis são **11 anos civis (2010–2020)**, 16.072 campos de 6 h, todos os tempos, por ponto de grade, sem estratificação e sem máscara terra/oceano.
3. Quantis por `numpy.percentile`, método `linear`, persistidos em `data/local_percentiles.nc` (float64).
4. Critério de seleção de linha: `dist <= 1100 km` **e** `wind_speed > min(15,6 ; q90_local)`; todas as comparações de limiar são estritas (`>`).
5. As 13.404 linhas com `exceeded_q90 = false` são exatamente os pontos onde o q90 local supera 15,6 m/s e o vento entrou pelo limiar fixo — verificado em 100% dos casos.
6. Centro vindo de `lat vor`/`lon vor` do catálogo, sem interpolação; cada hora de track casada com o campo ERA5 mais próximo (Δt ≤ 3 h), uma posição por (ciclone, instante).
7. `distance_km` é haversine com R = 6.371 km; máximo exatamente 1.100,0 km.
8. `fixed_quadrant` = 1 NO / 2 NE / 3 SE / 4 SO; `rotated_quadrant` = 1 frente-esq / 2 frente-dir / 3 trás-dir / 4 trás-esq; eixos fechados no norte, no leste, na frente e na direita.
9. Vetor de movimento por diferença centrada de 12 h (6 h nas pontas), com fallback para leste quando o deslocamento é nulo.
10. Chave (`track_id`,`time`,`lat`,`lon`) é única; 2,5% dos pontos-hora pertencem a mais de um ciclone.
11. 1.781 ciclones no parquet contra 1.785 com cobertura ERA5 no catálogo: os 4 ausentes (`20091196`, `20110523`, `20191177`, `20203207`) não produziram nenhuma linha porque nenhum ponto do círculo passou do limiar de entrada — `20091196` está inteiramente fora do domínio (lon 28° a 114° E); os outros três foram verificados caso a caso (ex.: `20110523` em 2011-06-16 18:00 tem vento máximo de 12,34 m/s no círculo contra limiar médio de 13,94 m/s).

## 2. Pontos ainda desconhecidos

1. Versão do ERA5 (`expver` / ERA5 vs ERA5.1) e recibo do pedido ao CDS.
2. Versão e proveniência formal do `local_percentiles.nc` (sem atributo de versão ou hash).
3. Definição operacional das fases do ciclo de vida e do que caracteriza um ciclo secundário (` 2`) — pertence ao catálogo, não a este repositório.
4. Quantas linhas usaram o fallback de direção (deslocamento nulo).
5. Justificativa metodológica documentada do raio de 1.100 km.

## 3. Correções sugeridas para o dicionário de dados

1. Trocar "dez anos" por **"2010–2020, 11 anos civis, 16.072 campos de 6 h"** em toda a documentação.
2. Registrar que **`exceeded_q90` não é 100%**: 13.404 linhas (0,08%) entram pelo limiar fixo de 15,6 m/s onde o q90 local é maior.
3. Documentar que o **mesmo ponto-hora pode aparecer em até 3 ciclones** (2,5% dos pontos-hora), com a consequência para agregações.
4. Documentar o **fallback de direção para leste** quando o deslocamento é nulo, e que ele não é sinalizado por coluna.
5. Documentar as **convenções de fronteira** dos dois quadrantes (norte/leste e frente/direita fechados).
6. Registrar que **9,1% dos pares (ciclone, instante) têm o centro fora do domínio** e que o círculo é truncado pela grade sem aviso.
7. Registrar que `phase` vem do catálogo e que **3,0% das linhas não têm fase**, com a recomendação de tratamento.
8. Acrescentar que `distance_km` é derivada e recalculável, e que está em float32 (erro de ~7 cm em 1.072 km).

## 4. Riscos de interpretação do parquet atual

1. **Dupla contagem entre ciclones:** somar pontos sem agrupar por `track_id` superestima 2,5% dos pontos-hora.
2. **"p90" no nome não significa que toda linha excede o p90** — ver correção 2.
3. **Truncamento nas bordas do domínio:** ciclones perto de −65°S, −85°W ou −15°W têm círculo incompleto, o que enviesa contagens por ciclone sem que nada no dado avise.
4. **Quadrante rotacionado degenerado** nos casos de deslocamento nulo (direção assumida como leste) e nas pontas de cada track (janela de 6 h em vez de 12 h).
5. **Percentis in-sample:** a climatologia de referência é o mesmo período analisado e inclui as horas de ciclone, o que amortece os limiares. Muda quando a referência passar para 1979–2020.
6. **Resolução temporal aparente:** a track é horária, mas o campo é de 6 h; posições distintas podem compartilhar o mesmo campo de vento (Δt de até 3 h).
7. **Vento de reanálise a 10 m em grade de 0,25°** não é rajada nem medida de estação; não representa vento local em terreno complexo.

## 5. Artefatos que precisam ser preservados para reproduzir o dado

1. `scripts/analysis/exceedances_by_track.py` (gerador, agora versionado no projeto).
2. `scripts/climatology/calculate_local_percentiles.py` e `scripts/download/download_historical.py`.
3. `data/local_percentiles.nc` (+ os dois backups datados) — sem ele o critério de entrada não é reconstruível.
4. `data/tracks_danilo/tracks_SAt_filtered_with_periods.csv` — insumo externo, sem versão declarada.
5. Os 11 arquivos `data/era5_wind_southern_hemisphere_{ano}.nc` (36 GB) ou, na falta deles, o recibo do pedido ao CDS.
6. `outputs/parquet/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md` e este documento.

## 6. Q-002 e Q-003 podem ser marcadas como RESOLVED?

- **Q-002 — RESOLVED com ressalva.** O caminho do dado bruto até `wind_speed` e até as seis flags está reconstruído com código, linhas e verificação numérica, incluindo o mecanismo exato das 13.404 linhas divergentes. A ressalva é a versão do ERA5 (`expver`), não recuperável dos arquivos atuais; ela não afeta a reprodução do procedimento, só a identificação exata do insumo.
- **Q-003 — RESOLVED.** Todas as convenções espaciais e temporais estão documentadas com a equação, a constante e a linha correspondente, incluindo tratamento de fronteiras, ciclones simultâneos e casos degenerados. O único item aberto (quantas linhas usaram o fallback de direção) é uma contagem ausente, não uma convenção desconhecida, e é reprodutível a partir do catálogo.
