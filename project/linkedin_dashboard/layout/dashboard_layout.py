from dash import dcc, html

from linkedin_dashboard.process.process_data import get_skill_dict, get_skill_names

skill_dict = get_skill_dict()
skill_names = get_skill_names()

layout = html.Div([
    dcc.Interval(id='interval-component', interval=60*5000, n_intervals=0),
    html.H1("Análise de Vagas no Linkedin por Habilidades",
            style={
                'position': 'absolute',
                'top': '0',  
                'left': '0',      
                'right': '0',        
                'margin': '0',        
                'padding': '10px',    
                'color': '#4CAF50',  
                'fontFamily': 'Arial',
                'fontSize': '28px',
                'fontWeight': 'bold',
                'backgroundColor': '#F0F0F0',
                'borderRadius': '10px 0 0 10px',  
                'boxShadow': '2px 2px 10px rgba(0, 0, 0, 0.1)'
            }),
    html.Div([
        html.Label("Selecione Habilidades:"),
        dcc.Dropdown(
            id='skill-dropdown',
            options=[{'label': name, 'value': skill_dict[name]} for name in skill_names],
            multi=True,
            placeholder="Selecione uma ou mais habilidades",
            clearable=False,
        ),
    ], style={'paddingTop': '60px'}),
    html.Div([
        html.P("Selecione o cargo:"),
        dcc.Dropdown(
            id="dropdown",
            options=["Leader", "Assistant", "Producer", "Developer"],
            value='Leader',
            clearable=False,
        ),
    ]),
    html.Div([
        dcc.Graph(id='graph'),
    ]),
    html.Div([
        html.Div([dcc.Graph(id='remote-job-pie-chart')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='salary-bar-chart')], style={'width': '50%', 'display': 'inline-block'}),
    ]),
], style={'position': 'relative'})
