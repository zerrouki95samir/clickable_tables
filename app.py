from dash_core_components.Store import Store
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from functions import helpers
from dash.exceptions import PreventUpdate

from flask import Flask

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN]
)
app.config['suppress_callback_exceptions'] = True

PAGE_SIZE = 10
offset = 0

server = app.server

# read csv data:
# executive_sammary = pd.read_excel('database/example_data.xlsx', sheet_name='executive_summary', engine='openpyxl',)
# tests = pd.read_excel('database/example_data.xlsx', sheet_name='tests', engine='openpyxl')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session_storage', storage_type='session'),
    dcc.Store(id='pagination_data'),
    html.H1('Nawar29 From U.S.', className="text-center",
            style={'margin': '50px', 'color': 'black'}),
    html.H5(id='title_detail', className="text-center", style={'margin': '100px 0 30px  0', 'color': 'black'}),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.Div([
        dcc.Upload(
            id='upload-file',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Your Excel File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
            },
            multiple=False
        ),
        html.Div([
            dbc.Input(id="main_sheet",
                      placeholder="Main sheet name", type="text"),
            dbc.Input(id="detail_sheet",
                      placeholder="Details sheet name", type="text"),
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Input(id="clickable_field",
                                      placeholder="Clickable Field", type="text")),
                    dbc.Col(dbc.Input(id="target_field",
                                      placeholder="Target Field", type="text"))
                ])
            ])
        ], className=''),
        html.Div(id='warning_div'),
        dbc.Button("Show table", id='show_main_table', color="info", className="mr-1",
                   style={'float': "right", 'margin': '20px 0 20px 150px'}),

    ], className='column', style={'maxWidth': '320px', 'width': '100%'}),

    dbc.Container(
        html.Div([
            html.Div(id='result_counter', style={'marginBottom': '15px'}),
            html.Div(id='main_table'),
            html.Div([
                dbc.Button("Previous", outline=True, color="dark",
                           id='previous_btn', className='spacer', disabled=True),
                dbc.Button("Next", outline=True, color="dark",
                           id='next_btn', className='spacer', disabled=True),
            ], style={'float': 'right'})
        ]), style={'marginTop': '15px'})
], className='uplTableContainer')


@app.callback(
    Output('main_table', 'children'),
    Output('result_counter', 'children'),
    Output('previous_btn', 'disabled'),
    Output('next_btn', 'disabled'),
    Input('pagination_data', 'data'),
    State('session_storage', 'data')
)
def show_main_table(data, sess_data):
    if data is not None:
        data = data or {}
        page_data = pd.DataFrame.from_dict(data.get('page', []))
        if not page_data.empty:
            clickable = sess_data['clickable_field']
            main_table = helpers.build_main_table(page_data, clickable)
            return main_table, html.B(f'Rows {data.get("start_offset", 0)+1} - {data.get("start_offset", 0) + data.get("page_size", 0)} ({data.get("total_size", 0)})'), data.get('prev_disabled', True), data.get('next_disabled', True)
        else:
            return '', '', True, True
    
    else:
            return '', '', True, True


@app.callback(
    Output('pagination_data', 'data'),
    Input('session_storage', 'data'),
    Input('next_btn', 'n_clicks'),
    Input('previous_btn', 'n_clicks'),
    State('pagination_data', 'data'),
)
def update_page_table(sess_data, next_btn, previous_btn, prev_data):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    prev_data = prev_data or {}
    if context == 'next_btn':
        if next_btn is None:
            raise PreventUpdate
        print('next-btn')
        data = pd.DataFrame.from_dict(sess_data['main_data'])
        start_offset = prev_data.get('start_offset', 0) + PAGE_SIZE
        stop_in = start_offset + PAGE_SIZE
        return_page = {
            'page': data[start_offset:stop_in].to_dict('records'),
            'start_offset': start_offset,
            'stop_in': stop_in,
            'page_size': len(data[start_offset:stop_in]),
            'total_size': len(data),
            'next_disabled': True,
            'prev_disabled': True,
        }
        if len(data[start_offset:stop_in+1]) > 10:
            return_page['next_disabled'] = False

        if start_offset >= 10:
            return_page['prev_disabled'] = False

        return return_page

    if context == 'previous_btn' and prev_data.get('start_offset', 0) !=0:
        data = pd.DataFrame.from_dict(sess_data['main_data'])
        start_offset = prev_data.get('start_offset', 0) - PAGE_SIZE
        stop_in = start_offset + PAGE_SIZE
        print(start_offset, stop_in)
        return_page = {
            'page': data[start_offset:stop_in].to_dict('records'),
            'start_offset': start_offset,
            'stop_in': stop_in,
            'page_size': len(data[start_offset:stop_in]),
            'total_size': len(data),
            'next_disabled': True,
            'prev_disabled': True,
        }
        if len(data[start_offset:stop_in+1]) > 10:
            return_page['next_disabled'] = False
        if start_offset >= 10:
            return_page['prev_disabled'] = False
        return return_page

 
    if sess_data:
        print('sess_data')
        data = pd.DataFrame.from_dict(sess_data['main_data'])
        start_offset = prev_data.get('start_offset', 0)
        stop_in = start_offset + PAGE_SIZE
        return_page = {
            'page': data[start_offset:stop_in].to_dict('records'),
            'start_offset': start_offset,
            'stop_in': stop_in,
            'page_size': len(data[start_offset:stop_in]),
            'total_size': len(data),
            'next_disabled': True,
            'prev_disabled': True,
        }
        if len(data[start_offset:stop_in+1]) > 10:
            return_page['next_disabled'] = False
        return return_page


@app.callback(
    Output('session_storage', 'data'),
    Output('warning_div', 'children'),
    Input('show_main_table', 'n_clicks'),
    State('main_sheet', 'value'),
    State('detail_sheet', 'value'),
    State('clickable_field', 'value'),
    State('target_field', 'value'),
    State('upload-file', 'contents'),
    State('upload-file', 'filename'),
    State('upload-file', 'last_modified'),
    State('session_storage', 'data')
)
def update_output(
    n_click,
    main_sheet,
    detail_sheet,
    clickable_field,
    target_field,
    list_of_contents,
    list_of_names,
    list_of_dates,
    histo_data
):
    if n_click:
        if list_of_contents is not None:
            data, is_error = helpers.parse_contents(
                list_of_contents, list_of_names, list_of_dates, main_sheet, detail_sheet, clickable_field, target_field)
            if data is not None and is_error:
                data['clickable_field'] = clickable_field
                data['target_field'] = target_field
                data['main_sheet_name'] = main_sheet
                data['detail_sheet_name'] = detail_sheet
                return data, ['']
            else:
                return {}, [dbc.Alert(f"{data}", color="danger")]
    else:
        return histo_data, ['']

# Update the index


@app.callback(
    Output('page-content', 'children'),
    Output('title_detail', 'children'),
    Input('url', 'pathname'),
    State('session_storage', 'data')
)
def display_page(pathname, data):
    if pathname == '/':
        return index_page, None
    else:
        if data is not None:
            data = data or {'main_data': [], 'detail_data': []}
            detail_data = pd.DataFrame.from_dict(data['detail_data'])
            # Filter data here:
            target = data['target_field']
            filtered_data = helpers.filter_data(pathname, detail_data, target)
            if not filtered_data.empty:
                # build the new table:
                detail_table = helpers.build_detail_table(filtered_data, pathname)
                title = html.Div(f'Detailed information on {pathname.replace("/", "").title()}')
                return detail_table, title


if __name__ == "__main__":
    app.run_server(debug=False)
