# Pêndulo Invertido com Controle PID

Este projeto tem como objetivo modelar e controlar um sistema de pêndulo invertido utilizando controle PID, analisando sua estabilidade e resposta dinâmica tanto com controle simbólico quanto com parâmetros numéricos definidos pelo usuário.

## 1. Introdução

O pêndulo invertido é um sistema clássico na teoria de controle, amplamente utilizado para testar técnicas de estabilização. Este projeto simula o comportamento do sistema utilizando a biblioteca `control` do Python.

## 2. Parâmetros do Sistema

| Parâmetro | Símbolo | Significado                           |
|----------|---------|----------------------------------------|
| M        | M       | Massa do carrinho                      |
| m        | m       | Massa do pêndulo                       |
| l        | l       | Distância do centro de massa ao ponto de rotação |
| g        | g       | Aceleração da gravidade                |
| I        | I       | Momento de inércia do pêndulo          |
| b        | b       | Coeficiente de atrito do carrinho      |

## 3. Modelo Matemático

### 3.1. Equações de Movimento (Newton-Euler)

Equação para o carrinho:

(M + m) * x'' + b * x' - m * l * θ'' * cos(θ) + m * l * (θ')² * sin(θ) = u

Equação para o pêndulo:

I * θ'' + m * l * x'' * cos(θ) + m * g * l * sin(θ) = 0

---

### 3.2. Linearização (em torno de θ = 0)

Para pequenos ângulos, usa-se:

- sin(θ) ≈ θ  
- cos(θ) ≈ 1

As equações linearizadas ficam:

(M + m) * x'' + b * x' - m * l * θ'' = u

I * θ'' + m * l * x'' + m * g * l * θ = 0

---

## 4. Forma Matricial do Sistema

Sistema linearizado na forma de espaço de estados:

dX/dt = A * X + B * u  
Y = C * X + D * u

Onde:

X = [x, x', θ, θ']ᵀ  
u = força aplicada  
Y = [x, θ]ᵀ

---

A =

|  0                                 1                      0                          0         |  
|  0   -(I + m * l²) * b / D   (m² * g * l²) / D           0         |  
|  0                                 0                      0                          1         |  
|  0     -(m * l * b) / D     m * g * l * (M + m) / D       0         |

B =

|  0                       |  
|  (I + m * l²) / D        |  
|  0                       |  
|  (m * l) / D             |

C =

| 1  0  0  0 |  
| 0  0  1  0 |

D =

| 0 |  
| 0 |

Com:

D = I * (M + m) + M * m * l²

---

## 5. Função de Transferência

Utilizando a transformada de Laplace nas equações linearizadas:

### 5.1. Posição do Carrinho (x)

Gx(s) = [l * m * s] / [s² * D + s * b * l * m - g * l * m * (M + m)]

### 5.2. Ângulo do Pêndulo (θ)

Gθ(s) = [g * l * (M + m)] / [s² * D + s * b * l * m - g * l * m * (M + m)]

---

## 6. Controle PID

Controlador PID:

PID(s) = Kp + Ki / s + Kd * s  
       = (Kd * s² + Kp * s + Ki) / s

---

## 7. Malha Fechada

A equação da malha fechada com realimentação unitária:

T(s) = [G(s) * PID(s)] / [1 + G(s) * PID(s)]

Aplicada separadamente para Gx(s) e Gθ(s), dependendo do objetivo de controle.

---

## 8. Análises Realizadas

- Estabilidade (análise dos polos)  
- Resposta ao degrau (sistema aberto e fechado)  
- Diagramas de Bode e Nyquist  

---

## 9. Uso do Código

O código pode operar em duas modalidades:

- **Simbólica**: usando `sympy`, imprime funções de transferência completas.  
- **Numérica**: o usuário define os parâmetros `Kp`, `Ki`, `Kd`, `M`, `m`, `l`, `b`, `I`, `g`.

---

## 10. Dependências

- Python >= 3.10  
- `control`  
- `sympy`  
- `matplotlib`  
- `numpy`

---

## 11. Execução

Para executar com parâmetros numéricos:

```bash
python Diagrama_blocos.py
