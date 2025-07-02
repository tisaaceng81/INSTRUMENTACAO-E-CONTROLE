from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import control as ctl

def desenhar_diagrama_aberto(ax):
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    rect = patches.FancyBboxPatch((4, 1.5), 2, 1, boxstyle="round,pad=0.1",
                                  edgecolor="black", facecolor="lightblue")
    ax.add_patch(rect)
    ax.text(5, 2, "G(s)", fontsize=14, ha='center', va='center')

    ax.text(1, 2, "Entrada", fontsize=12, ha='center', va='center')
    ax.text(9, 2, "Saída", fontsize=12, ha='center', va='center')

    ax.annotate('', xy=(4, 2), xytext=(2, 2), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(8, 2), xytext=(6, 2), arrowprops=dict(arrowstyle='->', lw=2))


def desenhar_diagrama_fechado(ax):
    ax.clear()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    circle = patches.Circle((1.5, 4), 0.5, edgecolor='black', facecolor='white', lw=2)
    ax.add_patch(circle)
    ax.text(1.5, 4.3, "+", fontsize=20, ha='center', va='center')
    ax.text(1.3, 3.7, "−", fontsize=20, ha='center', va='center')

    rect_pid = patches.FancyBboxPatch((3, 3.5), 2, 1, boxstyle="round,pad=0.1",
                                      edgecolor="black", facecolor="lightgreen")
    ax.add_patch(rect_pid)
    ax.text(4, 4, "PID(s)", fontsize=14, ha='center', va='center')

    rect_g = patches.FancyBboxPatch((6, 3.5), 2, 1, boxstyle="round,pad=0.1",
                                    edgecolor="black", facecolor="lightblue")
    ax.add_patch(rect_g)
    ax.text(7, 4, "G(s)", fontsize=14, ha='center', va='center')

    ax.text(0.5, 4, "Entrada", fontsize=12, ha='center', va='center')
    ax.text(9, 4, "Saída", fontsize=12, ha='center', va='center')

    ax.annotate('', xy=(1, 4), xytext=(0.7, 4), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(3, 4), xytext=(2, 4), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(6, 4), xytext=(5, 4), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(8, 4), xytext=(7.5, 4), arrowprops=dict(arrowstyle='->', lw=2))

    ax.annotate('', xy=(6, 3.5), xytext=(6, 2.5), arrowprops=dict(arrowstyle='-|>', lw=2))
    ax.annotate('', xy=(6, 2.5), xytext=(1.5, 2.5), arrowprops=dict(arrowstyle='-', lw=2))
    ax.annotate('', xy=(1.5, 2.5), xytext=(1.5, 3.5), arrowprops=dict(arrowstyle='-|>', lw=2))

    ax.text(1.2, 3, "- (feedback)", fontsize=10, color='red')

