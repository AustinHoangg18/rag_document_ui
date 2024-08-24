import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
import base64
import pandas as pd 


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = \
    html.Div(
        className="main-div",
        children=[
            html.H2('Documents AI Assistant',className="page-title"),
            html.H5('Create your document assistant with one click',className="sub-title"),
            html.H6([
                "Powered by ",
                html.Span("Austin Hoang",style={"color":"red"})
            ],className="sub-1-title"),
            dcc.Upload(
                className="upload-area",
                id='upload-file',
                children=html.Button(id="upload-file-button",children='Upload File',className='upload-button',n_clicks=0),
                multiple=False
                ),
            html.Img(id="success-icon",className="success-icon",src='assets/icon.png'),
            html.Div(id="upload-content",className="content-upload"),
            html.Button('SUBMIT', className="submit-button", id="submit-file-button", n_clicks=0,disabled=True),
            html.Div(
            dcc.ConfirmDialog(id='error_submit',message=""),
                className="error-search-dialog"),
            html.Div(id="chatbot-block",className="chatbot-block",
                     children=[
                        html.H6(className="chat-status",
                            children=[
                                "Chatbot is ready!",
                                html.Img(src="assets/online.png",className="online-icon"),
                            ]),
                        html.Div(className="chat-area",id="chat-area",children=[]),
                        html.Div(className="input-block",children=[
                            dcc.Input(id="user-input",className="user-input",placeholder="Enter your question here ..."),
                            html.Button(id="send-input",className="send-button",children="Send",n_clicks=0)
                        ]),
                     ])

        ])

@app.callback(
    [Output("upload-content","children"),
     Output("success-icon","style"),
     Output("submit-file-button","disabled"),
     Output("chatbot-block","style")],
    [Input("upload-file","contents"),
     Input("submit-file-button","n_clicks")],
    [dash.dependencies.State('upload-file', 'filename')]
    # prevent_initial_call=True
)
def toggle_chat(contents,submit_clicks,filename):
    if contents:
        if submit_clicks == 0:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            response = requests.post("http://127.0.0.1:8000/fetch",files={"file": (filename, decoded, 'application/pdf')})
            res = response.json()
            return f"Success uploaded file '{filename}'. Click SUBMIT to start conversation",{'display':'flex'},False,{'display':'None'}
        return f"Success uploaded file '{filename}'. \nClick SUBMIT to start conversation",{'display':'flex'},False,{'display':'flex'}
    return ['Drop a file here'],{'display':'None'},True,{'display':'None'}





@app.callback(
    Output("chat-area","children"),
    Output("chat-area","style"),
    Output("user-input","value"),
    Input("send-input","n_clicks"),
    Input("submit-file-button","n_clicks"),
    dash.dependencies.State("user-input","value"),
    dash.dependencies.State("chat-area","children")
)
def update_chat(send_n_clicks,submit_file_clicks,user_input,chat_history):
    if send_n_clicks > 0:
        if not user_input:
            return chat_history,{"display":"None"},""
        
        response = requests.post(f"http://127.0.0.1:8000/chat/{user_input}")
        chatbot_response = response.json()['message']
        if not chat_history:
            chat_history = [
                            html.Div([
                                html.B("You:"),
                                html.P(f"{user_input}")],
                                className="user-message"),
                            html.Div([
                                html.B("Chatbot:"),
                                html.P(f"{chatbot_response}")],
                                className="chatbot-message")
                            ]
                            

        else:
            chat_history.append(html.Div([
                                html.B("You:"),
                                html.P(f"{user_input}")],
                                className="user-message"))
            chat_history.append(html.Div([
                                html.B("Chatbot:"),
                                html.P(f"{chatbot_response}")],
                                className="chatbot-message"))
        return chat_history, {"display":"flex"}, ""
    
    return chat_history,{"display":"none"},""

if __name__ == '__main__':
    app.run(debug=True,port=8051)