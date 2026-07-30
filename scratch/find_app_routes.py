import ast

with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    tree = ast.parse(f.read(), filename='app.py')

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        decorators = [ast.dump(d) for d in node.decorator_list]
        print(f"Function: {node.name} (Line {node.lineno})")
        for d in decorators:
            if 'app.' in d or 'get' in d.lower() or 'post' in d.lower():
                print(f"  Decorator: {d[:120]}")
