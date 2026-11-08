# PRD — Beach Volleyball Vision / MVP web local

## Resumo executivo
Evoluir, sem reconstruir, um protótipo de análise de vídeos de vôlei de praia para uma ferramenta local de processamento e visualização. Este documento registra requisitos; evidências de implementação e bloqueios ficam em `current-state.md`.

## Problema, público e contexto
Um desenvolvedor precisa executar um pipeline de visão computacional em vídeos gravados, com câmera fixa e quadra inteira, sem depender exclusivamente da linha de comando. Uso individual e experimental no Windows (Core i3, 16 GB RAM, 250 GB; GPU desconhecida).

## Objetivos
Operação via navegador local; reaproveitar CLI/pipeline; processar offline em CPU; exibir resultado e falhas; impedir concorrência. Métrica de sucesso: completar fluxo de ponta a ponta com vídeo real no hardware-alvo, sem regressão na CLI; tempo e consumo serão medidos, não presumidos.

## Não objetivos
Reconhecimento de saque/recepção/ataque, rallies/pontos, placar, estatísticas, reconstrução 3D, API, banco, autenticação, cloud ou processamento em tempo real.

## Estado atual e ressalvas
O briefing relata leitura OpenCV, YOLOv8 para pessoa/bola, IDs temporários, marcações e vídeo opcional. Relata classes de ações/rallies/posições sem integração. **Status de tudo isso: não verificado.** Consultar `current-state.md`.

## Jornada
Abrir navegador local → escolher arquivo → validar vídeo/modelo → selecionar CPU → iniciar → acompanhar estado → receber resultado/erro → reproduzir e acessar vídeo gerado.

## Requisitos funcionais
| ID | Requisito | Estado |
|---|---|---|
| RF-001 | Selecionar vídeo local | Confirmado no código; execução não verificada |
| RF-002 | Validar entrada e informar erro legível | Confirmado no código; teste não verificado |
| RF-003 | Configurar modelo YOLO disponível | Confirmado no código; YOLO não verificado |
| RF-004 | Selecionar dispositivo com CPU padrão | Confirmado no código; execução não verificada |
| RF-005 | Iniciar pipeline existente via adaptador | Confirmado no código; pipeline não verificado |
| RF-006 | Mostrar idle/running/completed/failed | Confirmado no código; teste não verificado |
| RF-007 | Reproduzir vídeo anotado compatível com navegador | Confirmado no código; navegador não verificado |
| RF-008 | Disponibilizar arquivo de saída | Confirmado no código; teste não verificado |
| RF-009 | Impedir execuções simultâneas | Confirmado no código; teste não verificado |
| RF-010 | Mostrar informações básicas verificáveis da execução | Confirmado no código; execução não verificada |
| RF-011 | Preservar a CLI existente | Informado/não verificado: CLI ausente |
| RF-012 | Reconhecer ações e gerar estatísticas | Fora de escopo |

## Requisitos não funcionais
| ID | Requisito | Estado |
|---|---|---|
| RNF-001 | Executar localmente no Windows | Código confirmado; execução não verificada |
| RNF-002 | CPU padrão, GPU não obrigatória | Confirmado no código; execução não verificada |
| RNF-003 | Não carregar vídeo inteiro na RAM | Cópia em blocos confirmada; Streamlit não verificado |
| RNF-004 | UI acessível apenas em 127.0.0.1 por padrão | Confirmado na configuração; smoke não verificado |
| RNF-005 | Isolar UI de processamento | Confirmado no código |
| RNF-006 | Preservar original e limpar temporários com segurança | Confirmado no código; teste não verificado |
| RNF-007 | Logging e erros observáveis | Confirmado no código; execução não verificada |
| RNF-008 | Testes automatizados sem inferência pesada por padrão | Confirmado no código; execução não verificada |

## Regras de negócio
Um processamento por vez; nunca sobrescrever entrada; não tratar IDs temporários como identidade; não exibir estatísticas não calculadas; falha não pode ser exibida como sucesso; configuração do modelo deve apontar para recurso permitido.

## Critérios de aceite
| ID | Critério | Vinculação |
|---|---|---|
| CA-001 | UI abre localmente no Windows | RF-001, RNF-001 |
| CA-002 | Arquivo inválido gera mensagem e não executa pipeline | RF-002 |
| CA-003 | Vídeo válido processa via CPU com modelo configurado | RF-003–005 |
| CA-004 | Estados e erros correspondem à execução real | RF-006 |
| CA-005 | Vídeo gerado pode ser reproduzido e acessado | RF-007–008 |
| CA-006 | Segunda execução é bloqueada durante a primeira | RF-009 |
| CA-007 | CLI existente continua operante | RF-011 |
| CA-008 | Testes relevantes passam; bloqueios são registrados | RNF-008 |

## Riscos e dependências
Compatibilidade Streamlit/Python, codec, modelo YOLO, subprocessos Windows, consumo de disco, CPU lenta, bugs pré-existentes e ausência de vídeos de teste. Depende de acesso ao repositório, ambiente e vídeo autorizado.

## Futuro
Melhorar detecções/tracking; calibrar quadra e interpretar ações; somente depois considerar estatísticas e relatórios. Nada disso integra o MVP aprovado.
