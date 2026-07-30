import ast
import glob

test_files = glob.glob('tests/*.py') + [f for f in glob.glob('test_*.py')]

print(f"Total test files found: {len(test_files)}")

no_assert_count = 0
total_test_funcs = 0
tautological_asserts = 0

for tf in test_files:
    try:
        with open(tf, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ast.parse(f.read(), filename=tf)
    except Exception as e:
        print(f"Error parsing {tf}: {e}")
        continue

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                total_test_funcs += 1
                asserts = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                if not asserts:
                    # Check if pytest.raises or similar is used
                    calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
                    has_check = any('raises' in ast.dump(c) or 'assert' in ast.dump(c) for c in calls)
                    if not has_check:
                        print(f"[{tf}] Function '{node.name}' has no assert statement!")
                        no_assert_count += 1
                for a in asserts:
                    if isinstance(a.test, ast.Constant) and a.test.value is True:
                        print(f"[{tf}] Tautological assert True in '{node.name}'!")
                        tautological_asserts += 1

print(f"\nSummary:")
print(f"Total test functions analyzed: {total_test_funcs}")
print(f"Test functions without assertions: {no_assert_count}")
print(f"Tautological assertions found: {tautological_asserts}")
