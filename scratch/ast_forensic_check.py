import ast, os, glob, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

py_files = [
    os.path.join(project_root, 'bot.py'),
    os.path.join(project_root, 'app.py'),
    os.path.join(project_root, 'launcher.py'),
    os.path.join(project_root, 'database.py'),
] + glob.glob(os.path.join(project_root, 'scrapers', '*.py'))

print("=== PHASE B: AST & FORENSIC CHEATING / FACADE CHECK ===")
print(f"Auditing {len(py_files)} Python files...")

facades_found = []

for filepath in py_files:
    rel_path = os.path.relpath(filepath, project_root)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    try:
        tree = ast.parse(code, filename=filepath)
    except SyntaxError as e:
        print(f"SYNTAX ERROR IN {rel_path}: {e}")
        continue

    # AST checks
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for dummy functions (only pass or return constant)
            if len(node.body) == 1:
                stmt = node.body[0]
                if isinstance(stmt, ast.Pass):
                    facades_found.append((rel_path, node.name, "Single 'pass' body"))
                elif isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                    if stmt.value.value in (True, False, None, "PASS", "SUCCESS"):
                        facades_found.append((rel_path, node.name, f"Returns constant {stmt.value.value}"))

print(f"\nPotential facades / trivial functions found ({len(facades_found)}):")
for f in facades_found[:15]:
    print(f"  [{f[0]}] {f[1]}(): {f[2]}")

print("\n--- Hardcoded Test Results / Mocking in Production Files Check ---")
prohibited_keywords = [
    "HARDCODED_TEST_RESULT", "MOCK_SUCCESS_FORCE", "FAKE_SCRAPER_OUTPUT", "RETURN_TRUE_ALWAYS"
]
found_prohibited = False
for filepath in py_files:
    rel_path = os.path.relpath(filepath, project_root)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    for kw in prohibited_keywords:
        if kw in code:
            print(f"  ALERT! Prohibited keyword '{kw}' found in {rel_path}")
            found_prohibited = True

if not found_prohibited:
    print("  CLEAN: No prohibited cheat strings or hardcoded flags found.")

print("\nAST Forensic Check Completed.")
