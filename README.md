# cyclofex-br

O **cyclofex-br** investiga a estrutura espacial de ventos extremos associados a ciclones extratropicais no Atlântico Sul. A pergunta geral é como representar esses ventos em relação ao ciclone e, eventualmente, estimar o hazard em coordenadas geográficas. **A metodologia ainda está em desenvolvimento.** A proposta científica atual é uma hipótese de trabalho revisável, não uma especificação definitiva.

## Comece por aqui

| Para encontrar... | Acesse |
| --- | --- |
| Dados disponíveis | [`data/`](data/) e [dicionário de dados](docs/data_dictionary.md) |
| Código e resultados das análises | [`scripts/`](scripts/) ↔ [`outputs/`](outputs/) |
| Metodologia efetivamente usada | [Metodologia](docs/methodology.md) |
| Por que uma escolha foi feita | [Decisões](docs/decisions.md) |
| O que foi testado, inclusive alternativas rejeitadas | [Experimentos](docs/experiments.md) |
| O que falta decidir | [Questões abertas](docs/open_questions.md) |
| Pressupostos em uso | [Pressupostos](docs/assumptions.md) |
| Visão humana do estado do projeto | [Dashboard](dashboard/index.html) |

Abra `dashboard/index.html` diretamente no navegador. A página inicial funciona como mapa do projeto e aponta para a análise e a documentação detalhada; os arquivos Markdown em `docs/` continuam sendo a fonte canônica. O painel é estático e não executa cálculos no navegador.

## Estado atual

O conjunto atual de [ventos associados às tracks](data/cyclone_exceedances_by_track_2010_2020_p90.parquet), acompanhado pela [documentação de suas colunas](data/COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md), contém **1.781 ciclones distintos**, identificados por `track_id`, e 17.182.983 linhas de pontos de grade associados aos ciclones e instantes. A unidade de análise é o ciclone; as linhas espaciais não são tratadas como observações independentes. O rótulo `p90` identifica o recorte atual e **não fixa o threshold do projeto**.

O catálogo operacional canônico de tracks e lifecycle é o arquivo `tracks_SAt_filtered_with_energetics.csv` do [Zenodo 18133432](https://zenodo.org/records/18133432), DOI [`10.5281/zenodo.18133432`](https://doi.org/10.5281/zenodo.18133432), conforme [D-004](docs/decisions.md#d-004--adotar-o-zenodo-18133432-como-fonte-canônica-operacional-das-tracks-e-do-lifecycle). A coluna `phase` preserva `period` dessa fonte, inclusive sufixos, `residual` e nulos. A base de [Gramcianinov et al. (2020)](https://doi.org/10.17632/kwcvfr52hp.4) permanece como referência histórica da família de tracks, mas seus IDs e universo de sistemas não são o input operacional do projeto atual. A [Q-004](docs/open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases) registra o que ainda falta para reproduzir a execução original do CycloPhaser.

A [análise exploratória](dashboard/exploratory_analysis.html) reúne a caracterização da estrutura e a exploração visual: esquema e contagens, todas as tracks, distribuições de vento, ocorrências de excedência por fase e quadrante e uma animação do ciclone que contém o maior vento observado.

## Como adicionar uma análise

Crie `scripts/<analise>/` apenas quando houver uma pergunta e um script reais. Grave produtos reproduzíveis em `outputs/<analise>/`, mantendo a correspondência direta. O script deve identificar entrada, parâmetros e caminho de saída relativos ao repositório. Registre perguntas, testes, decisões e pressupostos nos documentos apropriados quando essas informações forem relevantes para retomar o raciocínio. Acrescente ao dashboard um bloco com o resultado real e referências aos IDs pertinentes. Não é necessário criar pastas para análises futuras.

## Preparar o catálogo de tracks e estados

As dependências Python estão registradas em `requirements.txt`. O download oficial é armazenado em `data/raw/`, ignorado pelo Git, e reutilizado somente se tamanho, MD5, SHA-256 e schema continuarem válidos:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/00_data_acquisition/download_tracks_zenodo.py
.venv/bin/python scripts/00_data_acquisition/prepare_tracks.py
```

A segunda etapa produz:

- [`data/tracks_SAt_1979_2020.parquet`](data/tracks_SAt_1979_2020.parquet), catálogo horário mínimo;
- [`data/cyclone_states_era5_6h_1979_2020.parquet`](data/cyclone_states_era5_6h_1979_2020.parquet), estados associados ao ERA5 de 6 h e metadados de suporte;
- [`provenance_manifest.json`](outputs/00_data_acquisition/provenance_manifest.json) e [`validation_report.json`](outputs/00_data_acquisition/validation_report.json).

O CSV bruto não precisa ser versionado. Depois de uma conversão validada, ele pode ser removido explicitamente com `prepare_tracks.py --remove-raw-after-success`; uma nova execução do script de aquisição o reconstrói da fonte oficial. O pipeline não recalcula vento, percentis ou footprints.

## Reproduzir a análise exploratória

As dependências Python da caracterização, das figuras e da animação estão registradas em `requirements.txt`. Com Python 3 disponível:

```sh
.venv/bin/python scripts/01_data_overview/inspect_parquet.py
```

O primeiro script reescreve o [resumo estrutural](outputs/01_data_overview/structural_summary.json), incluindo o SHA-256 da entrada. O segundo produz as figuras, tabelas e a animação da mesma análise exploratória:

```sh
.venv/bin/python scripts/02_exploratory_analysis/exploratory_analysis.py
```

Além dos pacotes em `requirements.txt`, a montagem do vídeo requer `ffmpeg`. Na primeira execução, o Cartopy pode baixar a linha de costa Natural Earth de 50 m para seu cache local.

Após editar qualquer documento em `docs/`, atualize as páginas HTML do dashboard com `python3 dashboard/build_docs.py`. Esse comando usa Pandoc **apenas na geração**; abrir o painel não requer Pandoc, servidor ou JavaScript.
