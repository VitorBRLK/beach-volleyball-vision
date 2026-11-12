# Especificações técnicas — MVP

## Princípio
O contrato do `run.py` baseline está confirmado. O pipeline original permanece
ausente e, se for fornecido, deverá ser auditado antes de substituir o baseline.
A interface reutiliza a CLI via adaptador e não duplica detecção.

## Entrada
Selecionar arquivo de vídeo local por interface Streamlit; validar extensão permitida e conteúdo legível (quando possível via OpenCV), tamanho e disponibilidade de espaço. Salvar upload em diretório de trabalho controlado com nome gerado, nunca confiar no nome original para caminho de destino. Não alterar arquivo fonte.

## Configuração
Modelo: opção disponível/validada localmente; não baixar automaticamente. Dispositivo: `cpu` padrão; `cuda` apenas se instalado e verificado. Argumentos da CLI devem ser conferidos antes de construir comando.

## Contrato UI ↔ adaptador (proposta)
Entrada: `input_path`, `output_path`, `model_path`, `device`. Saída: `status`, `output_path` quando existir, `elapsed_seconds` medido, mensagem de erro segura e log diagnóstico. Interface não chama diretamente inferência YOLO.

## Máquina de estados
`idle → running → completed | failed`; nova execução somente quando nenhuma está ativa. `completed` exige código de retorno bem-sucedido **e** arquivo de saída existente/legível. Reinicialização da UI não deve gerar execução duplicada. O estado deve refletir processo real, não apenas um botão.

## Subprocesso e concorrência
Construir lista de argumentos para `subprocess` com interpretador do ambiente; `shell=False`; `cwd` e caminhos absolutos controlados. Capturar retorno e stderr com limites seguros; manter controle de processo por sessão/instância e trava efetiva para impedir execução simultânea, inclusive após reruns do Streamlit. Tratar encerramento inesperado e processos órfãos no Windows. Política de cancelamento/timeout depende de decisão após auditoria; não adicionar estados desnecessários.

## Saída
Gerar nome único, preservar original, verificar tamanho/codec e oferecer reprodução com `st.video` se compatível; em caso de incompatibilidade, explicar e oferecer acesso ao arquivo. Exibir duração de execução apenas se medida. Limpar temporários sem apagar resultados enquanto em uso.

## Erros e logs
Distinguir vídeo inválido, modelo ausente, falha ao iniciar, código de retorno não zero, saída ausente, espaço insuficiente e execução concorrente. Mostrar mensagem amigável e registrar diagnóstico técnico sem expor caminhos privados desnecessários.

## Critérios de integração
CLI preservada; teste de comando com mock; integração com pipeline real apenas quando ambiente/modelo/vídeo estiverem disponíveis; teste manual de reprodução no Windows. Ver `test-plan.md`.
