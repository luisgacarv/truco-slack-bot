import os
import json
import requests
from http.server import BaseHTTPRequestHandler

# Importe a biblioteca para a API que você irá usar
from groq import Groq

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Extrai os dados enviados pelo primeiro script
        user_text = data.get('text', '')
        response_url = data.get('response_url', '')

        # Verifica se a chave de API da Groq existe
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            response_message = {
                "response_type": "ephemeral",
                "text": "Erro: A chave da API Groq não está configurada. Por favor, adicione-a às suas variáveis de ambiente."
            }
            self.send_slack_response(response_url, response_message)
            return

        client = Groq(api_key=groq_api_key)

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_text,
                    }
                ],
                model="llama3-8b-8192", # Substitua pelo modelo que você prefere
            )

            bot_response = chat_completion.choices[0].message.content

            # Formata a resposta para o Slack
            slack_payload = {
                "response_type": "in_channel", # ou "ephemeral"
                "text": bot_response
            }
            self.send_slack_response(response_url, slack_payload)

        except Exception as e:
            error_message = f"Ocorreu um erro ao interagir com a IA: {e}"
            slack_payload = {
                "response_type": "ephemeral",
                "text": error_message
            }
            self.send_slack_response(response_url, slack_payload)

    def send_slack_response(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        try:
            requests.post(url, data=json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar resposta para o Slack: {e}")
