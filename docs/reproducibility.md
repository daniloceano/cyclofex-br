# Proveniência e reprodutibilidade

## Papel desta camada

A narrativa científica explica o que foi feito e o que significa. Esta página conecta cada afirmação aos dados, versões, produtos e código necessários para auditoria computacional. Os detalhes de implementação ficam na [referência técnica](internal/README.md).

## Linhagem dos dados

| Objeto científico | Fonte ou produto | Versão e integridade | Transformação e evidência |
| --- | --- | --- | --- |
| Tracks e lifecycle horários | Zenodo 18133432, `tracks_SAt_filtered_with_energetics.csv` | registro v1; MD5 `a413e7f8…1d63d72`; SHA-256 `bf1059ab…d63cc26` | Catálogo mínimo validado contra schema, contagens e ordem |
| Catálogo horário canônico | [`tracks_SAt_1979_2020.parquet`](../data/tracks_SAt_1979_2020.parquet) | SHA-256 `7d8d628a…a71c553`; 631.009 linhas | Seleção e renomeação de sete campos; fases sem agrupamento |
| Estados de 6 h e suporte | [`cyclone_states_era5_6h_1979_2020.parquet`](../data/cyclone_states_era5_6h_1979_2020.parquet) | SHA-256 `4865bbc3…864782`; 109.857 linhas | Vizinho temporal, deduplicação por estado e suporte de 1.100 km |
| Vento e excedências | `cyclone_exceedances_by_track_2010_2020_p90.parquet` | SHA-256 `3913a1d8…d9efa0c`; 17.182.983 linhas | Produto preexistente condicionado por intensidade |
| Metadados estruturais | [`structural_summary.json`](../outputs/01_data_overview/structural_summary.json) | contém hash da entrada e schema | Caracterização reproduzível do Parquet de vento |
| Resultados exploratórios | [`analysis_summary.json`](../outputs/02_exploratory_analysis/analysis_summary.json) e tabelas/figuras associadas | entrada identificada pelo mesmo SHA-256 | Consultas descritivas, figuras e exemplo determinístico |
| E-001 — orientação | [`summary.json`](../outputs/03_e001_orientation/summary.json), tabelas e figuras associadas | protocolo, script, entradas e semente registrados no resumo | Coordenadas contínuas, suporte reconstruído, métricas e bootstrap por ciclone |
| E-002 — weighting | [`summary.json`](../outputs/04_e002_weighting/summary.json), contribuições, métricas, mapas e bootstrap | protocolo, scripts, entradas, resumo de E-001 e semente registrados | Regressão de E-001, quatro distribuições, concentração, TV, fases e incerteza |

O manifesto completo, com schemas, versões de ambiente e hashes dos scripts, está em [`provenance_manifest.json`](../outputs/00_data_acquisition/provenance_manifest.json). Os checks e contagens da reconstrução estão em [`validation_report.json`](../outputs/00_data_acquisition/validation_report.json).

## Rastreabilidade por etapa científica

### Dados e preparação

