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
- **Revisada:** 2026-09-21
- **Status:** `ADOPTED`
- **Questão:** como representar de forma legível ocorrências repetidas de uma fase na mesma track?
- **Alternativas consideradas:** mostrar as oito categorias literalmente ou reunir os rótulos `intensification 2`, `mature 2` e `decay 2` às respectivas fases principais.
- **Evidência disponível:** conforme documentado em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases), o CycloPhaser acrescenta o sufixo quando uma fase reaparece em um bloco não contíguo. O número indica a ordem da ocorrência, não uma classe física diferente.
- **Decisão atual:** agrupar os rótulos com sufixo `2` em figuras exploratórias e, quando preregistrado, em estratos do mesmo tipo físico de fase. Preservar sempre resultados pelos valores originais; manter `residual` e ausências separados.
- **Justificativa:** o agrupamento compara tipos equivalentes de fase e evita estratos muito pequenos sem modificar o dado-fonte. Em E-001, `mature 2` tinha apenas 35 estados q95-positivos, enquanto o estrato maduro agrupado tinha 1.821; as métricas por rótulo literal foram preservadas. A ordem original continua disponível quando a pergunta envolver reintensificação ou sequência do ciclo de vida.
- **Experimentos relacionados:** E-001 aplicou a regra nos quatro estratos de fase e publicou também a tabela literal.
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

## D-005 · Manter aberta a escolha entre centered e motion-relative após E-001

- **Data:** 2026-09-21
- **Status:** `PROVISIONAL`
- **Questão:** a orientação pelo movimento deve substituir a centralização geográfica como representação principal?
- **Alternativas consideradas:** adotar *motion-relative*, manter *centered* como representação científica principal ou preservar a questão aberta.
- **Evidência disponível:** em [E-001](e001_orientation.md), *motion-relative* reduziu A50 em 32.500 km², mas aumentou A75 em 45.000 km², A90 em 97.500 km² e RMS em 7,69 km. O IC bootstrap da diferença de entropia incluiu zero, e somente uma das quatro fases teve entropia e A75 pontualmente menores em conjunto.
- **Decisão atual:** não adotar nenhuma das duas representações como cientificamente superior. Usar *centered* apenas como referência simples e *motion-relative* como diagnóstico de assimetria quando necessário, sempre identificando que a escolha permanece aberta.
- **Justificativa:** as famílias de métricas e os estratos de fase não satisfizeram o critério preregistrado. A rotação mudou a forma e concentrou o núcleo, mas não organizou consistentemente a distribuição inteira.
- **Experimento relacionado:** E-001, status `INCONCLUSIVE`.
- **Revisar se:** um protocolo posterior isolar weighting, threshold, tamanho ou outra explicação sem ajustar retrospectivamente E-001.

**Revisão posterior, sem alteração do registro histórico.** E-002 isolou weighting e classificou a conclusão como robusta: sob *equal-cyclone*, A50 continuou favorecendo *motion-relative*, enquanto A75, A90 e RMS favoreceram *centered*. D-005 permanece vigente; E-001 continua `INCONCLUSIVE` sob seu protocolo original.

## D-006 · Usar o weighting que corresponde ao estimando declarado

- **Data:** 2026-09-21
- **Status:** `ADOPTED`
- **Questão:** *equal-state* ou *equal-cyclone* deve ser a representação universal das excedências q95?
- **Alternativas consideradas:** substituir *equal-state* por *equal-cyclone* em todas as análises; preservar *equal-state* sempre; ou declarar o estimando-alvo e manter ambos para perguntas diferentes.
- **Evidência disponível:** [E-002](e002_weighting.md) encontrou contribuição desigual em *equal-state* — os 10% superiores receberam 22,52% da massa e $N_{eff}=1.288,8$ entre 1.757 ciclones positivos —, mas nenhum weighting é um erro. A distância de variação total foi aproximadamente 0,079 nas duas orientações, e a conclusão de E-001 permaneceu robusta.
- **Decisão atual:** usar *equal-state* quando o estimando for a distribuição de um estado q95-positivo selecionado ao acaso; usar *equal-cyclone* quando o estimando for a distribuição média entre ciclones q95-positivos. Toda análise deve declarar qual população resume e, quando a escolha puder afetar a conclusão, apresentar o outro weighting como sensibilidade.
- **Não decidido:** nenhuma orientação foi promovida a principal; *equal-cyclone* não foi escolhido apenas porque `track_id` é a unidade inferencial.
- **Justificativa:** weighting define a população descritiva, enquanto bootstrap por ciclone define como a dependência é respeitada na incerteza. Confundir essas funções apagaria uma diferença científica real entre estimandos.
- **Experimento relacionado:** E-002, status `ADOPTED`, classificação `ROBUST_TO_WEIGHTING`.
- **Revisar se:** uma pergunta futura definir outra população-alvo, ou dados completos permitirem um estimando temporal ou climatológico distinto.
