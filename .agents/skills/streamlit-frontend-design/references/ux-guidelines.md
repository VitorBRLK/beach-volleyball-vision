# UX Guidelines — Beach Volleyball Vision

## Usuário e contexto
Uso individual, local, experimental, no Windows, com vídeos gravados de vôlei de praia. CPU é o padrão; GPU CUDA é opcional e deve ser validada. O pipeline real `run.py` não está presente no estado documentado.

## Jornada principal
1. Abrir a aplicação local.
2. Escolher um vídeo gravado.
3. Selecionar um modelo local válido.
4. Confirmar dispositivo (CPU padrão).
5. Iniciar execução quando os pré-requisitos estiverem disponíveis.
6. Acompanhar o estado real e mensagens de erro.
7. Reproduzir ou baixar a saída real, se gerada.

## Estados da interface
| Estado | Apresentação | Ações |
|---|---|---|
| `idle` | Instrução para selecionar vídeo e modelo | Permitir configuração |
| `running` | Mensagem de processamento sem percentual inventado | Bloquear segunda execução |
| `completed` | Mensagem de sucesso somente com arquivo de saída verificado | Reproduzir/baixar se possível |
| `failed` | Erro legível e orientação para correção | Permitir nova tentativa quando seguro |

## Casos de erro obrigatórios
- Nenhum vídeo ou modelo selecionado.
- Extensão/conteúdo inválido.
- Modelo inválido ou ausente.
- CLI `run.py` ausente.
- Falha ao iniciar subprocesso.
- Código de retorno diferente de zero.
- Saída inexistente, vazia ou incompatível.
- Falta de espaço ou erro de gravação.
- Outra execução em andamento.

## Acessibilidade
- Rótulos persistentes em campos e botões.
- Ordem lógica de tabulação e foco visível.
- Mensagens de estado textuais; não usar apenas cor/ícone.
- Contraste mínimo WCAG AA como meta.
- Botões desabilitados com explicação do motivo quando viável.
- Layout utilizável em larguras menores, sem corte de formulários.
- Evitar animações não essenciais e barras de progresso falsas.

## Segurança e confiança
- Não sobrescrever originais nem expor caminhos privados.
- Não carregar automaticamente modelos externos.
- Não apresentar IDs de tracking como identificação nominal de pessoas.
- Não exibir estatísticas esportivas que o pipeline não calculou.
- Identificar claramente qualquer mock, ilustração ou protótipo como demonstração.

## Testes de aceite recomendados
1. Abrir aplicação no endereço local configurado.
2. Validar upload ausente, arquivo inválido e modelo inválido.
3. Verificar que CPU é o padrão.
4. Simular sucesso/falha do adaptador com mocks, sem inferência pesada.
5. Verificar bloqueio de execução simultânea.
6. Confirmar que sucesso e download exigem saída real válida.
7. Verificar mensagens, foco por teclado e layout em viewport estreita.
8. Executar pytest e Ruff no ambiente disponível; registrar resultados e bloqueios.

## Relação com documentação existente
Esta referência complementa `docs/ux-guidelines.md`; não a substitui. Em caso de conflito, siga `AGENTS.md`, requisitos aprovados e comportamento comprovado no código.
