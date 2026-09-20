# Metodologia em uso

A metodologia científica para modelar footprints e estimar hazard **ainda não foi adotada**. A proposta atual é um mapa de hipóteses revisável. Este documento descreve apenas procedimentos efetivamente executados; perguntas, testes, decisões e pressupostos têm seus próprios registros.

## Aquisição e preparação das tracks

**Fonte e integridade.** A fonte operacional adotada em [D-004](decisions.md#d-004--adotar-o-zenodo-18133432-como-fonte-canônica-operacional-das-tracks-e-do-lifecycle) é `tracks_SAt_filtered_with_energetics.csv`, do [Zenodo 18133432](https://zenodo.org/records/18133432). [`download_tracks_zenodo.py`](../scripts/00_data_acquisition/download_tracks_zenodo.py) baixa o arquivo para um cache ignorado pelo Git, ou reutiliza o cache, somente depois de validar nome, tamanho, MD5, SHA-256 e as 31 colunas esperadas. O CSV bruto pode ser reconstruído da fonte e não integra os dados versionados.

**Catálogo horário.** [`prepare_tracks.py`](../scripts/00_data_acquisition/prepare_tracks.py) lê apenas `track_id`, `date`, `lon vor`, `lat vor`, `vor42`, `region` e `period`; renomeia os centros e a fase; interpreta o literal `nan` de `period` como nulo; ordena por ciclone e tempo; e grava [`tracks_SAt_1979_2020.parquet`](../data/tracks_SAt_1979_2020.parquet). Identificadores são `int64`, tempos são UTC em `timestamp[ms]` sem timezone armazenado, e centros/vorticidade permanecem `float64`. Nenhuma categoria de fase é agrupada nesse produto.

**Estados de 6 h.** Cada hora de track é associada ao campo de 6 h mais próximo, com diferença máxima de 3 h. O empate de 3 h usa o campo anterior; para cada `track_id + time`, conserva-se a hora original com menor diferença e, em novo empate, a anterior. O resultado é [`cyclone_states_era5_6h_1979_2020.parquet`](../data/cyclone_states_era5_6h_1979_2020.parquet), com hora original, hora ERA5, diferença temporal e proveniência do centro/fase.

**Suporte espacial.** Para cada estado, o script conta sem materializar o produto cartesiano as células da grade regular de 0,25° entre 65–10°S e 85–15°W cuja distância haversine, com raio terrestre de 6.371 km, satisfaz `distance <= 1.100 km`. `full_support` indica que o disco contínuo cabe no domínio; `partial_support`, que há células mas o disco é truncado; e `no_support`, que nenhuma célula da grade intersecta o disco. `parquet_state_status` separa estados presentes, ausentes com suporte, ausentes sem suporte e tempos fora do período comparável.

**Validação.** A transformação falha se checksum, schema, chaves, ordenação, categorias ou contagens divergirem. O [`validation_report.json`](../outputs/00_data_acquisition/validation_report.json) registra a correspondência com o Parquet atual e os quatro casos de regressão. O [`provenance_manifest.json`](../outputs/00_data_acquisition/provenance_manifest.json) registra fonte, ambiente, scripts e hashes dos produtos.

## Análise exploratória dos ventos associados aos ciclones

**Contexto e pergunta.** Esta é uma única análise exploratória: começa pela caracterização da estrutura dos dados e avança para a descrição das tracks, de `wind_speed` e das excedências por fase e quadrante. Ela também fornece um exemplo visual do campo q90 ao redor de um ciclone.

**Objeto.** O conjunto [`cyclone_exceedances_by_track_2010_2020_p90.parquet`](../data/cyclone_exceedances_by_track_2010_2020_p90.parquet), documentado por [`COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`](../data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md). O formato de armazenamento é Parquet; o objeto científico descrito são os ventos e as excedências vinculados às tracks.

**Unidades e agrupamentos.** O ciclone (`track_id`) é a unidade científica principal, conforme [D-002](decisions.md#d-002--usar-o-ciclone-como-unidade-de-análise). Um estado ciclone-tempo é o par único `track_id + time`. Cada linha armazena uma posição espacial vinculada a um ciclone e instante. Boxplots e heatmaps usam essas linhas e são identificados como descrições pontuais, não como amostras independentes. Para visualização, `intensification 2`, `mature 2` e `decay 2` são agrupadas às fases principais correspondentes conforme [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias); os valores originais permanecem preservados.

**Proveniência e escopo das fases.** A coluna `phase` foi herdada de `period` no Zenodo 18133432, que declara uso do [CycloPhaser](https://doi.org/10.21105/joss.07363) para um recorte limitado às regiões de gênese `ARG`, `SE-BR` e `LA-PLATA`. O Mendeley V4 é a referência histórica da família de tracks, não a fonte operacional desse namespace. A origem dos rótulos está confirmada; a versão e configuração da execução que delimitou os períodos permanecem abertas em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases).

**Caracterização estrutural.** [`inspect_parquet.py`](../scripts/01_data_overview/inspect_parquet.py) lê número de linhas, esquema, nulos e extremos observados, conta `track_id` distintos, categorias de `phase`, quadrantes e flags de excedência e registra exemplos e hashes. O resultado reproduzível é [`structural_summary.json`](../outputs/01_data_overview/structural_summary.json).

**Exploração descritiva.** [`exploratory_analysis.py`](../scripts/02_exploratory_analysis/exploratory_analysis.py) consulta os mesmos dados com DuckDB. Ele produz: mapa dos centros de todas as tracks; quantis de vento por fase e pelos dois sistemas de quadrantes; ocorrência de thresholds por estado ciclone-tempo; contagens q90 e percentuais q95 por fase e quadrante; e tabelas CSV correspondentes. Os heatmaps usam uma escala sequencial de amarelo-claro a roxo-escuro.

**Animação.** O exemplo seleciona de forma determinística o `track_id` da linha com maior `wind_speed` global. Para cada tempo existente no Parquet condicionado, mostra apenas pontos com `exceeded_q90 = true`, coloridos por velocidade do vento, além do centro colorido pela fase e de um círculo de 1.100 km. Áreas em branco significam somente “não desenhado”: sem consultar estado, grade, raio e domínio, elas não distinguem não-excedência, linha não armazenada e posição não avaliada. O painel esquerdo desenha os setores geográficos fixos. No painel direito, a orientação reproduz a regra do gerador: diferença centrada entre centros vizinhos da série de 6 h, diferença simples nas pontas, longitude corrigida por `cos(lat)` e fallback para leste quando o deslocamento é nulo. A extensão fixa envolve todos os centros da track presentes no Parquet, seus raios de 1.100 km e margem de 1°.

**Resultado descritivo.** Foram observados 1.781 ciclones distintos, 20.101 estados ciclone-tempo, 17.182.983 linhas espaciais e 17 colunas. O [dicionário de dados](data_dictionary.md) distingue a unidade de análise da unidade de armazenamento.

**Interpretação.** As figuras sustentam observações descritivas do recorte. Elas não estimam probabilidades, não corrigem a contribuição desigual de ciclones ou durações e não representam um footprint probabilístico ou hazard geográfico.

**Limitações.** O Parquet de vento armazena apenas pontos que passaram por `wind_speed > min(15,6; q90_local)`. Células omitidas dentro de um estado e suporte conhecidos podem ser reconstruídas como falsas para as seis flags, mas posições sem suporte não são zeros. Estados inteiros também desaparecem: o catálogo canônico recupera 9.210 no período, dos quais 3.233 têm suporte e 5.977 não intersectam o domínio. O p90 atual usa a própria janela de 2010–2020; há 13.404 linhas com `exceeded_q90 = false` e 509.788 linhas sem fase. A versão e a configuração exatas do CycloPhaser continuam desconhecidas. Esses produtos permanecem descritivos e não constituem coverage probability, footprint probabilístico ou hazard.

## Distinções conceituais a preservar

- **Excursion set:** realização espacial de excedência para um campo, evento ou instante, conforme definição futura.
- **Ocorrência / coverage probability:** probabilidade condicional de uma posição pertencer a um conjunto de excedência.
- **Magnitude condicional:** intensidade do vento dado que a excedência ocorreu; responde a outra pergunta.
- **Footprint:** requer definição operacional explícita antes de qualquer uso quantitativo.
- **Hazard geográfico:** exigirá uma construção que considere frequência, trajetórias, duração, estados e distribuição condicional dos ventos. Um padrão exploratório storm-relative não basta.

Essas distinções orientam a documentação; nenhuma formulação ou transformação foi escolhida. Quando surgir uma análise metodológica, descreva linearmente contexto, pergunta, motivação, unidade de análise, dados, formulação e termos, intuição, procedimento, hipóteses, diagnósticos, critério de decisão, resultado e limitações. Use equações apenas quando realmente explicarem o método e defina cada termo, domínio e unidade.
