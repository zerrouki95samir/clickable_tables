import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import time
from datetime import datetime
import dash_table
from dash.exceptions import PreventUpdate
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from flask import Flask
import json

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN]
)
server = app.server

# read csv data:
df = pd.read_csv('database/books.csv')

PAGE_SIZE = 50
offset = 0
ORDER_BY = ['author', 'title']
HOW = 'ASC'

app.layout = html.Div([
    html.Div([
        html.H1('ALMEDINA BOOK INTELLIGENCE', className="text-center",
                style={'margin': '50px', 'color': 'black'}),
        html.Div([
            dcc.Store(id='final-select'),
            dcc.Store(id='selected-books'),
            dcc.Store(id='memory-output'),
            dcc.Store(id='memory-output-paginated'),
            html.Div([
                dcc.Dropdown(
                    id='date-picker',
                    options=[
                        {'value': x, 'label': x} for x in df['scrape_date'].drop_duplicates()
                    ],
                    multi=True
                ),
            ], className='firstItem'),

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
                    {'value': x, 'label': f'{x}'} for x in df['Publisher'].drop_duplicates()
                ], multi=True),
            ], className='secondItem'),
        ], className='container_inputs'),

        html.Div(id='empty'),
        html.Div([
            html.Div(id='result-counter'), # Books 1 - 50 (xxxx)
            dbc.Button("Print Selected Books", id='print-btn', outline=True, color="info", className="mr-1", disabled=False), 
            Download(id="download")
            ], className='printBtn'),
        dbc.Spinner(
            html.Div([
                html.Div(id='dropdown-container-output'),
                html.Div([html.Div(id='child1')]),
                html.Div([
                    dbc.Button("Previous", outline=True, color="dark",
                            id='previous-btn', className='spacer', disabled=True),
                    dbc.Button("Next", outline=True, color="dark",
                            id='next-btn', disabled=True)
                ], className='paginationBtns')
            ], className='resultContainer')
        )
    ], className='container'),
])


@app.callback(
    Output('memory-output', 'data'),
    Input('date-picker', 'value'),
    Input('memory-author', 'value'),
    Input('memory-websites', 'value'),
)
def filter_dates(selected_date, selected_authors, selected_websites):
    global offset
    offset = 0
    filtered = df.copy()
    if selected_date:
        filtered = filtered.query('scrape_date in @selected_date')

    if selected_authors:
        filtered = filtered.query('author in @selected_authors')

    if selected_websites:
        filtered = filtered.query('Publisher in @selected_websites')

    return filtered.to_dict('records')


@app.callback(
    Output('memory-output-paginated', 'data'),
    Input('next-btn', 'n_clicks'),
    Input('previous-btn', 'n_clicks'),
    Input('memory-output', 'data'),
    State('selected-books', 'data'),
    State('memory-output-paginated', 'data'),
    State('final-select', 'data')
)
def filter_pagination(n_clicks_next, n_clicks_prev, data, selected_books, pages_data, final_select):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    global offset
    if data is None:
        raise PreventUpdate

    data = pd.DataFrame.from_dict(data)
    pages_data = pages_data or {}
    selected_books = selected_books or {}
    final_select = final_select or {}

    filtered = data[0:PAGE_SIZE]

    if context == 'next-btn':
        filtered = data[offset:offset+PAGE_SIZE]
        offset += PAGE_SIZE
        disabled = True
        if len(data[offset:offset+1]) > 0:
            disabled = False
        result = {
            'data': filtered.to_dict('records'),
            'nextPage': disabled,
            'selectedBooks': list(dict.fromkeys(pages_data.get('selectedBooks', [])+selected_books.get('selectedBooks', [])))
        }
        return result

    if context == 'previous-btn':
        offset -= PAGE_SIZE
        filtered = data[offset-PAGE_SIZE:offset]

        disabled = False
        result = {
            'data': filtered.to_dict('records'),
            'nextPage': disabled,
            'selectedBooks': list(dict.fromkeys(pages_data.get('selectedBooks', [])+selected_books.get('selectedBooks', [])))
        }
        return result

    offset += PAGE_SIZE
    disabled = True
    if (len(data) > PAGE_SIZE):
        disabled = False
    return {
        'data': filtered.to_dict('records'),
        'nextPage': disabled,
        'selectedBooks': list(dict.fromkeys(pages_data.get('selectedBooks', [])+selected_books.get('selectedBooks', [])))
    }


