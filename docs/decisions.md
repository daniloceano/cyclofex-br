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
- **Status:** `PROVISIONAL`
- **Questão:** como representar de forma legível as fases de um segundo ciclo na mesma track?
- **Alternativas consideradas:** mostrar as oito categorias literalmente ou reunir os rótulos `intensification 2`, `mature 2` e `decay 2` às respectivas fases principais.
- **Evidência disponível:** o sufixo `2` marca um segundo ciclo de vida na mesma track. A definição operacional das fases e da transição para esse segundo ciclo ainda não foi recuperada em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases).
- **Decisão atual:** agrupar os rótulos com sufixo `2` apenas nas figuras e resumos exploratórios. Preservar os valores originais no conjunto de dados e no resumo estrutural. Manter `residual` e ausências separados.
- **Justificativa:** o agrupamento permite aplicar a paleta de fases solicitada e mantém os gráficos legíveis, sem modificar o dado-fonte.
- **Experimentos relacionados:** nenhum; é uma escolha provisória de apresentação.
- **Revisar se:** a definição operacional do catálogo exigir que os ciclos sejam comparados separadamente ou que a transição entre ciclos seja preservada nas figuras.
