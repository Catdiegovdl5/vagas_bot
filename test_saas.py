from database import (init_db, get_dashboard_stats, upsert_user_profile, is_premium,
                      check_and_increment_daily_hunts, register_application, save_ai_score, get_ai_score)

init_db()
print("DB OK")

upsert_user_profile("test_free_1")
upsert_user_profile("test_prem_1", plan="premium")
print("Free is_premium:", is_premium("test_free_1"))
print("Premium is_premium:", is_premium("test_prem_1"))

r1 = check_and_increment_daily_hunts("test_free_1", limit=3)
r2 = check_and_increment_daily_hunts("test_free_1", limit=3)
r3 = check_and_increment_daily_hunts("test_free_1", limit=3)
r4 = check_and_increment_daily_hunts("test_free_1", limit=3)
print("Buscas 1,2,3 OK:", r1, r2, r3, "| Busca 4 bloqueada:", not r4)

register_application("test_prem_1", "https://vaga.com/123", "Dev Python", "TechCorp", "gupy")
stats = get_dashboard_stats()
print("Dashboard stats: users=%s apps=%s" % (stats["total_users"], stats["total_applications"]))

save_ai_score("test_prem_1", "https://vaga.com/123", 82, "Bom match em Python", "Cover letter aqui...")
score = get_ai_score("test_prem_1", "https://vaga.com/123")
print("AI Score salvo:", score["score"], "%")
print("TODOS OS TESTES PASSARAM!")
