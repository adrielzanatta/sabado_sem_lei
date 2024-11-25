import pandas as pd

lista_jogos_df = pd.read_csv(
    "assets/historico-completo-jogos.csv",
    encoding="UTF-8",
    sep=";",
    engine="python",
)

# Consolidar votos destaques
lista_jogos_df["Destaques"] = (lista_jogos_df["Votos Destaque"] >= 3).astype(int)
