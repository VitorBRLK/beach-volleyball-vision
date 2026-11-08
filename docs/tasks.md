# Backlog técnico

Prioridades: P0 = MVP, P1 = estabilidade, P2 = melhoria. O estado
**confirmado** abaixo significa evidência por inspeção; a execução permanece
**informado/não verificado** onde Python, CLI ou vídeo real são necessários.
Critérios CA referem-se a `prd.md`.

| ID | Título | Pri. | Dependência | Arquivos previstos | Aceite / teste | Estado |
|---|---|---|---|---|---|---|
| BL-001 | Auditar pipeline | P0 | — | run.py, docs/current-state.md | Evidências e CLI documentadas; inspeção | **confirmado**: material auditado; CLI ausente |
| BL-002 | Validar Windows | P0 | BL-001 | README.md | Dependências, CPU, codec verificados; smoke | **planejado**: sem Python/CLI |
| BL-003 | Adaptador de execução | P0 | BL-001 | app/runner.py | CA-003, CA-007; unitários com mocks | Código e testes unitários **confirmado**; CLI **informado/não verificado** |
| BL-004 | Base Streamlit | P0 | BL-002 | app/web.py | CA-001; smoke manual | **confirmado**: servidor local e HTTP 200 |
| BL-005 | Seleção e validação | P0 | BL-004 | app/web.py | CA-002; arquivos inválidos | Código e testes unitários **confirmado** |
| BL-006 | Iniciar execução | P0 | BL-003, BL-005 | app/web.py | CA-003; integração | Código **confirmado**; integração **informado/não verificado** |
| BL-007 | Estado e erros | P0 | BL-006 | app/web.py | CA-004; mocks de falha | Código e mocks de falha **confirmado** |
| BL-008 | Reproduzir saída | P0 | BL-006 | app/web.py | CA-005; navegador/codec | Código **confirmado**; navegador **informado/não verificado** |
| BL-009 | Acesso à saída | P0 | BL-006 | app/web.py | CA-005; arquivo íntegro | Código **confirmado**; teste **informado/não verificado** |
| BL-010 | Controle de concorrência | P0 | BL-003 | app/runner.py | CA-006; dupla tentativa | Código e teste com mock **confirmado**; teste multiprocesso **planejado** |
| BL-011 | Configurar YOLO | P0 | BL-003 | app/web.py | Modelo válido/inválido; testes | Upload/validação **confirmado**; YOLO **informado/não verificado** |
| BL-012 | Métricas reais de execução | P1 | BL-003 | app/runner.py | Tempo medido; testes | Medição em código **confirmado**; valor real **informado/não verificado** |
| BL-013 | Vídeos reais e regressão | P1 | BL-006–011 | tests/, docs/test-plan.md | CA-003–008; relatório | **planejado** |
| BL-014 | Metadados de vídeo | P2 | BL-005 | app/web.py | Dados extraídos, sem inventar | **planejado** |
| BL-015 | Organização de arquivos | P1 | BL-003 | data/, app/runner.py | Isolamento e limpeza; testes | Código e teste de contenção **confirmado** |

## Definição de pronto
Alteração mínima revisada; requisitos atendidos; testes pertinentes executados ou bloqueios registrados; CLI preservada; documentação atualizada. Não marcar como concluído por existência de código apenas.
