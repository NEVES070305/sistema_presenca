# Endpoint

- `/presenca/comentario`: Post
  - Descrição: Adicione um comentário a um aluno em determinado dia
  - Parâmetros: DateTime dataParaPresenca, INT usuarioId, string comentario
- `/presenca`: UPDATE
  - Descrição: Modificar a presença de um determinado aluno
  - Parâmetros: DateTime dataParaPresenca, INT usuarioId
- `/presenca/data`: GET
  - Descrição: Retorna uma lista de presenca em determinado dia
- `/presenca/pessoa`: GET
  - Descrição: Retorna a presença de uma pessoa entre duas data
  - Parêmetros: DateTime dataInicial, DateTime dataFinal, usuarioId
