# Experimentos

## Função do registro

Esta página é o índice do caderno científico estruturado. Um experimento é um teste com pergunta, hipótese, dados, método, métricas e critério de decisão definidos antes da interpretação. Status permitidos: **PLANNED**, **RUNNING**, **ADOPTED**, **REJECTED**, **INCONCLUSIVE** e **SUPERSEDED**. Resultados negativos e inconclusivos permanecem no histórico.

## Estado atual

E-001 permanece **INCONCLUSIVE** sob seu protocolo original. E-002 foi concluído com status **ADOPTED** para a hipótese de robustez: a conclusão de E-001 foi **ROBUSTA AO WEIGHTING**, embora o weighting tenha alterado quantitativamente a distribuição. Nenhum modelo probabilístico, *coverage probability*, magnitude condicional ou hazard geográfico foi ajustado.

## E-001 — Efeito da orientação pelo movimento na organização espacial das excedências

- **Status:** `INCONCLUSIVE`
- **Datas:** planejamento, execução e encerramento em 21 de setembro de 2026
- **Hipótese:** H2 — quadrantes rotacionados pelo movimento (`motion-relative`) reduzem a dispersão espacial em relação aos quadrantes fixos (`centered`).
- **Threshold principal:** q95 local, fixado antes dos resultados.
- **Unidade inferencial:** ciclone (`track_id`), com bootstrap pareado por ciclone.
- **Decisão associada:** [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001).

O teste usou 1.784 ciclones e 23.050 estados com suporte e heading confiável. A orientação pelo movimento reduziu A50 em 32.500 km², mas aumentou A75 em 45.000 km², A90 em 97.500 km² e a dispersão RMS em 7,69 km. A diferença de entropia foi −0,0023 nat, com intervalo bootstrap de 95% entre −0,0105 e +0,0057. Apenas uma das quatro fases apresentou entropia e A75 pontualmente menores ao mesmo tempo.

Como as famílias de métricas e as fases não concordaram, a hipótese não atingiu o critério preregistrado. O relatório científico completo — contexto, equações, dados, mapas, métricas, incerteza, interpretação, limitações, conclusão e reprodutibilidade — está em [E-001 — Orientação pelo movimento do ciclone](e001_orientation.md).

---

## E-002 — Sensibilidade da estrutura espacial ao weighting por estado versus por ciclone

