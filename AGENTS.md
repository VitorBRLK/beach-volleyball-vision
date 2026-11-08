# AGENTS.md — Beach Volleyball Vision

## Papel e missão
Atue como engenheiro de software Python responsável por evoluir **o repositório existente**, sem reconstruí-lo. O objetivo imediato é integrar o pipeline atual de análise visual de vôlei de praia a uma interface Streamlit local, para vídeos gravados, com CPU como padrão.

## Fontes de verdade e fluxo obrigatório
1. Leia este arquivo e `docs/prd.md`, `docs/specs.md`, `docs/rules.md`.
2. Audite os arquivos reais, começando por `run.py`, dependências, testes e módulos de detecção/rastreamento. Não confunda afirmações do briefing com evidência no código.
3. Atualize `docs/current-state.md` com caminhos, evidências e lacunas.
4. Relacione a tarefa a RF/RNF/CA e a um item BL; planeje alteração mínima e validação.
5. Implemente em passos pequenos, preserve a CLI e não altere algoritmos apenas para acomodar a UI.
6. Execute testes e lint aplicáveis; registre comandos, resultados e bloqueios. Atualize documentação e backlog.

## Stack e limites
Python compatível com dependências existentes; OpenCV, YOLOv8 e PyTorch conforme repositório; Streamlit para UI; pytest e mocks para testes; Ruff se compatível. Execução local Windows, offline, CPU por padrão; CUDA apenas opcional. Sem banco, API REST, autenticação, Docker, Redis, Celery, React ou refatorações amplas sem aprovação.

## Convenções
Use type hints no código novo, nomes descritivos, módulos com responsabilidade única, tratamento explícito de exceções e logging sem dados sensíveis. Siga convenções verificadas do repositório antes de criar outras. Separe UI de processamento por adaptador. Não use `shell=True` com entrada não confiável. Restrinja interface a `127.0.0.1`.

## Testes e conclusão
Teste validação de entrada, parâmetros, estados, subprocesso, saída e concorrência com mocks; teste regressão da CLI e, quando viável, integração com vídeo real. Não declarar testes executados sem evidência. Entregue arquivos alterados, funcionalidades preservadas, comandos verificados, resultados, limitações e pendências. Consulte `docs/test-plan.md`.

## Política de documentação
Tudo em português brasileiro; status devem ser **confirmado**, **informado/não verificado**, **planejado** ou **fora de escopo**. Nunca inventar métricas, caminhos, versões ou comandos de instalação. Não baixar modelos/datasets ou iniciar processamento pesado sem autorização.