def formatar_ft(num_coefs, den_coefs):
    sobrescrito = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                   '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}

    def termo_str(coef, grau):
        if abs(coef) < 1e-12:
            return ''
        s_coef = f"{abs(coef):.3g}" if abs(coef) != 1 or grau == 0 else ''
        s_sinal = '-' if coef < 0 else ''
        s_var = ''
        if grau > 0:
            expoente = ''.join(sobrescrito[d] for d in str(grau))
            s_var = f"s{expoente}"
        return f"{s_sinal}{s_coef}{s_var}"

    def polinomio_str(coefs):
        termos = []
        grau_max = len(coefs) - 1
        for i, c in enumerate(coefs):
            grau = grau_max - i
            t = termo_str(c, grau)
            if t:
                termos.append(t)
        if not termos:
            return '0'
        s = termos[0]
        for termo in termos[1:]:
            if termo.startswith('-'):
                s += ' - ' + termo[1:]
            else:
                s += ' + ' + termo
        return s

    num_str = polinomio_str(num_coefs)
    den_str = polinomio_str(den_coefs)

    largura = max(len(num_str), len(den_str))
    barra = '―' * largura
    return f"{num_str}\n{barra}\n{den_str}"


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        from kivy.graphics import Color, Rectangle

        barra_superior = BoxLayout(size_hint_y=None, height=40, padding=5)
        with barra_superior.canvas.before:
            Color(0, 0, 1, 1)
            self.rect = Rectangle(pos=barra_superior.pos, size=barra_superior.size)

        def atualizar_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

        barra_superior.bind(pos=atualizar_rect, size=atualizar_rect)
        label_barra = Label(text='Entrada da EDO do Sistema', color=(1, 1, 1, 1), bold=True)
        barra_superior.add_widget(label_barra)
        self.add_widget(barra_superior)

        linha_ordem = BoxLayout(size_hint_y=None, height=40)
        linha_ordem.add_widget(Label(text='Ordem da EDO:'))
        self.ordem = TextInput(text='1', multiline=False)
        linha_ordem.add_widget(self.ordem)
        self.add_widget(linha_ordem)

        linha_eq = BoxLayout(size_hint_y=None, height=40)
        linha_eq.add_widget(Label(text='Coef. Y(t):'))
        self.coef_y = TextInput(text='10 1', multiline=False)
        linha_eq.add_widget(self.coef_y)

        linha_eq.add_widget(Label(text='Coef. U(t):'))
        self.coef_u = TextInput(text='2', multiline=False)
        linha_eq.add_widget(self.coef_u)

        self.add_widget(linha_eq)

        linha = BoxLayout(size_hint_y=None, height=40)
        linha.add_widget(Label(text='Entrada:'))
        self.entrada = TextInput(text='u', multiline=False)
        linha.add_widget(self.entrada)
        linha.add_widget(Label(text='Saída:'))
        self.saida = TextInput(text='y', multiline=False)
        linha.add_widget(self.saida)
        self.add_widget(linha)

        btn = Button(text='Analisar Sistema', size_hint_y=None, height=50)
        btn.bind(on_press=self.analisar)
        self.add_widget(btn)

        self.resultado_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.resultado = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.resultado.bind(minimum_height=self.resultado.setter('height'))
        self.resultado_scroll.add_widget(self.resultado)
        self.add_widget(self.resultado_scroll)

    def analisar(self, instance):
        self.resultado.clear_widgets()
        try:
            entrada = self.entrada.text.strip() or 'u'
            saida = self.saida.text.strip() or 'y'

            try:
                ordem = int(self.ordem.text.strip())
                if ordem < 0:
                    raise ValueError()
            except ValueError:
                self.resultado.add_widget(Label(text="Erro: Ordem inválida, deve ser inteiro >= 0."))
                return

            # Tratamento para aceitar coeficientes negativos (exemplo: "-10 1")
            try:
                coef_y = [float(c) for c in self.coef_y.text.strip().split()]
            except ValueError:
                self.resultado.add_widget(Label(text="Erro: coeficientes Y(t) inválidos. Use números, separados por espaço, com sinal '-' se precisar."))
                return

            try:
                coef_u = [float(c) for c in self.coef_u.text.strip().split()]
            except ValueError:
                self.resultado.add_widget(Label(text="Erro: coeficientes U(t) inválidos. Use números, separados por espaço, com sinal '-' se precisar."))
                return

            if len(coef_y) != ordem + 1:
                self.resultado.add_widget(Label(
                    text=f"Erro: coeficientes Y(t) devem ter {ordem + 1} valores para ordem {ordem}."))
                return

            if len(coef_u) == 0:
                self.resultado.add_widget(Label(text="Erro: coeficientes U(t) inválidos."))
                return

            # Criar a FT malha aberta
            sys = ctl.TransferFunction(coef_u, coef_y)

            # Extrair coeficientes do numerador e denominador para formatar a FT
            num = sys.num[0][0]  # lista dos coeficientes numerador
            den = sys.den[0][0]  # lista dos coeficientes denominador

            ft_formatada_aberta = formatar_ft(num, den)
            self.resultado.add_widget(Label(
                text=f"Função de Transferência (Malha Aberta):\n{ft_formatada_aberta}",
                size_hint_y=None, height=100))

            # Resposta ao degrau em malha aberta
            tempo, resposta = ctl.step_response(sys)
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(tempo, resposta, label='Malha Aberta')
            ax.set_title("Resposta ao Degrau - Malha Aberta")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Saída")
            ax.grid(True)
            ax.legend()
            grafico1 = FigureCanvasKivyAgg(fig)
            grafico1.size_hint_y = None
            grafico1.height = 300
            self.resultado.add_widget(grafico1)

            # Cálculo dos parâmetros L e T pelo método de Ziegler-Nichols
            y_inf = resposta[-1]
            dy = np.gradient(resposta, tempo)
            idx_max = np.argmax(dy)
            m = dy[idx_max]
            t_inf = tempo[idx_max]

            L = t_inf - resposta[idx_max] / m if m != 0 else 0.01
            y_63 = 0.63 * y_inf
            T_plus_L = np.interp(y_63, resposta, tempo)
            T = T_plus_L - L

            if L <= 0:
                L = 0.01
            if T <= 0:
                T = 0.01

            Kp = 1.2 * T / L
            Ki = 2 * L
            Kd = 0.5 * L

            pid_tf = ctl.TransferFunction([Kd, Kp, Ki], [1, 0])

            sys_pid = ctl.feedback(pid_tf * sys, 1)

            # FT malha fechada
            num_pid = sys_pid.num[0][0]
            den_pid = sys_pid.den[0][0]
            ft_formatada_fechada = formatar_ft(num_pid, den_pid)
            self.resultado.add_widget(Label(
                text=f"Função de Transferência (Malha Fechada com PID):\n{ft_formatada_fechada}",
                size_hint_y=None, height=100))

            # Resposta ao degrau em malha fechada com PID
            t2, y2 = ctl.step_response(sys_pid)
            fig2, ax2 = plt.subplots(figsize=(12, 5))
            ax2.plot(t2, y2, label='Malha Fechada com PID')
            ax2.set_title("Resposta ao Degrau - Malha Fechada (PID)")
            ax2.set_xlabel("Tempo (s)")
            ax2.set_ylabel("Saída")
            ax2.grid(True)
            ax2.legend()
            grafico2 = FigureCanvasKivyAgg(fig2)
            grafico2.size_hint_y = None
            grafico2.height = 300
            self.resultado.add_widget(grafico2)

            texto_parametros = (
                f"L (Tempo de atraso) = {L:.4f} s\n"
                f"T (Constante de tempo) = {T:.4f} s\n"
                f"Kp = {Kp:.4f}\n"
                f"Ki = {Ki:.4f}\n"
                f"Kd = {Kd:.4f}\n"
            )
            label_param = Label(text=texto_parametros, size_hint_y=None, halign='left', valign='top')
            label_param.bind(size=lambda instance, value: instance.setter('text_size')(instance, value))
            label_param.text_size = (self.resultado.width, None)
            label_param.texture_update()
            label_param.height = label_param.texture_size[1]
            self.resultado.add_widget(label_param)

            pid_str = f"PID(s) = ({Kd:.4f})s² + ({Kp:.4f})s + ({Ki:.4f}) / s"
            self.resultado.add_widget(Label(
                text=f"Função de Transferência do PID:\n{pid_str}",
                size_hint_y=None,
                height=80
            ))

            # Diagramas de blocos
            fig3, ax3 = plt.subplots(figsize=(12, 3))
            desenhar_diagrama_aberto(ax3)
            grafico3 = FigureCanvasKivyAgg(fig3)
            grafico3.size_hint_y = None
            grafico3.height = 150
            self.resultado.add_widget(Label(text="Diagrama de Blocos - Malha Aberta", size_hint_y=None, height=30))
            self.resultado.add_widget(grafico3)

            fig4, ax4 = plt.subplots(figsize=(12, 4))
            desenhar_diagrama_fechado(ax4)
            grafico4 = FigureCanvasKivyAgg(fig4)
            grafico4.size_hint_y = None
            grafico4.height = 200
            self.resultado.add_widget(Label(text="Diagrama de Blocos - Malha Fechada com PID", size_hint_y=None, height=30))
            self.resultado.add_widget(grafico4)

        except Exception as e:
            self.resultado.add_widget(Label(text=f"Erro: {e}"))


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, Rectangle

        layout = BoxLayout(orientation='vertical')

        with layout.canvas.before:
            Color(0, 0, 1, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        def atualizar_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

        layout.bind(size=atualizar_rect, pos=atualizar_rect)

        label = Label(
            text="Analisador de Sistemas Dinâmicos",
            font_size=40,
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)

        self.add_widget(layout)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = MainLayout()
        self.add_widget(self.main_layout)


class SistemaApp(App):
    def build(self):
        Window.size = (900, 900)
        self.title = "Analisador de Sistemas Dinâmicos - Desenvolvido por Tiago Carneiro"

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(MainScreen(name='main'))

        # Splash fica 15 segundos antes de mudar para main
        Clock.schedule_once(lambda dt: setattr(sm, 'current', 'main'), 15)

        return sm


if __name__ == '__main__':
    SistemaApp().run()
