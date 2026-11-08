# Beach Volleyball Vision

Interface Streamlit local para acionar, por subprocesso, um pipeline existente de
análise de partidas gravadas de vôlei de praia. A interface usa CPU por padrão,
valida arquivos, impede duas execuções simultâneas e disponibiliza o vídeo gerado.

## Estado

**Confirmado:** a camada web, o adaptador e os testes estão presentes.

**Confirmado:** Python 3.13.17, Streamlit 1.67.0, OpenCV 5.0.0, pytest 9.2.0 e
Ruff 0.17.4 estão instalados no ambiente virtual `.venv`. Os testes e o lint
passam, e o smoke da interface retornou HTTP 200 em `127.0.0.1:8501`. O material
recebido ainda não inclui o pipeline `run.py`; a aplicação não simula resultados
e informa claramente essa ausência.

## Estrutura

- `streamlit_app.py`: entrada da interface.
- `app/web.py`: formulário, estados e apresentação do resultado.
- `app/runner.py`: validação do contrato, trava e subprocesso da CLI.
- `app/validation.py`: validação OpenCV e de modelo.
- `app/storage.py`: arquivos temporários controlados.
- `tests/`: testes unitários sem inferência pesada.

## Contrato esperado da CLI

O contrato abaixo veio do briefing e permanece **informado/não verificado**:

```powershell
py run.py VIDEO --out SAIDA --model MODELO --device cpu
```

O arquivo `run.py` deve permanecer na raiz. A implementação real de detecção e
rastreamento não faz parte desta camada e não foi reconstruída.

## Preparação e execução

Os comandos abaixo foram **confirmados** no Windows com Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

A configuração versionada restringe o servidor a `127.0.0.1`. Não altere o bind
para uma interface de rede sem avaliar os riscos. `requirements.txt` cobre somente
a camada web; as dependências do pipeline ausente devem vir de sua fonte original.

## Testes e lint

Com as dependências de desenvolvimento instaladas:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
py -m ruff check .
```

Status atual: **confirmado**, com 11 testes aprovados e Ruff sem ocorrências.
Consulte `docs/current-state.md` e `docs/test-plan.md` para evidências e pendências.

## Limites do MVP

Sem placar, estatísticas, identificação nominal, classificação de ações,
rallies automáticos, 3D, API, banco, autenticação ou processamento em nuvem.

