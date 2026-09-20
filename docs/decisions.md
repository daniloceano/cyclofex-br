# Decisões

Decisões mantêm IDs `D-...` mesmo quando forem substituídas. Status possíveis: `PROVISIONAL`, `ADOPTED`, `SUPERSEDED`. Uma mudança deve acrescentar a nova decisão e marcar a antiga como `SUPERSEDED`, com vínculo entre elas.

## D-001 · Organizar código e produtos por análise

- **Data:** 2026-09-18
- **Status:** `ADOPTED`
- **Questão:** como localizar o código responsável por cada produto sem criar arquitetura prematura?
- **Alternativas consideradas:** diretórios genéricos compartilhados ou uma estrutura profunda antecipada; nenhuma foi testada empiricamente nesta etapa.
- **Evidência disponível:** a análise exploratória possui uma etapa de caracterização estrutural e outra de visualização, cada uma com produtos reproduzíveis; a organização simples atende ao estado atual e à preferência expressa para o projeto.
- **Decisão atual:** manter `scripts/<analise>/` ↔ `outputs/<analise>/`; criar subdiretórios somente quando existir análise e produto correspondentes.
- **Justificativa:** a correspondência permite rastrear resultados com poucos elementos e sem abstrações ociosas.
- **Experimentos relacionados:** nenhum; trata-se de uma decisão estrutural inicial.
- **Revisar se:** o uso efetivo mostrar duplicação ou dificuldade de localização que a estrutura atual não resolva.

## D-002 · Usar o ciclone como unidade de análise

- **Data:** 2026-09-19
- **Status:** `ADOPTED`
- **Questão:** qual unidade deve orientar contagens, inferência e validação?
- **Evidência disponível:** o conjunto de dados inclui `track_id`, definido como identificador do ciclone no catálogo; a caracterização encontrou 1.781 valores distintos. Cada ciclone contribui com muitas linhas espaciais e temporais.
- **Decisão atual:** usar o ciclone, identificado por `track_id`, como unidade fundamental de análise quando aplicável. O número principal apresentado no dashboard é a contagem de `track_id` únicos.
- **Justificativa:** linhas de pontos de grade do mesmo ciclone não devem ser tratadas como unidades independentes.
- **Questão relacionada:** [Q-001](open_questions.md#q-001--qual-é-a-unidade-de-uma-linha-e-como-ela-se-vincula-a-um-ciclone).
- **Experimentos relacionados:** nenhum; a decisão segue a estrutura documentada do dado e a definição científica do projeto.
- **Revisar se:** a chave do catálogo mudar, forem detectados `track_id` reutilizados ou uma análise específica exigir outra unidade claramente declarada.

## D-003 · Agrupar rótulos `phase 2` nas figuras exploratórias

- **Data:** 2026-09-19
- **Revisada:** 2026-09-20
- **Status:** `ADOPTED`
- **Questão:** como representar de forma legível ocorrências repetidas de uma fase na mesma track?
- **Alternativas consideradas:** mostrar as oito categorias literalmente ou reunir os rótulos `intensification 2`, `mature 2` e `decay 2` às respectivas fases principais.
- **Evidência disponível:** conforme documentado em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases), o CycloPhaser acrescenta o sufixo quando uma fase reaparece em um bloco não contíguo. O número indica a ordem da ocorrência, não uma classe física diferente.
- **Decisão atual:** agrupar os rótulos com sufixo `2` apenas nas figuras e resumos exploratórios. Preservar os valores originais no conjunto de dados e no resumo estrutural. Manter `residual` e ausências separados.
- **Justificativa:** o agrupamento compara tipos equivalentes de fase e mantém os gráficos legíveis sem modificar o dado-fonte. A ordem original continua disponível quando a pergunta envolver reintensificação ou sequência do ciclo de vida.
- **Experimentos relacionados:** nenhum; é uma escolha de apresentação baseada na semântica dos rótulos.
- **Revisar se:** a pergunta científica exigir comparar ocorrências sucessivas separadamente ou se a rodada com o CycloPhaser 2.0 alterar o esquema dos rótulos.

## D-004 · Adotar o Zenodo 18133432 como fonte canônica operacional das tracks e do lifecycle

- **Data:** 2026-09-20
- **Status:** `ADOPTED`
- **Questão:** qual fonte deve produzir o catálogo versionado de centros, estados e fases usado pelo projeto?
- **Alternativas consideradas:** usar diretamente o Mendeley V4; tratar o Parquet de vento como catálogo de estados; ou usar o arquivo oficial `tracks_SAt_filtered_with_energetics.csv` do Zenodo 18133432.
- **Evidência disponível:** o Zenodo reproduz `track_id`, centro e `period` dos 20.101 estados presentes no Parquet e recupera 9.210 estados omitidos pelo filtro de entrada. O pipeline de validação encontra 20.101/20.101 centros e fases correspondentes e zero estados inesperados. A correspondência Mendeley–Zenodo é parcial: os IDs foram renumerados, o universo mudou e o Zenodo inclui 2020.
- **Decisão atual:** adotar o [Zenodo 18133432](https://zenodo.org/records/18133432), DOI [`10.5281/zenodo.18133432`](https://doi.org/10.5281/zenodo.18133432), como fonte canônica operacional. Preservar somente o catálogo mínimo derivado, os scripts, hashes, schema e relatórios; manter o CSV bruto em cache ignorado pelo Git e reproduzível sob demanda.
- **Justificativa:** a fonte contém o denominador temporal necessário, preserva o lifecycle usado pelo Parquet e possui arquivo/checksum oficiais. O Parquet de vento é condicionado e perde estados inteiros; o Mendeley não conserva o namespace operacional atual.
- **Escopo:** aquisição e preparação de dados. A decisão não valida a metodologia original do CycloPhaser, não escolhe threshold de vento e não adota um modelo de ocorrência ou footprint.
- **Relação com o Mendeley:** DOI `10.17632/kwcvfr52hp.4` permanece documentado como referência histórica da família original de tracks, não como input de produção do catálogo atual.
- **Questões relacionadas:** [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases) e [Q-005](open_questions.md#q-005--qual-é-a-fonte-operacional-dos-estados-de-track-e-lifecycle).
- **Experimentos relacionados:** nenhum; trata-se de uma decisão de proveniência apoiada por validação de dados.
- **Revisar se:** o registro Zenodo receber uma nova versão, uma fonte oficial substituir explicitamente esse catálogo ou uma nova rodada versionada do CycloPhaser for adotada.
