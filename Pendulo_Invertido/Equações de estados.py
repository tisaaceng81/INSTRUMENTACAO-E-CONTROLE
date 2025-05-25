import numpy as np
import sympy as sp

# Ativa impressão simbólica com expoentes e parênteses elegantes
sp.init_printing(use_unicode=True)

# === Variáveis de estado e entrada ===
x1, x2, x3, x4, u = sp.symbols('x1 x2 x3 x4 u')
X = sp.Matrix([x1, x2, x3, x4])
U = sp.Matrix([u])

# === Parâmetros simbólicos ===
M, m, b, l, I, g = sp.symbols('M m b l I g')

# === Denominador comum simbólico ===
den = I*(M + m) + M*m*l**2

# === Matrizes do sistema simbólicas ===
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
    [1, 0, 0, 0],
    [0, 0, 1, 0]
])

D = sp.Matrix([
    [0],
    [0]
])

# Nomes das variáveis de saída
nomes_saida = ['posição x', 'ângulo θ']

# === Menu de seleção ===
print("Escolha a forma de saída:")
print("1 - Equações simbólicas genéricas (com parâmetros)")
print("2 - Equações com parâmetros numéricos inseridos manualmente")
opcao = input("Digite 1 ou 2: ")

# === Opção 1: saída simbólica ===
if opcao == "1":
    print("\n=== EQUAÇÕES DE ESTADO (Simbólicas) ===\n")
    dXdt = A * X + B * U
    for i, eq in enumerate(dXdt, 1):
        simb = sp.Symbol(f'dx{i}/dt')
        sp.pprint(sp.Eq(simb, sp.simplify(eq)), use_unicode=True)
        print()

    print("\n=== SAÍDAS DO SISTEMA (Simbólicas) ===\n")
    Y = C * X + D * U
    for i, eq in enumerate(Y, 1):
        simb = sp.Symbol(nomes_saida[i-1])
        sp.pprint(sp.Eq(simb, sp.simplify(eq)), use_unicode=True)
        print()

# === Opção 2: com entrada de parâmetros ===
elif opcao == "2":
    print("\nDigite os parâmetros físicos do sistema:")
    M_val = float(input("Massa do carrinho (M) [kg]: "))
    m_val = float(input("Massa do pêndulo (m) [kg]: "))
    b_val = float(input("Coeficiente de atrito (b) [N/m/s]: "))
    l_val = float(input("Comprimento do pêndulo (l) [m]: "))
    I_val = float(input("Inércia do pêndulo (I) [kg·m²]: "))
    g_val = float(input("Gravidade (g) [m/s²]: "))

    # Substituições numéricas
    subs = {M: M_val, m: m_val, b: b_val, l: l_val, I: I_val, g: g_val}
    A_num = A.subs(subs).evalf()
    B_num = B.subs(subs).evalf()

    print("\n=== EQUAÇÕES DE ESTADO (Numéricas) ===\n")
    dXdt_num = A_num * X + B_num * U
    for i, eq in enumerate(dXdt_num, 1):
        simb = sp.Symbol(f'dx{i}/dt')
        sp.pprint(sp.Eq(simb, sp.simplify(eq)), use_unicode=True)
        print()

    print("\n=== SAÍDAS DO SISTEMA (Numéricas) ===\n")
    Y_num = C * X + D * U
    for i, eq in enumerate(Y_num, 1):
        simb = sp.Symbol(nomes_saida[i-1])
        sp.pprint(sp.Eq(simb, sp.simplify(eq)), use_unicode=True)
        print()

else:
    print("Opção inválida. Digite 1 ou 2.")
