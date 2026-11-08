# Arquitetura

## Atual

**Confirmado:** a camada Streamlit e o adaptador estão implementados. **Informado/não
verificado:** a CLI `run.py` e todo o pipeline de visão estão ausentes do material
recebido. O fluxo interno de detecção/tracking continua sendo apenas um relato do
briefing e não foi recriado.

## MVP implementado na camada de integração
```text
Navegador (127.0.0.1)
       |
Streamlit (seleção, validação, estados, resultado)
       |
Adaptador de execução (parâmetros, lock, subprocesso, logs)
       |
CLI esperada run.py (pipeline de visão ausente no material atual)
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
