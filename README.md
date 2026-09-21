# cyclofex-br

O **cyclofex-br** investiga como ventos extremos associados a ciclones extratropicais se organizam no espaço e ao longo do ciclo de vida no Atlântico Sul. O dashboard funciona como um **relatório científico vivo**: apresenta problema, dados, preparação, análises, evidências, limitações, decisões e questões abertas sem exigir conhecimento prévio do código.

## Comece pela ciência

Abra [`dashboard/index.html`](dashboard/index.html) ou leia a fonte canônica em [`docs/index.md`](docs/index.md).

| Para compreender... | Página científica |
| --- | --- |
| pergunta, ideia central e estágio | [Visão geral](docs/index.md) |
| origem, significado e unidades dos dados | [Dados](docs/data.md) |
| construção e validação da amostra | [Preparação dos dados](docs/data_preparation.md) |
| análise já executada | [Análise exploratória](docs/exploratory_analysis.md) |
| primeiro experimento formal | [E-001 — orientação pelo movimento](docs/e001_orientation.md) |
| segundo experimento formal | [E-002 — weighting por estado versus por ciclone](docs/e002_weighting.md) |
| achados e alcance das conclusões | [Resultados e evidências](docs/results.md) |
| método adotado versus proposta futura | [Metodologia atual](docs/methodology.md) e [Plano científico](docs/scientific_plan.md) |
| lacunas, escolhas e próximos testes | [Limitações](docs/limitations.md), [Questões abertas](docs/open_questions.md), [Decisões](docs/decisions.md) e [Experimentos](docs/experiments.md) |
| linhagem e reprodução | [Proveniência e reprodutibilidade](docs/reproducibility.md) |

A fonte operacional de tracks está validada, E-001 permanece **INCONCLUSIVE** e E-002 mostrou que essa conclusão é **ROBUSTA AO WEIGHTING**: orientar pelo movimento concentra o núcleo q95, mas dispersa a massa intermediária e a cauda tanto sob peso por estado quanto por ciclone. Nenhuma representação espacial principal, modelo probabilístico ou hazard geográfico foi adotado.

## Manutenção e reprodução

A [documentação técnica](docs/internal/README.md) reúne estrutura do repositório, comandos, dependências, cache e contratos de dados. As regras permanentes para qualquer atualização estão em [`docs/documentation_guidelines.md`](docs/documentation_guidelines.md) e devem ser lidas antes de modificar a documentação científica.

Para reconstruir o HTML a partir do Markdown:

```sh
python3 dashboard/build_docs.py
```

O dashboard é estático; Pandoc é necessário apenas durante a geração.
