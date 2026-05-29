# views/graficosView.py
import customtkinter as ctk
import os

class GraficosView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel  
        self.sidebar = sidebar 
        
        # Parâmetros padrão dos Filtros (Conectados aos Sliders)
        self.canal_corte_ruido = 20
        self.threshold_percentual = 0.02  # 2.0%
        
        self.configurar_layout_mestre()
        self.criar_painel_direita_filtros() # ➔ REATIVADO!
        self.criar_e_enviar_botoes_esquerda()

    def configurar_layout_mestre(self):
        """Divide o espaço central superior para acomodar o gráfico e o painel de filtros."""
        frame_arquivo = ctk.CTkFrame(self, fg_color="transparent")
        frame_arquivo.pack(fill="x", pady=(5, 10))
        
        lbl_arq_txt = ctk.CTkLabel(frame_arquivo, text="> Assinatura Espectral: ", font=("Arial Black", 14))
        lbl_arq_txt.pack(side="left", padx=10)

        self.arquivo_em_destaque = ctk.CTkFrame(frame_arquivo, height=35, fg_color="#2b2b2b", corner_radius=6)
        self.arquivo_em_destaque.pack(side="left", fill="x", expand=True, padx=10)
        self.arquivo_em_destaque.pack_propagate(False)

        self.lbl_nome_arquivo = ctk.CTkLabel(
            self.arquivo_em_destaque, 
            text="Nenhum arquivo selecionado para plotagem", 
            font=("Arial", 13, "italic"),
            text_color="#aaaaaa"
        )
        self.lbl_nome_arquivo.pack(fill="both", expand=True, padx=10)

        self.frame_superior_horizontal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_superior_horizontal.pack(fill="both", expand=True, pady=(0, 5))
        
        self.frame_grafico_centro = ctk.CTkFrame(self.frame_superior_horizontal, fg_color="transparent")
        self.frame_grafico_centro.pack(side="left", fill="both", expand=True, padx=(5, 5))

    def criar_painel_direita_filtros(self):
        """Cria a barra lateral direita com os controles deslizantes da imagem."""
        frame_direita = ctk.CTkFrame(self.frame_superior_horizontal, fg_color="#1e2022", width=260, corner_radius=0)
        frame_direita.pack(side="right", fill="y", padx=(5, 0))
        frame_direita.pack_propagate(False)
        
        # --- Controle 1: Corte de Canais ---
        lbl_corte_tit = ctk.CTkLabel(frame_direita, text="Corte de Ruído Eletrônico (Canais):", font=("Arial", 11), anchor="w")
        lbl_corte_tit.pack(fill="x", padx=15, pady=(20, 2))
        
        frame_slide1 = ctk.CTkFrame(frame_direita, fg_color="transparent")
        frame_slide1.pack(fill="x", padx=15)
        
        self.slider_corte = ctk.CTkSlider(frame_slide1, from_=0, to=100, number_of_steps=100, command=self.ao_ajustar_filtros)
        self.slider_corte.set(self.canal_corte_ruido)
        self.slider_corte.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.lbl_val_corte = ctk.CTkLabel(frame_slide1, text=str(self.canal_corte_ruido), font=("Arial", 11, "bold"), width=25)
        self.lbl_val_corte.pack(side="right")
        
        # --- Controle 2: Threshold de Intensidade ---
        lbl_thresh_tit = ctk.CTkLabel(master=frame_direita, text="Threshold de Intensidade (%):", font=("Arial", 11), anchor="w")
        lbl_thresh_tit.pack(fill="x", padx=15, pady=(15, 2))
        
        frame_slide2 = ctk.CTkFrame(frame_direita, fg_color="transparent")
        frame_slide2.pack(fill="x", padx=15)
        
        self.slider_threshold = ctk.CTkSlider(frame_slide2, from_=0, to=10, number_of_steps=100, command=self.ao_ajustar_filtros)
        self.slider_threshold.set(self.threshold_percentual * 100)
        self.slider_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.lbl_val_threshold = ctk.CTkLabel(frame_slide2, text=f"{self.threshold_percentual*100:.1f}", font=("Arial", 11, "bold"), width=25)
        self.lbl_val_threshold.pack(side="right")

    def criar_e_enviar_botoes_esquerda(self):
        """Instancia e renderiza os botões diretamente no container da barra lateral."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        btn_inspecionar = ctk.CTkButton(
            self.sidebar, 
            text="🔍 Inspecionar Filtro", 
            font=("Arial", 12, "bold"), 
            fg_color="#2da44e", 
            hover_color="#22863a", 
            command=self.atualizar_plotagem_inspecao
        )
        btn_abrir = ctk.CTkButton(self.sidebar, text="📁 Abrir Espectro", font=("Arial", 12, "bold"), command=self.ao_clicar_abrir)
        
        btn_inspecionar.pack(pady=10, fill="x", padx=20)
        btn_abrir.pack(pady=10, fill="x", padx=20)
        
        self.vm.registrar_botoes([btn_inspecionar, btn_abrir])

    def ao_clicar_abrir(self):
        nome_arquivo = self.vm.selecionar_mca()
        if nome_arquivo:
            self.lbl_nome_arquivo.configure(
                text=f" {nome_arquivo}", 
                font=("Arial", 13, "bold"),
                text_color="#ffffff"
            )
            self.ao_clicar_plotar()

    def ao_clicar_plotar(self):
        dados = self.vm.obter_dados_espectro()
        main_view = self.winfo_toplevel()
        
        if not dados:
            if hasattr(main_view, "result_frame"):
                for widget in main_view.result_frame.winfo_children(): widget.destroy()
                ctk.CTkLabel(main_view.result_frame, text="Nenhum espectro aberto para plotar!", text_color="crimson").pack(pady=20)
            return
            
        if hasattr(main_view, "plotar_no_app"):
            main_view.plotar_no_app(dados, titulo_grafico=f"Gráfico: {os.path.basename(self.vm.caminho_mca)}")

    def ao_ajustar_filtros(self, event=None):
        self.canal_corte_ruido = int(self.slider_corte.get())
        self.threshold_percentual = self.slider_threshold.get() / 100.0
        
        self.lbl_val_corte.configure(text=str(self.canal_corte_ruido))
        self.lbl_val_threshold.configure(text=f"{self.threshold_percentual*100:.1f}")
        
        if self.vm.dados_espectro_atual:
            self.atualizar_plotagem_inspecao()

    def atualizar_plotagem_inspecao(self):
        dados_duplos = self.vm.obter_dados_inspecao_filtro(self.canal_corte_ruido, self.threshold_percentual)
        main_view = self.winfo_toplevel()
        if dados_duplos and hasattr(main_view, "plotar_no_app"):
            main_view.plotar_no_app(dados_duplos, titulo_grafico="Modo Inspeção: Ajuste Fino do Sinal Espectral")
