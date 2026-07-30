import os
import time
import subprocess
import sys
import psutil

def get_latest_mtime(directory="."):
    max_mtime = 0
    # Avoid scanning too many unnecessary folders
    ignore_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".vscode", "brain"}
    
    for root, dirs, files in os.walk(directory):
        # Remove ignored directories in-place
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
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def start_services():
    print("\n[1/2] Acordando o Sniper Bot (Telegram)...")
    bot_process = subprocess.Popen([sys.executable, "bot.py"])

    print("[2/2] Acordando o Servidor Web (FastAPI)...")
    app_process = subprocess.Popen([sys.executable, "app.py"])
    
    return bot_process, app_process

def stop_services(bot_process, app_process):
    print("\n[!] Encerrando processos antigos...")
    if bot_process:
        kill_process_tree(bot_process.pid)
    if app_process:
        kill_process_tree(app_process.pid)
    
    # Optional wait to ensure port is freed
    time.sleep(1)

def main():
    print("=========================================")
    print("🚀 INICIANDO ECOSSISTEMA (HOT-RELOAD) 🚀")
    print("=========================================")
    
    # Initial startup
    bot_process, app_process = start_services()
    last_mtime = get_latest_mtime()
    
    print("\n=======================================================")
    print("TUDO PRONTO! O ECOSSISTEMA NATIVO ESTÁ NO AR.")
    print("Monitorando alterações em arquivos (.py, .html, .css, .js)...")
    print("Para DESLIGAR tudo, pressione Ctrl+C.")
    print("=======================================================\n")

    try:
        while True:
            time.sleep(2)
            
            # Check if any process died unexpectedly
            bot_died = bot_process.poll() is not None
            app_died = app_process.poll() is not None
            
            if bot_died or app_died:
                print("\n[ERRO] Um dos serviços caiu inesperadamente. Reiniciando...")
                stop_services(bot_process, app_process)
                bot_process, app_process = start_services()
                last_mtime = get_latest_mtime()
                continue
                
            # Check for file changes
            current_mtime = get_latest_mtime()
            if current_mtime > last_mtime:
                print("\n[♻️ HOT-RELOAD] Alteração de arquivo detectada! Reiniciando serviços...")
                stop_services(bot_process, app_process)
                bot_process, app_process = start_services()
                last_mtime = current_mtime
                print("\n[✅ HOT-RELOAD] Serviços reiniciados com sucesso.")

    except KeyboardInterrupt:
        print("\nDesligando sistema de forma manual (Ctrl+C)...")
    except Exception as e:
        print(f"\nQueda detectada no sistema: {e}")
    finally:
        print("Limpando subprocessos e portas...")
        stop_services(bot_process, app_process)
        print("Serviços encerrados. Volte sempre!")

if __name__ == "__main__":
    # Ensure psutil is installed for process tree killing
    try:
        import psutil
    except ImportError:
        print("Instalando psutil nativamente para gerenciamento de processos...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
        
    main()
