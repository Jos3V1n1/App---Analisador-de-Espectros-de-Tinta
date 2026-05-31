# views/filtrosView.py
import customtkinter as ctk
import os

class FiltrosView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        # Passando fg_color="transparent" para mesclar com o fundo do painel principal
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel
        self.sidebar = sidebar
        
        # Guardamos os estados dos filtros como atributos acessíveis do objeto
        self.canal_corte_ruido = 20
        self.threshold_percentual = 0.02
        
        self.configurar_interface_central()

    def configurar_interface_central(self):
        """Instancia os componentes visuais estritamente dentro do próprio frame."""
        self.lbl_titulo = ctk.CTkLabel(self, text="🛠️ Ajuste de Filtros e Tratamento de Ruído", font=("Arial Black", 16))
        self.lbl_titulo.pack(pady=(20, 30), anchor="w", padx=10)
        
        # --- Container do Filtro 1: Corte de Canais ---
        self.frame_corte = ctk.CTkFrame(self, fg_color="#18191b", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.frame_corte.pack(fill="x", pady=10, padx=10)
        
        self.lbl_corte = ctk.CTkLabel(
            self.frame_corte, 
            text=f"Corte de Canais Iniciais (Remover Ruído Eletrônico): {self.canal_corte_ruido}", 
            font=("Arial", 13, "bold")
        )
        self.lbl_corte.pack(pady=(15, 5), padx=20, anchor="w")
        
        self.slider_corte = ctk.CTkSlider(self.frame_corte, from_=0, to=150, number_of_steps=150, command=self.ao_mudar_corte)
        self.slider_corte.set(self.canal_corte_ruido)
        self.slider_corte.pack(pady=(5, 15), padx=20, fill="x")
        
        # --- Container do Filtro 2: Threshold Percentual ---
        self.frame_thresh = ctk.CTkFrame(self, fg_color="#18191b", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.frame_thresh.pack(fill="x", pady=10, padx=10)
        
        self.lbl_thresh = ctk.CTkLabel(
            self.frame_thresh, 
            text=f"Threshold Limiar (Corte de Background): {self.threshold_percentual * 100:.1f}%", 
            font=("Arial", 13, "bold")
        )
        self.lbl_thresh.pack(pady=(15, 5), padx=20, anchor="w")
        
        self.slider_thresh = ctk.CTkSlider(self.frame_thresh, from_=0.0, to=0.2, number_of_steps=40, command=self.ao_mudar_thresh)
        self.slider_thresh.set(self.threshold_percentual)
        self.slider_thresh.pack(pady=(5, 15), padx=20, fill="x")

    def ao_mudar_corte(self, valor):
        """Atualiza o label em tempo real enquanto arrasta o slider."""
        self.canal_corte_ruido = int(valor)
        self.lbl_corte.configure(text=f"Corte de Canais Iniciais (Remover Ruído Eletrônico): {self.canal_corte_ruido}")

    def ao_mudar_thresh(self, valor):
        """Atualiza o label do limiar em tempo real em formato percentual."""
        self.threshold_percentual = float(valor)
        self.lbl_thresh.configure(text=f"Threshold Limiar (Corte de Background): {self.threshold_percentual * 100:.1f}%")

    def criar_e_enviar_botoes_esquerda(self):
        """Renderiza o botão de ação na barra lateral do sistema de forma limpa."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        btn_aplicar = ctk.CTkButton(
            self.sidebar, 
            text="Aplicar Filtros", 
            font=("Arial Black", 12),
            fg_color="#2b719e", 
            hover_color="#1f5171",
            command=self.aplicar_filtros
        )
        btn_aplicar.pack(pady=20, padx=20, fill="x")
        
        # Registra o botão na VM correspondente se necessário
        if hasattr(self.vm, "registrar_botoes"):
            self.vm.registrar_botoes([btn_aplicar])

    def aplicar_filtros(self):
        """Coleta os filtros e força a MainView a redesenhar o gráfico com os cortes."""
        main_view = self.winfo_toplevel()
        
        # Verifica se existe um espectro carregado na memória global
        if hasattr(main_view, "database_vm") and main_view.database_vm.dados_espectro_atual:
            dados_originais = main_view.database_vm.obter_dados_espectro()
            nome_arq = main_view.database_vm.caminho_mca
            
            if dados_originais and hasattr(main_view, "plotar_no_app"):
                nome_base = os.path.basename(nome_arq) if nome_arq else "Espectro"
                # Força a replotagem. O método plotar_no_app vai ler os sliders automaticamente!
                main_view.plotar_no_app(dados_originais, titulo_grafico=f"Espectro Filtrado: {nome_base}")
        else:
            from tkinter import messagebox
            messagebox.showwarning("Aviso", "Abra um arquivo .mca primeiro em 'Arquivo > Abrir' para aplicar os filtros.")
