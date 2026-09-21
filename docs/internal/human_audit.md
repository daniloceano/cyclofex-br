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
| 9 | Que análise foi executada? | Uma análise exploratória e E-001, comparação formal entre coordenadas centered e motion-relative com bootstrap por ciclone. | [Análise exploratória](../exploratory_analysis.md) e [E-001](../e001_orientation.md) |
| 10 | Por que ela foi executada? | Para compreender cobertura, seleção e sinais descritivos antes de ajustar qualquer modelo. | [Análise exploratória](../exploratory_analysis.md#motivação) |
| 11 | O que foi encontrado? | Além dos padrões exploratórios, E-001 mostrou núcleo A50 menor após rotação, mas A75, A90 e RMS maiores; a orientação não melhorou consistentemente a concentração. | [Resultados e evidências](../results.md) |
| 12 | O que não pode ser concluído? | Causalidade, diferenças populacionais entre fases, probabilidades espaciais, footprint probabilístico, generalização climatológica e hazard. | [Resultados e evidências](../results.md) e [Limitações](../limitations.md) |
| 13 | Quais decisões metodológicas foram tomadas? | Ciclone como unidade, Zenodo como fonte operacional e, após E-001 inconclusivo, nenhuma orientação adotada como superior. | [Decisões](../decisions.md) |
| 14 | Quais perguntas permanecem abertas? | Reprodução integral do lifecycle, definição de extremo e objeto espacial e escolha da orientação principal. | [Questões abertas](../open_questions.md#prioridades-atuais) |
| 15 | Qual é a consequência do primeiro teste? | E-001 foi encerrado como inconclusivo; não se avança por ajuste retrospectivo e qualquer novo teste deve isolar um fator por vez. | [E-001](../e001_orientation.md#consequência-para-o-projeto) |
| 16 | Como reproduzir tecnicamente? | A página de proveniência vincula versões, hashes, dados, tabelas, figuras, código e comandos; a referência interna explica os fluxos. | [Reprodutibilidade](../reproducibility.md) e [Fluxos computacionais](computational_workflows.md) |

## Veredito

As 16 perguntas são respondidas sem exigir leitura do código-fonte para compreender a ciência. O código permanece acessível somente quando o avaliador decide reproduzir ou auditar a implementação. As lacunas científicas e de proveniência não foram preenchidas artificialmente; estão identificadas como limitações ou questões abertas.
