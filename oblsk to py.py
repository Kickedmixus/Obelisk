import re


# =========================
# NAME SYSTEM
# =========================

def py_name(name: str) -> str:
    return "obelisk_" + re.sub(r'[^a-zA-Z0-9_]', '_', name)


# =========================
# PREPROCESS
# =========================

def preprocess(src: str):
    out = []
    for line in src.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "#" in line:
            line = line.split("#")[0].strip()

        if line:
            out.append(line)

    return "\n".join(out)


# =========================
# SPLIT STATEMENTS
# =========================

def split_statements(src: str):
    return [s.strip() for s in src.split(";") if s.strip()]


# =========================
# SAFE EXPRESSION ENGINE
# =========================

def compile_expr(expr: str):

    expr = expr.strip()

    # <var."x".val>
    expr = re.sub(
        r'<var\."([^"]+)"\.val>',
        lambda m: py_name(m.group(1)),
        expr
    )

    # numbers
    if re.fullmatch(r'\d+(\.\d+)?', expr):
        return expr

    # string
    if re.fullmatch(r'"[^"]*"', expr):
        return expr

    # simple variable
    if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', expr):
        return py_name(expr)

    return expr


# =========================
# COMPILER
# =========================

class Compiler:

    def __init__(self):
        self.functions = {}
        self.errors = []

    def compile(self, src: str):

        src = preprocess(src)
        statements = split_statements(src)

        out = []

        for s in statements:

            # ---------------- VAR ----------------
            if s.startswith("new var"):
                m = re.match(r'new var "([^"]+)"', s)
                if m:
                    out.append(f"{py_name(m.group(1))} = None")
                else:
                    self.errors.append(f"bad var: {s}")
                continue

            if s.startswith('var."'):
                m = re.match(r'var\."([^"]+)"\.val\s*=\s*(.+)', s)
                if m:
                    out.append(f"{py_name(m.group(1))} = {compile_expr(m.group(2))}")
                else:
                    self.errors.append(f"bad assign: {s}")
                continue

            # ---------------- LIST ----------------
            if s.startswith("new list"):
                m = re.match(r'new list "([^"]+)"', s)
                if m:
                    out.append(f"{py_name(m.group(1))} = []")
                else:
                    self.errors.append(f"bad list: {s}")
                continue

            if "list." in s:
                m = re.match(r'list\."([^"]+)"\.items\s*=\s*(.+)', s)
                if m:
                    out.append(f"{py_name(m.group(1))} = {compile_expr(m.group(2))}")
                    continue

                m = re.match(r'list\."([^"]+)"\.items\.(\d+)\s*=\s*(.+)', s)
                if m:
                    out.append(
                        f"{py_name(m.group(1))}[{m.group(2)}] = {compile_expr(m.group(3))}"
                    )
                    continue

            # ---------------- PRINT ----------------
            if s.startswith("terminal_display"):
                m = re.match(r'terminal_display\{(.+)\}', s)
                if m:
                    out.append(f"print({compile_expr(m.group(1))})")
                else:
                    self.errors.append(f"bad print: {s}")
                continue

            # ---------------- LOOP (basic stub) ----------------
            if s.startswith("loop"):
                m = re.match(r'loop\{(.+),(.+),(.+)\}', s)
                if m:
                    var, body, count = m.group(1), m.group(2), m.group(3)
                    out.append(f"for _ in range({count.strip()}):")
                    out.append(f"    # loop body: {body.strip()}")
                else:
                    self.errors.append(f"bad loop: {s}")
                continue

            # ---------------- UNKNOWN ----------------
            self.errors.append(f"unknown: {s}")

        return "\n".join(out)


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    with open("test.oblsk", "r", encoding="utf-8") as f:
        src = f.read()

    c = Compiler()
    result = c.compile(src)

    print(result)

    print("\n--- ERRORS ---")
    for e in c.errors:
        print(e)

    with open("out.py", "w") as f:
        f.write(result)=