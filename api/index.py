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

        slack_text = form_data.get('text', [''])[0]

        try:
            if not slack_text:
                response = "Por favor, forneça um texto para o Gemini."
            else:
                # Pega a chave de API da variável de ambiente
                api_key = os.getenv("GENAI_API_KEY")

                # URL da API do Gemini
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

                # Dados da requisição
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [
                        {
                            "parts": [
                                {"text": slack_text}
                            ]
                        }
                    ]
                }

                # Faz a requisição HTTP POST para a API do Gemini
                api_response = requests.post(api_url, headers=headers, data=json.dumps(data))
                api_response.raise_for_status() # Lança um erro para status de erro (4xx ou 5xx)

                # Pega a resposta do JSON
                response_data = api_response.json()
                gemini_response = response_data['candidates'][0]['content']['parts'][0]['text']
                response = gemini_response

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                '{"response_type": "in_channel", "text": "' + response.replace('"', '\\"') + '"}'
                .encode('utf-8')
            )

        except requests.exceptions.RequestException as e:
            # Captura erros de rede ou de status HTTP
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                '{"response_type": "ephemeral", "text": "Erro na requisição à API do Gemini: ' + str(e) + '"}'
                .encode('utf-8')
            )
        except Exception as e:
            # Captura outros erros
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                '{"response_type": "ephemeral", "text": "Ocorreu um erro inesperado: ' + str(e) + '"}'
                .encode('utf-8')
            )
