"""
Módulo de Taxonomia Expandida para Engenharia de IA & Dados e IA Generativa no vagas_bot
"""

TAXONOMIA_IA_DADOS = {
    "desenvolvimento_backend": {
        "nome": "Dev Fullstack / Backend",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["backend", "fullstack", "fastapi", "django", "express", "nest.js", "python", "node.js", "api rest", "devops"]
    },
    "ia_ops": {
        "nome": "IA-Ops / MLOps Specialist",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["mlops", "llmops", "langchain", "llamaindex", "vector db", "chromadb", "pinecone", "vllm"]
    },
    "ai_conteudo_texto": {
        "nome": "AI para Conteúdo & Texto (LLM / RAG)",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["llm", "prompt engineering", "rag", "gpt-4", "claude", "fine-tuning", "agentes de ia", "copilot"]
    },
    "ai_video_imagem": {
        "nome": "AI para Vídeo & Imagem",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["stable diffusion", "comfyui", "midjourney", "google veo", "runway", "computer vision", "opencv", "yolo", "visão computacional"]
    },
    "ai_audio_voz": {
        "nome": "AI para Áudio & Voz",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["elevenlabs", "whisper", "tts", "stt", "audio ai", "voice cloning", "síntese de voz"]
    },
    "agentes_automacao": {
        "nome": "Agentes Autônomos & Workflows (n8n/CrewAI)",
        "category": "Desenvolvimento Backend & IA",
        "keywords": ["n8n", "make.com", "crewai", "autogen", "langgraph", "automação de processos", "zapier", "webhooks"]
    },
    "analytics_engineer": {
        "nome": "Analytics Engineer",
        "category": "Dados & Analytics",
        "keywords": ["dbt", "snowflake", "bigquery", "looker", "power bi", "databricks", "sql avançado", "data analyst"]
    },
    "engenharia_dados": {
        "nome": "Engenharia de Dados (ETL & Pipelines)",
        "category": "Dados & Analytics",
        "keywords": ["airflow", "spark", "pyspark", "kafka", "data lake", "data warehouse", "etl", "pipeline de dados"]
    },
    "server_side_tracking": {
        "nome": "Server-Side Tracking (sGTM)",
        "category": "Dados & Analytics",
        "keywords": ["server-side tracking", "sgtm", "google tag manager", "conversion api", "capi", "postback", "web analytics"]
    }
}

TAXONOMIA_AI_GENERATIVA = {
    "ai_generativa": {
        "nome": "IA Generativa & IA para Conteúdo",
        "subcategorias": {
            "ai_conteudo_copy": {
                "nome": "AI para Conteúdo & Copywriting (LLMs/Prompts)",
                "keywords": ["prompt engineer", "llm", "rag", "gpt-4", "claude", "copywriting ia", "ai content", "agente de ia"]
            },
            "ai_midia_audiovisual": {
                "nome": "AI Generativa de Mídia (Vídeo, Imagem e Áudio)",
                "keywords": ["stable diffusion", "comfyui", "midjourney", "google veo", "runway", "elevenlabs", "suno", "imagem ia", "video ia"]
            },
            "ai_ops_agents": {
                "nome": "Engenharia de Agentes & IA-Ops",
                "keywords": ["crewai", "autogen", "langgraph", "vector db", "chromadb", "pinecone", "vllm", "ollama"]
            }
        }
    }
}
