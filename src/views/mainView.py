# views/mainView.py
import customtkinter as ctk
import tkinter as tk  
from views.databaseView import DatabaseView
from viewmodels.databaseVM import DatabaseVM
from viewmodels.graficosVM import GraficosVM 
from views.graficosView import GraficosView 
from views.comparacaoView import ComparacaoView  
from models.graficosModel import gerar_figura_espectro
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Espectros")
        self.geometry("1400x800")

        self.database_vm = DatabaseVM()
        self.graficos_vm = GraficosVM()

        self.configurar_menu_superior()
        self.configurar_layout_base()
        
        self.subtela_banco = DatabaseView(self.dynamic_frame, self.database_vm, self.container_botoes_dinamicos)
        self.subtela_graficos = GraficosView(self.dynamic_frame, self.graficos_vm, self.container_botoes_dinamicos)
        self.subtela_comparacao = ComparacaoView(self.dynamic_frame, self.graficos_vm, self.container_botoes_dinamicos)

        # Inicia exibindo a tela principal de inserção
        self.alternar_tela("inserir")

    def configurar_menu_superior(self):
        """Cria a barra de menus no topo da janela com a opção de troca de telas."""
        barra_menu = tk.Menu(self)
        
        menu_arquivo = tk.Menu(barra_menu, tearoff=0)
        menu_arquivo.add_command(label="Abrir Arquivo (.mca)", command=self.disparar_abertura_global)
        barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)
                
        menu_opcoes = tk.Menu(barra_menu, tearoff=0)
        # 🌟 MODIFICADO: Modos separados bem definidos para cada opção
        menu_opcoes.add_command(label="Inserir Gráficos", command=lambda: self.alternar_tela("inserir"))
        menu_opcoes.add_command(label="Comparar Gráficos", command=lambda: self.alternar_tela("comparacao"))
        menu_opcoes.add_command(label="Gerenciar Banco de Dados", command=lambda: self.alternar_tela("gerenciar"))
        
        barra_menu.add_cascade(label="Opções", menu=menu_opcoes)

        menu_filtros = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Filtros", menu=menu_filtros)
        
        self.config(menu=barra_menu)

    def disparar_abertura_global(self):
        """Gerencia a abertura de arquivos sincronizando o estado e atualizando os gráficos instantaneamente."""
        nome_arquivo = self.database_vm.selecionar_mca()
        if nome_arquivo:
            self.subtela_banco.lbl_nome_arquivo.configure(
                text=f"{nome_arquivo}", 
                font=("Arial", 13, "bold"),
                text_color="#ffffff"
            )
            self.graficos_vm.dados_espectro_atual = self.database_vm.dados_espectro_atual
            self.graficos_vm.caminho_mca = self.database_vm.caminho_mca
            
            self.subtela_comparacao.atualizar_status_arquivo_carregado(nome_arquivo)

            dados_grafico = self.database_vm.obter_dados_espectro()
            if dados_grafico:
                self.plotar_no_app(dados_grafico, titulo_grafico=f"Espectro Carregado: {nome_arquivo}")

    def configurar_layout_base(self):
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.pack(side="left", fill="y")
        
        self.lbl_menu = ctk.CTkLabel(self.sidebar, text="☰ Menu", font=("Arial Black", 18, "bold"))
        self.lbl_menu.pack(pady=20)

        self.container_botoes_dinamicos = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.container_botoes_dinamicos.pack(fill="both", expand=True, pady=10)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.dynamic_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dynamic_frame.pack(fill="x", padx=40, pady=10)

        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", corner_radius=8)
        self.result_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))

    def alternar_tela(self, modo: str):
        """Gerencia visibilidade dos frames centrais e reconstrói a barra lateral."""
        self.subtela_banco.pack_forget()
        self.subtela_graficos.pack_forget()
        self.subtela_comparacao.pack_forget()
        
        for widget in self.container_botoes_dinamicos.winfo_children():
            widget.destroy()

        # Reexibe a seção de gráficos caso venha de outra tela que não seja a de gerenciamento puro
        if modo != "gerenciar":
            self.result_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        # 🌟 ESTADOS DA DATABASE VIEW (Inserir vs Gerenciar)
        if modo == "inserir":
            self.subtela_banco.pack(fill="both", expand=True)
            if hasattr(self.subtela_banco, "configurar_modo_inserir"):
                self.subtela_banco.configurar_modo_inserir()

        elif modo == "gerenciar":
            # Oculta o container inferior de gráficos para dar espaço total à visualização do banco
            self.result_frame.pack_forget()
            self.subtela_banco.pack(fill="both", expand=True)
            if hasattr(self.subtela_banco, "configurar_modo_gerenciar"):
                self.subtela_banco.configurar_modo_gerenciar()

        elif modo == "graficos":
            self.subtela_graficos.pack(fill="both", expand=True, pady=(10, 0))
            if hasattr(self.subtela_graficos, "criar_e_enviar_botoes_esquerda"):
                self.subtela_graficos.criar_e_enviar_botoes_esquerda()

        elif modo == "comparacao":
            self.subtela_comparacao.pack(fill="both", expand=True)
            if hasattr(self.subtela_comparacao, "criar_e_enviar_botoes_esquerda"):
                self.subtela_comparacao.criar_e_enviar_botoes_esquerda()

    def plotar_no_app(self, parsed_data, titulo_grafico):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        fig = gerar_figura_espectro(parsed_data, titulo_grafico)
        
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.result_frame)
        toolbar.update()
        toolbar.pack(fill="x", padx=10, pady=(0, 5))

        plt.close(fig)
