"""
Motor de Auto-Apply: Preenche formulários e realiza candidaturas automáticas / simplificadas
usando os dados do currículo do candidato e automação resiliente.

Estratégia & Recursos:
- Stealth Chrome com camuflagem (--disable-blink-features=AutomationControlled, user-agent desktop)
- Handler específico Gupy (GupyAutoApplyHandler) com seletores flexíveis
- Handler específico LinkedIn (LinkedInAutoApplyHandler) com suporte a Easy Apply
- Persistência de sessão de cookies JSON (gupy_cookies.json, linkedin_cookies.json)
- Captura de telas (screenshots) para diagnósticos de erro em falhas imprevisíveis
- Fallback seguro via e-mail e geração de links diretos de candidatura
"""

import os
import re
import json
import time
import sqlite3
import requests
from loguru import logger

# --- Utilitários de Extração de Dados do Currículo ---

def extract_email_from_text(text: str) -> str:
    """Extrai o primeiro e-mail encontrado no texto da vaga ou currículo."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def prepare_candidate_data(user_id: str = None) -> dict:
    """Lê o currículo e extrai dados básicos do candidato para preenchimento de formulários."""
    curriculo_path = f"curriculo_{user_id}.txt" if user_id else "curriculo.txt"
    data = {
        "name": "Diego Santos",
        "email": "diego@example.com",
        "phone": "+5511999999999",
        "resume_text": "",
        "resume_pdf_path": "temp_curriculo.pdf"
    }
    
    if os.path.exists(curriculo_path):
        try:
            with open(curriculo_path, "r", encoding="utf-8") as f:
                text = f.read()
                data["resume_text"] = text
                
                email = extract_email_from_text(text)
                if email:
                    data["email"] = email
                    
                phone_pattern = r'(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}'
                phone_match = re.search(phone_pattern, text)
                if phone_match:
                    data["phone"] = phone_match.group(0)
                    
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if lines:
                    first_line = lines[0]
                    if '@' not in first_line and not re.search(r'\d{5,}', first_line):
                        data["name"] = first_line
        except Exception as e:
            logger.warning(f"Erro ao ler currículo em {curriculo_path}: {e}")
    
    return data


# --- Configuração do Navegador Stealth Chrome ---

def get_stealth_chrome_options():
    """Retorna opções configuradas do Chrome para navegação furtiva (Stealth)."""
    try:
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options
    except ImportError:
        return None


def take_error_screenshot(driver, prefix="error"):
    """Salva captura de tela do navegador para diagnósticos em caso de falha."""
    try:
        os.makedirs("logs/screenshots", exist_ok=True)
        filename = f"logs/screenshots/{prefix}_{int(time.time())}.png"
        driver.save_screenshot(filename)
        logger.info(f"Screenshot de diagnóstico salvo em: {filename}")
        return filename
    except Exception as e:
        logger.warning(f"Não foi possível salvar screenshot de erro: {e}")
        return None


def load_cookies_to_driver(driver, cookies_file_path: str, domain: str):
    """Carrega cookies salvos em JSON para manter a sessão autenticada no navegador."""
    if os.path.exists(cookies_file_path):
        try:
            with open(cookies_file_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                driver.get(domain)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception:
                        pass
            logger.info(f"Cookies carregados com sucesso de {cookies_file_path}")
            return True
        except Exception as e:
            logger.warning(f"Erro ao carregar cookies de {cookies_file_path}: {e}")
    return False


# --- Handlers Específicos por Plataforma ---

class GupyAutoApplyHandler:
    """Handler especializado em automação de candidaturas na plataforma Gupy."""
    
    @staticmethod
    def apply(job_url: str, candidate: dict) -> dict:
        cookies_path = "gupy_cookies.json"
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = get_stealth_chrome_options()
            if not options:
                return apply_via_gupy(job_url, candidate)

            driver = webdriver.Chrome(options=options)
            try:
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                load_cookies_to_driver(driver, cookies_path, "https://www.gupy.io")
                driver.get(job_url)
                time.sleep(3)
                
                # Aceita cookies/termos de uso se existirem
                try:
                    cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar') or contains(text(), 'Concordar')]")
                    cookie_btn.click()
                    time.sleep(1)
                except Exception:
                    pass
                
                # Procura botões flexíveis de candidatura
                apply_selectors = [
                    "//button[contains(text(), 'Candidatar-se')]",
                    "//button[contains(text(), 'Candidatar')]",
                    "//a[contains(text(), 'Candidatar-se')]",
                    "//button[@id='apply-button']"
                ]
                
                applied = False
                for sel in apply_selectors:
                    try:
                        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, sel)))
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(1)
                        btn.click()
                        applied = True
                        logger.info("Clique no botão de candidatura da Gupy realizado com sucesso!")
                        break
                    except Exception:
                        continue
                        
                if applied:
                    return {
                        "success": True,
                        "method": "gupy_selenium",
                        "message": "Candidatura iniciada com sucesso na Gupy.",
                        "apply_url": job_url
                    }
                else:
                    take_error_screenshot(driver, "gupy_apply_fail")
                    return apply_via_gupy(job_url, candidate)
                    
            finally:
                driver.quit()
        except Exception as e:
            logger.warning(f"GupyAutoApplyHandler Selenium fallback: {e}")
            return apply_via_gupy(job_url, candidate)


class LinkedInAutoApplyHandler:
    """Handler especializado em automação de candidatura simplificada (Easy Apply) no LinkedIn."""
    
    @staticmethod
    def apply(job_url: str, candidate: dict) -> dict:
        cookies_path = "linkedin_cookies.json"
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = get_stealth_chrome_options()
            if not options:
                return {
                    "success": False,
                    "method": "linkedin_redirect",
                    "message": "LinkedIn Easy Apply requer login. Link direto gerado.",
                    "apply_url": job_url
                }

            driver = webdriver.Chrome(options=options)
            try:
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                load_cookies_to_driver(driver, cookies_path, "https://www.linkedin.com")
                driver.get(job_url)
                time.sleep(3)
                
                # Procura o botão de Candidatura Simplificada
                easy_apply_selectors = [
                    "//button[contains(@class, 'jobs-apply-button') and contains(., 'Candidatura')]",
                    "//button[contains(., 'Easy Apply') or contains(., 'Candidatura Simplificada')]"
                ]
                
                found_easy = False
                for sel in easy_apply_selectors:
                    try:
                        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, sel)))
                        btn.click()
                        found_easy = True
                        logger.info("Botão Candidatura Simplificada (Easy Apply) acionado!")
                        break
                    except Exception:
                        continue
                        
                if found_easy:
                    time.sleep(2)
                    return {
                        "success": True,
                        "method": "linkedin_easy_apply",
                        "message": "Modal de Candidatura Simplificada acionado com sucesso.",
                        "apply_url": job_url
                    }
                else:
                    return {
                        "success": False,
                        "method": "linkedin_redirect",
                        "message": "Vaga exige candidatura externa no site da empresa.",
                        "apply_url": job_url
                    }
            finally:
                driver.quit()
        except Exception as e:
            logger.warning(f"LinkedInAutoApplyHandler fallback: {e}")
            return {
                "success": False,
                "method": "linkedin_redirect",
                "message": f"LinkedIn candidatura redirecionada: {e}",
                "apply_url": job_url
            }


# --- Funções de Fallback e Retrocompatibilidade ---

def apply_via_gupy(job_url: str, candidate: dict) -> dict:
    """Retorna resposta segura com link direto para candidatura na Gupy."""
    return {
        "success": False,
        "method": "gupy_redirect",
        "message": "Gupy exige login do candidato. Link direto gerado.",
        "apply_url": job_url
    }


def apply_via_email(job: dict, candidate: dict) -> dict:
    """Verifica se a vaga contém um e-mail de contato e prepara a candidatura via e-mail."""
    job_text = job.get("requirements", "") + " " + job.get("title", "")
    contact_email = extract_email_from_text(job_text)
    
    if not contact_email:
        return {
            "success": False,
            "method": "no_email",
            "message": "Nenhum e-mail de contato encontrado na vaga."
        }
    
    return {
        "success": True,
        "method": "email",
        "message": f"E-mail de candidatura preparado para: {contact_email}",
        "contact_email": contact_email,
        "subject": f"Candidatura: {job.get('title', 'Vaga')} - {candidate.get('name', 'Candidato')}",
        "body": f"""Prezados,

