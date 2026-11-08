# Regras obrigatórias

1. Auditar antes de alterar; não presumir funcionalidades relatadas.
2. Preservar CLI e comportamento funcional; não reescrever pipeline.
3. Separar Streamlit e processamento por adaptador mínimo.
4. Priorizar Windows e CPU; não exigir CUDA.
5. Não incluir API, banco, autenticação, Docker ou microsserviços.
6. Não implementar ações, rallies automáticos, placar, estatísticas ou 3D neste MVP.
7. Usar type hints, nomes claros, tratamento de erros e evitar duplicação.
8. Não mascarar falhas ou inventar resultados/benchmarks.
9. IDs P1/P2/P3 são temporários, não identidades de atletas.
10. Validar arquivos/caminhos e subprocessos; não usar `shell=True` com entrada não confiável.
11. Escutar em `127.0.0.1` por padrão; nunca expor serviço sem autorização.
12. Não baixar pesos/datasets nem rodar inferência pesada sem necessidade/autorização.
13. Criar testes para lógica crítica e registrar o que foi ou não executado.
14. Não refatorar código fora do escopo; dependências novas exigem justificativa.
15. Documentar decisões e manter PRD, especificações, backlog e README coerentes.
