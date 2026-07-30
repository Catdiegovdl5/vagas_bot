import asyncio
import importlib
import sys
import os
import copy

sys.path.insert(0, r"C:/Users/99196/OneDrive/Documentos/vagas_bot")

from unittest.mock import MagicMock, AsyncMock, patch
import bot
from bot import _do_hunt, get_user_settings, user_settings_db

def test_end_to_end_hunt_pipeline():
    print("\n=================================================================")
    print("RUNNING END-TO-END _DO_HUNT SENIORITY PIPELINE VERIFICATION")
    print("=================================================================")

    # Prepare mock message and status updater
    mock_chat = MagicMock()
    mock_chat.id = 99999
    
    mock_message = MagicMock()
    mock_message.chat = mock_chat

    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)

    # Sample raw jobs returned by scrapers
    raw_mock_jobs = [
        {
            "platform": "linkedin",
            "title": "Jovem Aprendiz de TI",
            "requirements": "Atuação no suporte técnico e aprendizagem de ti.",
            "link": "https://example.com/job1",
            "location": "Remoto",
            "company": "Company A"
        },
        {
            "platform": "linkedin",
            "title": "Desenvolvedor Python Voluntário",
            "requirements": "Projeto social sem fins lucrativos em código aberto.",
            "link": "https://example.com/job2",
            "location": "Remoto",
            "company": "Company B"
        },
        {
            "platform": "linkedin",
            "title": "Desenvolvedor Junior Python",
            "requirements": "Desenvolvimento backend python com django.",
            "link": "https://example.com/job3",
            "location": "Remoto",
            "company": "Company C"
        },
        {
            "platform": "linkedin",
            "title": "Desenvolvedor Pleno Python",
            "requirements": "Desenvolvimento backend python pleno com django e docker.",
            "link": "https://example.com/job4",
            "location": "Remoto",
            "company": "Company D"
        },
        {
            "platform": "linkedin",
            "title": "Desenvolvedor Senior Python",
            "requirements": "Arquitetura backend python senior com django e microservices.",
            "link": "https://example.com/job5",
            "location": "Remoto",
            "company": "Company E"
        }
    ]

    # Mock scraper function
    async def mock_scrape(**kwargs):
        return copy.deepcopy(raw_mock_jobs)

    levels_to_test = [
        ("Todos", 5),               # All pass
        ("Júnior", 1),              # Only Junior (job3)
        ("Pleno", 1),               # Only Pleno (job4)
        ("Sênior", 1),              # Only Senior (job5)
        ("Jovem Aprendiz", 1),      # Only Aprendiz (job1)
        ("Ganhar Experiência", 1),  # Only Voluntario (job2)
        ("Iniciantes Tudo", 2)      # Aprendiz (job1) + Voluntario (job2) = 2
    ]

    async def run_all_levels():
        for level_name, expected_count in levels_to_test:
            # Set user settings
            chat_id = "99999"
            user_settings_db[chat_id] = {
                "level": level_name,
                "location": "Brasil (Remoto)",
                "contract": "Todos",
                "education": "Todos",
                "platforms": {
                    "linkedin": True
                },
                "ai_filter": False,
                "escudo_ptbr": True
            }

            captured_jobs = []

            # Mock answers from bot message.answer to capture sent messages
            async def fake_answer(text, reply_markup=None, parse_mode=None):
                return mock_status_msg

            mock_message.answer = AsyncMock(side_effect=fake_answer)

            # Patch importlib to return a module with our mock_scrape
            mock_module = MagicMock()
            mock_module.scrape = mock_scrape

            real_import_module = importlib.import_module
            def selective_import(name, package=None):
                if name.startswith("scrapers."):
                    return mock_module
                return real_import_module(name, package)

            with patch("importlib.import_module", side_effect=selective_import):
                # We catch any message sent during _do_hunt
                sent_messages = []
                async def mock_answer_job(text, reply_markup=None, parse_mode=None):
                    sent_messages.append(text)
                    return AsyncMock()

                # Patching send job output or tracking unique jobs filtered in _do_hunt
                with patch.object(bot, "is_job_relevant", wraps=bot.is_job_relevant) as spy_is_job_relevant:
                    await _do_hunt("Desenvolvedor Python", mock_message)

                    # Calculate how many jobs passed filtering
                    passed_jobs = []
                    for call_args in spy_is_job_relevant.call_args_list:
                        job_arg = call_args[0][0]
                        kw_arg = call_args[0][1]
                        settings_arg = call_args[0][2]
                        
                        # Only look at calls for this user/level
                        if settings_arg.get("level") == level_name:
                            res = spy_is_job_relevant.side_effect
                            # Re-eval
                            if bot.is_job_relevant(job_arg, kw_arg, settings_arg):
                                passed_jobs.append(job_arg["title"])

                    # Unique count of passed jobs
                    unique_passed = list(set(passed_jobs))
                    status_ok = len(unique_passed) == expected_count
                    print(f"Level: {level_name:<18} | Expected: {expected_count} | Got: {len(unique_passed)} | Jobs: {unique_passed} -> {'[PASS]' if status_ok else '[FAIL]'}")

                    assert status_ok, f"Expected {expected_count} jobs for level '{level_name}', got {len(unique_passed)}: {unique_passed}"

    asyncio.run(run_all_levels())
    print("\n[SUCCESS] ALL END-TO-END LEVEL FILTERING PIPELINE TESTS PASSED 100%!")

if __name__ == "__main__":
    test_end_to_end_hunt_pipeline()
