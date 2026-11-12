# Arquitetura

## Atual

**Confirmado:** a camada Streamlit, o adaptador e uma CLI baseline em `run.py`
estão implementados. **Informado/não verificado:** o pipeline original descrito
no briefing não foi fornecido. O baseline autorizado detecta pessoa/bola, mas não
recria tracking nem interpretação esportiva.

## MVP implementado na camada de integração
```text
Navegador (127.0.0.1)
       |
Streamlit (seleção, validação, estados, resultado)
       |
Adaptador de execução (parâmetros, lock, subprocesso, logs)
       |
CLI baseline run.py (Ultralytics/OpenCV; CPU padrão)
       |
Arquivo de vídeo anotado + metadados medidos
```

## Responsabilidades
- UI: formulário, mensagens, estado e reprodução; sem inferência.
- Adaptador: comando seguro, gerenciamento do processo, resultado e exclusão mútua.
- Pipeline: permanece responsável por leitura, detecção, tracking e gravação.
- Armazenamento: arquivos locais de entrada, saída e temporários, com nomes únicos.

## Decisões e trade-offs
Adaptador via subprocesso reduz acoplamento e risco de regressão, mas requer tratamento de logs/erros e sincronização com reruns. Integração por import direto só se auditoria mostrar API interna estável e vantagens claras. Streamlit dispensa frontend separado e REST, mas exige cuidado com estado e operações longas.

## Evolução
Separar componentes apenas quando necessidade real surgir; futuras fases de tracking e estatísticas não justificam arquitetura distribuída agora. A estrutura de pastas sugerida no prompt não deve ser imposta ao repositório existente.

## Baseline autorizado em 11/11/2026

**Confirmado:** após autorização explícita, foi adicionado um baseline em `run.py`
que implementa o contrato já consumido por `app/runner.py`. A CLI carrega um peso
Ultralytics, seleciona classes de pessoa/bola, processa o vídeo quadro a quadro e
publica a saída somente depois de concluir um MP4 temporário válido.

```text
Streamlit -> app/runner.py -> subprocesso run.py
                              |-> Ultralytics / PyTorch CPU
                              |-> OpenCV VideoCapture/VideoWriter
                              `-> MP4 anotado
```

**Confirmado:** a UI continua sem chamar inferência diretamente. O peso padrão
`models/yolov8n.pt` é local, ignorado pelo Git e copiado para a área controlada de
sessão antes de o adaptador executar a CLI.

**Fora de escopo:** tracking, identidade de atletas, interpretação de ações,
rallies, placar e estatísticas.
