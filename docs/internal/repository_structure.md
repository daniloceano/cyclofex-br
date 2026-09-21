# Estrutura do repositório

## Mapa

```text
cyclofex-br/
├── data/                 dados derivados versionados e documentação herdada
├── docs/                 fontes Markdown do relatório científico
│   └── internal/         referência técnica e operacional
├── scripts/              código organizado por etapa ou análise
├── outputs/              produtos reproduzíveis organizados pela mesma etapa
├── dashboard/            HTML estático gerado e estilos
├── README.md             ponto de entrada do repositório
└── requirements.txt      dependências Python
```

## Correspondência código–produto

O registro [D-001](../decisions.md#d-001--organizar-código-e-produtos-por-análise) mantém a correspondência `scripts/<etapa>/` ↔ `outputs/<etapa>/`. Subdiretórios só devem ser criados quando houver uma etapa real e produto correspondente.

| Etapa | Código | Produtos |
| --- | --- | --- |
| Aquisição e preparação | `scripts/00_data_acquisition/` | `outputs/00_data_acquisition/` e catálogos em `data/` |
| Caracterização estrutural | `scripts/01_data_overview/` | `outputs/01_data_overview/` |
| Análise exploratória | `scripts/02_exploratory_analysis/` | `outputs/02_exploratory_analysis/` |
| E-001 — orientação | `scripts/03_e001_orientation/` | `outputs/03_e001_orientation/` |

## Convenções

- Arquivos científicos canônicos usam Markdown; HTML é sempre derivado.
- Produtos não devem ser copiados para criar uma segunda fonte de verdade. O dashboard referencia `outputs/` diretamente.
- Dados brutos reconstruíveis podem permanecer em cache ignorado pelo Git; produtos mínimos e manifestos preservam a linhagem.
- Um novo experimento só recebe diretório de código e saída quando seu protocolo está pronto para execução.
- IDs `D-...`, `Q-...`, `A-...` e `E-...` são persistentes; itens substituídos permanecem no histórico com status apropriado.
