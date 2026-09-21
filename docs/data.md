# Dados

## Que informação o projeto necessita

Para estudar a organização espacial de ventos extremos associados a ciclones extratropicais, são necessárias três informações sincronizadas: a posição do centro de cada ciclone ao longo do tempo, sua fase do ciclo de vida e o campo de vento próximo ao centro no mesmo instante. A combinação dessas informações permite descrever o vento em coordenadas relativas ao ciclone sem perder a identidade do evento nem confundir pontos de grade com ciclones independentes.

## Tracks e ciclo de vida

Uma **track** é a sequência temporal dos centros atribuídos ao mesmo ciclone. Cada posição em uma hora específica representa um estado daquele sistema. Depois da associação temporal com o ERA5, o projeto usa a expressão **estado ciclone–tempo** para o par formado por um ciclone identificado por `track_id` e um horário de campo de 6 h. Um mesmo ciclone contribui com vários estados; por isso, esses estados e seus pontos espaciais não são réplicas independentes do ciclone.

A fonte operacional é `tracks_SAt_filtered_with_energetics.csv`, do [Zenodo 18133432](https://zenodo.org/records/18133432), DOI [`10.5281/zenodo.18133432`](https://doi.org/10.5281/zenodo.18133432). Ela fornece centros horários, vorticidade central, região de gênese e o campo `period`, preservado no projeto como `phase`. O catálogo cobre tracks iniciadas entre 1979 e 2020; as últimas terminam em 7 de janeiro de 2021.

O Zenodo foi adotado porque usa o mesmo namespace operacional do recorte de vento, reproduz exatamente seus 20.101 estados presentes e recupera estados omitidos pelo filtro de seleção. A base de [Gramcianinov et al. (2020) no Mendeley Data](https://doi.org/10.17632/kwcvfr52hp.4) permanece como referência histórica da família de tracks. Seus identificadores e universo de sistemas não coincidem integralmente com o catálogo operacional e, por isso, ela não é usada para gerar os estados atuais. Essa escolha é formalizada em [D-004](decisions.md#d-004--adotar-o-zenodo-18133432-como-fonte-canônica-operacional-das-tracks-e-do-lifecycle).

O **lifecycle**, ou ciclo de vida, divide a evolução do ciclone em fases como incipiente, intensificação, madura e decaimento. Os rótulos foram produzidos com o CycloPhaser e incluem repetições com sufixo `2`, fase residual e intervalos sem rótulo. A origem está confirmada, mas a versão e configuração exatas da execução original ainda não são reproduzíveis; essa limitação permanece em [Q-004](open_questions.md#q-004--como-foram-produzidas-e-como-devem-ser-tratadas-as-fases).

## Vento ERA5

O vento analisado provém do ERA5 em *single levels*, na grade nativa regular de 0,25° e em intervalos de 6 h no produto atualmente reconstruído. A variável `wind_speed` é a magnitude do vento a 10 m, em metros por segundo, obtida dos componentes zonal e meridional. Em linguagem direta, ela informa a intensidade do vento horizontal perto da superfície em cada ponto da grade.

O recorte disponível contém indicadores para limiares fixos de 15,6, 20 e 25 m/s e para percentis locais q90, q95 e q99. Um **threshold**, ou limiar, é o valor acima do qual o vento é classificado como excedência. Um **quantil local** varia de ponto para ponto: q90 é o valor superado em 10% da distribuição usada para aquele local. Os percentis atuais foram calculados com 16.072 campos de 6 h dos 11 anos civis de 2010–2020, sem estratificação e sem máscara terra–oceano. Eles são experimentais e não constituem a definição final de extremo do projeto.

A versão ou reprocessamento exato do ERA5 e um artefato formalmente versionado dos percentis não foram recuperados. A regra de cálculo é conhecida, mas essa lacuna impede identificar integralmente os insumos originais.

## Como ciclone e vento são associados

Cada centro horário da track é ligado ao horário ERA5 de 6 h mais próximo, desde que a diferença não ultrapasse 3 h. Se dois horários forem igualmente próximos, escolhe-se o anterior. Quando mais de uma hora da mesma track aponta para o mesmo campo, permanece a posição com menor diferença temporal e, em novo empate, a anterior. A posição do centro não é interpolada.

Para o estado resultante, são considerados pontos da grade entre 65°S–10°S e 85°W–15°W situados a até 1.100 km do centro, segundo distância haversine numa esfera de raio 6.371 km. Esse círculo é o **suporte espacial** atual: o conjunto de posições que poderiam contribuir para aquele estado dentro do domínio disponível.

- **Suporte completo:** o círculo está inteiramente contido no domínio.
- **Suporte parcial:** parte do círculo intersecta o domínio e parte fica fora; apenas a interseção foi observada.
- **Sem suporte:** nenhuma célula do domínio fica dentro do círculo; não há observação espacial para classificar.

Ausência, zero e não observado são conceitos diferentes. Quando um estado tem suporte e nenhuma linha no recorte condicionado, nenhuma célula passou pelo filtro de entrada e as excedências podem ser reconstruídas como falsas sob o contrato atual. Quando não há suporte, a ausência de linhas significa **não observado**, não vento zero nem não-excedência.

## Estrutura científica final

| Nível | O que representa | Dimensão atual | Papel científico |
| --- | --- | --- | --- |
| Ciclone | Um sistema identificado por `track_id` | 6.789 no catálogo completo; 1.781 no recorte de vento | Unidade fundamental de análise quando aplicável |
| Estado horário | Centro e lifecycle de uma track em uma hora | 631.009 | Fonte temporal canônica |
| Estado ciclone–tempo de 6 h | Um ciclone associado a um campo ERA5 | 109.857 | Ponte entre trajetória e atmosfera |
| Estado no recorte de vento | Estado com ao menos uma linha selecionada | 20.101 entre 2010–2020 | Objeto da análise exploratória atual |
| Ponto espacial | Uma célula de grade ligada a um estado | 17.182.983 linhas armazenadas | Unidade de armazenamento; não é ciclone independente |

No período comparável de 2010–2020, o catálogo completo contém 29.311 estados de 1.785 tracks: 20.101 estão presentes no recorte, 3.233 estão ausentes apesar de terem suporte e 5.977 não possuem suporte. Quatro tracks do catálogo não aparecem entre os 1.781 ciclones com linhas selecionadas.

## Produtos derivados

Depois de compreender as unidades científicas, a implementação pode ser auditada nos três produtos: catálogo horário, catálogo de estados de 6 h e recorte condicionado de vento. Campos, tipos, hashes e contratos estão na [referência técnica dos dados](internal/data_reference.md); a linhagem completa está em [proveniência e reprodutibilidade](reproducibility.md).
