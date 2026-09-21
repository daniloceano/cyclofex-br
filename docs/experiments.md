# Experimentos

## Função do registro

Esta página é o índice do caderno científico estruturado. Um experimento é um teste com pergunta, hipótese, dados, método, métricas e critério de decisão definidos antes da interpretação. Status permitidos: **PLANNED**, **RUNNING**, **ADOPTED**, **REJECTED**, **INCONCLUSIVE** e **SUPERSEDED**. Resultados negativos e inconclusivos permanecem no histórico.

## Estado atual

E-001 foi concluído e recebeu status **INCONCLUSIVE**. Foi o primeiro experimento formal do projeto. Nenhum modelo probabilístico, *coverage probability*, magnitude condicional ou hazard geográfico foi ajustado.

## E-001 — Efeito da orientação pelo movimento na organização espacial das excedências

- **Status:** `INCONCLUSIVE`
- **Datas:** planejamento, execução e encerramento em 21 de setembro de 2026
- **Hipótese:** H2 — *motion-relative* reduz a dispersão espacial em relação a *centered*.
- **Threshold principal:** q95 local, fixado antes dos resultados.
- **Unidade inferencial:** ciclone (`track_id`), com bootstrap pareado por ciclone.
- **Decisão associada:** [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001).

O teste usou 1.784 ciclones e 23.050 estados com suporte e heading confiável. A orientação pelo movimento reduziu A50 em 32.500 km², mas aumentou A75 em 45.000 km², A90 em 97.500 km² e a dispersão RMS em 7,69 km. A diferença de entropia foi −0,0023 nat, com intervalo bootstrap de 95% entre −0,0105 e +0,0057. Apenas uma das quatro fases apresentou entropia e A75 pontualmente menores ao mesmo tempo.

Como as famílias de métricas e as fases não concordaram, a hipótese não atingiu o critério preregistrado. O relatório científico completo — contexto, equações, dados, mapas, métricas, incerteza, interpretação, limitações, conclusão e reprodutibilidade — está em [E-001 — Orientação pelo movimento do ciclone](e001_orientation.md).

---

## Template obrigatório para novos experimentos

Copie a estrutura abaixo e substitua todas as instruções. Se uma seção não se aplicar, explique por quê; não a remova silenciosamente.

### E-XXX — Título científico

- **Status:** `PLANNED | RUNNING | ADOPTED | REJECTED | INCONCLUSIVE | SUPERSEDED`
- **Datas:** planejamento, início, encerramento
- **Questões e decisões relacionadas:** IDs persistentes

#### Contexto

Apresente o problema maior e defina os termos necessários para que a entrada seja compreendida isoladamente.

#### Pergunta

Formule uma pergunta específica que o experimento possa responder.

#### Hipótese

Declare o padrão esperado e o que ele significaria.

#### Hipótese alternativa ou explicações concorrentes

Registre mecanismos ou artefatos que também poderiam produzir o resultado.

#### Motivação

Explique por que o teste é necessário antes do próximo passo.

#### Dados

Identifique população, amostra, período, versão, unidade de análise e critérios de inclusão e exclusão.

#### Representação e variáveis

Defina todas as variáveis, unidades, domínios, transformações e tratamento de ausências.

#### Método

Explique o procedimento conceitualmente e com precisão suficiente para reprodução. Toda equação deve ter propósito, símbolos, unidades, domínio e interpretação intuitiva.

#### Métricas

Indique o que cada métrica mede e por que responde à pergunta.

#### Critério de decisão

Registre, antes do resultado, o que contará como evidência favorável, contrária ou inconclusiva.

#### Resultado

Apresente observações, números, tabelas e figuras sem antecipar a interpretação.

#### Interpretação

Explique o significado científico dentro do alcance do desenho.

#### Robustez e diagnósticos

Registre verificações, sensibilidades, falhas e resultados negativos.

#### Limitações

Declare o que o experimento não demonstra.

#### Conclusão

Responda diretamente à pergunta.

#### Consequência para o projeto

Indique a decisão permitida e o próximo passo.

#### Reprodutibilidade

Vincule configuração congelada, versão e hash dos dados, código, ambiente, produtos e decisão associada.
