# Metodologia em uso

A metodologia científica para modelar footprints e estimar hazard **ainda não foi adotada**. A proposta atual é um mapa de hipóteses revisável. Este documento descreve apenas procedimentos efetivamente executados; perguntas, testes, decisões e pressupostos têm seus próprios registros.

## Análise exploratória dos ventos associados aos ciclones

**Contexto e pergunta.** Esta é uma única análise exploratória: começa pela caracterização da estrutura dos dados e avança para a descrição das tracks, de `wind_speed` e das excedências por fase e quadrante. Ela também fornece um exemplo visual do campo q90 ao redor de um ciclone.

**Objeto.** O conjunto [`cyclone_exceedances_by_track_2010_2020_p90.parquet`](../data/cyclone_exceedances_by_track_2010_2020_p90.parquet), documentado por [`COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md`](../data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md). O formato de armazenamento é Parquet; o objeto científico descrito são os ventos e as excedências vinculados às tracks.

**Unidades e agrupamentos.** O ciclone (`track_id`) é a unidade científica principal, conforme [D-002](decisions.md#d-002--usar-o-ciclone-como-unidade-de-análise). Um estado ciclone-tempo é o par único `track_id + time`. Cada linha armazena uma posição espacial vinculada a um ciclone e instante. Boxplots e heatmaps usam essas linhas e são identificados como descrições pontuais, não como amostras independentes. Para visualização, `intensification 2`, `mature 2` e `decay 2` são agrupadas às fases principais correspondentes conforme [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias); os valores originais permanecem preservados.

**Caracterização estrutural.** [`inspect_parquet.py`](../scripts/01_data_overview/inspect_parquet.py) lê número de linhas, esquema, nulos e extremos observados, conta `track_id` distintos, categorias de `phase`, quadrantes e flags de excedência e registra exemplos e hashes. O resultado reproduzível é [`structural_summary.json`](../outputs/01_data_overview/structural_summary.json).

**Exploração descritiva.** [`exploratory_analysis.py`](../scripts/02_exploratory_analysis/exploratory_analysis.py) consulta os mesmos dados com DuckDB. Ele produz: mapa dos centros de todas as tracks; quantis de vento por fase e pelos dois sistemas de quadrantes; ocorrência de thresholds por estado ciclone-tempo; contagens q90 e percentuais q95 por fase e quadrante; e tabelas CSV correspondentes. Os heatmaps usam uma escala sequencial de amarelo-claro a roxo-escuro.

**Animação.** O exemplo seleciona de forma determinística o `track_id` da linha com maior `wind_speed` global. Para cada tempo da track, mostra apenas pontos com `exceeded_q90 = true`, coloridos por velocidade do vento, além do centro colorido pela fase e de um círculo de 1.100 km. O painel esquerdo desenha os setores geográficos fixos. No painel direito, a orientação reproduz a regra do gerador: diferença centrada entre centros vizinhos da série de 6 h, diferença simples nas pontas, longitude corrigida por `cos(lat)` e fallback para leste quando o deslocamento é nulo. A extensão fixa envolve todos os centros da track, seus raios de 1.100 km e margem de 1°.

**Resultado descritivo.** Foram observados 1.781 ciclones distintos, 20.101 estados ciclone-tempo, 17.182.983 linhas espaciais e 17 colunas. O [dicionário de dados](data_dictionary.md) distingue a unidade de análise da unidade de armazenamento.

**Interpretação.** As figuras sustentam observações descritivas do recorte. Elas não estimam probabilidades, não corrigem a contribuição desigual de ciclones ou durações e não representam um footprint probabilístico ou hazard geográfico.

**Limitações.** O p90 atual usa a própria janela de 2010–2020 e será recalculado após a incorporação das tracks completas de 1979–2020. Há 13.404 linhas com `exceeded_q90 = false` porque o recorte também aceita `wind_speed > 15,6 m/s`; 509.788 linhas têm fase ausente. A definição operacional das fases e do segundo ciclo permanece em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases). O círculo é truncado nos limites do domínio, e posições fora dele não foram avaliadas.

## Distinções conceituais a preservar

- **Excursion set:** realização espacial de excedência para um campo, evento ou instante, conforme definição futura.
- **Ocorrência / coverage probability:** probabilidade condicional de uma posição pertencer a um conjunto de excedência.
- **Magnitude condicional:** intensidade do vento dado que a excedência ocorreu; responde a outra pergunta.
- **Footprint:** requer definição operacional explícita antes de qualquer uso quantitativo.
- **Hazard geográfico:** exigirá uma construção que considere frequência, trajetórias, duração, estados e distribuição condicional dos ventos. Um padrão exploratório storm-relative não basta.

Essas distinções orientam a documentação; nenhuma formulação ou transformação foi escolhida. Quando surgir uma análise metodológica, descreva linearmente contexto, pergunta, motivação, unidade de análise, dados, formulação e termos, intuição, procedimento, hipóteses, diagnósticos, critério de decisão, resultado e limitações. Use equações apenas quando realmente explicarem o método e defina cada termo, domínio e unidade.
