import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import time
import dash_dangerously_set_inner_html
from datetime import datetime
import dash_table
from dash.exceptions import PreventUpdate
import dateutil
from flask import Flask, request
import sqlite3



app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN]
)
server = app.server

# read csv data:
df = pd.read_csv('database/books.csv')

PAGE_SIZE = 10
offset = 0
ORDER_BY = ['author', 'title']
HOW = 'ASC'

app.layout = dbc.Container([
    html.H1('ALMEDINA BOOK INTELLIGENCE', className="text-center",
            style={'margin': '50px', 'color': 'black'}),

    html.Div([
        dcc.Store(id='selected-books'),
        dcc.Store(id='memory-output'),
        dcc.Store(id='memory-output-paginated'),
        html.Div([
            dcc.DatePickerRange(
                start_date=datetime.today().date() - dateutil.relativedelta.relativedelta(months=1),
                end_date=datetime.today().date(),
                display_format='MMM Do, YY',
                start_date_placeholder_text='MMM Do, YY',
                id='date_range'
            ),
        ]),

        html.Div([
            dcc.Dropdown(
                id='memory-author',
                options=[
                    {'value': x, 'label': x} for x in df['author'].drop_duplicates()
                ],
                multi=True
            ),
        ], className='firstItem'),

        html.Div([
            dcc.Dropdown(id='memory-websites', options=[
                {'value': x, 'label': f'{x} Website'} for x in df['website_name'].drop_duplicates()
            ], multi=True),
        ], className='secondItem'),
    ], className='container_inputs'),
    html.Div(id='empty'),
    dbc.Spinner(
        html.Div([
            html.Div(id='dropdown-container-output'),
            html.Div([html.Div(id='child1')]),
            html.Div([
                dbc.Button("Previous", outline=True, color="dark", id='previous-btn', className='spacer', disabled=True),
                dbc.Button("Next", outline=True, color="dark", id='next-btn', disabled=True)
            ], className='paginationBtns')
        ], className='resultContainer')    
    )
], className='container')

@app.callback(
    Output('memory-output', 'data'),
    Input('date_range', 'start_date'),
    Input('date_range', 'end_date'), # ADD Other inputs (author & websites names)
    Input('memory-author', 'value'),
    Input('memory-websites', 'value'),
)
def filter_dates(start_date, end_date, selected_authors, selected_websites):
    global offset
    offset = 0
    filtered = df.copy()
    if start_date or end_date:
        #return df.to_dict('records')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        filtered = filtered.loc[
            (pd.to_datetime(filtered['scrape_date']).dt.date >= start_date) & 
            (pd.to_datetime(filtered['scrape_date']).dt.date <= end_date)
        ]
        
    if selected_authors:
        filtered = filtered.query('author in @selected_authors') 

    if selected_websites: 
        filtered = filtered.query('website_name in @selected_websites') 

    return filtered.to_dict('records')

@app.callback(
    Output('memory-output-paginated', 'data'),
    Input('next-btn', 'n_clicks'),
    Input('previous-btn', 'n_clicks'),
    Input('memory-output', 'data'),
    )
def filter_pagination(n_clicks_next, n_clicks_prev, data):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    context_value = dash.callback_context.triggered[0]['value']
    global offset
    if data is None:
        raise PreventUpdate
    
    data = pd.DataFrame.from_dict(data)
    
    filtered = data[0:10]
    
    if context == 'next-btn':
        filtered = data[offset:offset+PAGE_SIZE]
        offset+=PAGE_SIZE
        disabled = True
        if len(data[offset:offset+1]) > 0:
            disabled = False
        result = {
            'data': filtered.to_dict('records'), 
            'nextPage': disabled,
        }
        return result
    
    if context == 'previous-btn':
        offset-=PAGE_SIZE
        filtered = data[offset-PAGE_SIZE:offset]
        
        disabled = False
        result = {
            'data': filtered.to_dict('records'), 
            'nextPage': disabled
        }
        return result

    offset+=PAGE_SIZE
    disabled = True
    if (len(data)>10):
        disabled = False
    return {
        'data': filtered.to_dict('records'),
        'nextPage': disabled,
    }



@app.callback(
    Output('child1', 'children'), 
    Output('next-btn', 'disabled'), 
    Output('previous-btn', 'disabled'), 
    Input('memory-output-paginated', 'data')
)
def on_data_set_table(data):
    if data is None:
        raise PreventUpdate
    container = []
    page_data = pd.DataFrame.from_dict(data['data'])
    def get_thumbnail(l):   
        return (html.Img(src=f'{l}', style={'height':'240px', 'width':'150px'}))

    def get_link(values):   
        return html.A(html.P(values[0]), href=f"{values[1]}", target="_blank")
    
    def build_check(x):
        check =dbc.Checklist(
                options=[
                    {"label": "", "value": x},
                ],
                value=[],
                id={
                    'type': 'filter-dropdown',
                    'index': x
                }
            )
        return check

    previous_btn = True
    global offset
    if offset > 10:
        previous_btn = False
    
    if not page_data.empty:
        page_data['Book Cover'] = page_data['cover_link'].map(lambda l: get_thumbnail(l))
        page_data['Title'] = page_data[['title', 'book_link']].apply(get_link, axis=1)
        page_data['Selected Books'] = page_data['book_id'].map(lambda x: build_check(x))
        page_data = page_data.drop(['cover_link', 'book_link', 'website_source', 'website_name', 'title'], axis=1)
        page_data = page_data[['Selected Books', 'Title', 'author', 'price', 'scrape_date', 'Book Cover']]

        table_container =  dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True} for i in page_data.columns
            ],
            data=page_data.to_dict('records'),
            row_selectable="multi",
            selected_rows=[]
        ),


        table_container2 = html.Div([
            dbc.Table.from_dataframe(page_data, striped=True, bordered=True, hover=True, responsive="sm")],
            style = {'margin-right':'30px','margin-left':'30px'})

        return table_container2, data['nextPage'], previous_btn
    warning = dbc.Alert("Sorry; No Books Available With The Specified Parameters!!", color="warning")
    return warning, data['nextPage'], previous_btn


# @app.callback(
#     Output('empty', 'children'),
#     Input('selected-books', 'data'),
# )
# def store_selected(data):
#     if not data:
#         raise PreventUpdate
#     conn = sqlite3.connect('database/books.db')
#     c = conn.cursor()
#     for id in data['selectedBooks']:
        
#         c.execute(f'''
#             INSERT INTO selectedBooks (book_id, selectCount) VALUES ({id}, 1) 
#             ON CONFLICT(book_id) DO UPDATE SET selectCount = selectCount + 1;
#         ''')
#         conn.commit()
    
#     conn.close()


@app.callback(
    Output('selected-books', 'data'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value')
)
def display_output(values):
    
    selected_books = []
    for lst in values:
        for val in lst:
            if val:
                selected_books.append(val)
    
    return {
        'selectedBooks': selected_books,
        'ipAddress': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    }

if __name__ == "__main__":
    app.run_server(debug=False)
