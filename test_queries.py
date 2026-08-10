"""
Test the new listar_vagas logic directly against jobs.db using the same logic.
This simulates what the API endpoint will do.
"""
import sys, os
sys.path.insert(0, '.')
from database import get_connection
import sqlite3

conn = get_connection()
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

SENIOR_MARKS  = ["s_nior", "senior", " sr ", "sênio", "s%nio"]
LEAD_MARKS    = ["lead", "especialista", "head ", "tech lead", "principal", "coordenador", "gerente"]
JUNIOR_MARKS  = ["jr", "j_nior", "junior", "j%nior"]
PLENO_MARKS   = ["pleno", " pl "]
ESTAGIO_MARKS = ["est_gio", "estagio", "trainee", "intern"]

# ── Test Jr (Modo Flexível) ──────────────────────────────
excl_clauses = []
excl_params  = []
for mark in SENIOR_MARKS + LEAD_MARKS + PLENO_MARKS + ESTAGIO_MARKS:
    excl_clauses.append(f"LOWER(j.title) NOT LIKE ?")
    excl_params.append(f"%{mark}%")

incl_clauses = []
incl_params  = []
for mark in JUNIOR_MARKS:
    incl_clauses.append(f"LOWER(j.title) LIKE ?")
    incl_params.append(f"%{mark}%")
incl_clauses.append("j.level IN ('jr', 'nao_informado')")

q_jr = f"""
    SELECT COUNT(*) FROM jobs j
    WHERE ({' AND '.join(excl_clauses)})
    AND ({' OR '.join(incl_clauses)})
"""
count_jr = cursor.execute(q_jr, excl_params + incl_params).fetchone()[0]
print(f"Jr filter (Modo Flexível): {count_jr} vagas")

# 5 samples including nao_informado
q_sample = q_jr.replace("COUNT(*)", "j.title, j.level, j.platform") + " LIMIT 5"
rows = cursor.execute(q_sample, excl_params + incl_params).fetchall()
for r in rows:
    print(f"  [{r['level']}] {r['title'][:60]} ({r['platform']})")

# ── Test Pl (Modo Flexível) ──────────────────────────────
excl2 = []
ep2   = []
for mark in SENIOR_MARKS + LEAD_MARKS + ESTAGIO_MARKS:
    excl2.append("LOWER(j.title) NOT LIKE ?")
    ep2.append(f"%{mark}%")

incl2 = []
ip2   = []
for mark in PLENO_MARKS:
    incl2.append("LOWER(j.title) LIKE ?")
    ip2.append(f"%{mark}%")
incl2.append("j.level IN ('pl', 'nao_informado')")

q_pl = f"""
    SELECT COUNT(*) FROM jobs j
    WHERE ({' AND '.join(excl2)})
    AND ({' OR '.join(incl2)})
"""
count_pl = cursor.execute(q_pl, ep2 + ip2).fetchone()[0]
print(f"\nPl filter (Modo Flexível): {count_pl} vagas")

# ── Test Sr (Estrito) ─────────────────────────────────
sr_incl = [f"LOWER(j.title) LIKE ?" for m in SENIOR_MARKS]
sr_params = [f"%{m}%" for m in SENIOR_MARKS]
q_sr = f"SELECT COUNT(*) FROM jobs j WHERE (({' OR '.join(sr_incl)}) OR j.level = 'sr')"
count_sr = cursor.execute(q_sr, sr_params).fetchone()[0]
print(f"Sr filter (Estrito): {count_sr} vagas")

# ── Test Lead (Estrito) ───────────────────────────────
lead_incl = [f"LOWER(j.title) LIKE ?" for m in LEAD_MARKS]
lead_params = [f"%{m}%" for m in LEAD_MARKS]
q_lead = f"SELECT COUNT(*) FROM jobs j WHERE (({' OR '.join(lead_incl)}) OR j.level = 'lead')"
count_lead = cursor.execute(q_lead, lead_params).fetchone()[0]
print(f"Lead filter (Estrito): {count_lead} vagas")

# ── Test Todos ────────────────────────────────────────
count_all = cursor.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
print(f"\nTodos: {count_all} vagas")
print(f"Jr+Pl overlap (nao_informado) is expected and by design")

conn.close()
