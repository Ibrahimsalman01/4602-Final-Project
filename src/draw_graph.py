import os
import itertools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

movies_df = pd.read_csv(os.path.join(DATA_DIR, "movies.csv"))
cast_df = pd.read_csv(os.path.join(DATA_DIR, "cast.csv"))

# merge cast and movie data
merged_df = cast_df.merge(
    movies_df[["movie_id", "decade", "genre"]],
    on="movie_id"
)


# set color for genres
genre_colors = {
    "Action": "red",
    "Drama": "blue",
    "Comedy": "green"
}


# build one graph per decade
for decade in sorted(merged_df["decade"].unique()):
    decade_df = merged_df[merged_df["decade"] == decade]


    # give each actor a main genre
    actor_genre_counts = defaultdict(list)

    for _, row in decade_df.iterrows():
        actor_genre_counts[row["actor_name"]].append(row["genre"])

    actor_main_genre = {}
    for actor, genres in actor_genre_counts.items():
        actor_main_genre[actor] = Counter(genres).most_common(1)[0][0]


    # build graph
    G = nx.Graph()

    for movie_id, group in decade_df.groupby("movie_id"):
        actors = group["actor_name"].drop_duplicates().tolist()

        for a, b in itertools.combinations(actors, 2):
            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)

    nx.set_node_attributes(G, actor_main_genre, "main_genre")

    print(f"\n=== {decade}s ===")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Connected components:", nx.number_connected_components(G))


    try:
        # Attribute Assortativity
        genre_assort = nx.attribute_assortativity_coefficient(G, "main_genre")
        print(f"Genre Assortativity: {genre_assort:.4f}")
        
        # Degree Assortativity
        degree_assort = nx.degree_assortativity_coefficient(G)
        print(f"Degree Assortativity: {degree_assort:.4f}")
    except Exception as e:
        print(f"Assortativity calculation failed: {e}")


    # give node color by main genre
    node_colors = []
    for node in G.nodes():
        main_genre = actor_main_genre[node]
        node_colors.append(genre_colors[main_genre])


    # give edge widths by weight
    edge_widths = [G[u][v]["weight"] * 1.5 for u, v in G.edges()]


    # draw graph
    plt.figure(figsize=(12, 9))
    pos = nx.spring_layout(G, seed=42, k=0.3)

    nx.draw_networkx_edges(
        G,
        pos,
        width=edge_widths,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors,
        node_size=500
    )

    # # label node with actors name
    # labels = {node: node for node in G.nodes()}

    # nx.draw_networkx_labels(
    #     G,
    #     pos,
    #     labels=labels,
    #     font_size=8
    # )

    # legend
    for genre, color in genre_colors.items():
        plt.scatter([], [], c=color, label=genre)
    plt.legend(title="Main Genre")

    plt.title(f"Actor Collaboration Network ({decade}s)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, f"{int(decade)}s_actor_network_by_genre.png"),
        dpi=300
    )
    plt.show()