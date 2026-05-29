# views/mainView.py
import customtkinter as ctk
from views.databaseView import DatabaseView
from viewmodels.databaseVM import DatabaseVM
from viewmodels.graficosVM import GraficosVM           # Adicionado a importação da GraficosVM
from views.graficosView import GraficosView             # Adicionado a importação da GraficosView
from models.graficosModel import gerar_figura_espectro  # Importa a construção limpa do gráfico
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Espectros")
        self.geometry("1400x800")

        # Mantém intactas as VMs originais e adiciona a de gráficos recebida
        self.database_vm = DatabaseVM()
        self.graficos_vm = GraficosVM()

        self.configurar_layout_base()
        self.mostrar_tela_inicial()

    def configurar_layout_base(self):
        # --- SIDEBAR FIXA ---
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.pack(side="left", fill="y")
        
        self.lbl_menu = ctk.CTkLabel(self.sidebar, text="☰ Menu", font=("Arial Black", 18, "bold"))
        self.lbl_menu.pack(pady=20)

        # Mantém o container limpo para receber os botões originais da DatabaseView
        self.container_botoes_dinamicos = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.container_botoes_dinamicos.pack(fill="both", expand=True, pady=10)

        # --- ÁREA CENTRAL PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Container Dinâmico Central (Onde a GraficosView injetará a label sem deletar o resto)
        self.dynamic_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dynamic_frame.pack(fill="x", padx=40, pady=10)

        # Container Inferior Fixado (Para os gráficos)
        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", corner_radius=8)
        self.result_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))

    def mostrar_tela_inicial(self):
        """Instancia e unifica as views para que os elementos originais permaneçam visíveis."""
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        # 1. Carrega os inputs e botões padrão da sua DatabaseView original
        self.subtela_banco = DatabaseView(self.dynamic_frame, self.database_vm, self.container_botoes_dinamicos)
        self.subtela_banco.pack(fill="both", expand=True)

        # 2. Injeta estritamente a label de Gráficos no mesmo frame central, sem apagar o banco
        self.subtela_graficos = GraficosView(self.dynamic_frame, self.graficos_vm, self.container_botoes_dinamicos)
        self.subtela_graficos.pack(fill="both", expand=True, pady=(10, 0))

        # Atualiza a barra lateral organizando o layout dos botões originais do seu sistema
        self.atualizar_sidebar_com_botoes_da_vm()

    def atualizar_sidebar_com_botoes_da_vm(self):
        """Preenche a barra lateral com os botões vindos do banco e dos gráficos."""
        # Limpa o que estava na barra antes
        for widget in self.container_botoes_dinamicos.winfo_children():
            widget.pack_forget() 

        # 1. Pega e renderiza os botões originais da DatabaseVM
        botoes_banco = self.database_vm.obter_botoes_registrados()
        for botao in botoes_banco:
            botao.pack(pady=10, fill="x", padx=20)

        # 2. Pega e renderiza o botão de Comparar da GraficosVM
        botoes_grafico = self.graficos_vm.obter_botoes_registrados()
        for botao in botoes_grafico:
            botao.pack(pady=10, fill="x", padx=20)

    def plotar_no_app(self, parsed_data, titulo_grafico):
            """Renderiza no Canvas a figura gerada e estruturada estritamente dentro do Model."""
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            # O modelo constrói o gráfico de forma isolada
            fig = gerar_figura_espectro(parsed_data, titulo_grafico)
            
            canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            # 🔍 ADICIONA A BARRA DE ZOOM E NAVEGAÇÃO DO MATPLOTLIB
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(canvas, self.result_frame)
            toolbar.update()
            toolbar.pack(fill="x", padx=10, pady=(0, 5))

            plt.close(fig)
