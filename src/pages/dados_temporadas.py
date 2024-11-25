import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
import dash_ag_grid as dag
from dfs.lista_jogos import lista_jogos_df

dash.register_page(__name__, name="Dados da Temporada", order=2)


# Tratamento de dados
df = lista_jogos_df

# Gols na Temporada
df_temporadas_resumo = df.groupby("Ano")[["Gols"]].sum()
df_temporadas_resumo = df_temporadas_resumo.rename(columns={"Gols": "Total de Gols"})
df_max_gols = df.groupby(["Ano", "Rodada"])[["Gols"]].sum()
df_temporadas_resumo["Máximo de Gols"] = df_max_gols.groupby("Ano")[["Gols"]].max()
df_temporadas_resumo["Média de Gols"] = (
    df_max_gols.groupby("Ano")[["Gols"]].mean().map("{:,.1f}".format)
)

# Partidas Jogadas na Temporada
df_temporadas_resumo["Partidas Jogadas"] = df.groupby("Ano")[["Rodada"]].max()

# Número de Jogadores na Temporada
df_temporadas_resumo["Número de Atletas"] = df.groupby("Ano")[["Jogador"]].nunique()

# Aproveitamento Escalador
df_escalador = df.loc[df["Escalador"] == df["Jogador"]]
df_temporadas_resumo["Aproveitamento Escalador"] = (
    df_escalador.groupby("Ano")["Pontos"].sum()
    / (df_escalador.groupby("Ano")["Pontos"].count() * 3)
).map("{:,.1%}".format)

# Chocolate >3, Clutch 1, Empate
df_resultados = df.groupby(["Ano", "Rodada", "Time"])[["Gols"]].sum().reset_index()
df_resultados = df_resultados.pivot_table(
    "Gols", ["Ano", "Rodada"], "Time"
).reset_index()
df_resultados["Resultado"] = abs(df_resultados[1] - df_resultados[2])
df_resultados[">=3"] = df_resultados["Resultado"] >= 3
df_resultados["=2"] = df_resultados["Resultado"] == 2
df_resultados["=1"] = df_resultados["Resultado"] == 1
df_resultados["=0"] = df_resultados["Resultado"] == 0
df_temporadas_resumo["Chocolate >= 3"] = df_resultados.groupby("Ano")[[">=3"]].sum()
df_temporadas_resumo["Parelho = 2"] = df_resultados.groupby("Ano")[["=2"]].sum()
df_temporadas_resumo["Clutch = 1"] = df_resultados.groupby("Ano")[["=1"]].sum()
df_temporadas_resumo["Empate"] = df_resultados.groupby("Ano")[["=0"]].sum()

# Maior Número de Gols Por Um Jogador em Uma Partida
df_maior_numero_gols = df.groupby(["Ano", "Jogador"])["Gols"].max().reset_index()
df_maior_numero_gols = df_maior_numero_gols.loc[
    df_maior_numero_gols.groupby("Ano")["Gols"].idxmax()
]
df_temporadas_resumo["Mais Gols Marcados #"] = df_maior_numero_gols.groupby("Ano")[
    "Gols"
].max()
df_temporadas_resumo["Mais Gols Marcados"] = df_maior_numero_gols.groupby("Ano")[
    "Jogador"
].max()


# Maior Sequência de Vitórias
max_consecutive_wins = lambda x: x.loc[x.eq(3)].groupby(x.ne(3).cumsum()).size().max()
df_seq_vit = df.groupby(["Ano", "Jogador"], as_index=False)["Pontos"].agg(
    max_consecutive_wins
)
df_seq_vit = df_seq_vit.loc[df_seq_vit.groupby("Ano")["Pontos"].idxmax()]
df_temporadas_resumo["Sequência de Vitórias #"] = df_seq_vit.groupby("Ano")[
    "Pontos"
].max()
df_temporadas_resumo["Sequência de Vitórias"] = df_seq_vit.groupby("Ano")[
    "Jogador"
].max()

# Maior Sequência de Derrotas
max_consecutive_losses = lambda x: x.loc[x.eq(0)].groupby(x.ne(0).cumsum()).size().max()
df_seq_der = df.groupby(["Ano", "Jogador"], as_index=False)["Pontos"].agg(
    max_consecutive_losses
)
df_seq_der = df_seq_der.loc[df_seq_der.groupby("Ano")["Pontos"].idxmax()]
df_temporadas_resumo["Sequência de Derrotas #"] = df_seq_der.groupby("Ano")[
    "Pontos"
].max()
df_temporadas_resumo["Sequência de Derrotas"] = df_seq_der.groupby("Ano")[
    "Jogador"
].max()

# Tratamento para AgGrid
df_temporadas_resumo = df_temporadas_resumo.sort_values(by=["Ano"], ascending=False)
df_temporadas_resumo = df_temporadas_resumo.T.reset_index()

layout = dbc.Container(
    [
        html.H2("Dados da Temporada"),
        dag.AgGrid(
            id="tabela_dados_temporadas",
            defaultColDef={"sortable": True, "rezisable": True},
            columnDefs=[
                {
                    "field": "index",
                    "headerName": "Estatísticas",
                    "width": 400,
                    "rowDrag": True,
                },
                {"field": "2024"},
                {"field": "2023"},
                {"field": "2022"},
                {"field": "2021"},
                {"field": "2018"},
                {"field": "2017"},
                {"field": "2016"},
                {"field": "2015"},
                {"field": "2014"},
            ],
            rowData=df_temporadas_resumo.to_dict("records"),
            dashGridOptions={"rowDragManaged": True, "animateRows": True},
            columnSize="sizeToFit",
            style={"height": 800},
        ),
    ],
    fluid=True,
)
