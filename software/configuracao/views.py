from django.shortcuts import render, redirect
from django.http import HttpResponse

def index_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Index - Horta Viva API Gateway</title>
        <style>
            body {
                background-color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: sans-serif;
            }
            h1 {
                color: #333;
            }
            .btn {
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
            .btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <h1>Index - Horta Viva API Gateway</h1>
        <a href="/api/login/" class="btn">Aceder à API</a>
    </body>
    </html>
    """
    return HttpResponse(html)
