import pandas as pd
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dfs.lista_jogos import lista_jogos_df
import dash_ag_grid as dag
from tools.criar_df_classificação import criar_df_classificação
import dash


dash.register_page(__name__, name="Tabela de Classificação", order=3)


tabela_classificação = dag.AgGrid(
    id="tabela_classificação",
    defaultColDef={"sortable": True, "rezisable": True},
    columnDefs=[
        {
            "field": "make",
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "width": 5,
            "pinned": True,
        },
        {
            "field": "#",
            "type": "numericColumn",
            "width": 75,
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
            "width": 75,
        },
        {
            "field": "V",
            "width": 75,
        },
        {
            "field": "E",
            "width": 75,
        },
        {
            "field": "D",
            "width": 75,
        },
    ],
    dashGridOptions={"animateRows": True, "rowSelection": "multiple"},
    style={"height": 850, "width": "100%"},
)


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(tabela_classificação),
            ]
        ),
        dbc.Row(),
    ],
    # fluid=True,
)