Meu nome é {candidate.get('name', 'Candidato')} e venho por meio deste me candidatar à vaga de {job.get('title', 'a vaga anunciada')}.

Segue meu currículo em anexo para análise.

Atenciosamente,
{candidate.get('name', 'Candidato')}
{candidate.get('email', '')}
{candidate.get('phone', '')}
""",
        "attachment": candidate.get("resume_pdf_path", "")
    }


def auto_apply(job: dict, user_id: str = None) -> dict:
    """
    Motor principal de Auto-Apply. Decide a melhor estratégia de candidatura
    baseada na plataforma de origem da vaga.
    """
    candidate = prepare_candidate_data(user_id)
    platform = job.get("platform", "").lower()
    link = job.get("link", "")
    
    result = {
        "success": False,
        "method": "manual",
        "message": "Aplique manualmente clicando no link da vaga.",
        "apply_url": link
    }
    
    try:
        if "gupy" in platform:
            result = GupyAutoApplyHandler.apply(link, candidate)
        elif "linkedin" in platform:
            result = LinkedInAutoApplyHandler.apply(link, candidate)
        else:
            email_result = apply_via_email(job, candidate)
            if email_result["success"]:
                result = email_result
            else:
                result["apply_url"] = link
    except Exception as e:
        logger.error(f"Erro no Auto-Apply: {e}")
        result["message"] = f"Erro: {e}"
    
    return result


def apply_to_job(job_link: str, resume_path: str, candidate: dict, mock_ats_url: str = None) -> bool:
    """Envia candidatura com currículo anexado para ATS ou servidor de testes."""
    if isinstance(candidate, str):
        mock_ats_url = candidate
        candidate = {"name": "Diego Candidate", "email": "diego@example.com"}

    if not mock_ats_url:
        mock_ats_url = os.getenv("MOCK_ATS_URL", "http://127.0.0.1:8081/apply")

    if not os.path.exists(resume_path):
        with open(resume_path, "wb") as f:
            f.write(b"%PDF-1.4 Mock PDF Content")

    try:
        with open(resume_path, "rb") as f:
            files = {"resume": (os.path.basename(resume_path), f, "application/pdf")}
            data = {
                "job_link": job_link,
                "name": candidate.get("name", "Diego Candidate"),
                "email": candidate.get("email", "diego@example.com")
            }
            response = requests.post(mock_ats_url, data=data, files=files, timeout=5)
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    return res_data.get("status") == "success"
                except Exception:
                    return False
            return False
    except Exception as e:
        logger.warning(f"Auto-apply HTTP request para {mock_ats_url} erro: {e}")
        return False


def run_auto_apply(db_path: str, resume_path: str, candidate: dict, mock_ats_url: str = None) -> int:
    """Executa o ciclo de auto-apply no banco de dados SQLite registrando status APPLIED ou FAILED."""
    if isinstance(candidate, str):
        mock_ats_url = candidate
        candidate = {"name": "Diego Candidate", "email": "diego@example.com"}

    import uuid
    batch_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute('PRAGMA busy_timeout = 30000')
    conn.execute('PRAGMA journal_mode=WAL')
    try:
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'pending'")
        except sqlite3.OperationalError:
            pass
            
        try:
            c.execute("ALTER TABLE jobs ADD COLUMN score INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
            
        c.execute("UPDATE jobs SET status = ? WHERE score >= 80 AND (status = 'pending' OR status IS NULL)", (f"applying_{batch_id}",))
        conn.commit()

        c.execute("SELECT link FROM jobs WHERE status = ?", (f"applying_{batch_id}",))
        jobs = c.fetchall()
        
        applied_count = 0
        for (link,) in jobs:
            success = apply_to_job(link, resume_path, candidate, mock_ats_url)
            if success:
                applied_count += 1
            new_status = "applied" if success else "failed"
            c.execute("UPDATE jobs SET status = ? WHERE link = ?", (new_status, link))
            
        conn.commit()
    finally:
        conn.close()
            
    return applied_count
