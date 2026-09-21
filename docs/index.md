# Visão geral do projeto

## O problema científico

O **cyclofex-br** investiga como ventos extremos associados a ciclones extratropicais se organizam no Atlântico Sul. O centro de um ciclone descreve sua trajetória, mas não informa sozinho onde os ventos mais intensos ocorrem, quanto espaço ocupam ou como essa organização muda durante o ciclo de vida. Essa lacuna precisa ser resolvida antes que padrões relativos ao ciclone possam ser traduzidos, no futuro, em *hazard* geográfico — a frequência e a intensidade esperadas do fenômeno em posições fixas da superfície.

## Ideia central e objeto estudado

A ideia de trabalho é representar cada campo de vento em coordenadas relativas ao centro e, quando pertinente, ao movimento do ciclone. Essa representação *storm-relative* descreve uma posição por sua distância e direção em relação à tempestade, em vez de usar apenas latitude e longitude. Ela poderá permitir que ocorrência, geometria e magnitude das excedências sejam estudadas separadamente antes de qualquer combinação probabilística.

Essa ideia orienta o projeto, mas **não foi confirmada como representação superior**. E-001 mostrou que alinhar pelo movimento concentra o núcleo das excedências q95, porém dispersa suas regiões intermediária e externa. O objeto observado nesta etapa são ciclones extratropicais, seus estados ao longo do tempo e os ventos ERA5 a 10 m situados até 1.100 km de seus centros, dentro do domínio atualmente disponível.

## Estratégia científica

O trabalho segue uma sequência deliberada:

1. estabelecer a proveniência das trajetórias e das fases do ciclo de vida;
2. construir a amostra de estados ciclone–tempo compatíveis com os campos ERA5 de 6 h;
3. caracterizar o recorte de vento e suas regras de seleção;
4. explorar, de forma descritiva, diferenças entre fases e setores relativos ao ciclone;
5. definir operacionalmente extremo, evento e *footprint* antes de testar modelos;
6. somente depois, avaliar ocorrência, geometria, magnitude, robustez e tradução para coordenadas geográficas.

Consulte o [plano científico](scientific_plan.md) para distinguir o que foi proposto, testado, adotado e ainda não testado.

## Estado científico em 21 de setembro de 2026

| Elemento | Estado | Evidência disponível |
| --- | --- | --- |
| Fonte de tracks e lifecycle | **ADOTADO** | O Zenodo 18133432 reproduz todos os 20.101 estados presentes no recorte de vento e recupera os estados omitidos por sua seleção. |
| Catálogo horário | **VALIDADO** | 631.009 horas de 6.789 tracks, de 1979-01-01 a 2021-01-07 UTC. |
| Associação à grade temporal de 6 h | **VALIDADA** | 109.857 estados ciclone–tempo; regra do campo mais próximo com tolerância máxima de 3 h. |
| Recorte de vento disponível | **CARACTERIZADO** | 1.781 ciclones, 20.101 estados e 17.182.983 linhas espaciais entre 2010 e 2020. |
| Análise exploratória | **CONCLUÍDA** | Tracks, distribuições pontuais de vento, ocorrência de excedências, quadrantes e um caso individual foram descritos. |
| E-001 — orientação espacial | **INCONCLUSIVO** | Primeiro experimento formal: 1.784 ciclones, comparação pareada e bootstrap por ciclone; métricas de concentração discordaram. |
| Modelo probabilístico e hazard | **AINDA NÃO TESTADOS** | Não há *coverage probability*, *footprint* probabilístico ou estimativa de hazard. |

## O que a análise existente encontrou

No recorte condicionado de 2010–2020, a fase madura apresentou a maior mediana pontual de velocidade do vento (15,58 m/s) e o maior percentil 95 pontual (19,77 m/s). As medianas entre quadrantes foram próximas: 14,47–14,90 m/s nos quadrantes geográficos e 14,51–14,78 m/s nos quadrantes relativos ao movimento.

Esses são **resultados descritivos do recorte armazenado**. Eles são consistentes com ventos pontualmente mais intensos na fase madura, mas não constituem um teste entre fases, não corrigem a contribuição desigual dos ciclones e não demonstram causalidade, probabilidade espacial ou hazard. A interpretação completa está na [análise exploratória](exploratory_analysis.md) e a síntese, em [resultados e evidências](results.md).

O primeiro experimento formal encontrou um resultado diferente e mais específico: a representação *motion-relative* reduziu a área A50 em 32.500 km², mas aumentou A75 em 45.000 km², A90 em 97.500 km² e RMS em 7,69 km. A diferença de entropia foi pequena e incerta. A rotação revelou assimetria, mas não maior organização espacial global. O relatório completo está em [E-001](e001_orientation.md).

## Consequência científica atual

E-001 foi encerrado como **INCONCLUSIVE**. Nenhuma representação foi adotada como cientificamente superior: *centered* permanece uma referência simples e *motion-relative*, um diagnóstico de assimetria. Definição final de extremo, weighting por ciclone, normalização por tamanho e modelagem probabilística continuam abertas e não foram incorporadas retrospectivamente ao experimento.

## Como navegar

- **Entender a base empírica:** [Dados](data.md) → [Preparação dos dados](data_preparation.md).
- **Ler o que já foi analisado:** [Análise exploratória](exploratory_analysis.md) → [E-001](e001_orientation.md) → [Resultados e evidências](results.md).
- **Distinguir execução de proposta:** [Metodologia atual](methodology.md) → [Plano científico](scientific_plan.md) → [Experimentos](experiments.md).
- **Auditar incertezas e escolhas:** [Limitações](limitations.md) → [Questões abertas](open_questions.md) → [Decisões](decisions.md).
- **Reproduzir tecnicamente:** [Proveniência e reprodutibilidade](reproducibility.md) → [Referência técnica](internal/README.md).
