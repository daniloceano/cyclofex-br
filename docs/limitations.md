# Limitações

## Finalidade

Estas limitações definem o alcance da evidência atual. Elas não são notas laterais: qualquer experimento futuro deve mostrar quais foram resolvidas, quais permanecem e como afetam a interpretação.

## Dados e proveniência

- A versão ou reprocessamento exato do ERA5 usado no produto de vento não foi recuperado.
- O arquivo de percentis locais não possui, no material disponível, versão formal e hash preservados.
- Os percentis atuais usam somente 2010–2020, embora o catálogo de tracks cubra 1979–2020; eles não devem ser tratados como climatologia final.
- A versão, os parâmetros, a configuração e os artefatos intermediários da execução original do CycloPhaser não estão disponíveis. Os rótulos podem ser usados como fornecidos, mas seus limites não podem ser reproduzidos integralmente.

## Seleção da amostra

- O recorte de vento é condicionado por `wind_speed > min(15,6 m/s; q90_local)`. Ele não contém campos completos.
- Ciclones sem qualquer ponto selecionado ficam ausentes do recorte de vento, ainda que existam no catálogo.
- O mesmo ponto de grade e hora pode ser associado a mais de um ciclone simultâneo; foram observados 414.124 pontos–hora nessa situação, com máximo de três ciclones.
- A justificativa científica original para o raio de 1.100 km não foi localizada. A regra é reproduzida, mas sua adequação ainda não foi testada.

## Suporte espacial

- O domínio de 65°S–10°S e 85°W–15°W trunca círculos próximos às bordas.
- Entre os 29.311 estados do período comparável, 5.977 não possuem suporte e 7.716 têm suporte parcial.
- Para suporte parcial, somente a interseção com o domínio pode entrar no denominador; a região externa permanece não observada.
- Ausência de linha é não-excedência apenas quando estado, grade, raio e domínio demonstram que a célula era observável.

## Cobertura temporal e lifecycle

- O recorte de vento cobre 2010–2020; ele não representa diretamente todo o período das tracks.
- Há 509.788 linhas espaciais sem fase.
- Os rótulos com sufixo `2`, `residual` e intervalos nulos têm origem conhecida, mas sua execução original não é plenamente auditável.
- A associação da track horária ao ERA5 usa vizinho temporal, não interpolação do centro; diferenças de até 3 h são aceitas.

## Dependência e potencial de viés

- Pontos do mesmo estado e estados do mesmo ciclone são dependentes. Tratar linhas como unidades independentes produziria pseudorreplicação.
- Ciclones longos, estados com maior área selecionada e fases mais frequentes contribuem mais linhas às estatísticas pontuais. E-002 quantificou especificamente o efeito do número de estados q95-positivos: os 10% superiores reuniram 22,52% da massa *equal-state*.
- A seleção por intensidade altera distribuições, contagens e contrastes por fase ou quadrante.
- Suporte parcial e trajetórias fora do domínio podem gerar cobertura desigual ligada à posição do ciclone.
- A análise atual não quantifica como essas fontes de seleção se combinam.

## Métodos ainda não testados

- Não foi escolhido threshold científico definitivo.
- Evento, *excursion set* e *footprint* ainda não têm definição operacional adotada.
- Não foram estimadas *coverage probabilities* nem magnitude condicional.
- A orientação *centered* versus *motion-relative* foi comparada em E-001, mas o resultado foi inconclusivo. E-002 mostrou que essa conclusão é robusta a *equal-state* versus *equal-cyclone*; sensibilidade ao threshold e normalização por tamanho não foram testadas.
- E-001 e E-002 usaram bootstrap por ciclone para diferenças específicas, mas não houve validação fora da amostra, remoção de ciclones influentes nem estudo abrangente de generalização.
- Não foi calculado hazard geográfico.

## Consequência para as conclusões

Os resultados atuais sustentam descrição, formulação de hipóteses, a conclusão limitada de E-001 e sua robustez ao weighting demonstrada em E-002. Eles não sustentam causalidade, probabilidades populacionais, generalização climatológica, avaliação de risco, escolha definitiva de orientação ou escolha de um modelo. A página [resultados e evidências](results.md) registra explicitamente, para cada achado, o que pode e o que não pode ser concluído.
