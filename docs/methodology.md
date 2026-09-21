# Metodologia atual

## Escopo

Esta página descreve somente métodos efetivamente usados e decisões vigentes. Não existe metodologia adotada para estimar *footprints* probabilísticos ou hazard. [E-001](e001_orientation.md) comparou duas orientações e foi inconclusivo; [E-002](e002_weighting.md) mostrou que essa conclusão é robusta a weighting por estado versus por ciclone. Nenhuma orientação foi promovida a representação principal.

## Unidade de análise

O **ciclone**, identificado por `track_id`, é a unidade científica fundamental quando a pergunta compara eventos. Um estado ciclone–tempo representa esse ciclone em um horário ERA5 de 6 h. Uma linha do recorte de vento representa apenas um ponto de grade pertencente a um estado; linhas do mesmo ciclone não são tratadas como observações independentes.

Essa decisão evita pseudorreplicação: um ciclone duradouro ou com área maior pode gerar mais estados e pontos sem se tornar vários ciclones independentes. Uma análise que use outra unidade deverá justificá-la explicitamente e preservar o agrupamento por evento.

## Construção da amostra

Os centros e as fases são obtidos do catálogo operacional do Zenodo 18133432. O catálogo horário é associado aos campos ERA5 de 6 h pelo vizinho temporal mais próximo, com tolerância máxima de 3 h. Empates usam o horário anterior; duplicidades dentro da mesma track são resolvidas pela menor diferença temporal e, depois, pela hora anterior.

Para cada estado, o suporte espacial é definido pelas células de 0,25° no domínio 65°S–10°S e 85°W–15°W situadas a até 1.100 km do centro. Estados são classificados como suporte completo, parcial ou ausente. A descrição integral, os resultados de validação e as consequências estão em [preparação dos dados](data_preparation.md).

## Representação espacial em uso descritivo

Dois sistemas de quadrantes foram usados na análise exploratória:

- **Geográfico:** noroeste, nordeste, sudeste e sudoeste em relação ao centro.
- **Relativo ao movimento:** frente–esquerda, frente–direita, trás–direita e trás–esquerda, após orientar os setores pela direção de deslocamento da track.

Na análise exploratória, a direção relativa ao movimento reproduziu a regra herdada, inclusive o fallback leste. Em E-001, a direção foi recalculada do catálogo completo: diferenças centradas no plano tangente local, diferenças simples nas pontas e exclusão de velocidades abaixo de 5 km/h. Foram excluídos 284 de 23.334 estados com suporte; nenhum heading físico foi inventado para movimento quase nulo.

E-001 usou coordenadas azimutais equidistantes em km, rotação contínua para frente/direita e bins comuns de 50 km. A distribuição q95 atribuiu massa total um a cada estado q95-positivo. O bootstrap reamostrou `track_id`, preservando todos os estados e células de cada ciclone. A comparação encontrou métricas conflitantes e não autorizou escolher *centered* ou *motion-relative* como representação superior.

E-002 reutilizou literalmente essa população e geometria e alterou apenas o weighting. *Equal-state* atribui massa total um a cada estado q95-positivo e estima a distribuição da população de estados. *Equal-cyclone* divide massa total um entre os estados positivos de cada ciclone e estima a distribuição média da população de ciclones q95-positivos. Conforme [D-006](decisions.md#d-006--usar-o-weighting-que-corresponde-ao-estimando-declarado), o estimando-alvo deve ser declarado; nenhum dos dois substitui universalmente o outro.

## Definição observacional do vento

`wind_speed` é a magnitude do vento ERA5 a 10 m, em m/s. O recorte disponível armazena pontos dentro de 1.100 km que satisfazem `wind_speed > min(15,6 m/s; q90_local)`. Flags indicam excedência estrita de 15,6, 20 e 25 m/s e de q90, q95 e q99 locais.

Esses thresholds descrevem o produto atual, não uma definição científica definitiva de extremo. A versão futura deve ser decidida por experimento e não inferida do nome do arquivo.

## Agrupamento de fases

Rótulos com sufixo `2` podem ser agrupados à fase principal de mesmo nome quando isso estiver preregistrado e a pergunta comparar o tipo físico da fase. O sufixo representa uma ocorrência posterior não contígua, e não outra classe física. E-001 aplicou esse agrupamento porque `mature 2` isolada tinha apenas 35 estados q95-positivos e publicou também as métricas literais. Dados canônicos mantêm os rótulos originais; fase residual e ausência não são combinadas com outras categorias. A regra está formalizada em [D-003](decisions.md#d-003--agrupar-rótulos-phase-2-nas-figuras-exploratórias).

## Procedimento da análise exploratória

A análise já executada:

1. mapeou os centros distintos de todas as tracks presentes no recorte;
2. descreveu quantis pontuais de vento por fase e quadrante;
3. contou, por fase, estados com pelo menos uma excedência de cada threshold;
4. comparou contagens q90 e proporções q95 entre fases e setores;
5. selecionou de forma determinística o ciclone que contém o maior vento do arquivo para um exemplo espaço-temporal.

As estatísticas pontuais são rotuladas como tais. Contagens por estado reduzem, mas não eliminam, a dependência dentro de ciclones. Não foram ajustados modelos nem calculados intervalos inferenciais.

## Distinções conceituais obrigatórias

- **Evento:** ocorrência física ou unidade científica individual; não é uma climatologia agregada.
- **Excursion set:** conjunto de posições onde um campo excede um threshold em um evento ou estado definido.
- **Ocorrência ou coverage probability:** probabilidade condicional de uma posição pertencer a um *excursion set*; ainda não estimada.
- **Magnitude condicional:** intensidade do vento quando uma excedência ocorre; responde a outra pergunta.
- **Footprint:** representação espacial cuja definição operacional ainda será fixada; o termo não deve ser usado como sinônimo automático de pontos selecionados.
- **Hazard geográfico:** frequência e intensidade esperadas em coordenadas fixas; exige frequência de eventos, trajetórias, duração, ocorrência e magnitude.
- **Não-excedência:** posição observável que não superou o limiar; não equivale a posição sem suporte ou não observada.

## O que esta metodologia permite concluir

Ela permite reproduzir a amostra de estados, distinguir suporte de ausência, descrever o recorte condicionado, concluir que a orientação pelo movimento não melhorou consistentemente a concentração q95 em E-001 e que essa conclusão é robusta ao weighting testado em E-002. Não permite atribuir causalidade às fases, tratar pixels como réplicas, generalizar para climatologia completa, escolher definitivamente uma orientação, escolher um modelo probabilístico ou estimar hazard.

## Auditoria técnica

Hashes, versões, comandos e produtos ficam em [proveniência e reprodutibilidade](reproducibility.md). Contratos de campos e detalhes de implementação ficam na [documentação técnica](internal/README.md), para não interromper a narrativa científica.
