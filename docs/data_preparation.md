# Preparação dos dados

## Problema de construção da amostra

As tracks operacionais descrevem o centro do ciclone a cada hora, enquanto os campos ERA5 usados pelo produto atual estão espaçados em 6 h. Além disso, o arquivo de vento armazena apenas pontos que passaram por um filtro de intensidade. Usá-lo sozinho como catálogo eliminaria estados inteiros e confundiria ausência de excedência com ausência de observação.

A preparação, portanto, precisa construir primeiro um denominador temporal e espacial independente do recorte condicionado de vento.

## Solução adotada

O catálogo horário do Zenodo é preservado como fonte dos centros e das fases. A partir dele, cada track é associada à grade temporal ERA5 de 6 h. Para cada estado resultante, o suporte espacial é calculado geometricamente, mesmo quando nenhuma linha de vento foi armazenada. Essa separação permite perguntar se um estado existia, se podia ser observado no domínio e se produziu alguma linha selecionada.

## Regra temporal

<ul class="method-io">
<li>catálogo horário de centros de ciclone, uma linha por <code>track_id</code> e hora</li>
<li>associação ao campo ERA5 de 6 h mais próximo, com tolerância e regra de desempate</li>
<li>estados ciclone–tempo, uma linha por <code>track_id + time</code> de 6 h</li>
</ul>

Para cada hora de track:

1. localiza-se o campo ERA5 de 6 h mais próximo;
2. exige-se diferença absoluta máxima de 3 h;
3. em empate exato de 3 h, escolhe-se o campo anterior;
4. se duas horas da mesma track forem associadas ao mesmo campo, conserva-se a de menor diferença e, em novo empate, a anterior;
5. mantém-se uma única linha por `track_id + time`.

O horário original, o horário ERA5 escolhido e sua diferença permanecem registrados. Assim, a associação é auditável e não implica interpolação da posição do centro.

A diferença registrada é sempre **hora original da track menos hora do campo ERA5**, no campo `track_minus_era5_hours`. Um valor negativo significa que o centro foi observado **antes** do campo associado; um valor positivo, depois. Por causa da regra 3, a diferença `−3 h` não existe: todo empate de três horas é resolvido para o campo anterior e aparece como `+3 h`.

<div class="method-box example">

Um centro registrado às `13:00 UTC` está a 1 h do campo das `12:00` e a 5 h do campo das `18:00`. Ele é associado ao campo das `12:00`, com diferença `+1 h`. Um centro das `16:00` está a 4 h das `12:00` e a 2 h das `18:00`: vai para as `18:00`, com diferença `−2 h`. Um centro das `15:00` está a exatamente 3 h dos dois campos; o desempate leva ao campo anterior, das `12:00`, com diferença `+3 h`.

Se as horas `13:00` e `14:00` da mesma track caírem no campo das `12:00`, apenas a de menor diferença absoluta — `13:00` — sobrevive, para que o estado ciclone–tempo continue único.

</div>

## Regra espacial

<ul class="method-io">
<li>centro do ciclone de um estado e a grade regular de 0,25° do domínio</li>
<li>contagem geométrica das células do domínio situadas até 1.100 km do centro</li>
<li>número de células observáveis e classe de suporte: completo, parcial ou ausente</li>
</ul>

Para cada estado ciclone–tempo, contam-se as células da grade regular de 0,25° no domínio 65°S–10°S e 85°W–15°W cuja distância ao centro é menor ou igual a 1.100 km. A distância é calculada sobre uma esfera com raio de 6.371 km.

O resultado recebe um de três estados de suporte: completo, parcial ou sem suporte. Suporte parcial é uma observação espacial truncada, não uma observação ausente; sem suporte significa que nenhuma posição do domínio pôde ser avaliada.

<div class="method-box example">

Três estados do mesmo ciclone ilustram as três classes. Com o centro no meio do domínio, o disco de 1.100 km cabe inteiro nele e o estado tem **suporte completo**. Conforme o ciclone se aproxima da borda leste, parte do disco passa a cair fora do recorte: as células restantes continuam observáveis e o estado tem **suporte parcial**, com um denominador espacial menor. Se o centro sai do domínio o bastante para que nenhuma célula do recorte fique a menos de 1.100 km, o estado fica **sem suporte** e não possui denominador — por isso ele nunca é convertido em zero de excedência.

```
suporte completo    suporte parcial     sem suporte
+---------+         +---------+         +---------+
|  # # #  |         |     # # | · ·     |         |  · · ·
|  # C #  |         |     # C | · ·     |         |  · C ·
|  # # #  |         |     # # | · ·     |         |  · · ·
+---------+         +---------+         +---------+
```

O retângulo é o domínio, `C` é o centro do ciclone, `#` é uma célula do domínio situada a até 1.100 km do centro — portanto observável — e `·` é uma posição dentro de 1.100 km mas fora do domínio, que não foi observada e não pode ser lida como não-excedência. Esquema conceitual: número de células, densidade e tamanho do disco não estão em escala.

</div>

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
