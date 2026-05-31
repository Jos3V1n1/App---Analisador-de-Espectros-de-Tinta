# views/mainView.py
import customtkinter as ctk
import tkinter as tk  
from views.databaseView import DatabaseView
from viewmodels.databaseVM import DatabaseVM
from viewmodels.graficosVM import GraficosVM 
from views.graficosView import GraficosView 
from views.comparacaoView import ComparacaoView  
from views.filtrosView import FiltrosView
from models.graficosModel import gerar_figura_espectro
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        self.subtela_filtros = FiltrosView(self.dynamic_frame, self.graficos_vm, self.container_botoes_dinamicos)

        # Inicia exibindo a tela principal de inserção
        self.alternar_tela("inserir")

    def configurar_menu_superior(self):
        """Cria a barra de menus no topo da janela com a opção de troca de telas."""
        barra_menu = tk.Menu(self)
        
        menu_arquivo = tk.Menu(barra_menu, tearoff=0)
        menu_arquivo.add_command(label="Escolher arquivo (.mca)", command=self.disparar_abertura_global)
        barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)
                
        menu_opcoes = tk.Menu(barra_menu, tearoff=0)
        # 🌟 MODIFICADO: Modos separados bem definidos para cada opção
        menu_opcoes.add_command(label="Inserir Gráficos", command=lambda: self.alternar_tela("inserir"))
        menu_opcoes.add_command(label="Comparar Gráficos", command=lambda: self.alternar_tela("comparacao"))
        menu_opcoes.add_command(label="Gerenciar Banco de Dados", command=lambda: self.alternar_tela("gerenciar"))
        
        barra_menu.add_cascade(label="Opções", menu=menu_opcoes)

        menu_filtros = tk.Menu(barra_menu, tearoff=0)
        # Agora ele chama a função alternar_tela corretamente
        menu_filtros.add_command(label="Ajustar Canais e Threshold", command=lambda: self.alternar_tela("filtros"))
        barra_menu.add_cascade(label="Filtros", menu=menu_filtros)
        
        self.config(menu=barra_menu)

    def disparar_abertura_global(self):
        """Gerencia a abertura de arquivos sincronizando o estado, resetando filtros para o padrão e plotando."""
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

            # 🌟 NOVO: FORÇA O RESET DOS FILTROS PARA OS VALORES PADRÕES DO SISTEMA
            padrao_corte = 20
            padrao_thresh = 0.02

            if hasattr(self, "subtela_filtros") and self.subtela_filtros:
                # 1. Reseta os atributos lógicos da tela de filtros
                self.subtela_filtros.canal_corte_ruido = padrao_corte
                self.subtela_filtros.threshold_percentual = padrao_thresh
                
                # 2. Reseta os Sliders visuais se eles existirem na memória
                if hasattr(self.subtela_filtros, "slider_corte") and self.subtela_filtros.slider_corte:
                    self.subtela_filtros.slider_corte.set(padrao_corte)
                if hasattr(self.subtela_filtros, "slider_thresh") and self.subtela_filtros.slider_thresh:
                    self.subtela_filtros.slider_thresh.set(padrao_thresh)
                    
                # 3. Reseta os textos (Labels) associados
                if hasattr(self.subtela_filtros, "lbl_corte") and self.subtela_filtros.lbl_corte:
                    self.subtela_filtros.lbl_corte.configure(text=f"Corte de Canais Iniciais (Remover Ruído Eletrônico): {padrao_corte}")
                if hasattr(self.subtela_filtros, "lbl_thresh") and self.subtela_filtros.lbl_thresh:
                    self.subtela_filtros.lbl_thresh.configure(text=f"Threshold Limiar (Corte de Background): {padrao_thresh * 100:.1f}%")

            # 4. Obtém os dados e plota o gráfico limpo
            dados_grafico = self.database_vm.obter_dados_espectro()
            if dados_grafico:
                # Como limpamos a subtela_filtros logo acima, o plotar_no_app vai ler 20 e 0.02 automaticamente!
                self.plotar_no_app(dados_grafico, titulo_grafico=f"Espectro Carregado de Arquivos: {nome_arquivo}")

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
        # 🌟 AJUSTADO: Agora todas as quatro subtelas são devidamente ocultadas ao alternar
        self.subtela_banco.pack_forget()
        self.subtela_graficos.pack_forget()
        self.subtela_comparacao.pack_forget()
        self.subtela_filtros.pack_forget()  # <--- Linha crucial para sumir com os sliders fantasmas
        
        # Limpa os botões antigos da barra lateral
        for widget in self.container_botoes_dinamicos.winfo_children():
            widget.destroy()

        # Reexibe a seção de gráficos caso venha de outra tela que não seja a de gerenciamento puro
        if modo == "gerenciar":
            self.result_frame.pack_forget()
        else:
            self.result_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        # ESTADOS DA DATABASE VIEW (Inserir vs Gerenciar)
        if modo == "inserir":
            self.subtela_banco.pack(fill="both", expand=True)
            if hasattr(self.subtela_banco, "configurar_modo_inserir"):
                self.subtela_banco.configurar_modo_inserir()

        elif modo == "gerenciar":
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

        elif modo == "filtros":
            self.subtela_filtros.pack(fill="both", expand=True)
            if hasattr(self.subtela_filtros, "criar_e_enviar_botoes_esquerda"):
                self.subtela_filtros.criar_e_enviar_botoes_esquerda()

    def plotar_no_app(self, parsed_data, titulo_grafico):
        """Renderiza o gráfico aplicando dinamicamente os filtros ativos ou vindos do banco."""
        import numpy as np
        
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # 1. Copia os dados originais para não corromper o arquivo na memória
        dados_filtrados = parsed_data.copy()
        
        # Garante que estamos lidando com um array NumPy desde o início
        channels = np.array(dados_filtrados.get("channels", []))
        
        # 🌟 NOVO: Preserva ou reconstrói o eixo X (canais ou energia) se já veio calibrado do banco
        if "canais" in dados_filtrados:
            # Se a ComparacaoView já calculou o eixo em keV, mantemos ele intacto!
            pass
        else:
            # Caso contrário (abertura de arquivo comum), inicia como canais normais
            dados_filtrados["canais"] = np.arange(len(channels))
        
        # 2. DEFINIÇÃO DOS FILTROS: Prioriza o que veio no dicionário (Banco) e usa a View como Fallback
        if "canal_corte" in dados_filtrados:
            canal_corte = dados_filtrados["canal_corte"]
        elif hasattr(self, "subtela_filtros"):
            canal_corte = self.subtela_filtros.canal_corte_ruido
        else:
            canal_corte = 20

        if "threshold" in dados_filtrados:
            threshold_pct = dados_filtrados["threshold"]
        elif hasattr(self, "subtela_filtros"):
            threshold_pct = self.subtela_filtros.threshold_percentual
        else:
            threshold_pct = 0.02
            
        # Sincronização mandatória com a aba de filtros
        if hasattr(self, "subtela_filtros") and self.subtela_filtros:
            self.subtela_filtros.canal_corte_ruido = canal_corte
            self.subtela_filtros.threshold_percentual = threshold_pct
            if hasattr(self.subtela_filtros, "slider_corte") and self.subtela_filtros.slider_corte:
                self.subtela_filtros.slider_corte.set(canal_corte)
            if hasattr(self.subtela_filtros, "slider_thresh") and self.subtela_filtros.slider_thresh:
                val_visual = 0.199 if threshold_pct == 0.2 else threshold_pct
                self.subtela_filtros.slider_thresh.set(val_visual)
            if hasattr(self.subtela_filtros, "lbl_corte") and self.subtela_filtros.lbl_corte:
                self.subtela_filtros.lbl_corte.configure(text=f"Corte de Canais Iniciais (Remover Ruído Eletrônico): {canal_corte}")
            if hasattr(self.subtela_filtros, "lbl_thresh") and self.subtela_filtros.lbl_thresh:
                self.subtela_filtros.lbl_thresh.configure(text=f"Threshold Limiar (Corte de Background): {threshold_pct * 100:.1f}%")

        # FILTRO 1: Corte de Canais Iniciais
        if canal_corte > 0 and len(channels) > canal_corte:
            channels[:canal_corte] = 0
            
        # FILTRO 2: Threshold Percentual
        if threshold_pct > 0 and len(channels) > 0:
            limiar_absoluto = np.max(channels) * threshold_pct
            channels[channels < limiar_absoluto] = 0

        dados_filtrados["channels"] = channels

        # 3. Gera a figura usando a sua função do modelo (que agora receberá 'calibrado': True e o eixo x em 'canais')
        fig = gerar_figura_espectro(dados_filtrados, titulo_grafico)
        
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.result_frame)
        toolbar.update()
        toolbar.pack(fill="x", padx=10, pady=(0, 5))

        plt.close(fig)
