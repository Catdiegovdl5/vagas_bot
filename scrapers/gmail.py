import os
import re
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# Definimos que o robô só pode ler e-mails, para segurança
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    creds = None
    
    # O token armazena o acesso persistente do usuário.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Se não houver credencial válida, tenta atualizar ou retorna erro em ambiente headless
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as refresh_err:
                print(f"WARNING: Falha ao atualizar credenciais do Gmail: {refresh_err}")
                return []
        else:
            print("WARNING: O arquivo token.json está ausente ou inválido, e não há token de atualização disponível. Evitando execução do servidor local de OAuth em ambiente headless.")
            return []
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    jobs = []
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Busca usando a sintaxe nativa do Gmail
        query = 'subject:vaga OR subject:alert'
        results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
        messages = results.get('messages', [])

        for msg in messages:
            try:
                msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                
                payload = msg_data.get('payload', {})
                parts = payload.get('parts', [])
                
                body = ""
                
                def decode_gmail_body(raw_data):
                    if not raw_data:
                        return ""
                    try:
                        if isinstance(raw_data, bytes):
                            raw_data = raw_data.decode('utf-8', errors='ignore')
                        # Fix base64 padding
                        rem = len(raw_data) % 4
                        if rem:
                            raw_data += '=' * (4 - rem)
                        decoded_bytes = base64.urlsafe_b64decode(raw_data)
                    except Exception:
                        try:
                            decoded_bytes = base64.urlsafe_b64decode(raw_data)
                        except Exception:
                            return ""
                    
                    # Try alternative encodings
                    for encoding in ['utf-8', 'iso-8859-1', 'latin-1', 'cp1252', 'ascii']:
                        try:
                            return decoded_bytes.decode(encoding)
                        except Exception:
                            continue
                    return decoded_bytes.decode('utf-8', errors='ignore')

                if parts:
                    for part in parts:
                        if part.get('mimeType') == 'text/html':
                            data = part['body'].get('data')
                            if data:
                                body = decode_gmail_body(data)
                            break
                else:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = decode_gmail_body(data)

                if not body:
                    continue

                soup = BeautifulSoup(body, 'html.parser')
                links = soup.find_all('a')
                
                for a in links:
                    href = a.get('href', '')
                    text = a.text.strip()
                    
                    if ("jobs/view" in href or "viewjob" in href or "job-post" in href or "rc/clk" in href):
                        if len(text) > 4:
                            jobs.append({
                                "platform": "Gmail API",
                                "title": text,
                                "company": "Notificação por E-mail",
                                "budget": "A Combinar",
                                "link": href,
                                "job_type": "Diversos",
                                "profession": keyword,
                                "level": level,
                                "requirements": "Vaga coletada pela API Oficial do Google."
                            })
            except Exception as item_err:
                print(f"Erro ao parsear mensagem {msg.get('id')}: {item_err}")
                continue

    except Exception as e:
        print(f"Erro no scraper Gmail API: {e}")

    unique_jobs = {j["link"]: j for j in jobs}
    return list(unique_jobs.values())[:20]
