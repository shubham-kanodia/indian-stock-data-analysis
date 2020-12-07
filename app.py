import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash('Stocker', external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Stocker'
app.layout = dbc.Tabs([
    dbc.Tab(
        dbc.Card([
            dcc.Dropdown(id='dropdown',
                         options=[
                             {'label': 'Item 1', 'value': 'foo'},
                             {'label': 'Item 2', 'value': 'bar'},
                         ],
                         ),
            html.Br(),
            html.Div(id='item-display'),
        ])
    )])


if __name__ == '__main__':
    app.run_server(debug=True)
