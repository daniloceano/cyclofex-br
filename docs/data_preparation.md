# Preparação dos dados

## Problema de construção da amostra

As tracks operacionais descrevem o centro do ciclone a cada hora, enquanto os campos ERA5 usados pelo produto atual estão espaçados em 6 h. Além disso, o arquivo de vento armazena apenas pontos que passaram por um filtro de intensidade. Usá-lo sozinho como catálogo eliminaria estados inteiros e confundiria ausência de excedência com ausência de observação.

A preparação, portanto, precisa construir primeiro um denominador temporal e espacial independente do recorte condicionado de vento.

## Solução adotada

O catálogo horário do Zenodo é preservado como fonte dos centros e das fases. A partir dele, cada track é associada à grade temporal ERA5 de 6 h. Para cada estado resultante, o suporte espacial é calculado geometricamente, mesmo quando nenhuma linha de vento foi armazenada. Essa separação permite perguntar se um estado existia, se podia ser observado no domínio e se produziu alguma linha selecionada.

## Regra temporal

Para cada hora de track:

1. localiza-se o campo ERA5 de 6 h mais próximo;
2. exige-se diferença absoluta máxima de 3 h;
3. em empate exato de 3 h, escolhe-se o campo anterior;
4. se duas horas da mesma track forem associadas ao mesmo campo, conserva-se a de menor diferença e, em novo empate, a anterior;
5. mantém-se uma única linha por `track_id + time`.

O horário original, o horário ERA5 escolhido e sua diferença permanecem registrados. Assim, a associação é auditável e não implica interpolação da posição do centro.

## Regra espacial

Para cada estado ciclone–tempo, contam-se as células da grade regular de 0,25° no domínio 65°S–10°S e 85°W–15°W cuja distância ao centro é menor ou igual a 1.100 km. A distância é calculada sobre uma esfera com raio de 6.371 km.

O resultado recebe um de três estados de suporte: completo, parcial ou sem suporte. Suporte parcial é uma observação espacial truncada, não uma observação ausente; sem suporte significa que nenhuma posição do domínio pôde ser avaliada.

## Relação com o recorte condicionado de vento

O arquivo de vento inclui uma célula quando ela está no raio de 1.100 km e satisfaz `wind_speed > min(15,6 m/s; q90_local)`. As seis flags de excedência são calculadas depois dessa seleção.

Consequentemente:

- uma célula elegível ausente num estado com suporte não passou pelo filtro e pode ser tratada como não-excedência para as flags atuais;
- um estado com suporte e zero linhas selecionadas contém zeros reconstruíveis, não uma observação perdida;
- um estado sem suporte não possui denominador espacial e não pode receber zero;
- uma posição fora do domínio não foi observada, ainda que esteja a menos de 1.100 km do centro.

## Resultado da preparação

| Etapa | Resultado |
| --- | --- |
| Catálogo horário | 631.009 estados horários de 6.789 tracks; chave `track_id + date` única e sem lacunas horárias internas |
| Associação de 6 h | 109.857 estados de 6.789 tracks; nenhuma duplicata de `track_id + time` |
| Período comparável ao vento | 29.311 estados de 1.785 tracks |
| Presentes no recorte condicionado | 20.101 estados |
| Ausentes com suporte | 3.233 estados |
| Ausentes sem suporte | 5.977 estados |

As diferenças temporais observadas entre a hora original e o campo ERA5 foram: 105.332 associações exatas, 1.044 com −1 h, 906 com −2 h, 870 com +1 h, 849 com +2 h e 856 com +3 h.

## Validação

A reconstrução foi comparada ao recorte de vento já existente. Todos os 20.101 centros coincidiram após a conversão para a precisão `float32` usada no arquivo, todos os 20.101 rótulos de fase corresponderam e nenhum estado inesperado foi encontrado. Também foram verificados checksum da fonte, schema, contagens, ordem horária, unicidade das chaves, categorias de fase e casos especiais com e sem suporte.

Essa validação sustenta a adoção do Zenodo como fonte operacional. Ela **não** valida a escolha científica do raio de 1.100 km, do threshold ou do método original de classificação das fases.

## Consequência científica

A amostra agora distingue explicitamente presença de um estado, possibilidade de observação espacial e ocorrência de excedência. Essa distinção impede que eventos omitidos pelo filtro sejam perdidos e evita transformar áreas não observadas em não-excedências. Ela fornece a infraestrutura necessária para os experimentos futuros, sem decidir ainda qual evento espacial ou modelo será adotado.

## Reprodutibilidade

Versões, hashes, arquivos e comandos estão em [proveniência e reprodutibilidade](reproducibility.md). A descrição de campos e contratos computacionais está na [referência técnica dos dados](internal/data_reference.md).
