# Beach Volleyball Vision

Interface Streamlit local para acionar, por subprocesso, um pipeline existente de
análise de partidas gravadas de vôlei de praia. A interface usa CPU por padrão,
valida arquivos, impede duas execuções simultâneas e disponibiliza o vídeo gerado.

## Estado

**Confirmado:** a camada web, o adaptador, a CLI baseline e os testes estão presentes.

**Confirmado:** Python 3.13.17, Streamlit 1.67.0, OpenCV 5.0.0, pytest 9.2.0 e
Ruff 0.17.4, Ultralytics 8.4.211 e PyTorch 2.15.0+cpu estão instalados no ambiente
virtual `.venv`. Os testes e o lint passam, o smoke da interface retornou HTTP 200
em `127.0.0.1:8501` e a CLI processou um vídeo sintético curto em CPU.

**Confirmado:** o pipeline original não foi recuperado. Com autorização explícita,
foi criado `run.py` como baseline mínimo para detectar as classes genéricas
`person` e `sports ball` e gerar um MP4 anotado.

## Estrutura

- `streamlit_app.py`: entrada da interface.
- `run.py`: CLI baseline de inferência YOLO quadro a quadro.
- `app/web.py`: formulário, estados e apresentação do resultado.
- `app/runner.py`: validação do contrato, trava e subprocesso da CLI.
- `app/validation.py`: validação OpenCV e de modelo.
- `app/storage.py`: arquivos temporários controlados.
- `tests/`: testes unitários sem inferência pesada.

## Contrato da CLI

O contrato abaixo está **confirmado** por testes e smoke sintético:

```powershell
py run.py VIDEO --out SAIDA --model MODELO --device cpu
```

O arquivo `run.py` permanece na raiz. O baseline não implementa tracking,
identificação de atletas, ações, rallies, placar ou estatísticas.

## Preparação e execução

Os comandos abaixo foram **confirmados** no Windows com Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

A configuração versionada restringe o servidor a `127.0.0.1`. Não altere o bind
para uma interface de rede sem avaliar os riscos. O peso local não é versionado.
Para preparar explicitamente o modelo padrão em uma nova instalação:

```powershell
New-Item -ItemType Directory -Force models
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"
```

Esse comando baixa o peso; execute-o somente com autorização e acesso à rede. Se
`models/yolov8n.pt` existir, a interface o usa por padrão. Um upload `.pt` ou
`.onnx` personalizado substitui o modelo padrão na execução atual.

## Testes e lint

Com as dependências de desenvolvimento instaladas:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
py -m ruff check .
```

Status atual: **confirmado**, com 21 testes aprovados e Ruff sem ocorrências.
Consulte `docs/current-state.md` e `docs/test-plan.md` para evidências e pendências.

## Limites do MVP

Sem placar, estatísticas, identificação nominal, classificação de ações,
rallies automáticos, 3D, API, banco, autenticação ou processamento em nuvem.