@app.callback(
    Output('child1', 'children'),
    Output('next-btn', 'disabled'),
    Output('previous-btn', 'disabled'),
    Output('result-counter', 'children'),
    Input('memory-output-paginated', 'data'),
    State('final-select', 'data'),
    State('memory-output', 'data'),
)
def on_data_set_table(data, selected_books, books_len):
    if data is None:
        raise PreventUpdate
    container = []
    page_data = pd.DataFrame.from_dict(data['data'])

    selected_books = selected_books or {'selectedBooks': []}
    def get_thumbnail(l):
        return (html.Img(src=f'{l}', style={'height': '240px', 'width': '150px'}))

    def get_link(values):
        return html.A(html.P(values[0]), href=f"{values[1]}", target="_blank")

    def build_check(x):
        selected = []
        if x in selected_books.get('selectedBooks'):
            selected.append(x)
        check = dbc.Checklist(
            options=[
                {"label": "", "value": x},
            ],
            value=selected,
            id={
                'type': 'filter-dropdown',
                'index': x
            }
        )
        return check

    previous_btn = True
    global offset
    if offset > PAGE_SIZE:
        previous_btn = False

    if not page_data.empty:
        page_data['Book Cover'] = page_data['cover_link'].map(
            lambda l: get_thumbnail(l))
        page_data['Title'] = page_data[[
            'title', 'book_link']].apply(get_link, axis=1)
        page_data['Selected Books'] = page_data['book_id'].map(
            lambda x: build_check(x))
        page_data = page_data.drop(
            ['cover_link', 'book_link', 'website_source', 'title'], axis=1)
        page_data = page_data[['Selected Books', 'Title', 'author',
                               'price', 'scrape_date', 'Book Cover', 'Publisher']]

        table_container = dash_table.DataTable(
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
        )

        return table_container2, data['nextPage'], previous_btn, f'Books {offset-PAGE_SIZE+1} - {offset-PAGE_SIZE+len(page_data)} ({len(books_len)})'
    warning = dbc.Alert(
        "Sorry; No Books Available With The Specified Parameters!!", color="warning")
    return warning, data['nextPage'], previous_btn, ''


@app.callback(
    Output('download', 'data'),
    Input('print-btn', 'n_clicks'),
    State('final-select', 'data'),
)
def print_books(n_clicks, selected_books):
    if n_clicks is None:
        raise PreventUpdate
    selected_books = selected_books or {'selectedBooks': []}
    if len(selected_books.get('selectedBooks')) > 0:
        result = df.loc[df['book_id'].isin(
            selected_books.get('selectedBooks'))]
        return send_data_frame(result.to_excel, filename="data.xlsx")


@app.callback(
    Output('selected-books', 'data'),
    Output('final-select', 'data'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
    State('final-select', 'data'),
)
def display_output(values, all_selected):
    triggered_checkbox = dash.callback_context.triggered
    selected_books = []
    for lst in values:
        for val in lst:
            if val:
                selected_books.append(val)

    selected_per_page = {
        'selectedBooks': selected_books,
    }
    all_selected = all_selected or {'selectedBooks': []}
    if len(triggered_checkbox) == 1:
        try:
            book_id = json.loads(triggered_checkbox[0].get('prop_id').replace('.value', ''))['index']
            value = triggered_checkbox[0].get('value')
            if (len(value) == 0) and (book_id in all_selected.get('selectedBooks')):
                all_selected.get('selectedBooks').remove(book_id)
            elif len(value) == 1:
                print('append ', book_id)
                all_selected.get('selectedBooks').append(book_id)
        except:
            print('exception')
    # all_selected['selectedBooks'] += selected_books
    # all_selected['selectedBooks'] = list(
    #     dict.fromkeys(all_selected.get('selectedBooks')))
    return selected_per_page, all_selected


if __name__ == "__main__":
    app.run_server(debug=True)
