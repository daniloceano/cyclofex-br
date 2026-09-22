# Fluxos computacionais

## Ambiente

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` é a referência de dependências Python. A animação exige `ffmpeg`; o Cartopy pode obter a linha de costa Natural Earth na primeira execução.

## Aquisição e cache

```sh
.venv/bin/python scripts/00_data_acquisition/download_tracks_zenodo.py
```

O CSV oficial é armazenado em `data/raw/zenodo/18133432/`, ignorado pelo Git. Um cache só é reutilizado se nome, tamanho, MD5, SHA-256 e schema coincidirem. O arquivo bruto pode ser reconstruído da fonte; sua remoção após conversão deve ser solicitada explicitamente pelo parâmetro previsto no preparador.

## Preparação e validação

```sh
.venv/bin/python scripts/00_data_acquisition/prepare_tracks.py
```

O comando gera os catálogos horário e de 6 h, o manifesto de proveniência e o relatório de validação. Ele não recalcula vento, percentis ou *footprints*.

## Caracterização e análise exploratória

```sh
.venv/bin/python scripts/01_data_overview/inspect_parquet.py
.venv/bin/python scripts/02_exploratory_analysis/exploratory_analysis.py
```

O primeiro comando atualiza o resumo estrutural. O segundo atualiza tabelas, figuras, resumo JSON e animação. Ambos devem registrar a entrada e seu hash. Executá-los é reprodução de análise existente; alterações metodológicas exigem registro científico correspondente.

## E-001 — orientação

```sh
.venv/bin/python -m unittest scripts/03_e001_orientation/test_orientation.py
.venv/bin/python scripts/03_e001_orientation/e001_orientation.py
.venv/bin/python scripts/03_e001_orientation/methodology_figures.py
```

O primeiro comando verifica a geometria; o segundo valida hashes, calcula headings do catálogo completo, agrega q95 e suporte na grade relativa, executa o bootstrap e atualiza os produtos analíticos em `outputs/03_e001_orientation/`. O terceiro recria o fluxograma, a grade real com um estado observado, a comparação entre quadrantes fixos e rotacionados e as figuras didáticas das métricas, sem recalcular ou modificar o experimento. Mudanças em `protocol.json` caracterizam outro protocolo e exigem novo registro científico.

## E-002 — weighting

```sh
.venv/bin/python scripts/04_e002_weighting/test_weighting.py
.venv/bin/python scripts/04_e002_weighting/e002_weighting.py
```

O teste verifica identidades de normalização. O pipeline reutiliza as funções espaciais de E-001, valida hashes e toda a população antes de calcular *equal-state* e *equal-cyclone*. Ele exige regressão das métricas e do bootstrap *equal-state*, produz diagnósticos de contribuição, métricas globais e por fase, TV, bootstrap por ciclone e figuras em `outputs/04_e002_weighting/`. Os caminhos são independentes do diretório corrente.

## Geração do dashboard

```sh
python3 dashboard/build_docs.py
```

O gerador requer Pandoc apenas no build. Ele converte as fontes listadas em `dashboard/build_docs.py`, reescreve links entre páginas canônicas, aplica navegação temática e produz HTML estático. A abertura do dashboard não requer servidor nem JavaScript.

Não edite o corpo dos HTML gerados. Mudanças de conteúdo devem ocorrer no Markdown; mudanças compartilhadas de apresentação pertencem ao template ou a `dashboard/docs.css`.

## Verificações antes de entregar documentação

1. Execute o gerador sem erros.
2. Confirme que todos os arquivos científicos esperados possuem HTML.
3. Verifique links locais e recursos referenciados.
4. Abra a homepage e ao menos uma página com tabela, figura e vídeo em navegador.
5. Faça o teste de auditoria humana definido no [padrão documental](../documentation_guidelines.md).
