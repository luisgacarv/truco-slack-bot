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
        response_url = form_data.get('response_url', [''])[0]

        # 1. Envie uma resposta HTTP 200 (OK) imediata para o Slack.
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'')  # Resposta vazia para não mostrar nada no Slack

        # 2. Processamento do Gemini e resposta para a response_url em seguida.
        try:
            api_key = os.getenv("GENAI_API_KEY")
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

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

            api_response = requests.post(api_url, headers=headers, data=json.dumps(data))
            api_response.raise_for_status()

            response_data = api_response.json()
            gemini_response = response_data['candidates'][0]['content']['parts'][0]['text']

            final_payload = {
                "response_type": "in_channel",
                "text": gemini_response
            }
            requests.post(response_url, data=json.dumps(final_payload), headers={'Content-Type': 'application/json'})

        except requests.exceptions.RequestException as e:
            error_message = "Erro na requisição à API do Gemini: " + str(e)
            error_payload = {
                "response_type": "ephemeral",
                "text": error_message
            }
            requests.post(response_url, data=json.dumps(error_payload), headers={'Content-Type': 'application/json'})
        except Exception as e:
            error_message = "Ocorreu um erro inesperado: " + str(e)
            error_payload = {
                "response_type": "ephemeral",
                "text": error_message
            }
            requests.post(response_url, data=json.dumps(error_payload), headers={'Content-Type': 'application/json'})