- **Status:** `ADOPTED` — robustez ao weighting sustentada pelo critério registrado.
- **Datas:** planejamento, execução e encerramento em 21 de setembro de 2026.
- **Pergunta:** a estrutura q95 e a conclusão de E-001 mudam quando cada ciclone q95-positivo recebe a mesma massa total, em vez de cada estado q95-positivo?
- **Hipótese:** a distribuição pode ser sensível à participação adicional de ciclones com mais estados, mas o conflito núcleo–cauda de E-001 deve permanecer se for uma propriedade geral dos ciclones.
- **Protocolo:** alterar somente o weighting; preservar população, q95, suporte, heading de 5 km/h, coordenadas, domínio, bins, fases e ausência de smoothing de E-001; construir quatro distribuições; comparar H, A50, A75, A90, RMS e TV; reamostrar `track_id` 500 vezes.
- **Conclusão:** `ROBUST_TO_WEIGHTING`. Sob *equal-cyclone*, a diferença quadrantes rotacionados menos fixos (`motion_relative − centered`) foi −22.500 km² em A50, +27.500 km² em A75, +77.500 km² em A90 e +8,21 km em RMS; o conflito de E-001 permaneceu.
- **Decisão associada:** [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado); [D-005](decisions.md#d-005--manter-aberta-a-escolha-entre-centered-e-motion-relative-após-e-001) permanece vigente.

O experimento reproduziu exatamente 1.784 ciclones, 23.050 estados, 16.921 estados q95-positivos, 9.090.570 células excedentes e 284 exclusões por heading. Os 10% de ciclones positivos com mais estados receberam 22,52% da massa *equal-state*; o número efetivo foi 1.288,8 sob *equal-state* e 1.757 sob *equal-cyclone*. O weighting redistribuiu 7,92% da massa *centered* e 7,86% da massa *motion-relative*, mas não tornou uma orientação consistentemente superior.

O relatório autossuficiente está em [E-002 — Weighting por estado versus por ciclone](e002_weighting.md).

---

## Agenda científica futura

Os itens abaixo são **PROPOSTOS** ou **AINDA NÃO TESTADOS**. Eles registram a ordem pretendida, não protocolos completos nem decisões irrevogáveis.

### Próximo — sensibilidade ao threshold

- **Estado:** `PROPOSED`.
- **Objetivo:** verificar se estrutura espacial e conclusões de orientação e weighting persistem quando a definição de extremo muda.
- **Candidatos:** q90, q95, q99 e thresholds físicos disponíveis.
- **Ainda não definido:** protocolo comparativo, critério de decisão e threshold científico final.

### Depois — lifecycle versus intensidade

- **Estado:** `PROPOSED`.
- **Objetivo:** testar se a fase do ciclo de vida contém informação espacial ou preditiva além da intensidade do ciclone.
- **Pergunta central:** diferenças atribuídas ao lifecycle permanecem depois de controlar intensidade?
- **Ainda não executado:** nenhum efeito independente de lifecycle foi demonstrado.

### Depois — estabilidade e generalização por ciclone

- **Estado:** `PROPOSED`.
- **Objetivo:** avaliar se os padrões dependem de poucos ciclones e se generalizam a eventos não usados na construção.
- **Candidatos:** bootstrap por ciclone mais abrangente, análise de influência e remoção de ciclones, *leave-one-cyclone-out* ou validação por grupos e estabilidade de superfícies e métricas.
- **Distinção:** os bootstraps internos de E-001 e E-002 medem incerteza local de seus contrastes; não substituem esta futura etapa de robustez.

### Depois — modelo probabilístico completo de ocorrência

- **Estado:** `NOT_YET_TESTED`.
- **Objetivo provisório:** construir e validar um modelo de ocorrência somente depois das decisões anteriores.
- **Arquitetura candidata, não adotada:** posição *storm-relative*, lifecycle, intensidade, velocidade de translação, tamanho e heterogeneidade entre ciclones, conforme dados e evidência permitirem.
- **Validação exigida:** comparação com benchmarks simples e avaliação em ciclones não usados no ajuste.
- **Não assumido:** família estatística, GAM/GAMM, efeito obrigatório do lifecycle ou inclusão obrigatória de todas as covariáveis.

Magnitude condicional e hazard geográfico permanecem etapas separadas e posteriores ao modelo de ocorrência.

---

## Template obrigatório para novos experimentos

Copie a estrutura abaixo e substitua todas as instruções. Se uma seção não se aplicar, explique por quê; não a remova silenciosamente.

Duas exigências permanentes valem para todo experimento formal, conforme [como explicar metodologia](documentation_guidelines.md#como-explicar-metodologia):

1. **O método é descrito na ordem cognitiva** — intuição, depois procedimento, depois formalização, depois exemplo concreto. A seção de método é dividida nas subseções abaixo; não é um bloco único de equações.
2. **Todo `E-XXX` possui um fluxograma científico-metodológico**, salvo justificativa explícita registrada na página. O fluxograma representa o protocolo real, usa linguagem científica em vez de nomes de scripts, aparece antes da descrição matemática detalhada, é acompanhado da leitura textual etapa por etapa, é atualizado se o protocolo mudar antes da execução e permanece congelado depois da conclusão, exceto por correções editoriais.

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

#### Método — visão geral e fluxograma

Apresente o fluxograma metodológico e, logo abaixo, uma seção **“Como ler o fluxo do experimento”** que explique cada etapa em uma ou duas frases. O leitor deve ver o mapa inteiro antes de percorrer qualquer detalhe matemático. Declare aqui qual é o objeto de entrada do experimento e qual é o produto final do método.

#### Método — passo a passo

Descreva uma transformação por vez, na ordem real de execução. Cada passo declara o que entra, o que se quer obter, por que a operação é necessária, como é calculada em linguagem verbal, o que sai e qual passo consome essa saída. Não agrupe várias transformações conceituais no mesmo parágrafo.

Quando o método atravessar níveis — ciclone, estado ciclone–tempo, célula e bin —, diga explicitamente em qual nível cada operação acontece, qual nível recebe peso, qual é agregado e qual é a unidade inferencial.

#### Método — formalização

Introduza as equações progressivamente, já depois da explicação verbal do passo correspondente. Defina todo símbolo antes ou imediatamente ao aparecer, com unidade, natureza e domínio. Siga cada equação relevante de uma leitura em linguagem comum. Reserve a fórmula compacta para o papel de síntese, nunca de primeiro contato.

#### Método — exemplo concreto

Obrigatório sempre que houver weighting, normalização, agregação, probabilidades, bins, transformação de coordenadas, bootstrap, seleção, thresholds ou combinação hierárquica. Use números simples, mostre a aritmética, verifique a normalização e, quando existirem variantes do método, repita o mesmo exemplo sob cada variante. Esquemas espaciais pequenos contam como exemplo concreto quando o método envolver posição.

#### Métricas

Para cada métrica, documente nesta ordem: a pergunta que ela responde; a intuição; o cálculo, verbal antes de formal; os símbolos com unidade e domínio; um exemplo simples quando ajudar; a interpretação de valores altos e baixos e do sinal da diferença; e **o que a métrica não mede**. O último item é obrigatório.

#### Incerteza

Explique a unidade de reamostragem de forma didática, mostre uma réplica concreta, justifique por que essa unidade foi escolhida em vez de uma unidade mais fina e declare o que o intervalo não cobre.

#### Síntese metodológica

Feche o método com três a seis frases **sem equações**, sob o título “Em resumo: o que este método faz?”. A síntese consolida o raciocínio; não introduz método novo nem antecipa resultado.

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
