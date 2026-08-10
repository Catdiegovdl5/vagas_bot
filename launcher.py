import os
import time
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def get_latest_mtime(directory="."):
    max_mtime = 0
    ignore_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".vscode", "brain", "logs", "patches"}
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js')):
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime > max_mtime:
                        max_mtime = mtime
                except OSError:
                    pass
    return max_mtime

def kill_process_tree(pid):
    """Safely kills a process and all its children on Windows."""
    try:
        import psutil
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except Exception:
        pass

def ensure_port_free(port=8000):
    """Encerra processos antigos rodando na porta 8000 se houver."""
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr and conn.laddr.port == port:
                        if proc.pid != current_pid:
                            print(f"[Porta {port}] Encerrando processo antigo/conflitante (PID {proc.pid})...")
                            proc.terminate()
                            try:
                                proc.wait(timeout=2)
                            except Exception:
                                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except Exception:
        pass

def start_services():
    ensure_port_free(8000)
    bot_process = None
    
    print("[1/2] Acordando o Sniper Bot (Telegram)...")
    try:
        bot_process = subprocess.Popen([sys.executable, "bot.py"])
    except Exception as e:
        print(f"[Aviso] Não foi possível iniciar o bot.py: {e}")

    print("[2/2] Acordando o Servidor Web FastAPI (http://localhost:8000)...")
    env = os.environ.copy()
    env["LAUNCHER_MANAGED"] = "1"
    app_process = subprocess.Popen([sys.executable, "app.py"], env=env)
    
    return bot_process, app_process

def stop_services(bot_process, app_process):
    if bot_process and bot_process.poll() is None:
        kill_process_tree(bot_process.pid)
    if app_process and app_process.poll() is None:
        kill_process_tree(app_process.pid)
    time.sleep(1)

MAX_RESTART_RETRIES = 5
RESTART_BACKOFF_SECONDS = 5

def main():
    print("=========================================")
    print("   INICIANDO ECOSSISTEMA SNIPER BOT SAAS  ")
    print("=========================================")
    
    bot_process, app_process = start_services()
    last_mtime = get_latest_mtime()
    last_start_time = time.time()
    consecutive_failures = 0
    
    # Abre o navegador automaticamente
    try:
        import webbrowser
        time.sleep(2)
        webbrowser.open("http://localhost:8000/")
    except Exception:
        pass

    print("\n=======================================================")
    print("TUDO PRONTO! PAINEL WEB NO AR EM http://localhost:8000/")
    print("Monitorando alterações em arquivos (.py, .html, .css, .js)...")
    print("Para DESLIGAR tudo, pressione Ctrl+C.")
    print("=======================================================\n")

    try:
        while True:
            time.sleep(2)
            
            # Se o servidor web esteve online por mais de 15s, reseta o contador de falhas consecutivas
            if app_process and app_process.poll() is None:
                if time.time() - last_start_time > 15 and consecutive_failures > 0:
                    consecutive_failures = 0

            # Verifica apenas se o servidor web caiu
            if app_process and app_process.poll() is not None:
                consecutive_failures += 1
                if consecutive_failures > MAX_RESTART_RETRIES:
                    print(f"\n[ERRO CRÍTICO] O Servidor Web caiu {consecutive_failures} vezes consecutivas.")
                    print("Cancelando tentativas de reinicialização para evitar loop infinito.")
                    break

                print(f"\n[ERRO] O Servidor Web caiu inesperadamente (tentativa {consecutive_failures}/{MAX_RESTART_RETRIES}).")
                print(f"Aguardando {RESTART_BACKOFF_SECONDS}s antes de reiniciar...")
                stop_services(bot_process, app_process)
                time.sleep(RESTART_BACKOFF_SECONDS)
                bot_process, app_process = start_services()
                last_start_time = time.time()
                last_mtime = get_latest_mtime()
                continue
                
            # Verifica se algum arquivo mudou
            current_mtime = get_latest_mtime()
            if current_mtime > last_mtime:
                consecutive_failures = 0
                print("\n[HOT-RELOAD] Alteração de arquivo detectada! Reiniciando serviços...")
                stop_services(bot_process, app_process)
                bot_process, app_process = start_services()
                last_start_time = time.time()
                last_mtime = current_mtime

    except KeyboardInterrupt:
        print("\nDesligando sistema de forma manual (Ctrl+C)...")
    except Exception as e:
        print(f"\nQueda detectada no sistema: {e}")
    finally:
        stop_services(bot_process, app_process)
        print("Serviços encerrados.")

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    main()

