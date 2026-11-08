# Diretrizes de UX/UI

## Princípios
Desktop-first, simples, funcional, legível e responsivo dentro do Streamlit. Não mostrar indicadores esportivos fictícios. Exibir informações técnicas verificáveis e mensagens em português brasileiro.

## Estrutura de tela
1. **Configuração:** vídeo, modelo, dispositivo (`CPU` selecionado), iniciar.
2. **Processamento:** status, mensagens, tempo decorrido somente quando medido; botão desabilitado durante execução.
3. **Resultado:** vídeo anotado, informações de arquivo, acesso à saída.

## Estados e microcopy
- Idle: “Selecione um vídeo para começar.”
- Running: “Processando vídeo. Isso pode levar algum tempo neste computador.”
- Completed: “Processamento concluído. Confira o vídeo gerado.” (somente após verificar saída)
- Failed: “Não foi possível concluir o processamento.” + motivo seguro e orientação.

## Acessibilidade e feedback
Labels explícitos, contraste, mensagens textuais além de cor, indicação de ação indisponível, erros junto ao campo relevante e layout que não dependa de animações. Não apresentar IDs temporários como nomes de atletas. Se codec não for reproduzível no navegador, informar e disponibilizar arquivo.
