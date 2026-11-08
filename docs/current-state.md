# Estado atual — auditoria de 08/11/2026

## Escopo auditado

**Confirmado:** antes desta implementação, a raiz continha apenas `AGENTS.md`,
`README.md` e arquivos em `docs/`. Não havia `run.py`, manifesto de dependências,
testes, modelos, vídeos, módulos Python ou repositório Git inicializado. A listagem
foi feita com `Get-ChildItem -Force` e `rg --files`.

Na auditoria inicial, o launcher `py` respondeu `No installed Python found!`.
**Confirmado após configuração:** Python 3.13.17 foi instalado para o usuário e o
ambiente virtual `.venv` foi criado. Streamlit 1.67.0, OpenCV 5.0.0, pytest 9.2.0
e Ruff 0.17.4 foram importados/executados. O launcher também identificou um Python
3.14.3 preexistente, que não foi alterado.

## Implementação presente

| Item | Evidência | Estado |
|---|---|---|
| Entrada Streamlit | `streamlit_app.py`; `app/web.py:31` | **confirmado** por inspeção |
| Bind local | `.streamlit/config.toml:2` (`127.0.0.1`) | **confirmado** por inspeção e HTTP 200 em `127.0.0.1:8501` |
| Upload controlado | `app/storage.py:15` | **confirmado** por inspeção |
| Validação de vídeo/modelo | `app/validation.py` | **confirmado** por inspeção |
| Adaptador da CLI | `app/runner.py:101` | **confirmado** por inspeção |
| Subprocesso sem shell | `app/runner.py:137` | **confirmado** por inspeção |
| Exclusão mútua | `app/runner.py:51` | **confirmado** por inspeção |
| CPU padrão e CUDA opcional | `app/runner.py`; `app/web.py` | **confirmado** por inspeção |
| Reprodução e download | `app/web.py:154` | **confirmado** por inspeção |
| Testes com mocks | `tests/test_runner.py`; `tests/test_validation.py` | **confirmado**: 11 aprovados |

Os uploads são copiados em blocos para `data/work/<sessão>` com nomes UUID,
e os resultados usam nomes únicos em `data/outputs`. Entradas temporárias são
removidas após a tentativa; resultados não são apagados automaticamente.

## Pipeline de visão

**Informado/não verificado:** o contrato do briefing indica:

```text
run.py VIDEO --out SAIDA --model MODELO --device cpu|cuda
```

**Confirmado:** `run.py` continua ausente. Logo, detecção YOLO, tracking,
anotações e geração real de vídeo não existem neste material e não foram
recriados. O adaptador encerra com mensagem explícita quando a CLI não está
presente. A compatibilidade do contrato deverá ser revisada quando o pipeline real
for fornecido.

## Requisitos e aceite relacionados

- RF-001–010, RNF-001–008 e CA-001–006: camada de integração **confirmado** por
  inspeção e testes unitários; execução real **informado/não verificado** pela
  ausência da CLI, modelo e vídeo autorizado.
- RF-011 e CA-007: **informado/não verificado**, pois não há CLI a preservar ou
  testar neste diretório.
- CA-008: **confirmado**; 11 testes passaram e Ruff não encontrou ocorrências.
- RF-012: **fora de escopo**.

## Lacunas e riscos restantes

- Obter o `run.py` e seus módulos reais; auditar argumentos, códigos de retorno,
  logs, saída e dependências antes de declarar integração concluída.
- Executar com vídeo curto e modelo autorizado; validar CPU, codec, reprodução,
  encerramento inesperado, consumo de disco e concorrência no Windows.
- Definir licença e política de retenção dos resultados.

