import sympy as sp

sp.init_printing(use_unicode=True)

# Definição de variáveis simbólicas
x1, x2, x3, x4, u = sp.symbols('x1 x2 x3 x4 u')
X = sp.Matrix([x1, x2, x3, x4])
U = sp.Matrix([u])
M, m, b, l, I, g = sp.symbols('M m b l I g')
den = I*(M + m) + M*m*l**2

# Matrizes do sistema
A = sp.Matrix([
    [0, 1, 0, 0],
    [0, -((I + m*l**2)*b)/den, (m**2)*g*l**2/den, 0],
    [0, 0, 0, 1],
    [0, -m*l*b/den, m*g*l*(M + m)/den, 0]
])

B = sp.Matrix([
    [0],
    [(I + m*l**2)/den],
    [0],
    [m*l/den]
])

C = sp.Matrix([
    [1, 0, 0, 0],  # posição (x1)
    [0, 0, 1, 0]   # ângulo θ (x3)
])

D = sp.Matrix([
    [0],
    [0]
])

def imprimir_matrizes():
    print("\n=== Matriz A (dinâmica do sistema) ===")
    sp.pprint(A)
    print("\n=== Matriz B (entrada do sistema) ===")
    sp.pprint(B)
    print("\n=== Matriz C (saídas: posição e ângulo θ) ===")
    sp.pprint(C)
    print("\n=== Matriz D (influência direta da entrada na saída) ===")
    sp.pprint(D)

def imprimir_equacoes_estado_expandida_formatada(A, B, X, U):
    dXdt = A * X + B * U

    def formatar_eq_para_linhas(eq):
        s = str(eq.expand())
        s = s.replace('**2', '²').replace('*', '.')
        termos = s.replace('+', '\n + ').replace('-', '\n - ').split('\n')
        termos = [t.strip() for t in termos if t.strip()]
        return termos

    print("\n=== Equações de Estado (Forma Expandida Formatada) ===")
    print("dx1/dt = x2                           # posição: x1, velocidade: x2 = dx1/dt\n")

    eq2_termos = formatar_eq_para_linhas(dXdt[1])
    print("dx2/dt = (")
    for termo in eq2_termos:
        print("    " + termo)
    print(")   # aceleração linear do carrinho\n")

    print("dx3/dt = x4                           # ângulo: x3, velocidade angular: x4 = dx3/dt\n")

    eq4_termos = formatar_eq_para_linhas(dXdt[3])
    print("dx4/dt = (")
    for termo in eq4_termos:
        print("    " + termo)
    print(")   # aceleração angular do pêndulo\n")

    print("=== Legenda ===")
    print("x1 = posição do carrinho")
    print("x2 = velocidade do carrinho = dx1/dt")
    print("dx2/dt = aceleração linear do carrinho")
    print("x3 = ângulo θ do pêndulo")
    print("x4 = velocidade angular do pêndulo = dx3/dt")
    print("dx4/dt = aceleração angular do pêndulo")

def sistema_simbólico():
    imprimir_matrizes()
    imprimir_equacoes_estado_expandida_formatada(A, B, X, U)

def sistema_numerico():
    print("Digite os parâmetros físicos do sistema:")
    M_val = float(input("Massa do carrinho (M) [kg]: "))
    m_val = float(input("Massa do pêndulo (m) [kg]: "))
    b_val = float(input("Coeficiente de atrito (b) [N/m/s]: "))
    l_val = float(input("Comprimento do pêndulo (l) [m]: "))
    I_val = float(input("Inércia do pêndulo (I) [kg·m²]: "))
    g_val = float(input("Gravidade (g) [m/s²]: "))

    subs = {M: M_val, m: m_val, b: b_val, l: l_val, I: I_val, g: g_val}

    A_num = A.subs(subs).evalf()
    B_num = B.subs(subs).evalf()
    dXdt_num = A_num * X + B_num * U

    print("\n=== Matriz A (numérica) ===")
    sp.pprint(A_num)
    print("\n=== Matriz B (numérica) ===")
    sp.pprint(B_num)
    print("\n=== Matriz C ===")
    sp.pprint(C)
    print("\n=== Matriz D ===")
    sp.pprint(D)

    print("\n=== Equações de Estado (Forma Expandida Numérica) ===")
    for i, eq in enumerate(dXdt_num, 1):
        print(f"dx{i}/dt =", eq)

    return A_num, B_num, C, D

def main():
    print("Escolha a forma de saída:")
    print("1 - Sistema simbólico")
    print("2 - Sistema numérico")
    opcao = input("Digite 1 ou 2: ")

    if opcao == "1":
        sistema_simbólico()
    elif opcao == "2":
        sistema_numerico()
    else:
        print("Opção inválida. Digite 1 ou 2.")

if __name__ == "__main__":
    main()
