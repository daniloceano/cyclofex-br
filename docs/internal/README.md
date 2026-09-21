# Documentação técnica e interna

## Finalidade

Esta área responde **como reproduzir e manter** o projeto. Ela contém caminhos, scripts, comandos, contratos de dados e convenções de implementação. A explicação do problema, dos métodos e das evidências pertence ao [relatório científico](../index.md).

## Referências técnicas

- [Estrutura do repositório](repository_structure.md): responsabilidade de cada diretório e correspondência entre código e produtos.
- [Fluxos computacionais](computational_workflows.md): ambiente, comandos, cache, geração de resultados e dashboard.
- [Referência dos dados](data_reference.md): arquivos, schemas, campos, unidades de linha, hashes e contratos.
- [Investigação de Q-002 e Q-003](q002_q003_provenance.md): reconstrução detalhada do código legado de vento, thresholds, tempo e quadrantes.
- [Auditoria humana simulada](human_audit.md): verificação das 16 perguntas que um pesquisador externo deve conseguir responder.
- [Padrão permanente da documentação](../documentation_guidelines.md): regras obrigatórias para modificar o relatório científico.

## Limite entre as camadas

Uma página científica pode vincular esta área para permitir auditoria, mas não deve obrigar o leitor a conhecer nomes de scripts para compreender a ciência. Da mesma forma, esta área pode ser direta e operacional: ela não precisa repetir interpretações, resultados ou limitações já mantidos nas fontes científicas.

## Fonte canônica e geração

Markdown em `docs/` e `docs/internal/` é fonte canônica. O HTML em `dashboard/` é derivado por `python3 dashboard/build_docs.py` e não deve receber edições de conteúdo manuais.
