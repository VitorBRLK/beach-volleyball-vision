# Segurança e privacidade local

## Superfície
Ferramenta local, sem autenticação no MVP. Configurar Streamlit para escutar apenas `127.0.0.1`; não abrir portas externas nem expor à LAN por padrão.

## Entrada e caminhos
Validar extensão, conteúdo legível, tamanho e espaço disponível. Tratar nomes de upload como dados não confiáveis; gerar nome próprio e usar diretórios controlados; normalizar/resolver caminhos e impedir path traversal/sobrescrita de arquivos arbitrários. Preservar vídeo original.

## Processos
Usar `subprocess` com lista de argumentos, `shell=False`, executável conhecido e diretório de trabalho controlado. Não aceitar parâmetros livres para executar comandos. Capturar falhas e evitar processos órfãos.

## Modelos e dependências
Carregar apenas modelos de origem confiável; pesos serializados podem representar risco. Não baixar pesos automaticamente. Fixar versões compatíveis após auditoria, revisar dependências e manter ambiente virtual.

## Dados, logs e limpeza
Evitar dados pessoais em logs; não expor caminhos completos sem necessidade; criar nomes únicos; impor limites de upload/armazenamento compatíveis com espaço disponível; limpar temporários com cautela, nunca remover saída em uso. Tratar erros sem vazar stack trace na interface.

## Validação
Testar traversal, arquivo inválido, modelo não confiável/ausente, upload excessivo, colisões de nomes e concorrência.