- **Fonte:** Zenodo 18133432; Mendeley V4 apenas como genealogia histórica.
- **Produtos:** catálogos horário e de 6 h.
- **Código:** [`download_tracks_zenodo.py`](../scripts/00_data_acquisition/download_tracks_zenodo.py) e [`prepare_tracks.py`](../scripts/00_data_acquisition/prepare_tracks.py).
- **Decisão:** [D-004](decisions.md#d-004--adotar-o-zenodo-18133432-como-fonte-canônica-operacional-das-tracks-e-do-lifecycle).
- **Questão ainda aberta:** [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases).

### Caracterização e análise exploratória

- **Entrada:** recorte de vento com SHA-256 `3913a1d8ab49856212e1e5a19275b3644ae947dcf940872fb2f40a884d9efa0c`.
- **Código:** [`inspect_parquet.py`](../scripts/01_data_overview/inspect_parquet.py) e [`exploratory_analysis.py`](../scripts/02_exploratory_analysis/exploratory_analysis.py).
- **Tabelas:** [`phase_statistics.csv`](../outputs/02_exploratory_analysis/phase_statistics.csv), [`quadrant_statistics.csv`](../outputs/02_exploratory_analysis/quadrant_statistics.csv), [`cyclone_timestep_exceedances_by_phase.csv`](../outputs/02_exploratory_analysis/cyclone_timestep_exceedances_by_phase.csv) e [`phase_quadrant_exceedances.csv`](../outputs/02_exploratory_analysis/phase_quadrant_exceedances.csv).
- **Figuras:** [tracks](../outputs/02_exploratory_analysis/all_tracks_by_phase.png), [boxplots](../outputs/02_exploratory_analysis/wind_speed_boxplots.png), [ocorrências](../outputs/02_exploratory_analysis/exceedance_occurrence_by_phase.png) e [fase por quadrante](../outputs/02_exploratory_analysis/exceedances_by_phase_and_quadrant.png).
- **Caso individual:** [vídeo](../outputs/02_exploratory_analysis/max_wind_cyclone_animation.mp4) e [quadro do máximo](../outputs/02_exploratory_analysis/max_wind_cyclone_peak_frame.png).
- **Decisões:** [D-002](decisions.md#d-002--usar-o-ciclone-como-unidade-de-análise) e [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias).

### E-001 — orientação pelo movimento

- **Protocolo congelado:** [`protocol.json`](../scripts/03_e001_orientation/protocol.json), com q95, grade de 50 km, corte de 5 km/h, weighting, métricas, bootstrap e critério de decisão.
- **Código:** [`e001_orientation.py`](../scripts/03_e001_orientation/e001_orientation.py) e [`test_orientation.py`](../scripts/03_e001_orientation/test_orientation.py).
- **Resumo:** [`summary.json`](../outputs/03_e001_orientation/summary.json), incluindo hashes SHA-256 das três entradas, protocolo e script.
- **Tabelas:** métricas por estrato e fase literal, comparações com IC, réplicas bootstrap, bins com suporte, distribuição da translação e contagens de estados.
- **Figuras:** comparação global, estratos de fase, diagnóstico do heading e sanidade da rotação.
- **Semente e réplicas:** `20260921`, 500 réplicas pareadas por `track_id`.
- **Decisão:** [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001).

### E-002 — sensibilidade ao weighting

- **Protocolo congelado:** [`protocol.json`](../scripts/04_e002_weighting/protocol.json), com isolamento do weighting, fórmulas, população esperada, métricas, bootstrap e critério de robustez.
- **Código:** [`e002_weighting.py`](../scripts/04_e002_weighting/e002_weighting.py) e [`test_weighting.py`](../scripts/04_e002_weighting/test_weighting.py); a geometria é importada da implementação congelada de E-001.
- **Resumo:** [`summary.json`](../outputs/04_e002_weighting/summary.json), incluindo hashes das três entradas, protocolo, script e resumo de E-001.
- **Tabelas:** contribuições por `track_id`, concentração por fase, quatro conjuntos de métricas, contrastes, probabilidades por bin e 10.000 diferenças bootstrap.
- **Figuras:** distribuição de estados positivos, contribuição acumulada, dois contrastes de weighting, comparação de orientação sob *equal-cyclone* e intervalos.
- **Semente e réplicas:** `20260921`, 500 réplicas por `track_id`.
- **Regressão:** contagens exatas; áreas *equal-state* idênticas e métricas contínuas e resumos bootstrap dentro de $10^{-6}$.
- **Decisão:** [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado).

## Reproduzir a preparação

As dependências estão fixadas em [`requirements.txt`](../requirements.txt). A sequência técnica é:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/00_data_acquisition/download_tracks_zenodo.py
.venv/bin/python scripts/00_data_acquisition/prepare_tracks.py
```

O download bruto fica em cache ignorado pelo Git. Ele só é reutilizado depois da validação de tamanho, MD5, SHA-256 e schema.

## Reproduzir a análise exploratória

```sh
.venv/bin/python scripts/01_data_overview/inspect_parquet.py
.venv/bin/python scripts/02_exploratory_analysis/exploratory_analysis.py
```

A animação requer `ffmpeg`; o Cartopy pode baixar a costa Natural Earth para seu cache na primeira execução. Esses comandos reproduzem produtos existentes; eles não foram executados nesta reorganização documental.

## Reproduzir E-001

```sh
.venv/bin/python -m unittest scripts/03_e001_orientation/test_orientation.py
.venv/bin/python scripts/03_e001_orientation/e001_orientation.py
```

O experimento valida os hashes antes de executar, processa as excedências em lotes, reconstrói o suporte sem materializar um produto de 136 milhões de linhas e sobrescreve deterministicamente os produtos de `outputs/03_e001_orientation/`. O horário de conclusão no JSON é o único campo não determinístico.

## Reproduzir E-002

```sh
.venv/bin/python scripts/04_e002_weighting/test_weighting.py
.venv/bin/python scripts/04_e002_weighting/e002_weighting.py
```

Os caminhos são resolvidos a partir do próprio script; a execução também foi validada fora da raiz usando o caminho absoluto do interpretador e do arquivo. Os produtos de E-002 são determinísticos, inclusive a data científica fixada no protocolo. O pipeline valida hashes, população, métricas e bootstrap *equal-state* antes de aceitar os resultados novos.

## Gerar o relatório HTML

Os arquivos Markdown em `docs/` são as fontes canônicas. Com Pandoc disponível:

```sh
python3 dashboard/build_docs.py
```

O resultado é HTML estático: abrir [`dashboard/index.html`](../dashboard/index.html) não exige servidor, JavaScript ou acesso aos scripts científicos.

## Lacunas de reprodutibilidade conhecidas

- versão/reprocessamento exato do ERA5 do produto original;
- artefato versionado dos percentis locais;
- versão, ambiente e configuração da execução original do CycloPhaser;
- justificativa científica original do raio de 1.100 km;
- adequação científica do corte de heading de 5 km/h fora do escopo específico de E-001/E-002; o fallback leste não foi usado nos experimentos.

Essas lacunas não são preenchidas por suposição. Elas aparecem também em [questões abertas](open_questions.md) e [limitações](limitations.md).
