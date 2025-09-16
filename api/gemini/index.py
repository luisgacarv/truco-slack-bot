import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(post_data)
            slack_text = payload.get('text')
            response_url = payload.get('response_url')

            # Pega a chave de API da variável de ambiente
            api_key = os.getenv("GENAI_API_KEY")
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

            # Dados da requisição para a API do Gemini
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
            api_response.raise_for_status()

            response_data = api_response.json()
            gemini_response = response_data['candidates'][0]['content']['parts'][0]['text']

            # Envia a resposta final para o Slack usando a response_url
            final_payload = {
                "response_type": "in_channel",
                "text": gemini_response
            }
            requests.post(response_url, data=json.dumps(final_payload), headers={'Content-Type': 'application/json'})

            # Resposta de sucesso para a chamada Vercel
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')

        except Exception as e:
            # Em caso de erro, envia a mensagem de erro de volta para o Slack
            error_message = "Ocorreu um erro inesperado: " + str(e)
            error_payload = {
                "response_type": "ephemeral",
                "text": error_message
            }
            if 'response_url' in locals():
                requests.post(response_url, data=json.dumps(error_payload), headers={'Content-Type': 'application/json'})
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
