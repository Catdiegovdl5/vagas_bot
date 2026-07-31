import sys
from bot import is_job_relevant

def run_verification():
    # 3. Define settings dictionary
    settings = {
        "level": "Todos",
        "location": "Todos",
        "contract": "Todos"
    }

    # 4. Define 5 creative AI jobs (must return True under 'Especialista em IA Generativa')
    creative_ai_jobs = [
        {"title": "Copywriter ChatGPT", "requirements": ""},
        {"title": "Designer Midjourney", "requirements": ""},
        {"title": "Editor de Vídeo - IA", "requirements": ""},
        {"title": "Gestor de Tráfego com IA", "requirements": ""},
        {"title": "Redator SEO com IA (Claude/ChatGPT)", "requirements": ""}
    ]

    # 5. Define 5 non-AI jobs (must return False under 'Especialista em IA Generativa')
    non_ai_jobs = [
        {"title": "Desenvolvedor Java", "requirements": ""},
        {"title": "Analista de RH", "requirements": ""},
        {"title": "Vendedor", "requirements": ""},
        {"title": "Assistente Administrativo", "requirements": ""},
        {"title": "Gestor de Tráfego", "requirements": ""}
    ]

    keyword = "Especialista em IA Generativa"

    print("\033[94m[INFO] Starting verification of creative AI jobs filtering logic...\033[0m")
    
    # 6. Call is_job_relevant and mathematically assert
    print("\033[93m[TEST] Verifying creative AI jobs (Expected: True)...\033[0m")
    for job in creative_ai_jobs:
        result = is_job_relevant(job, keyword, settings)
        print(f"  Job: '{job['title']}' -> Result: {result}")
        assert result is True, f"Assertion failed: Job '{job['title']}' should be relevant under '{keyword}' but got {result}"

    print("\033[93m[TEST] Verifying non-AI jobs (Expected: False)...\033[0m")
    for job in non_ai_jobs:
        result = is_job_relevant(job, keyword, settings)
        print(f"  Job: '{job['title']}' -> Result: {result}")
        assert result is False, f"Assertion failed: Job '{job['title']}' should NOT be relevant under '{keyword}' but got {result}"

    print("\n\033[92m=============================================\033[0m")
    print("\033[92m[SUCCESS] All 10 assertions passed successfully!\033[0m")
    print("\033[92m[SUCCESS] 100% of jobs match expected relevance.\033[0m")
    print("\033[92m=============================================\033[0m")

if __name__ == "__main__":
    run_verification()
