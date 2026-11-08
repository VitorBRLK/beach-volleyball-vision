# Plano de testes

## Estratégia
pytest e `unittest.mock`; execução rápida sem modelos grandes por padrão. Separar unitários, integração, regressão e testes manuais. Registrar ambiente, comando, data, resultado e limitações.

## Casos prioritários
| Caso | Tipo | Esperado |
|---|---|---|
| Caminho ausente, traversal, extensão/conteúdo inválidos | Unitário/segurança | Rejeição sem executar |
| Modelo ausente, device inválido | Unitário | Mensagem clara |
| Construção de argumentos com espaços Windows | Unitário | Lista segura, sem shell |
| Transições idle/running/completed/failed | Unitário | Estados coerentes |
| Processo retorna erro ou não cria saída | Unitário/integração | `failed` e log |
| Segunda execução simultânea | Concorrência | Bloqueada |
| Falta de espaço e falha de escrita | Falha | Sem falso sucesso |
| UI → adaptador → CLI | Integração | Parâmetros corretos |
| Geração e acesso ao vídeo | Integração | Arquivo íntegro |
| CLI, caixas, IDs e bola | Regressão | Sem mudança indevida |
| Navegador Windows, CPU, codec, RAM | Manual | Uso viável, métricas registradas |
| Encerramento inesperado | Manual/integração | Sem lock/processo órfão |

## Dados de teste
Vídeo curto autorizado e arquivo inválido pequeno; modelos locais existentes. Não baixar datasets ou processar vídeo grande automaticamente.

## Registro de execução
| Data | Ambiente | Comando/caso | Resultado | Evidência/bloqueio |
|---|---|---|---|---|
| 08/11/2026 | Windows / PowerShell | `Get-ChildItem -Force`; `rg --files` | **confirmado** | Somente documentação existia antes da implementação; `run.py` ausente |
| 08/11/2026 | Windows / PowerShell | `python --version` | **informado/não verificado** | Comando `python` não reconhecido |
| 08/11/2026 | Windows / PowerShell | `py --version` | **informado/não verificado** | Launcher respondeu `No installed Python found!` |
| 08/11/2026 | Windows / PowerShell | `py -m pytest -q` | **informado/não verificado** | Comando executado, mas não iniciou: `No installed Python found!` |
| 08/11/2026 | Windows / PowerShell | `py -m ruff check .` | **informado/não verificado** | Comando executado, mas não iniciou: `No installed Python found!` |
| 08/11/2026 | Windows / navegador | Smoke Streamlit e vídeo real | **planejado** | Bloqueado por `run.py`, modelo e vídeo autorizado ausentes |
| 08/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m pytest -q` | **confirmado** | `11 passed in 0.30s` |
| 08/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m ruff check .` | **confirmado** | `All checks passed!` |
| 08/11/2026 | Windows / Python 3.13.17 | Importar Streamlit/OpenCV/pytest | **confirmado** | Streamlit 1.67.0; OpenCV 5.0.0; pytest 9.2.0 |
| 08/11/2026 | Windows / Streamlit 1.67.0 | `streamlit run streamlit_app.py` | **confirmado** | Servidor em `127.0.0.1:8501`; requisição HTTP retornou 200 |
