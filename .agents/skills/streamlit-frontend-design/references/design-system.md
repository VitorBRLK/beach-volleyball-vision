# Design System — Beach Volleyball Vision

## Direção visual
Interface de análise esportiva profissional, escura, limpa e funcional. A prioridade é o vídeo e o estado real do processamento. A identidade deve sugerir tecnologia e esporte sem efeitos visuais excessivos.

## Tokens sugeridos (proposta, não implementação confirmada)
| Token | Valor | Uso |
|---|---|---|
| `background` | `#0B111B` | Fundo geral |
| `surface` | `#151E2C` | Cards e painéis |
| `surface-raised` | `#1E2B3C` | Elementos destacados |
| `border` | `#2A3546` | Divisórias |
| `text-primary` | `#E8EEF7` | Texto principal |
| `text-secondary` | `#A7B7CA` | Texto auxiliar |
| `accent` | `#57E3AA` | Ações principais e foco |
| `warning` | `#FFC57C` | Avisos |
| `danger` | `#FF8791` | Erros |

Essas cores são ponto de partida: valide contraste WCAG AA (4.5:1 para texto normal e 3:1 para texto grande e elementos de interface relevantes) antes de aprovar.

## Tipografia e espaçamento
- Fonte: família sans-serif do sistema, com fallback seguro.
- Títulos de página: 24–30 px; seções: 16–20 px; corpo: 14–16 px; legenda: 12–14 px quando legível.
- Escala de espaçamento: 4, 8, 12, 16, 24, 32 px.
- Raio: 8 px em controles e 12 px em painéis.
- Evite textos informativos com menos de 12 px.

## Layout
- Desktop-first, mas com colunas que empilham em telas estreitas.
- Cabeçalho: nome do produto, título da seção e estado do ambiente.
- Navegação: poucas opções, com rótulos explícitos; não criar páginas vazias.
- Conteúdo principal: largura confortável e vídeo 16:9 quando possível.
- Espaço suficiente para erros, estados de execução e ações de download.

## Componentes
### Cabeçalho
Nome do produto, descrição curta e status real do pipeline. Nunca exibir `Online` se só a interface estiver funcionando.

### Card de configuração
Upload de vídeo, upload de pesos de modelo local e seleção de dispositivo. Rótulos, formatos aceitos e instruções claras. Validação deve permanecer no módulo existente.

### Painel de processamento
Exiba o estado real (`idle`, `running`, `completed`, `failed`) e mensagem textual. Só mostre barra de progresso percentual se o pipeline fornecer progresso mensurável; caso contrário, use indicador indeterminado.

### Player de resultado
Vídeo real produzido, metadados medidos e download condicional. Se o codec não for compatível, informe e ofereça o arquivo quando disponível.

### Avisos
Aviso para CLI ausente, vídeo inválido, modelo ausente, erro de execução, saída ausente e execução concorrente. Não dependa apenas da cor para comunicar estado.

## Streamlit
Prefira componentes nativos e configuração de tema em `.streamlit/config.toml`. Use CSS apenas para personalização complementar; evite seletores dependentes de estrutura interna não documentada. Não adicione bibliotecas UI sem demonstrar necessidade e compatibilidade.

## Conteúdo e microcopy
- Linguagem: português brasileiro, curta e objetiva.
- CTA principal: `Iniciar processamento`.
- Estado inicial: `Selecione um vídeo para começar.`
- Em execução: `Processando vídeo. Isso pode levar algum tempo neste computador.`
- Sucesso: `Processamento concluído. Confira o vídeo gerado.` somente após saída validada.
- Erro: `Não foi possível concluir o processamento.` seguido de orientação segura.
- Ausência de pipeline: `O pipeline de análise ainda não está disponível neste ambiente.`

## Não fazer
- Inventar heatmaps, placares, eventos, atletas, estatísticas ou histórico.
- Usar fotos ou vídeos de demonstração como se fossem resultados reais.
- Criar cartões decorativos sem função ou métricas sem fonte.
- Sacrificar acessibilidade por aparência.
