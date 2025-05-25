# Sistema de Controle para Pêndulo Invertido

## 1. Modelo Físico e Matemático

O pêndulo invertido é um sistema dinâmico não linear, formado por um pêndulo ligado a um carrinho que pode se mover ao longo de uma linha reta. O objetivo é controlar o movimento do carrinho de forma a manter o pêndulo invertido de maneira estável.

### 1.1. Descrição Física

- \( M \): Massa do carrinho.
- \( m \): Massa do pêndulo.
- \( b \): Coeficiente de atrito.
- \( l \): Comprimento do pêndulo.
- \( I \): Inércia do pêndulo.
- \( g \): Aceleração devido à gravidade.
- \( x \): Posição do carrinho.
- \( \theta \): Ângulo do pêndulo (em relação à vertical).
- \( u \): Força aplicada no carrinho.

A dinâmica do sistema pode ser descrita pelas equações diferenciais de segunda ordem que modelam a posição do carrinho e a posição angular do pêndulo.

#### Equações de Movimento:

As equações de movimento que descrevem o sistema podem ser derivadas usando a Lagrangiana, que é a diferença entre a energia cinética (\( T \)) e a energia potencial (\( V \)) do sistema. A equação de movimento resultante para as variáveis \( x \) e \( \theta \) é:

\[
\frac{d^2 x}{dt^2} = \frac{m l}{M + m} \cdot \left( \frac{m l \cdot \frac{d^2 \theta}{dt^2} + m g \theta}{M + m} \right)
\]

\[
\frac{d^2 \theta}{dt^2} = \frac{g \theta}{l}
\]

Este modelo é amplamente utilizado para testar técnicas de controle, como o controle PID, que visa manter o pêndulo equilibrado enquanto o carrinho se move.

---

## 2. Forma Matricial do Sistema

A forma de espaço de estados do sistema linearizado pode ser escrita como:

\[
\frac{dX}{dt} = A X + B u
\quad , \quad
Y = C X + D u
\]

#### Vetor de estado:

\[
X = \begin{bmatrix}
x \\
\dot{x} \\
\theta \\
\dot{\theta}
\end{bmatrix}
\]

#### Vetor de entrada:

\[
u = \text{força aplicada no carrinho}
\]

#### Vetor de saída:

\[
Y = \begin{bmatrix}
x \\
\theta
\end{bmatrix}
\]

#### Matriz A (dinâmica do sistema):

\[
A = 
\begin{bmatrix}
0 & 1 & 0 & 0 \\
0 & \frac{-(I + m l^2) b}{D} & \frac{m^2 g l^2}{D} & 0 \\
0 & 0 & 0 & 1 \\
0 & \frac{-m l b}{D} & \frac{m g l (M + m)}{D} & 0
\end{bmatrix}
\]

#### Matriz B (entrada):

\[
B = 
\begin{bmatrix}
0 \\
\frac{I + m l^2}{D} \\
0 \\
\frac{m l}{D}
\end{bmatrix}
\]

#### Matriz C (seleção da saída):

\[
C = 
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0
\end{bmatrix}
\]

#### Matriz D (acoplamento direto da entrada à saída):

\[
D = 
\begin{bmatrix}
0 \\
0
\end{bmatrix}
\]

#### Denominador comum \( D \) (determinante auxiliar):

\[
D = I(M + m) + M m l^2
\]

---

## 3. Implementação Computacional

O modelo do pêndulo invertido foi implementado utilizando o `SymPy` para cálculos simbólicos e o `Graphviz` para gerar diagramas de blocos do sistema de controle PID.

### 3.1. Código para Sistema Simbólico

O código abaixo define as variáveis simbólicas do sistema, as equações de estado, e imprime as matrizes \( A \), \( B \), \( C \) e \( D \) em formato simbólico:

```python
import sympy as sp

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

def sistema_simbólico():
    imprimir_matrizes()

sistema_simbólico()
