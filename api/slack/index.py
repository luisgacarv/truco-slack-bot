import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        # Envia uma resposta HTTP 200 (OK) imediata para o Slack.
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'') # Resposta vazia para não mostrar nada no Slack

        # Pega a URL do seu projeto no Vercel a partir das variáveis de ambiente
        # A URL deve ser no formato https://nome-do-seu-projeto.vercel.app
        vercel_url = os.getenv("VERCEL_URL")

        # Dados da requisição a serem enviados para a função do Gemini
        payload = {
            "text": form_data.get('text', [''])[0],
            "response_url": form_data.get('response_url', [''])[0]
        }

        # Faz a requisição HTTP POST para a segunda função (gemini) em segundo plano.
        if vercel_url:
            requests.post(f"https://{vercel_url}/api/gemini", json=payload)
