# Auditoria simulada do relatório científico

- **Data:** 21 de setembro de 2026
- **Perspectiva:** pesquisador externo sem leitura prévia do código
- **Escopo:** páginas HTML geradas a partir do Markdown canônico
- **Resultado:** `PASS`

## Critério

Cada pergunta deve ser respondida pela narrativa do dashboard. Links de reprodutibilidade podem apontar para arquivos e código, mas a compreensão científica não pode depender de abrir esses artefatos.

| # | Pergunta do avaliador | Resposta encontrada no dashboard | Página principal |
| ---: | --- | --- | --- |
| 1 | Qual é a pergunta científica? | Representar ocorrência, geometria e magnitude de ventos extremos em relação a ciclones extratropicais sem confundir o padrão relativo com hazard geográfico. | [Visão geral](../index.md#o-problema-científico) |
| 2 | Por que o problema é relevante? | A track localiza o centro, mas não informa onde os ventos intensos ocorrem, que área ocupam nem como mudam no lifecycle; essa lacuna precede qualquer tradução geográfica. | [Visão geral](../index.md#o-problema-científico) |
| 3 | Quais dados são utilizados? | Tracks e fases do Zenodo, campos ERA5 a 10 m e um recorte condicionado de vento e excedências. | [Dados](../data.md) |
| 4 | Qual é a proveniência? | Zenodo 18133432 é a fonte operacional; Mendeley V4 é genealogia histórica; ERA5 fornece o vento, com lacunas de versão explicitadas. | [Dados](../data.md#tracks-e-ciclo-de-vida) e [Reprodutibilidade](../reproducibility.md#linhagem-dos-dados) |
| 5 | Qual é a unidade de análise? | O ciclone identificado por `track_id`; estados e pontos são níveis internos dependentes. | [Metodologia](../methodology.md#unidade-de-análise) |
| 6 | Como os dados foram preparados? | Track horária associada ao ERA5 de 6 h mais próximo, deduplicação por estado e classificação do suporte num raio de 1.100 km. | [Preparação dos dados](../data_preparation.md) |
| 7 | O que é um estado ciclone–tempo? | O par formado por um ciclone e um horário de campo ERA5 de 6 h. | [Dados](../data.md#tracks-e-ciclo-de-vida) |
| 8 | O que é suporte espacial? | O conjunto de células do domínio que poderia contribuir para um estado dentro de 1.100 km, classificado como completo, parcial ou ausente. | [Dados](../data.md#como-ciclone-e-vento-são-associados) |
| 9 | Que análise foi executada? | Uma análise exploratória, E-001 sobre orientação e E-002 sobre weighting por estado versus por ciclone, ambos com bootstrap por ciclone. | [Análise exploratória](../exploratory_analysis.md), [E-001](../e001_orientation.md) e [E-002](../e002_weighting.md) |
| 10 | Por que ela foi executada? | Para compreender cobertura, seleção e sinais descritivos antes de ajustar qualquer modelo. | [Análise exploratória](../exploratory_analysis.md#motivação) |
| 11 | O que foi encontrado? | E-001 mostrou núcleo A50 menor após rotação, mas A75, A90 e RMS maiores; E-002 mostrou que o conflito permanece sob peso igual por ciclone. | [Resultados e evidências](../results.md) |
| 12 | O que não pode ser concluído? | Causalidade, diferenças populacionais entre fases, probabilidades espaciais, footprint probabilístico, generalização climatológica e hazard. | [Resultados e evidências](../results.md) e [Limitações](../limitations.md) |
| 13 | Quais decisões metodológicas foram tomadas? | Ciclone como unidade, Zenodo como fonte, nenhuma orientação superior e weighting escolhido pelo estimando declarado. | [Decisões](../decisions.md) |
| 14 | Quais perguntas permanecem abertas? | Threshold, escolha da orientação, lifecycle além da intensidade, generalização por ciclone e arquitetura probabilística. | [Questões abertas](../open_questions.md#prioridades-atuais) |
| 15 | Qual é a consequência dos experimentos? | E-001 permanece inconclusivo, E-002 demonstra robustez ao weighting e o próximo teste isolará o threshold. | [E-002](../e002_weighting.md#consequência-para-o-projeto) |
| 16 | Como reproduzir tecnicamente? | A página de proveniência vincula versões, hashes, dados, tabelas, figuras, código e comandos; a referência interna explica os fluxos. | [Reprodutibilidade](../reproducibility.md) e [Fluxos computacionais](computational_workflows.md) |
| 17 | Qual é o próximo teste e por que ainda não começou? | Sensibilidade ao threshold é o próximo experimento proposto; q90, q95, q99 e limiares físicos são candidatos, mas protocolo e critério ainda não foram fixados. | [Plano científico](../scientific_plan.md#5-sensibilidade-ao-threshold--próximo-e-proposto) |

## Veredito

As 17 perguntas são respondidas sem exigir leitura do código-fonte para compreender a ciência. O código permanece acessível somente quando o avaliador decide reproduzir ou auditar a implementação. As lacunas científicas e de proveniência não foram preenchidas artificialmente; estão identificadas como limitações ou questões abertas.
