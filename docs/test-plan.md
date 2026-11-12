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
| 10/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m pytest -q` | **confirmado** | `15 passed in 3.96s`; inclui smoke do dashboard e mocks de sucesso/falha da UI |
| 10/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m ruff check .` | **confirmado** | `All checks passed!` |
| 10/11/2026 | Windows / Streamlit 1.67.0 | `streamlit run streamlit_app.py --server.headless=true --server.port=8511` + HTTP local | **confirmado** | Resposta `HTTP 200` em `127.0.0.1:8511`; processo encerrado após o smoke |
| 10/11/2026 | Navegador | Inspeção visual desktop e viewport estreita | **informado/não verificado** | Nenhuma instância de navegador estava disponível na sessão |
| 11/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m pip install ultralytics` | **confirmado** | Ultralytics 8.4.211 e PyTorch 2.15.0+cpu instalados; CUDA indisponível |
| 11/11/2026 | Windows / modelo local | Carregar `models/yolov8n.pt` | **confirmado** | Peso com 6.549.796 bytes; classes `person` e `sports ball` verificadas |
| 11/11/2026 | Windows / smoke sintético | Primeira tentativa com temporário em `data/` | **informado/não verificado** | Comando de teste não iniciou a CLI porque `data/` não existia; comando corrigido |
| 11/11/2026 | Windows / CPU | `run.py` com vídeo sintético de dois quadros | **confirmado** | Retorno 0; saída MP4 de 2.540 bytes legível pelo OpenCV |
| 11/11/2026 | Windows / Python 3.13.17 | `.venv\Scripts\python.exe -m pytest -q` | **confirmado** | Execução final: `21 passed in 6.55s` |
| 11/11/2026 | Windows / Ruff 0.17.4 | `.venv\Scripts\python.exe -m ruff check .` | **confirmado** | `All checks passed!` |
| 11/11/2026 | Vídeo real do usuário | Fluxo Streamlit completo | **planejado** | Aguardando seleção e início explícito pelo usuário; precisão e tempo ainda não medidos |
