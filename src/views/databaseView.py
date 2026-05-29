# views/databaseView.py
import customtkinter as ctk
import os
from tkinter import messagebox

class DatabaseView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel  
        self.sidebar = sidebar 
        
        self.configurar_componentes_centro()
        self.criar_e_enviar_botoes()

    def configurar_componentes_centro(self):
        """Desenha o conteúdo central (Nome da Tinta e Indicador de Arquivo)."""

        # --- Linha que indica o Arquivo Selecionado (A que tinha sumido) ---
        frame_arquivo = ctk.CTkFrame(self, fg_color="transparent")
        frame_arquivo.pack(fill="x", pady=(5, 15))
        
        lbl_arq_txt = ctk.CTkLabel(frame_arquivo, text="> Arquivo Carregado: ", font=("Arial Black", 14))
        lbl_arq_txt.pack(side="left", padx=10)
        
        # Frame de fundo escuro para destacar o nome do arquivo
        self.arquivo_em_destaque = ctk.CTkFrame(frame_arquivo, height=35, fg_color="#2b2b2b", corner_radius=6)
        self.arquivo_em_destaque.pack(side="left", fill="x", expand=True, padx=10)
        self.arquivo_em_destaque.pack_propagate(False) # Mantém o tamanho fixo do frame
        
        self.lbl_nome_arquivo = ctk.CTkLabel(
            self.arquivo_em_destaque, 
            text="Nenhum arquivo selecionado", 
            font=("Arial", 13, "italic"),
            text_color="#aaaaaa"
        )
        self.lbl_nome_arquivo.pack(fill="both", expand=True, padx=10)

        # --- Campo para Nome da Tinta ---
        frame_nome = ctk.CTkFrame(self, fg_color="transparent")
        frame_nome.pack(fill="x", pady=(10, 5))
        
        lbl_nome = ctk.CTkLabel(frame_nome, text="> Nome da Tinta: ", font=("Arial Black", 14))
        lbl_nome.pack(side="left", padx=10)
        
        self.txt_nome_tinta = ctk.CTkEntry(frame_nome, placeholder_text="Ex: Vermelho Lote 45", font=("Arial", 14))
        self.txt_nome_tinta.pack(side="left", fill="x", expand=True, padx=10)

    def criar_e_enviar_botoes(self):
        """Gera os botões físicos diretamente dentro da sidebar."""
        btn_carregar = ctk.CTkButton(self.sidebar, text="Carregar MCA", font=("Arial Black", 12), command=self.ao_clicar_carregar)
        btn_analisar = ctk.CTkButton(self.sidebar, text="📊 Gerar Gráfico", font=("Arial Black", 12), fg_color="#2b719e", command=self.ao_clicar_analisar)
        btn_salvar = ctk.CTkButton(self.sidebar, text="💾 Salvar Assinatura", font=("Arial Black", 12), fg_color="#2ba84a", hover_color="#1f7a35", command=self.ao_clicar_salvar)

        self.vm.registrar_botoes([btn_carregar, btn_analisar, btn_salvar])

    def ao_clicar_carregar(self):
        """Chama a VM e atualiza a label local da própria View."""
        nome_arquivo = self.vm.selecionar_mca()
        if nome_arquivo:
            # Atualiza diretamente a label local
            self.lbl_nome_arquivo.configure(
                text=f"{nome_arquivo}", 
                font=("Arial", 13, "bold"),
                text_color="#ffffff"
            )

    def ao_clicar_analisar(self):
        dados = self.vm.obter_dados_espectro()
        main_view = self.winfo_toplevel()
        if not dados:
            if hasattr(main_view, "result_frame"):
                for widget in main_view.result_frame.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(main_view.result_frame, text="Selecione um arquivo .mca/.spe primeiro!", text_color="yellow").pack(pady=20)
            return
        if hasattr(main_view, "plotar_no_app"):
            main_view.plotar_no_app(dados, titulo_grafico=f"Espectro: {os.path.basename(self.vm.caminho_mca)}")

    def ao_clicar_salvar(self):
        nome_digitado = self.txt_nome_tinta.get()
        sucesso, mensagem = self.vm.executar_salvamento(nome_digitado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.txt_nome_tinta.delete(0, 'end')
            self.lbl_nome_arquivo.configure(text="Nenhum arquivo selecionado", font=("Arial", 13, "italic"), text_color="#aaaaaa")
        else:
            messagebox.showerror("Erro", mensagem)
