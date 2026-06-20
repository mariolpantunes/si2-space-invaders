import matplotlib.pyplot as plt
import re
import os


def parse_neat_log(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        content = f.read()

    avg_fitness = [
        float(x)
        for x in re.findall(r"Population's average fitness: ([\d\.-]+)", content)
    ]
    best_matches = re.findall(
        r"Best fitness: ([\d\.-]+) - size: \((\d+), (\d+)\)", content
    )

    max_fitness = [float(m[0]) for m in best_matches]
    complexity = [int(m[2]) for m in best_matches]
    generations = [i + 1 for i in range(len(avg_fitness))]

    return {
        "gen": generations,
        "max": max_fitness,
        "avg": avg_fitness,
        "complexity": complexity,
    }


def plot_individual_fitness(data, title, filename, color):
    plt.figure(figsize=(10, 5))
    plt.plot(data["gen"], data["max"], label="Fitness Máximo", color=color, linewidth=2)
    plt.plot(
        data["gen"],
        data["avg"],
        label="Fitness Médio",
        color=color,
        linestyle="--",
        alpha=0.5,
    )
    plt.title(f"Convergência de Treino: {title}", fontsize=14)
    plt.xlabel("Geração", fontsize=12)
    plt.ylabel("Fitness (Reward)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def plot_complexity_comparison(my_data, peer_data):
    plt.figure(figsize=(10, 5))
    if my_data:
        plt.plot(
            my_data["gen"],
            my_data["complexity"],
            label="Modelo (11 inputs, Linear)",
            color="blue",
        )
    if peer_data:
        plt.plot(
            peer_data["gen"],
            peer_data["complexity"],
            label="Modelo (2 inputs, Hidden)",
            color="red",
        )

    plt.title("Eficiência Estrutural: Conexões Neurais ao longo do tempo", fontsize=14)
    plt.xlabel("Geração", fontsize=12)
    plt.ylabel("Nº de Conexões (Complexidade)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


if __name__ == "__main__":
    my_model = parse_neat_log("main_fitness_evolution.txt")
    peer_model = parse_neat_log("mini_fitness_evolution.txt")

    # 1. Gráfico do teu Modelo (Main)
    if my_model:
        plot_individual_fitness(
            my_model, "Modelo sem camada escondida", "0 hidden layers", "blue"
        )

    # 2. Gráfico do Modelo do Colega (Mini)
    if peer_model:
        plot_individual_fitness(
            peer_model, "Modelo com camada escondida", "1x6 hidden layer", "red"
        )

    # 3. Gráfico de Complexidade (Este sim, faz sentido comparar juntos)
    plot_complexity_comparison(my_model, peer_model)

    plt.show()
