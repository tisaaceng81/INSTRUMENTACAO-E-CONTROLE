from graphviz import Digraph
import sympy as sp
import os

# Garantir que o Graphviz está no PATH
os.environ["PATH"] += os.pathsep + r"C:\\Program Files\\Graphviz\\bin"

# Definições simbólicas
s = sp.symbols('s')
M, m, b, l, I, g = sp.symbols('M m b l I g')
Kp, Ki, Kd = sp.symbols('Kp Ki Kd')
U = sp.symbols('U(s)')

# Denominador comum (mesmo para ambas as saídas)
den = s**2 * (I*(M + m) + M*l**2*m) + s * b*l*m - g*l*m*(M + m)

# Matriz G(s): Sistema MIMO (2 saídas x e theta)
G = sp.Matrix([
    [l*m*s / den],
    [g*l*(M + m) / den]
])

# Controlador PID (aplicado à entrada)
PID = Kp + Ki/s + Kd*s

# Função para calcular malha fechada para sistema MIMO
def malha_fechada(G, PID_controller):
    return sp.Matrix([
        (PID_controller * G[i]) / (1 + PID_controller * G[i]) for i in range(G.rows)
    ])

G_pid = malha_fechada(G, PID)

# Impressão simbólica com U(s)
def imprimir_terminal():
    print("=== Matriz de Funções de Transferência G(s) com entrada U(s) ===")
    print("\nGx(s):")
    sp.pprint(G[0] * U)
    print("\nGθ(s):")
    sp.pprint(G[1] * U)

    print("\n=== Malha Fechada com PID ===")
    print("\nFunção de transferência da saída x(s):")
    sp.pprint((PID * G[0]) / (1 + PID * G[0]) * U)

    print("\nFunção de transferência da saída θ(s):")
    sp.pprint((PID * G[1]) / (1 + PID * G[1]) * U)

# Diagrama de blocos com saídas x(s) e θ(s)
def gerar_diagrama_blocos():
    dot = Digraph(comment="Diagrama de Blocos MIMO PID", format='png')
    dot.attr(rankdir='LR')

    dot.node('U', 'U(s)', shape='rectangle')
    dot.node('Sum', '', shape='circle', width='0.4', height='0.4', fixedsize='true', style='filled', fillcolor='lightyellow')
    dot.node('PID', 'PID\nKp + Ki/s + Kd*s', shape='rectangle')
    dot.node('G', 'G(s)', shape='rectangle', xlabel='[Gx(s); Gθ(s)]')
    dot.node('x', 'x(s)', shape='rectangle')
    dot.node('theta', 'θ(s)', shape='rectangle')

    dot.edge('U', 'Sum', label='+', arrowhead='none')
    dot.edge('x', 'Sum', label='-', style='dashed', arrowhead='normal')      # seta na realimentação
    dot.edge('theta', 'Sum', label='-', style='dashed', arrowhead='normal')  # seta na realimentação
    dot.edge('Sum', 'PID')
    dot.edge('PID', 'G')
    dot.edge('G', 'x', label='Gx(s)')
    dot.edge('G', 'theta', label='Gθ(s)')

    output_path = 'diagrama_blocos_pid_mimo'
    dot.render(output_path, cleanup=True)
    print(f"Diagrama gerado: {output_path}.png")

# Execução principal
def main():
    print("=== Escolha o modo de operação ===")
    print("1 - Sistema simbólico")
    print("2 - Sistema numérico")
    opcao = input("Digite 1 ou 2: ").strip()

    if opcao == '1':
        imprimir_terminal()
        gerar_diagrama_blocos()

    elif opcao == '2':
        print("\nDigite os parâmetros físicos do sistema:")
        M_val = float(input("Massa do carrinho (M) [kg]: "))
        m_val = float(input("Massa do pêndulo (m) [kg]: "))
        b_val = float(input("Coeficiente de atrito (b) [N/m/s]: "))
        l_val = float(input("Comprimento do pêndulo (l) [m]: "))
        I_val = float(input("Inércia do pêndulo (I) [kg·m²]: "))
        g_val = float(input("Gravidade (g) [m/s²]: "))
        Kp_val = float(input("Kp: "))
        Ki_val = float(input("Ki: "))
        Kd_val = float(input("Kd: "))

        subs = {M: M_val, m: m_val, b: b_val, l: l_val, I: I_val,
                g: g_val, Kp: Kp_val, Ki: Ki_val, Kd: Kd_val}

        G_num = G.subs(subs).evalf()
        PID_num = PID.subs(subs).evalf()
        G_pid_num = malha_fechada(G_num, PID_num)

        print("\n=== Matriz G(s) Numérica multiplicada por U(s) ===")
        print("\nGx(s):")
        sp.pprint(G_num[0] * U)
        print("\nGθ(s):")
        sp.pprint(G_num[1] * U)

        print("\n=== Malha Fechada Numérica multiplicada por U(s) ===")
        print("\nSaída x(s):")
        sp.pprint(G_pid_num[0] * U)
        print("\nSaída θ(s):")
        sp.pprint(G_pid_num[1] * U)

        gerar_diagrama_blocos()
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()
