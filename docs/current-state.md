# Estado atual — auditoria atualizada em 11/11/2026

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
| Entrada Streamlit | `streamlit_app.py`; `app/web.py` | **confirmado** por inspeção e smoke HTTP |
| Dashboard e tema escuro | `app/web.py`; `.streamlit/config.toml` | **confirmado** por inspeção e teste de UI |
| Bind local | `.streamlit/config.toml:2` (`127.0.0.1`) | **confirmado** por inspeção e HTTP 200 em `127.0.0.1:8501` |
| Upload controlado | `app/storage.py:15` | **confirmado** por inspeção |
| Validação de vídeo/modelo | `app/validation.py` | **confirmado** por inspeção |
| Adaptador da CLI | `app/runner.py:101` | **confirmado** por inspeção |
| Subprocesso sem shell | `app/runner.py:137` | **confirmado** por inspeção |
| Exclusão mútua | `app/runner.py:51` | **confirmado** por inspeção |
| CPU padrão e CUDA opcional | `app/runner.py`; `app/web.py` | **confirmado** por inspeção |
| Reprodução e download | `app/web.py` | **confirmado** por inspeção |
| Testes com mocks | `tests/test_runner.py`; `tests/test_validation.py`; `tests/test_web.py` | **confirmado**: 15 aprovados |

Os uploads são copiados em blocos para `data/work/<sessão>` com nomes UUID,
e os resultados usam nomes únicos em `data/outputs`. Entradas temporárias são
removidas após a tentativa; resultados não são apagados automaticamente.

## Pipeline de visão

**Informado/não verificado:** o contrato do briefing indica:

```text
run.py VIDEO --out SAIDA --model MODELO --device cpu|cuda
```

**Confirmado:** o pipeline original continua ausente. Em 11/11/2026, após
autorização explícita, foi criado um baseline em `run.py` que respeita esse
contrato, executa detecção YOLO de pessoa/bola e gera vídeo anotado. A
compatibilidade com o pipeline original continua **informado/não verificado**.

## Requisitos e aceite relacionados

- RF-001–010, RNF-001–008 e CA-001–006: camada de integração **confirmado** por
  inspeção e testes unitários/de UI; inferência baseline em vídeo sintético
  **confirmado**; vídeo real do usuário **planejado**.
- RF-011 e CA-007: contrato da nova CLI baseline **confirmado**; preservação do
  pipeline original **informado/não verificado**, pois ele não foi fornecido.
- CA-008: **confirmado**; 21 testes passaram e Ruff não encontrou ocorrências.
- RF-012: **fora de escopo**.

## Lacunas e riscos restantes

- Obter o pipeline original, se ele existir, e comparar seu comportamento com o
  baseline antes de substituir ou ampliar algoritmos.
- Executar com o vídeo real autorizado; validar precisão, tempo em CPU, reprodução,
  consumo de disco e concorrência no Windows.
- Definir licença e política de retenção dos resultados.
- Inspeção visual em navegador real e viewport estreita: **informado/não
  verificado** em 10/11/2026 porque não havia navegador conectado à sessão. O
  smoke automatizado do Streamlit e a resposta HTTP 200 foram confirmados.

## Modernização da interface — 10/11/2026

**Confirmado:** `app/web.py` organiza a experiência em Configuração →
Processamento → Resultado, apresenta somente estados verificáveis do pipeline,
da sessão e do bind local, mantém CPU como padrão e desabilita o CTA quando
faltam uploads, há execução ativa ou `run.py` está ausente. O resultado e o
download continuam condicionados à saída real verificada pelo adaptador.

**Confirmado:** `.streamlit/config.toml` aplica tema escuro e `app/web.py` usa
CSS complementar responsivo com foco visível. Nenhuma dependência foi adicionada
e os contratos de `app/runner.py`, `app/validation.py` e `app/storage.py` não
foram alterados.

**Fora de escopo:** estatísticas esportivas, histórico fictício, progresso
percentual sem fonte, mudanças em YOLO/tracking e reconstrução do pipeline.

## Baseline YOLO autorizado — 11/11/2026

**Confirmado:** o usuário autorizou a criação de um baseline para substituir a
lacuna do pipeline original e autorizou o download das dependências e do peso.
Foi criado `run.py` com o contrato `VIDEO --out SAIDA --model MODELO --device`,
mantendo CPU como padrão e o subprocesso isolado da interface.

**Confirmado:** `requirements.txt` inclui `ultralytics==8.4.211`. O ambiente
resolveu Ultralytics 8.4.211 e PyTorch 2.15.0+cpu; `torch.cuda.is_available()`
retornou `False`. O peso `models/yolov8n.pt` foi baixado localmente, possui
6.549.796 bytes e SHA-256
`F59B3D833E2FF32E194B5BB8E08D211DC7C5BDF144B90D2C8412C47CCFC83B36`.
O arquivo é ignorado pelo Git e não faz parte do código versionado.

**Confirmado:** a CLI filtra as classes `person` e `sports ball`, processa quadro
a quadro, recusa sobrescrita e remove saída parcial após falha. O upload manual de
modelo continua disponível; quando nenhum modelo personalizado é enviado, a UI
usa o peso padrão local e o copia para a área controlada da sessão.

**Confirmado:** RF-003–005, RNF-002/003/005/006/008, CA-003/007/008 e BL-017
foram cobertos por inspeção, testes com mocks e smoke sintético. A suíte concluiu
com `21 passed in 6.55s`; Ruff retornou `All checks passed!`. Um smoke real em CPU
processou dois quadros, retornou código 0 e gerou MP4 de 2.540 bytes legível pelo
OpenCV.

**Informado/não verificado:** a precisão do YOLOv8n no vídeo real, a detecção da
bola pequena, o tempo total no hardware-alvo e a reprodução do resultado real no
navegador. O vídeo do usuário não foi processado automaticamente.

**Fora de escopo:** o baseline não implementa tracking, identidade persistente,
ações esportivas, rallies, placar, estatísticas ou reconstrução 3D.

