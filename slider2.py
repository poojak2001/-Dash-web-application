import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd

# Load your DataFrame from the CSV file
df = pd.read_csv("country1.csv")

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Store(id='my-store', storage_type='memory', data=[]),
    html.Button('World', id='country_button', n_clicks=0, style={'display': 'none', 'margin': '5px'}),
    html.Button('countrystatesname', id='state_button', n_clicks=0, style={'display': 'none', 'margin': '5px'}),
    dcc.Graph(
        id='country-bar-chart',
        config={'displayModeBar': True},
    ),
    html.Div([
        dcc.Slider(
            id='population-slider',
            min=0,
            max=1,
            step=1,
            marks={0: 'Descending', 1: 'Ascending'},
            value=0,
            #vertical=True,
        )
    ], style={'width':'20%','height': '400px', 'position': 'absolute', 'top': '50px', 'right': '10px'}),
    html.Div(id='output')
])

def get_country(order_by):
    c_df = df.groupby('country')['population'].sum().reset_index().sort_values("population", ascending=order_by)
    return {
        'data':[{'x':c_df['country'],'y':c_df['population'],'type':'bar','name':'countries'}],
        'layout':{'title':'countries and their population',
                  'x axis':{ 'title':'country'},
                  'y axis': { 'title':'population'} }
    }

def states(selected_name, order_by):
    filtere_data = df[df['country'] == selected_name]
    state_df = filtere_data.groupby('state')['population'].sum().reset_index()
    state_df = state_df.sort_values("population", ascending=order_by)
    return {
        'data':[{'x':state_df['state'],'y':state_df['population'],'type':'bar','name':'states'}],
        'layout':{'title':f'states in {selected_name}',
                  'x axis':{ 'title':'state'},
                  'y axis': { 'title':'population'} }
    }

def cities(selected_name, order_by):
    filtered_data = df[df['state'] == selected_name]
    city_df = filtered_data.groupby('city')['population'].sum().reset_index()
    city_df = city_df.sort_values("population", ascending=order_by)
    return {
        'data':[{'x':city_df['city'],'y':city_df['population'],'type':'bar','name':'city'}],
        'layout':{'title':f'states in {selected_name}',
                  'x axis':{ 'title':'state'},
                  'y axis': { 'title':'population'} }
    }

@app.callback(
    Output('country-bar-chart', 'figure'),
    Output('country_button', 'style'),
    Output('state_button', 'style'),
    Output('my-store', 'data'),
    Input('country-bar-chart', 'clickData'),
    Input('country_button', 'n_clicks'),
    Input('state_button', 'n_clicks'),
    Input('population-slider', 'value'),
    State('my-store', 'data')
)
def update_and_button_visibility(country_clickData, p1, p2, order_by,temp_list):
    ctx = dash.callback_context
    button_style_country, button_style_state = {'display': 'none'}, {'display': 'none'}
    
    
    if country_clickData is None or "country_button" == ctx.triggered_id:
        figure = get_country(order_by)
        temp_list = []
    else:
        selected_name = country_clickData['points'][0]['x']
        if selected_name in df['country'].unique():
            temp_list.append(selected_name)
            button_style_country, button_style_state = {'display': 'inline'}, {'display': 'none'}
            figure = states(selected_name, order_by)
        elif "state_button" == ctx.triggered_id:
            selected_name = temp_list[0]
            temp_list.pop(-1)
            button_style_country, button_style_state = {'display': 'inline', 'margin': '5px'}, {'display': 'none', 'margin': '5px'}
            figure = states(selected_name, order_by)
        elif selected_name in df['state'].unique():
            temp_list.append(selected_name)
            button_style_state, button_style_country = {'display': 'inline', 'margin': '5px'}, {'display': 'inline', 'margin': '5px'}
            figure = cities(selected_name, order_by)
        elif selected_name in df["city"].unique():
            return dash.no_update

    return figure, button_style_country, button_style_state, temp_list

if __name__ == '__main__':
    app.run_server(debug=True)
