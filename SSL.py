import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc


PRESENÇA_MINIMA = 1

lista_jogos_df = pd.read_csv(
    "./SSL_Jogos.csv", encoding="UTF-8", sep="\;", engine="python"
)

# Consolidar votos destaques
lista_jogos_df["Destaques"] = (lista_jogos_df["Destaques"] >= 3).astype(int)

# Dados únicos dos Jogos
num_jogos = lista_jogos_df["Rodada"].max()

# Dados individuais dos jogadores
jogadores_df = lista_jogos_df.groupby("Jogador")[["Pontos", "Gols", "Destaques"]].sum()

jogadores_df["Presença"] = (
    lista_jogos_df.groupby("Jogador")["Rodada"].count().astype(int)
)

jogadores_df["Presença%"] = ((jogadores_df["Presença"] / num_jogos) * 100).map(
    "{:,.1f}%".format
)

jogadores_df["Gols/Jogo"] = (jogadores_df["Gols"] / jogadores_df["Presença"]).astype(float)

jogadores_df["Aproveitamento%"] = (
    jogadores_df["Pontos"] / (jogadores_df["Presença"] * 3) * 100
).map("{:,.1f}%".format)

jogadores_df["Vitórias"] = (
    lista_jogos_df.loc[lista_jogos_df["Pontos"] == 3]
    .groupby("Jogador")["Pontos"]
    .size()
    .astype(int)
)

jogadores_df["Empates"] = (
    lista_jogos_df.loc[lista_jogos_df["Pontos"] == 1]
    .groupby("Jogador")["Pontos"]
    .size()
    .astype(int)
)

jogadores_df["Derrotas"] = (
    lista_jogos_df.loc[lista_jogos_df["Pontos"] == 0]
    .groupby("Jogador")["Pontos"]
    .size()
    .astype(int)
)

jogadores_df = jogadores_df.replace(np.nan, 0)

# Classificação ao longo do tempo
lista_jogos_completa_df = lista_jogos_df[["Rodada", "Jogador", "Pontos", "Gols"]]

lista_jogos_completa_df = (
    lista_jogos_completa_df.groupby(["Rodada", "Jogador"])
    .sum()
    .unstack(fill_value=0)
    .stack()
    .reset_index()
)

linha_de_corte = jogadores_df.loc[jogadores_df["Presença"] >= PRESENÇA_MINIMA].index

lista_jogos_completa_df = lista_jogos_completa_df[
    lista_jogos_completa_df["Jogador"].isin(linha_de_corte)
].reset_index()

lista_jogos_completa_df["Pontos Acc"] = lista_jogos_completa_df.groupby("Jogador")[
    "Pontos"
].cumsum()

lista_jogos_completa_df["Gols Acc"] = lista_jogos_completa_df.groupby("Jogador")[
    "Gols"
].cumsum()

lista_jogos_completa_df["Posição"] = (
    lista_jogos_completa_df.sort_values(["Pontos Acc", "Gols Acc"], ascending=False)
    .groupby("Rodada")
    .cumcount()
    .add(1)
)


# Tabela de classificação final
tabela = jogadores_df.copy().reset_index()
tabela = tabela[tabela["Jogador"].isin(linha_de_corte)]
tabela = tabela.sort_values(by=["Pontos"], ascending=False)
tabela = tabela[
    [
        "Jogador",
        "Pontos",
        "Aproveitamento%",
        "Gols",
        "Gols/Jogo",
        "Presença",
        "Presença%",
        "Destaques",
        "Vitórias",
        "Empates",
        "Derrotas",
    ]
]
tabela = tabela.rename(
    columns={
        "Jogador": "JOGADOR",
        "Pontos": "PTS",
        "Aproveitamento%": "APRV",
        "Gols": "GOLS",
        "Gols/Jogo": "MÉDIA",
        "Presença": "PJ",
        "Presença%": "FREQ",
        "Destaques": "S+",
        "Vitórias": "V",
        "Empates": "E",
        "Derrotas": "D",
    }
)

# gráficos
line_classificação = px.line(
    lista_jogos_completa_df,
    x="Rodada",
    y="Posição",
    color="Jogador",
    template="none",
    # title="Classificação",
)
line_classificação.update_traces(x0=1)
line_classificação.update_yaxes(autorange="reversed")
line_classificação.update_layout(showlegend=False, template="none", yaxis={"title": ""})
for i, d in enumerate(line_classificação.data):
    line_classificação.add_scatter(
        x=[d.x[-1]],
        y=[d.y[-1]],
        mode="markers+text",
        text=str(d.y[-1]) + "-" + d.name,
        textfont=dict(color=d.line.color),
        textposition="middle right",
        marker=dict(color=d.line.color, size=12),
        legendgroup=d.name,
        showlegend=False,
    )


bar_pontos = px.bar(
    lista_jogos_completa_df,
    x="Pontos Acc",
    y="Jogador",
    color="Jogador",
    animation_frame="Rodada",
    orientation="h",
    text="Posição",
    template="none",
    title="Classificação",
)
bar_pontos.update_layout(
    showlegend=False,
    yaxis={
        "categoryorder": "total ascending",
        "title": "",
        "side": "right",
        "automargin": "width",
    },
    xaxis={"title": ""},
)
bar_pontos.update_yaxes(ticklabelposition="inside")
bar_pontos.add_vline(x=0)

bar_gols = px.bar(
    lista_jogos_completa_df,
    x="Gols Acc",
    y="Jogador",
    color="Jogador",
    animation_frame="Rodada",
    orientation="h",
    text="Gols Acc",
    template="none",
    title="Gols Acumudalos",
)
bar_gols.update_layout(
    showlegend=False,
    yaxis={"categoryorder": "total ascending", "side": "right", "title": ""},
    xaxis={"title": ""},
)
bar_gols.update_yaxes(ticklabelposition="inside")
bar_gols.add_vline(x=0)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        children="Sábado Sem Lei - 2022",
                        style={"text-align": "center", "display": "flex"},
                    ),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.P("Presença Mínima"),
                            dbc.Input(type="number", min=0, max=num_jogos, step=1),
                        ]
                    ),
                    width=1,
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.RangeSlider(
                                2011,
                                2023,
                                1,
                                marks={
                                    2011: "2021",
                                    2012: "2012",
                                    2013: "2013",
                                    2014: "2014",
                                    2015: "2015",
                                    2016: "2016",
                                    2017: "2017",
                                    2018: "2018",
                                    2019: "2019",
                                    2020: "2020",
                                    2021: "2021",
                                    2022: "2022",
                                    2023: "2023",
                                },
                                value=[2022, 2023],
                                id="my-slider",
                            ),
                            html.Div(id="slider-output-container"),
                        ]
                    ),
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        dbc.Table.from_dataframe(
                            tabela,
                            size="sm",
                            hover=True,
                            style={"width": "100%", "height": "90vh"},
                        ),
                        style={"max-height": "90vh", "overflow": "auto"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(figure=line_classificação, style={"height": "100vh"})
                    ),
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(dcc.Graph(figure=bar_pontos, style={"height": "95vh"})),
                    width=6,
                ),
                dbc.Col(
                    html.Div(dcc.Graph(figure=bar_gols, style={"height": "95vh"})),
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)

app.run_server(debug=True, use_reloader=False)