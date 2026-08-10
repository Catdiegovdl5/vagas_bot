import sys
import os
import asyncio
import glob

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from core.ai_self_healer import diagnose_and_heal_error

async def test_self_healer():
    print("=" * 70)
    print("🧪 TESTANDO GERAÇÃO DE PATCH DE AUTOCORREÇÃO DO AI SELF-HEALER")
    print("=" * 70)

    sample_context = {
        "timestamp_str": "20260804_120000",
        "endpoint": "/api/test_route",
        "method": "POST",
        "exception_type": "ZeroDivisionError",
        "exception_message": "division by zero",
        "filepath": os.path.join(PROJECT_ROOT, "prioriti", "app.py"),
        "line_number": 260,
        "traceback": "Traceback (most recent call last):\n  File 'prioriti/app.py', line 260\nZeroDivisionError: division by zero"
    }

    result = await diagnose_and_heal_error(sample_context)
    print(f"Resultado do Diagnóstico: {result}")

    patches_dir = os.path.join(PROJECT_ROOT, "patches")
    patches = glob.glob(os.path.join(patches_dir, "fix_suggested_*.py"))
    print(f"Patches de autocorreção encontrados na pasta patches/: {len(patches)}")

    assert len(patches) > 0, "Nenhum patch de autocorreção foi gerado em patches/"
    latest_patch = max(patches, key=os.path.getmtime)
    print(f"Último patch gerado: {latest_patch}")

    with open(latest_patch, "r", encoding="utf-8") as f:
        content = f.read()
    print("\n📜 Trecho do Patch Gerado:")
    print(content[:300])

    print("\n" + "=" * 70)
    print("✅ TESTE DIRETO DO AI SELF-HEALER CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_self_healer())
