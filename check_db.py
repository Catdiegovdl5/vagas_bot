import sqlite3, os

# Testar todos os possíveis bancos de dados no projeto
for db_name in ['vagas.db', 'jobs.db', 'app.db', 'data.db']:
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    print(f'\n=== {db_name} ===')
    print('Existe:', os.path.exists(db_path))
    if os.path.exists(db_path):
        print('Tamanho:', os.path.getsize(db_path), 'bytes')
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in cursor.fetchall()]
                print('Tabelas:', tables)
                for t in tables:
                    cursor.execute(f'PRAGMA table_info({t})')
                    cols = [c[1] for c in cursor.fetchall()]
                    cursor.execute(f'SELECT COUNT(*) FROM {t}')
                    count = cursor.fetchone()[0]
                    print(f'  {t}: {count} registros, colunas={cols}')
                    if count > 0 and t in ['jobs', 'vagas']:
                        cursor.execute(f'SELECT * FROM {t} LIMIT 2')
                        rows = cursor.fetchall()
                        for row in rows:
                            d = dict(zip(cols, row))
                            print(f'    amostra: { {k:v for k,v in d.items() if v and k != "requirements"} }')
        except Exception as e:
            print('Erro:', e)
