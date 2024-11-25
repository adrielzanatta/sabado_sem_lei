import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dfs.lista_jogos import lista_jogos_df
import dash_ag_grid as dag
from PIL import Image
from tools.criar_df_classificação import criar_df_classificação
import dash

dash.register_page(__name__, name="Classificação Histórica", order=10)


slicer_temporadas = html.Div(
    [
        html.H6("Selecionar Temporadas para Analisar"),
        dcc.RangeSlider(
            min=lista_jogos_df["Ano"].unique().min(),
            max=lista_jogos_df["Ano"].unique().max(),
            step=1,
            value=[
                lista_jogos_df["Ano"].unique().min(),
                lista_jogos_df["Ano"].unique().max(),
            ],
            id="slincer_temporadas",
            marks={
                i: "{}".format(i)
                for i in range(
                    lista_jogos_df["Ano"].unique().min(),
                    lista_jogos_df["Ano"].unique().max() + 1,
                    1,
                )
            },
        ),
    ]
)

check_filtro_jogadores = html.Div(
    [
        html.H6("Ativar Filtros Laterais"),
        dcc.Dropdown(
            options=["Sim", "Não"],
            value="Não",
            id="ativar_filtro_jogadores",
            persistence=True,
            persistence_type="memory",
        ),
    ]
)

tabela_historica = dag.AgGrid(
    id="tabela_historica",
    defaultColDef={"sortable": True, "rezisable": True},
    columnDefs=[
        {
            "field": "#",
            "type": "numericColumn",
            "width": 30,
            "pinned": True,
        },
        {
            "field": "JOGADOR",
            "width": 200,
            "sortable": False,
            "pinned": True,
        },
        {
            "field": "PTS",
            "width": 75,
        },
        {
            "field": "APRV",
            "width": 90,
            "valueFormatter": {"function": 'd3.format(".1%")(params.value)'},
        },
        {
            "field": "GOLS",
            "width": 75,
        },
        {
            "field": "MÉDIA",
            "width": 90,
            "valueFormatter": {"function": 'd3.format(".2f")(params.value)'},
        },
        {
            "field": "PJ",
            "width": 75,
        },
        {
            "field": "FREQ",
            "width": 90,
            "valueFormatter": {"function": 'd3.format(".1%")(params.value)'},
        },
        {
            "field": "S+",
            "width": 60,
        },
        {
            "field": "V",
            "width": 60,
        },
        {
            "field": "E",
            "width": 60,
        },
        {
            "field": "D",
            "width": 60,
        },
    ],
    dashGridOptions={"animateRows": True},
    style={"height": 775, "width": "100%"},
)

grafico_gols_pontos = (
    html.Div(
        dcc.Graph(figure={}, style={"height": 775}, id="gráfico_pontos_gols"),
    ),
)


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(check_filtro_jogadores, width=6),
                dbc.Col(slicer_temporadas, width=6),
            ]
        ),
        dbc.Row(
            [dbc.Col(tabela_historica, width=6), dbc.Col(grafico_gols_pontos, width=6)]
        ),
    ],
    fluid=True,
)


@callback(
    Output("tabela_historica", "rowData"),
    Input("slincer_temporadas", "value"),
    Input("ativar_filtro_jogadores", "value"),
    Input("linhas_filtradas_tabela_classificação", "data"),
)
def criar_tabela_historica(temporadas, ativar_filtro_jogadores, jogadores_tabela):
    if len(temporadas) == 1:
        temporadas_selecionadas = temporadas
    else:
        temporadas_selecionadas = range(temporadas[0], temporadas[1] + 1, 1)

    df = lista_jogos_df.loc[lista_jogos_df["Ano"].isin(temporadas_selecionadas)]

    if ativar_filtro_jogadores == "Sim":
        jogadores_selecionados_df = pd.DataFrame(jogadores_tabela)
        df = df.loc[df["Jogador"].isin(jogadores_selecionados_df["JOGADOR"])]
    else:
        pass

    row_data = criar_df_classificação(df).to_dict("records")

    return row_data


@callback(
    Output("gráfico_pontos_gols", "figure"),
    Input("slincer_temporadas", "value"),
    Input("ativar_filtro_jogadores", "value"),
    Input("linhas_filtradas_tabela_classificação", "data"),
)
def criar_graph2(temporadas, ativar_filtro_jogadores, jogadores_tabela):
    if len(temporadas) == 1:
        temporadas_selecionadas = temporadas
    else:
        temporadas_selecionadas = range(temporadas[0], temporadas[1] + 1, 1)

    df = lista_jogos_df.loc[lista_jogos_df["Ano"].isin(temporadas_selecionadas)]
    tabela_df = pd.DataFrame(jogadores_tabela)

    if ativar_filtro_jogadores == "Sim":
        df = df.loc[df["Jogador"].isin(tabela_df["JOGADOR"])]
    else:
        pass

    dff = df.groupby("Jogador")[["Pontos", "Gols"]].sum()
    dff["PJ"] = df.groupby("Jogador")["Rodada"].count()
    dff["Gols/PJ"] = dff["Gols"] / dff["PJ"]
    dff["Pontos/PJ"] = dff["Pontos"] / dff["PJ"]
    grafico_gols_pontos = px.scatter(
        data_frame=dff,
        x="Pontos",
        y="Gols",
        size="PJ",
        color=dff.index,
        size_max=50,
        # text=dff.index,
    )
    grafico_gols_pontos.update_layout(showlegend=False, template="none")
    grafico_gols_pontos.update_traces(
        textposition="middle right", marker_color="rgba(0,0,0,0)"
    )

    try:
        for i, row in dff.iterrows():
            jogador = i.replace(" ", "-")
            grafico_gols_pontos.add_layout_image(
                dict(
                    source=Image.open(f"sabado_sem_lei/src/assets/fotos/{jogador}.png"),
                    xref="x",
                    yref="y",
                    xanchor="center",
                    yanchor="middle",
                    x=row["Pontos"],
                    y=row["Gols"],
                    sizex=int(row["PJ"] * 0.35),
                    sizey=int(row["PJ"] * 0.35),
                    sizing="contain",
                    layer="above",
                )
            )
    except:
        pass

    return grafico_gols_pontos
