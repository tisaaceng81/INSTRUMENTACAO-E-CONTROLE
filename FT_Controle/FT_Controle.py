
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from io import BytesIO
from PIL import Image, ImageTk
import sympy as sp
from sympy.abc import t, s
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import control as ctl

class AnalisadorDeSistemas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador Dinâmico de Sistemas - Desenvolvido por Tiago Carneiro")
        self.geometry("1100x1000")

        # --- Estrutura com Scrollbar ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.area_scroll = ttk.Frame(self.canvas)
        self.area_scroll.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.area_scroll, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._criar_widgets()

    def _criar_widgets(self):
        """Cria a estrutura estática da interface gráfica."""
        for widget in self.area_scroll.winfo_children(): widget.destroy()

        # --- Frame de Entrada ---
        frame_entrada = ttk.LabelFrame(self.area_scroll, text="1. Definição do Sistema")
        frame_entrada.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_entrada, text="Equação Diferencial:").pack(anchor="w", padx=10, pady=5)
        self.txt_equacao = tk.Text(frame_entrada, height=3, font=("Courier New", 11))
        self.txt_equacao.pack(fill="x", padx=10, pady=5)
        self.txt_equacao.insert("1.0", "10*diff(y(t),t) + y(t) = 2*u(t)")

        frame_vars = ttk.Frame(frame_entrada)
        frame_vars.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_vars, text="Entrada:").grid(row=0, column=0); self.ent_entrada = ttk.Entry(frame_vars, width=10); self.ent_entrada.grid(row=0, column=1, padx=(5,20)); self.ent_entrada.insert(0, "u")
        ttk.Label(frame_vars, text="Saída:").grid(row=0, column=2); self.ent_saida = ttk.Entry(frame_vars, width=10); self.ent_saida.grid(row=0, column=3, padx=5); self.ent_saida.insert(0, "y")
        
        # --- Frame de Análise e Controle ---
        frame_controle = ttk.LabelFrame(self.area_scroll, text="2. Opções de Análise e Controle")
        frame_controle.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_controle, text="Método de Sintonia PID:").pack(anchor="w", padx=10, pady=(5,0))
        self.metodo_sintonia = tk.StringVar(value="reacao")
        ttk.Radiobutton(frame_controle, text="Curva de Reação (Z-N 1)", variable=self.metodo_sintonia, value="reacao").pack(anchor="w", padx=20)
        ttk.Radiobutton(frame_controle, text="Resposta em Frequência (Z-N 2)", variable=self.metodo_sintonia, value="frequencia").pack(anchor="w", padx=20)

        ttk.Button(frame_controle, text="Analisar Sistema e Sintonizar PID", command=self.executar_analise, style="Accent.TButton").pack(pady=10)
        self.style = ttk.Style(self); self.style.configure("Accent.TButton", font=("", 10, "bold"))

        self.frame_resultados = ttk.Frame(self.area_scroll)
        self.frame_resultados.pack(fill="x", padx=10, pady=10)

    def _limpar_resultados(self):
        for widget in self.frame_resultados.winfo_children(): widget.destroy()
    
    def _renderizar_figura(self, fig, parent_frame):
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        plt.close(fig)

    def executar_analise(self):
        self._limpar_resultados()
        try:
            eq_raw = self.txt_equacao.get("1.0", "end-1c").strip()
            var_u, var_y = self.ent_entrada.get().strip() or 'u', self.ent_saida.get().strip() or 'y'
            if not eq_raw: raise ValueError("O campo da equação está vazio.")

            u_func, y_func = sp.Function(var_u)(t), sp.Function(var_y)(t)
            U_s, Y_s = sp.symbols(f"{var_u.capitalize()}(s) {var_y.capitalize()}(s)")
            
            lado_esq_str, lado_dir_str = (eq_raw.split("=") if "=" in eq_raw else (eq_raw, "0"))
            lado_esq = sp.sympify(lado_esq_str, locals={"diff": sp.diff})
            lado_dir = sp.sympify(lado_dir_str, locals={"diff": sp.diff})

            def aplicar_laplace(expr):
                res = expr
                for T_func, S_var in [(y_func, Y_s), (u_func, U_s)]:
                    for ordem in range(10, -1, -1):
                        res = res.replace(sp.Derivative(T_func, (t, ordem)), s**ordem * S_var) if ordem > 0 else res.replace(T_func, S_var)
                return res
            
            eq_s = sp.Eq(aplicar_laplace(lado_esq), aplicar_laplace(lado_dir))
            sol = sp.solve(eq_s, Y_s)
            if not sol: raise ValueError("Não foi possível isolar a variável de saída Y(s).")
            Gs_simbolica = sp.cancel(sol[0] / U_s)

            simbolos = sorted(Gs_simbolica.free_symbols - {s}, key=str)
            valores = {}
            if simbolos:
                for p in simbolos:
                    valor_str = simpledialog.askstring("Entrada de Parâmetro", f"Digite o valor numérico para '{p}':", parent=self)
                    if valor_str is None: raise ValueError("Análise cancelada pelo usuário.")
                    valores[p] = float(valor_str.replace(",", "."))
            
            Gs_numerica = Gs_simbolica.subs(valores)
            num_c, den_c = [float(c) for c in sp.Poly(sp.numer(Gs_numerica), s).all_coeffs()], [float(c) for c in sp.Poly(sp.denom(Gs_numerica), s).all_coeffs()]
            sistema_ma = ctl.TransferFunction(num_c, den_c)

            frame_ma = ttk.LabelFrame(self.frame_resultados, text="Resultados - Malha Aberta")
            frame_ma.pack(fill="x", pady=5)
            
            fig_ft = plt.figure(figsize=(8, 3)); plt.axis("off")
            if simbolos:
                fig_ft.text(0.5, 0.7, f"Simbólica (Genérica): $G(s) = {sp.latex(Gs_simbolica)}$", fontsize=16, ha="center", va="center")
                fig_ft.text(0.5, 0.3, f"Numérica: $G(s) = {sp.latex(Gs_numerica)}$", fontsize=16, ha="center", va="center", color="darkgreen")
            else:
                fig_ft.text(0.5, 0.5, rf"$G(s) = {sp.latex(Gs_numerica)}$", fontsize=16, ha="center", va="center", color="darkgreen")
            self._renderizar_figura(fig_ft, frame_ma)
            
            fig_diag, ax = plt.subplots(figsize=(7, 1.5)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 2)
            ax.text(1, 1, f"${var_u.capitalize()}(s)$"); ax.arrow(1.5, 1, 2, 0, head_width=0.08, head_length=0.2, fc="k", ec="k")
            ax.add_patch(plt.Rectangle((3.6, 0.6), 2.8, 0.8, fc="#add8e6", ec="k")); ax.text(5, 1, "G(s)", fontsize=12)
            ax.arrow(6.4, 1, 2, 0, head_width=0.08, head_length=0.2, fc="k", ec="k"); ax.text(9, 1, f"${var_y.capitalize()}(s)$")
            self._renderizar_figura(fig_diag, frame_ma)
            
            polos = sistema_ma.poles()
            if np.any(np.real(polos) > 0):
                messagebox.showerror("Sistema Instável", "O sistema em malha aberta é INSTÁVEL. Os métodos de sintonia não serão aplicados."); return

            frame_mf = ttk.LabelFrame(self.frame_resultados, text="Resultados - Controle PID e Malha Fechada")
            frame_mf.pack(fill="x", pady=5)

            if self.metodo_sintonia.get() == "reacao":
                self.sintonia_curva_reacao(sistema_ma, Gs_numerica, frame_ma, frame_mf)
            else:
                self.sintonia_resposta_frequencia(sistema_ma, Gs_numerica, frame_mf)

        except Exception as e:
            messagebox.showerror("Erro Durante a Análise", f"Ocorreu um erro: {e}")

    def sintonia_curva_reacao(self, sistema_ma, Gs_numerica, frame_ma, frame_mf):
        t_sim = np.linspace(0, 75, 2000)
        tempo, resposta = ctl.step_response(sistema_ma, T=t_sim)
        fig_resp_ma, ax_ma = plt.subplots(figsize=(8, 4)); ax_ma.plot(tempo, resposta, label="Saída")
        ax_ma.set_title("Resposta ao Degrau em Malha Aberta"); ax_ma.set_xlabel("Tempo (s)"); ax_ma.set_ylabel("Amplitude"); ax_ma.grid(True)
        
        y_final = resposta[-1]
        dy, idx_inf = np.gradient(resposta, tempo), np.argmax(np.gradient(resposta, tempo))
        t_inf, y_inf, m = tempo[idx_inf], resposta[idx_inf], dy[idx_inf]
        if m < 1e-6:
            messagebox.showwarning("Análise Interrompida", "A inclinação da curva é muito baixa para este método."); self._renderizar_figura(fig_resp_ma, frame_ma); return
        
        K, L, T = y_final, t_inf - y_inf / m, y_final / m
        if L <= 0: L = 1e-4
        
        t_reta = np.array([L, L + T]); y_reta = np.array([0, K])
        ax_ma.plot(t_reta, y_reta, 'r--', label="Tangente (Z-N)"); ax_ma.legend()
        self._renderizar_figura(fig_resp_ma, frame_ma)

        texto_analise = f"Parâmetros da Curva: K = {K:.3f} | L = {L:.3f} s | T = {T:.3f} s"
        ttk.Label(frame_mf, text=texto_analise, font=("", 10, "bold")).pack(pady=5)

        Kp, Ki, Kd = (1.2 * T / L), (1.2 * T / L) / (2 * L), (1.2 * T / L) * (0.5 * L)
        self.exibir_resultados_finais(sistema_ma, Gs_numerica, Kp, Ki, Kd, frame_mf)
    
    def sintonia_resposta_frequencia(self, sistema_ma, Gs_numerica, frame_mf):
        try:
            gm, _, _, wc = ctl.margin(sistema_ma)
            
            Ku = gm
            if Ku <= 1 or not np.isfinite(Ku):
                messagebox.showwarning("Método Inaplicável", "O sistema não possui uma margem de ganho > 1. O método Z-N 2 não é aplicável.")
                return

            if not np.isfinite(wc) or wc <= 0:
                den_ma, num_ma = sistema_ma.den[0][0], sistema_ma.num[0][0]
                char_poly_coeffs = den_ma + Ku * num_ma
                polos_mf = np.roots(char_poly_coeffs)
                
                wc_calc = 0
                for p in polos_mf:
                    if abs(np.real(p)) < 1e-5 and np.imag(p) > 0:
                        wc_calc = np.imag(p)
                        break
                if wc_calc == 0:
                    raise ValueError(f"Não foi possível calcular a frequência de oscilação para Ku={Ku:.3f}.")
                wc = wc_calc
            
            Pu = 2 * np.pi / wc
            texto_analise = f"Parâmetros de Frequência: Ganho Último (Ku) = {Ku:.3f} | Período Último (Pu) = {Pu:.3f} s"
            ttk.Label(frame_mf, text=texto_analise, font=("", 10, "bold")).pack(pady=5)
            
            Kp, Ki, Kd = 0.6 * Ku, (0.6 * Ku) / (0.5 * Pu), (0.6 * Ku) * (0.125 * Pu)
            self.exibir_resultados_finais(sistema_ma, Gs_numerica, Kp, Ki, Kd, frame_mf)
        except Exception as e:
            messagebox.showerror("Erro no Método 2", f"Ocorreu um erro inesperado durante a sintonia por resposta em frequência:\n{e}")

    def exibir_resultados_finais(self, sistema_ma, Gs_numerica, Kp, Ki, Kd, frame_mf):
        texto_pid = f"Ganhos do Controlador: Kp = {Kp:.3f} | Ki = {Ki:.3f} | Kd = {Kd:.3f}"
        ttk.Label(frame_mf, text=texto_pid, font=("", 10, "bold"), foreground="darkgreen").pack(pady=5)
        
        pid_numerico = ctl.TransferFunction([Kd, Kp, Ki], [1, 0])
        sistema_mf = ctl.feedback(pid_numerico * sistema_ma, 1)

        num_g, den_g = np.array(sistema_ma.num[0][0]), np.array(sistema_ma.den[0][0])
        num_c, den_c = np.array(pid_numerico.num[0][0]), np.array(pid_numerico.den[0][0])
        num_L = np.polymul(num_c, num_g); den_L = np.polymul(den_c, den_g)
        den_MF = np.polyadd(den_L, num_L); num_MF = num_L
        mf_simbolica = sp.Poly(num_MF, s) / sp.Poly(den_MF, s)
        pid_simbolico = sp.Poly(num_c, s) / sp.Poly(den_c, s)

        fig_ft_mf = plt.figure(figsize=(8, 3)); fig_ft_mf.text(0.5, 0.75, rf"$G_c(s) = {sp.latex(sp.N(pid_simbolico, 3))}$", fontsize=14, ha="center", color="darkred"); fig_ft_mf.text(0.5, 0.25, rf"$G_{{MF}}(s) = {sp.latex(sp.N(mf_simbolica, 3))}$", fontsize=14, ha="center", color="darkblue")
        self._renderizar_figura(fig_ft_mf, frame_mf)
        
        fig_diag_mf, ax = plt.subplots(figsize=(9, 2)); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(-1, 2)
        ax.text(0.5, 1, "R(s)"); ax.arrow(1, 1, 0.8, 0, head_width=0.1, head_length=0.2, fc='k', ec='k'); ax.add_patch(plt.Circle((2, 1), 0.2, fill=False, ec='k')); ax.text(2, 1, "+", ha='center', va='center'); ax.text(1.9, 0.7, "-", ha='center', va='center', fontsize=14); ax.arrow(2.2, 1, 1.1, 0, head_width=0.1, head_length=0.2, fc='k', ec='k'); ax.add_patch(plt.Rectangle((3.4, 0.6), 2.5, 0.8, fc="#f4cccc", ec="k")); ax.text(4.65, 1, r"$G_c(s)$", color="red"); ax.arrow(5.9, 1, 1.1, 0, head_width=0.1, head_length=0.2, fc='k', ec='k'); ax.add_patch(plt.Rectangle((7.1, 0.6), 2.5, 0.8, fc="#add8e6", ec="k")); ax.text(8.35, 1, r"$G(s)$", color="blue"); ax.arrow(9.6, 1, 1.2, 0, head_width=0.1, head_length=0.2, fc='k', ec='k'); ax.text(11.2, 1, "Y(s)"); ax.plot([8.35, 8.35, 2.3, 2.3], [0.6, -0.5, -0.5, 0.8], 'k-'); ax.arrow(2.3, 0.8, 0, 0.1, head_width=0.1, head_length=0.2, fc='k', ec='k')
        self._renderizar_figura(fig_diag_mf, frame_mf)
        

        t_sim = np.linspace(0, 75, 2000)
        tempo_mf, resposta_mf = ctl.step_response(sistema_mf, T=t_sim)
        fig_resp_mf, ax_mf = plt.subplots(figsize=(8, 4)); ax_mf.plot(tempo_mf, resposta_mf, label="Saída com PID"); ax_mf.axhline(1, color='r', linestyle='--', label='Setpoint'); ax_mf.set_title("Resposta ao Degrau no Setpoint (Malha Fechada)"); ax_mf.set_xlabel("Tempo (s)"); ax_mf.set_ylabel("Amplitude"); ax_mf.grid(True); ax_mf.legend()
        self._renderizar_figura(fig_resp_mf, frame_mf)

        tf_pert = sistema_ma / (1 + pid_numerico * sistema_ma)
        t_pert, r_pert = ctl.step_response(tf_pert, T=t_sim)
        fig_pert, ax_pert = plt.subplots(figsize=(8, 4)); ax_pert.plot(t_pert, r_pert, label="Desvio na Saída", color='orange')
        ax_pert.set_title("Rejeição a Perturbação em Degrau na Entrada da Planta"); ax_pert.set_xlabel("Tempo (s)"); ax_pert.set_ylabel("Amplitude do Desvio"); ax_pert.grid(True); ax_pert.legend()
        self._renderizar_figura(fig_pert, frame_mf)

if __name__ == "__main__":
    app = AnalisadorDeSistemas()
    app.mainloop()