from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import re

def scrape(keyword="Python", level="Todos", location="", country="", contract="Todos", **kwargs):
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    target_loc = loc or "Brasil"
    if "Londrina" in target_loc:
        loc_param = "Londrina%2C%20Paran%C3%A1%2C%20Brasil"
    elif "Assaí" in target_loc:
        loc_param = "Assa%C3%AD%2C%20Paran%C3%A1%2C%20Brasil"
    elif target_loc and target_loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
        loc_param = urllib.parse.quote(target_loc)
    else:
        loc_param = "Brasil"
        
    jobs = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # Generic keyword mapping for LinkedIn advanced boolean queries
    keyword_mapping = {
        "especialista em ia": '("Inteligência Artificial" OR "Artificial Intelligence" OR "AI" OR "IA" OR "Generative AI" OR "GenAI" OR "ChatGPT" OR "LLM")',
        "desenvolvedor python": '("Python" OR "Django" OR "FastAPI" OR "Flask" OR "PySpark")',
        "desenvolvedor backend": '("Backend" OR "Back-end" OR "Desenvolvedor Backend" OR "Back End Developer")',
        "desenvolvedor frontend": '("Frontend" OR "Front-end" OR "Desenvolvedor Frontend" OR "Front End Developer")',
        "desenvolvedor fullstack": '("Fullstack" OR "Full-stack" OR "Desenvolvedor Fullstack" OR "Full Stack Developer")',
    }

    kw_clean = keyword.lower().strip()
    
    # Mapeamento completo de termos → queries booleanas para LinkedIn
    keyword_mapping = {
        # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
        # 1. Operações Físicas
        "operações físicas":            '"Operador CNC" OR "Pintor Industrial" OR "Mecânico Industrial" OR "Soldador" OR "Eletricista Industrial" OR "Operador de Produção" OR "Conferente"',
        "operacoes fisicas":            '"Operador CNC" OR "Pintor Industrial" OR "Mecânico Industrial" OR "Soldador" OR "Eletricista Industrial" OR "Operador de Produção" OR "Conferente"',
        "indústria":                    '"Industrial" OR "Fábrica" OR "Operador de Produção" OR "Manutenção Industrial"',
        "industria":                    '"Industrial" OR "Fábrica" OR "Operador de Produção" OR "Manutenção Industrial"',
        "operador cnc":                 '"Operador CNC" OR "Torno CNC" OR "Usinagem"',
        "pintor industrial":            '"Pintor Industrial" OR "Pintura Industrial"',
        "mecânico industrial":          '"Mecânico Industrial" OR "Manutenção Mecânica"',
        "mecanico industrial":          '"Mecânico Industrial" OR "Manutenção Mecânica"',
        "soldador":                     '"Soldador" OR "Soldagem" OR "Caldeireiro"',
        "soldador / caldeireiro":       '"Soldador" OR "Caldeireiro"',
        "eletricista":                  '"Eletricista" OR "Eletricista Industrial"',
        "operador de produção":         '"Operador de Produção" OR "Auxiliar de Produção"',
        "operador de producao":         '"Operador de Produção" OR "Auxiliar de Produção"',
        "auxiliar de produção":         '"Auxiliar de Produção" OR "Linha de Produção"',
        "auxiliar de producao":         '"Auxiliar de Produção" OR "Linha de Produção"',
        "auxiliar de operações":        '"Auxiliar de Operações" OR "Operacional"',
        "auxiliar de operacoes":        '"Auxiliar de Operações" OR "Operacional"',
        "conferente":                   '"Conferente" OR "Conferência de Carga"',

        # 2. Logística
        "logística":                    '"Logística" OR "Almoxarifado" OR "Estoque" OR "Expedição" OR "Supply Chain"',
        "logistica":                    '"Logística" OR "Almoxarifado" OR "Estoque" OR "Expedição" OR "Supply Chain"',
        "assistente de logística":     '"Assistente de Logística" OR "Auxiliar de Logística"',
        "assistente de logistica":     '"Assistente de Logística" OR "Auxiliar de Logística"',
        "auxiliar de logística":        '"Auxiliar de Logística" OR "Logística"',
        "auxiliar de logistica":        '"Auxiliar de Logística" OR "Logística"',
        "auxiliar de almoxarifado":     '"Auxiliar de Almoxarifado" OR "Almoxarifado"',
        "operador de empilhadeira":     '"Operador de Empilhadeira" OR "Empilhadeira"',
        "auxiliar de expedição":        '"Auxiliar de Expedição" OR "Expedição"',
        "auxiliar de expedicao":        '"Auxiliar de Expedição" OR "Expedição"',
        "motorista":                    '"Motorista" OR "Condutor"',
        "almoxarife":                   '"Almoxarife" OR "Estoquista"',

        # 3. Administrativo
        "administrativo":               '"Assistente Administrativo" OR "Auxiliar Administrativo" OR "Escritório" OR "Backoffice"',
        "assistente administrativo":    '"Assistente Administrativo" OR "Auxiliar Administrativo"',
        "auxiliar administrativo":      '"Auxiliar Administrativo" OR "Assistente Administrativo"',
        "recepcionista":                '"Recepcionista" OR "Recepção"',
        "auxiliar de escritório":       '"Auxiliar de Escritório" OR "Escritório"',
        "auxiliar de escritorio":       '"Auxiliar de Escritório" OR "Escritório"',
        "data entry":                   '"Data Entry" OR "Digitador" OR "Entrada de Dados"',
        "digitador":                    '"Digitador" OR "Data Entry"',
        "assistente financeiro":        '"Assistente Financeiro" OR "Contas a Pagar" OR "Contas a Receber"',

        # 4. Criativos de Performance
        "criativos de performance":     '"Designer de Performance" OR "Copywriter" OR "Motion Designer" OR "Editor de Vídeo" OR "Gestor de Tráfego"',
        "criativos":                    '"Designer" OR "Copywriter" OR "Editor de Vídeo" OR "Criativos"',
        "design":                       '"Designer Gráfico" OR "Graphic Designer" OR "Figma"',
        "designer conversional":        '"Designer Conversional" OR "Chatbot Designer"',
        "copywriter":                   '"Copywriter" OR "Copywriting" OR "Redator"',
        "criador de anúncios":          '"Criador de Anúncios" OR "Ad Creator" OR "Designer de Performance"',
        "criador de anuncios":          '"Criador de Anúncios" OR "Ad Creator" OR "Designer de Performance"',
        "motion designer":              '"Motion Designer" OR "Motion Design" OR "After Effects"',
        "editor de vídeo":              '"Editor de Vídeo" OR "Video Editor" OR "Premiere"',
        "editor de video":              '"Editor de Vídeo" OR "Video Editor" OR "Premiere"',
        "gestor de tráfego":            '"Gestor de Tráfego" OR "Traffic Manager" OR "Meta Ads" OR "Google Ads"',
        "gestor de trafego":            '"Gestor de Tráfego" OR "Traffic Manager" OR "Meta Ads" OR "Google Ads"',
        "designer gráfico":             '"Designer Gráfico" OR "Graphic Designer"',
        "designer grafico":             '"Designer Gráfico" OR "Graphic Designer"',

        # 5. Inteligência de Vendas
        "inteligência de vendas":       '"SDR" OR "BDR" OR "Inside Sales" OR "Sales Ops" OR "Executivo de Vendas"',
        "inteligencia de vendas":       '"SDR" OR "BDR" OR "Inside Sales" OR "Sales Ops" OR "Executivo de Vendas"',
        "vendas":                       '"Executivo de Vendas" OR "Consultor de Vendas" OR "Comercial"',
        "sdr":                          '"SDR" OR "BDR" OR "Sales Development" OR "Inside Sales"',
        "bdr":                          '"BDR" OR "Business Development" OR "SDR"',
        "inside sales":                 '"Inside Sales" OR "Vendas Internas"',
        "analista de sales ops":        '"Sales Ops" OR "Analista de Vendas"',
        "executivo de vendas":          '"Executivo de Vendas" OR "Account Executive"',
        "crm":                          '"Analista de CRM" OR "CRM Specialist" OR "HubSpot"',
        "analista de crm":              '"Analista de CRM" OR "CRM Specialist"',
        "analista de vendas":           '"Analista de Vendas" OR "Sales Analyst"',

        # 6. Engenharia de IA/Dados
        "engenharia de ia/dados":       '"Engenheiro de Dados" OR "Engenheiro de IA" OR "Machine Learning" OR "Data Scientist"',
        "engenharia de ia dados":       '"Engenheiro de Dados" OR "Engenheiro de IA" OR "Machine Learning" OR "Data Scientist"',
        "engenharia de dados":          '"Engenheiro de Dados" OR "Data Engineer" OR "ETL" OR "Spark"',
        "engenheiro de dados":          '"Engenheiro de Dados" OR "Data Engineer"',
        "data engineer":                '"Data Engineer" OR "Engenheiro de Dados"',
        "engenheiro de ia":              '"AI Engineer" OR "Engenheiro de IA"',
        "machine learning":             '"Machine Learning Engineer" OR "ML Engineer"',
        "cientista de dados":            '"Cientista de Dados" OR "Data Scientist"',
        "analista de dados":            '"Analista de Dados" OR "Data Analyst"',

        # IA / AI
        "especialista em ia":        '"Especialista em IA" OR "AI Specialist" OR "Inteligência Artificial" OR "Artificial Intelligence" OR "LLM" OR "GenAI" OR "Generative AI" OR "ChatGPT" OR "Prompt Engineer"',
        "especialista em ia generativa": '"IA Generativa" OR "Generative AI" OR "GenAI" OR "Midjourney" OR "DALL-E" OR "Stable Diffusion" OR "LLM" OR "Sora" OR "Flux"',
        "desenvolvedor de agentes ia": '"Agentes de IA" OR "AI Agents" OR "LangChain" OR "CrewAI" OR "AutoGen" OR "n8n" OR "Flowise" OR "VAPI"',
        "prompt engineer":           '"Prompt Engineer" OR "Prompt Engineering" OR "Engenharia de Prompt" OR "LLM" OR "ChatGPT" OR "Gemini"',
        "machine learning engineer": '"Machine Learning" OR "ML Engineer" OR "MLOps" OR "Deep Learning" OR "TensorFlow" OR "PyTorch" OR "Scikit-learn" OR "LLMOps"',
        # Desenvolvimento
        "desenvolvedor python":       '"Python" OR "Django" OR "FastAPI" OR "Flask" OR "PySpark" OR "Celery"',
        "desenvolvedor backend":      '"Backend" OR "Back-end" OR "Desenvolvedor Backend" OR "API REST" OR "Microsserviços" OR "Docker" OR "Node.js"',
        "desenvolvedor node":         '"Node.js" OR "NodeJS" OR "NestJS" OR "Express" OR "JavaScript" OR "TypeScript"',
        "desenvolvedor react":        '"React" OR "ReactJS" OR "Next.js" OR "TypeScript" OR "Frontend" OR "Front-end"',
        "desenvolvedor fullstack":    '"Fullstack" OR "Full-stack" OR "Full Stack Developer" OR "Web Developer"',
        "desenvolvedor django":       '"Django" OR "Python" OR "DRF" OR "Django REST Framework" OR "Backend"',
        "desenvolvedor fastapi":      '"FastAPI" OR "Fast-API" OR "Python" OR "API REST" OR "Backend"',
        "desenvolvedor rpa":          '"RPA" OR "Automação" OR "UiPath" OR "Power Automate" OR "Blue Prism" OR "n8n" OR "Make" OR "Selenium"',
        "desenvolvedor junior python": '"Python Junior" OR "Desenvolvedor Python" OR "Django" OR "FastAPI" OR "Estágio Python"',
        "desenvolvedor junior react": '"React Junior" OR "Desenvolvedor Frontend" OR "ReactJS" OR "Next.js" OR "JavaScript Junior"',
        "desenvolvedor junior fullstack": '"Fullstack Junior" OR "Web Developer" OR "Desenvolvedor Fullstack"',
        "desenvolvedor pleno python": '"Python Pleno" OR "Desenvolvedor Python Pleno" OR "Django Pleno" OR "FastAPI"',
        "desenvolvedor pleno react":  '"React Pleno" OR "Frontend Pleno" OR "Next.js" OR "TypeScript Pleno"',
        "desenvolvedor pleno fullstack": '"Fullstack Pleno" OR "Full Stack Pleno" OR "Desenvolvedor Web Pleno"',
        # Dados & Analytics
        "analista de analytics":     '"Analytics" OR "Google Analytics" OR "GA4" OR "GTM" OR "Looker Studio" OR "Tracking" OR "CAPI"',
        "analista sql":              '"SQL" OR "MySQL" OR "PostgreSQL" OR "DBA" OR "Banco de Dados" OR "SQL Server"',
        "analista de power bi":      '"Power BI" OR "Business Intelligence" OR "DAX" OR "Power Query" OR "BI" OR "Looker" OR "Tableau"',
        "analista de dados junior":  '"Analista de Dados Junior" OR "Data Analyst" OR "SQL Junior" OR "Power BI" OR "Python"',
        "analista de dados pleno":   '"Analista de Dados Pleno" OR "Data Analyst Pleno" OR "SQL" OR "Power BI" OR "Python"',
        # Marketing & Growth
        "gestor de trafego pleno":   '"Gestor de Tráfego Pleno" OR "Tráfego Pago" OR "Facebook Ads" OR "Google Ads" OR "Meta Ads"',
        "growth hacker":             '"Growth" OR "Growth Hacking" OR "CRO" OR "Aquisição" OR "Funil" OR "Head of Growth"',
        "analista de marketing digital": '"Marketing Digital" OR "Analista de Marketing" OR "Inbound Marketing" OR "Content Marketing" OR "Social Media" OR "Email Marketing"',
        "especialista em seo":       '"SEO" OR "Search Engine Optimization" OR "Otimização" OR "Semrush" OR "Ahrefs" OR "Google Search Console"',
        "analista de marketing junior": '"Analista de Marketing Junior" OR "Marketing Digital" OR "Social Media" OR "Conteúdo"',
        # Design & Video
        "video maker":               '"Videomaker" OR "Video Maker" OR "Produtor de Vídeo" OR "Filmmaker" OR "Reels" OR "YouTube"',
        "social media":              '"Social Media" OR "Redes Sociais" OR "Instagram" OR "TikTok" OR "Conteúdo Digital" OR "Community Manager"',
        "ux designer":               '"UX Designer" OR "UI Designer" OR "UX/UI" OR "User Experience" OR "Figma" OR "Product Designer" OR "Wireframe"',
        # Administrativo / RH / Suporte
        "analista de rh":            '"Analista de RH" OR "Recursos Humanos" OR "Recrutamento" OR "R&S" OR "Folha de Pagamento" OR "Business Partner"',
        "suporte tecnico n1":        '"Suporte Técnico" OR "Helpdesk" OR "Service Desk" OR "N1" OR "Tickets" OR "TI"',
        "assistente de faturamento": '"Assistente de Faturamento" OR "Nota Fiscal" OR "Billing" OR "Faturamento"',
    }
    
    boolean_query = keyword_mapping.get(kw_clean, keyword)

    # Level filters
    level_filter = ""
    detected_level = level.lower().strip()
    if detected_level == "todos":
        if "junior" in kw_clean or "júnior" in kw_clean or "jr" in kw_clean or "estágio" in kw_clean or "estagio" in kw_clean or "estagiário" in kw_clean or "estagiária" in kw_clean:
            detected_level = "junior"
        elif "pleno" in kw_clean or "pl" in kw_clean or "mid" in kw_clean:
            detected_level = "pleno"
        elif "senior" in kw_clean or "sênior" in kw_clean or "sr" in kw_clean or "lead" in kw_clean:
            detected_level = "senior"

    if detected_level == "junior":
        level_filter = '("Júnior" OR "Junior" OR "Jr" OR "Estágio" OR "Estagiário" OR "Estagiária")'
    elif detected_level == "pleno":
        level_filter = '("Pleno" OR "Mid" OR "Mid-level" OR "Pl")'
    elif detected_level == "senior":
        level_filter = '("Sênior" OR "Senior" OR "Sr" OR "Lead")'

    # Contract filters
    contract_filter = ""
    contract_param = ""
    if contract.upper() == "PJ":
        contract_filter = '("PJ" OR "Pessoa Jurídica" OR "Contractor" OR "Prestador" OR "Prestação de Serviços")'
        contract_param = "&f_JT=C"
    elif contract.upper() == "CLT":
        contract_filter = '("CLT" OR "Efetivo" OR "Carteira Assinada")'
        contract_param = "&f_JT=F"

    # Workplace Type (Remote) filter
    remote_filter = ""
    wt_param = ""
    if "remote" in c_str or "remoto" in c_str or "remote" in l_str or "remoto" in l_str:
        remote_filter = '("Remoto" OR "Remote")'
        wt_param = "&f_WT=2"

    # Combine parts into query
    query_parts = [boolean_query]
    if level_filter:
        query_parts.append(level_filter)
    if contract_filter:
        query_parts.append(contract_filter)
    if remote_filter:
        query_parts.append(remote_filter)

    if len(query_parts) > 1:
        final_query = " AND ".join(query_parts)
    else:
        final_query = boolean_query

    encoded_kw = urllib.parse.quote(final_query)
    
    # Return at least 10 valid jobs. Increment start offset (0, 25, 50, 75, 100, 125, etc.)
    offsets = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250]
    
    for start in offsets:
        url = f"https://br.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_kw}&location={loc_param}&start={start}{contract_param}{wt_param}"
        print(f"[LinkedIn Scraper] Request URL: {url}")
        
        try:
            response = requests.get(url, impersonate="chrome110", headers=headers, timeout=15)
            if response.status_code != 200:
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("li")
            if not cards:
                break
                
            for card in cards:
                    
                title_el = card.find("h3", class_="base-search-card__title")
                title = title_el.text.strip() if title_el else "Sem Título"
                
                comp_el = card.find("h4", class_="base-search-card__subtitle")
                company = comp_el.text.strip() if comp_el else "Empresa Confidencial"
                
                link_el = card.find("a", class_="base-card__full-link")
                link = link_el.get("href", "") if link_el else ""
                
                if link and "?" in link:
                    link = link.split("?")[0]
                    
                loc_el = card.find("span", class_="job-search-card__location")
                location = loc_el.text.strip() if loc_el else "Remoto/Brasil"
                
                if title == "Sem Título" or not link:
                    continue
                    
                # Extract job_id
                job_id = None
                
                # Check data-entity-urn
                div_card = card.find(attrs={"data-entity-urn": True})
                if div_card:
                    urn = div_card["data-entity-urn"]
                    if "jobPosting:" in urn:
                        job_id = urn.split("jobPosting:")[-1].strip()
                
                if not job_id and card.has_attr("data-entity-urn"):
                    urn = card["data-entity-urn"]
                    if "jobPosting:" in urn:
                        job_id = urn.split("jobPosting:")[-1].strip()
                        
                # Extract from link URL
                if not job_id and link:
                    match = re.search(r'/view/(?:.+?-)?(\d+)', link)
                    if match:
                        job_id = match.group(1)
                    else:
                        match_fallback = re.search(r'\b\d{8,12}\b', link)
                        if match_fallback:
                            job_id = match_fallback.group(0)
                            
                if not job_id:
                    continue
                    
                # Fetch full description using guest API
                desc_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                description_text = ""
                
                try:
                    desc_response = requests.get(desc_url, headers=headers, impersonate="chrome110", timeout=10)
                    if desc_response.status_code == 200:
                        desc_soup = BeautifulSoup(desc_response.text, "html.parser")
                        
                        desc_container = desc_soup.find(class_="show-more-less-html__markup") or desc_soup.find(class_="description__text") or desc_soup.find(class_="jobs-description")
                        if not desc_container:
                            desc_container = desc_soup
                        
                        description_text = desc_container.get_text(separator="\n").strip()
                        
                except Exception as desc_e:
                    print(f"Erro ao buscar detalhes da vaga {job_id}: {desc_e}")
                    
                # Setup proper job_type returning
                ret_job_type = "PJ" if (contract or "Todos").upper() == "PJ" else "CLT"
                
                # Garantir descrição completa ou fallback descritivo sem descartar a vaga
                if not description_text or len(description_text) < 50:
                    description_text = f"Oportunidade para {title} na empresa {company}. Excelente oportunidade para profissional com foco em {keyword}. Para mais detalhes sobre os requisitos completos, responsabilidades da posição e processo seletivo, acesse a página oficial da vaga através do link direto fornecido."
                
                job_obj = {
                    "platform": "LinkedIn",
                    "title": title,
                    "company": company,
                    "budget": "A Combinar",
                    "link": link,
                    "job_type": ret_job_type,
                    "profession": keyword,
                    "level": level,
                    "requirements": description_text
                }
                try:
                    from bot import classify_job_profession
                    job_obj = classify_job_profession(job_obj)
                except Exception:
                    pass
                jobs.append(job_obj)
                    
        except Exception as e:
            print(f"Erro no scraper LinkedIn na página {start}: {e}")
            
    return jobs
