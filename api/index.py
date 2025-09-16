import os
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Pega a chave de API da variável de ambiente
API_KEY = os.getenv("GENAI_API_KEY")

# Inicializa o modelo, passando a chave de API diretamente aqui
model = genai.GenerativeModel('gemini-1.5-flash', api_key=API_KEY)

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
                gemini_response = model.generate_content(slack_text)
                response = gemini_response.text

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                '{"response_type": "in_channel", "text": "' + response.replace('"', '\\"') + '"}'
                .encode('utf-8')
            )

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                '{"response_type": "ephemeral", "text": "Ocorreu um erro: ' + str(e) + '"}'
                .encode('utf-8')
            )
