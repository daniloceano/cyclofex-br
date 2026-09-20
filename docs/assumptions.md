# Pressupostos

Nenhum pressuposto científico foi adotado para produzir uma inferência nesta etapa. Em particular, a precisão dos centros, a adequação do `q90` e a independência entre linhas **não** foram assumidas como fatos.

A associação ao ERA5 de 6 h, o domínio, a grade, a distância haversine e o raio de 1.100 km não são pressupostos novos: são regras operacionais recuperadas e validadas contra os 20.101 estados do Parquet atual. Os estados sem interseção são marcados como não avaliados, sem assumir que representem não-excedências. A execução original do CycloPhaser continua sendo uma lacuna de proveniência em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases), não um pressuposto convertido em fato.

Quando um pressuposto passar a sustentar uma análise, registre um ID persistente (`A-001`, `A-002`, ...), sua necessidade, onde afeta o trabalho, evidência, forma de teste e status (`UNTESTED`, `SUPPORTED`, `CHALLENGED` ou `REJECTED`). Referencie esse ID na metodologia e nos experimentos pertinentes.
