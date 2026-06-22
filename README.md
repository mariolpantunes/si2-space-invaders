# <img src="server/viewer/favicon.svg" alt="logo" width="128" height="128" align="middle"> SI2 - Space Invaders

# Agente Inteligente para Space Invaders (NEAT)

Este repositório contém a implementação de um agente autónomo para o jogo Space Invaders, desenvolvido para a unidade curricular de Sistemas Inteligentes II. O agente utiliza Neuroevolução (**NEAT**) para dominar o jogo através de sensores customizados e uma função de fitness evolutiva.

## 1. Instruções de Execução

### Pré-requisitos

- Python 3.10+
- `pip install -r requirements.txt` (inclui `neat-python`, `numpy` e `matplotlib`)

### Como correr o agente

1. Iniciar o servidor:

   ```bash
   python3 -m server.server
   ```

2. Num novo terminal, carregar o modelo treinado:

   ```bash
   python3 -m agents.ml_agent
   ```

*Nota: O agente carrega por defeito o ficheiro `winner.pkl` na raiz do projeto.*

---

Durante o desenvolvimento, testámos duas filosofias de design distintas para o cérebro do agente:

### Modelo A: Engenharia de Features (A Nossa Solução Final)

- **Topologia:** 11 inputs, 4 outputs (Oeste, Este, Disparar, Idle), **0 camadas escondidas**.
- **Inputs (11):** Coordenadas X/Y da nave e lasers; Sensor de Cooldown (disponibilidade de tiro); Ameaça prioritária (alien em *dive* mais baixo); Alvo tático (alien estático mais próximo); Densidade lateral de inimigos.
- **Justificação:** Ao "mastigar" os dados para a IA (ex: focar no perigo iminente), permitimos que uma rede linear simples atingisse performance máxima com custo computacional mínimo.

### Modelo B: Complexidade Arquitetural (Modelo de Comparação)

- **Topologia:** 2 inputs, 4 outputs, **1 camada escondida com 6 neurónios**.
- **Inputs (2):** Distância relativa em X entre o alien e a nave ($alien\_x - player\_x$) e a coordenada Y do alien.
- **Filosofia:** Fornecer dados brutos e deixar que a camada escondida descubra as correlações lógicas (como a necessidade de disparar apenas quando alinhado).

---

## 3. Funções de Recompensa (Reward Shaping)

A evolução do agente A foi dividida em fases de **Fine-Tuning**, onde cada nova versão partia do "campeão" da fase anterior, enquanto que o modelo B, 

### Fase 0: Modelo Base (`winner_goated_behaviour.pkl`)

O treino inicial focou-se na sobrevivência básica com a função:
$$Fitness = (Score \times 10) + (Steps \times 0.5) - (VidasPerdidas \times 500)$$

- **Resultado:** O agente aprendeu a caçar aliens em *dive*.
- **Problema:** O comportamento era passivo. O agente encostava-se ao lado esquerdo quando o ecrã estava seguro, tornando-se vulnerável a ataques vindos do lado oposto.

### Fase 1: Paradigma "Speedrun"

Para aumentar a agressividade, mudámos a recompensa de tempo por uma penalização. O objetivo passou a ser limpar a ronda o mais rápido possível.
$$Fitness = (Score \times 10) - (Steps \times k) - (VidasPerdidas \times 500)$$

- Foram testados dois coeficientes: $k=0.75$ e $k=1.0$ (denominados `winner_k_vi.pkl`, sendo $i$ a versão/fase de desenvolvimento).
- **Resultado:** O agente tornou-se muito mais decisivo nos disparos para "parar o cronómetro".

### Fase 2: Modo Caçador e Robustez

Introduzimos o bónus por alinhamento com aliens estáticos quando não havia ameaças imediatas e aumentámos o limite de treino para 6000 steps.

- **Objetivo:** Garantir que o agente caça ativamente a "nuvem" de aliens para evitar que estes cheguem a iniciar o modo *dive*.

### Fase 3: Reforço de Prioridades e o Problema do *Jitter*

Aumentámos a recompensa de alinhamento ($0.4$ para alvos em *dive* e $1.0$ para estáticos).

- **Problema Detetado:** O modelo de $k=0.75$ começou a "tremer" (oscilação esquerda-direita). Sendo o movimento da nave discreto (inteiros) e o dos aliens contínuo (floats), a IA tentava alinhar-se com casas decimais impossíveis de atingir.

### Fase 4: Discretização e Modelo Final

Aplicámos a função `round()` na posição X dos aliens para o cálculo de distância na função de fitness.

- **Efeito:** O alinhamento passou a ser considerado perfeito assim que o agente entra no mesmo "bloco" que o alien.
- **Resultado Final:** Eliminação total do tremor, movimentos fluidos e performance imbatível.

### Componentes Dinâmicas

- **Anti-Camping (Mapa de Calor):** Registo de permanência em cada bloco X. Se o agente passar >45% do tempo num único bloco, o fitness total sofre uma penalização de 90%.
- **Modos de Prioridade:**
  - **Evasão:** Bónus por distância de aliens em *dive* que estejam abaixo de $Y=4.0$.
  - **Caçador:** Recompensa de alinhamento com aliens estáticos ($1.0$ por frame) quando não existem ameaças imediatas.

---

## 4. Avaliação de Performance

### Resultados Obtidos

- **Pontuação Máxima:** 50.000+ pontos.
- **Consistência:** O agente é capaz de sobreviver a centenas de *waves* consecutivas sem perder vidas, demonstrando uma gestão perfeita de *cooldown* e reflexos preventivos contra ataques diagonais.

### Estudo de Convergência

*(Podes inserir aqui os gráficos gerados pelo script: fitness_meu_modelo.png e comparativo_complexidade.png)*

1. **Convergência:** O modelo atingiu o patamar de estabilidade por volta da geração 80, onde a média da população se aproximou do fitness máximo.
2. **Eficiência Estrutural:** Ao longo das 100 gerações, observou-se uma redução no número de conexões neurais, provando que o agente aprendeu a ignorar inputs ruidosos e focou-se apenas na lógica crítica de sobrevivência.

### Comparação de Abordagens

Comparou-se a solução linear (11 inputs) com uma solução de camadas escondidas (2 inputs). A solução linear provou ser mais robusta, atingindo pontuações superiores e movimentos mais fluidos, enquanto a rede com camadas escondidas apresentou maior dificuldade em gerir o cooldown da arma e situações de RNG múltiplo.
