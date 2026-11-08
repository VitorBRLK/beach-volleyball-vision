# Estratégia de desempenho

## Hardware de referência informado
Windows; Intel Core i3 (geração desconhecida); 16 GB RAM; disco 250 GB (livre desconhecido); GPU dedicada não confirmada. CPU é o padrão. **Nenhum benchmark foi executado.**

## Linha de base a medir
Versões de Python/PyTorch/OpenCV/YOLO; resolução, FPS e duração do vídeo; tamanho de entrada/saída; tempo de carregamento do modelo; tempo total; quadros processados por segundo; uso máximo de RAM, CPU e disco. Registrar máquina, modelo e configurações para comparação.

## Estratégia incremental
1. Executar vídeo curto e medir baseline no hardware real.
2. Garantir leitura em streaming por frame e uma execução por vez.
3. Inspecionar gargalos de inferência, gravação e codec.
4. Avaliar resolução, frequência de inferência e modelo menor **somente** comparando qualidade de detecção e custo.
5. Repetir medições com o mesmo vídeo e configuração; registrar trade-offs.

Não prometer tempo real ou velocidade sem evidência. Não sacrificar precisão sem avaliação, especialmente da bola pequena.
