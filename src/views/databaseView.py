# views/databaseView.py
import customtkinter as ctk
from tkinter import messagebox, ttk

class DatabaseView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel  
        self.sidebar = sidebar 
        
        # Criação das estruturas base em memória
        self.configurar_componentes_insercao()
        self.criar_tabela_gerenciamento()
        self.atualizar_tabela_dados()

    def configurar_componentes_insercao(self):
        """Frame contendo a parte superior dedicada ao carregamento e preenchimento de novas tintas."""
        self.container_insercao = ctk.CTkFrame(self, fg_color="transparent")
        self.container_insercao.pack(fill="x")

        # --- Linha do Arquivo Selecionado ---
        frame_arquivo = ctk.CTkFrame(self.container_insercao, fg_color="transparent")
        frame_arquivo.pack(fill="x", pady=(5, 5))
        
        lbl_arq_txt = ctk.CTkLabel(frame_arquivo, text="> Arquivo Carregado: ", font=("Arial Black", 14))
        lbl_arq_txt.pack(side="left", padx=10)
        
        self.arquivo_em_destaque = ctk.CTkFrame(frame_arquivo, height=35, fg_color="#2b2b2b", corner_radius=6)
        self.arquivo_em_destaque.pack(side="left", fill="x", expand=True, padx=10)
        self.arquivo_em_destaque.pack_propagate(False) 
        
        self.lbl_nome_arquivo = ctk.CTkLabel(
            self.arquivo_em_destaque, 
            text="Nenhum arquivo selecionado. Vá em Arquivo > Abrir...", 
            font=("Arial", 13, "italic"),
            text_color="#aaaaaa"
        )
        self.lbl_nome_arquivo.pack(fill="both", expand=True, padx=10)

        # --- Campo para Nome da Tinta ---
        frame_nome = ctk.CTkFrame(self.container_insercao, fg_color="transparent")
        frame_nome.pack(fill="x", pady=(5, 10))
        
        lbl_nome = ctk.CTkLabel(frame_nome, text="> Nome da Tinta: ", font=("Arial Black", 14))
        lbl_nome.pack(side="left", padx=10)
        
        self.txt_nome_tinta = ctk.CTkEntry(frame_nome, placeholder_text="Ex: Vermelho Lote 45", font=("Arial", 14))
        self.txt_nome_tinta.pack(side="left", fill="x", expand=True, padx=10)

    def criar_tabela_gerenciamento(self):
        """Estrutura a Treeview e o container para listar os dados salvos."""
        self.container_gerenciamento = ctk.CTkFrame(self, fg_color="transparent")
        self.container_gerenciamento.pack(fill="both", expand=True)

        self.lbl_secao = ctk.CTkLabel(self.container_gerenciamento, text="🗄️ Registros Salvos no Banco de Dados", font=("Arial Black", 14))
        self.lbl_secao.pack(anchor="w", padx=10, pady=(10, 5))

        self.frame_tabela = ctk.CTkFrame(self.container_gerenciamento, fg_color="#1e1e1e", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.frame_tabela.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=28, borderwidth=0, font=("Arial", 11))
        style.configure("Treeview.Heading", background="#1e2022", foreground="white", borderwidth=1, font=("Arial", 11, "bold"))
        style.map("Treeview", background=[('selected', '#2b719e')])

        colunas = ("id", "nome", "tamanho")
        self.tabela = ttk.Treeview(self.frame_tabela, columns=colunas, show="headings", style="Treeview")
        
        self.tabela.heading("id", text="ID / Índice")
        self.tabela.heading("nome", text="Nome da Assinatura / Tinta")
        self.tabela.heading("tamanho", text="Canais Detectados")

        self.tabela.column("id", width=80, anchor="center")
        self.tabela.column("nome", width=450, anchor="w")
        self.tabela.column("tamanho", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def configurar_modo_inserir(self):
        """Configuração visual para o modo 'Inserir Gráficos'."""
        self.container_insercao.pack(fill="x")
        self.container_gerenciamento.pack_forget() 
        
        # Limpa a barra lateral
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # 🌟 REMOVIDO: O botão 'Gerar Gráfico' foi removido desta seção
        btn_salvar = ctk.CTkButton(self.sidebar, text="💾 Salvar Assinatura", font=("Arial Black", 12), fg_color="#2ba84a", hover_color="#1f7a35", command=self.ao_clicar_salvar)
        btn_salvar.pack(pady=10, fill="x", padx=20)
        
        self.vm.registrar_botoes([btn_salvar])

    def configurar_modo_gerenciar(self):
        """Configuração visual para o modo 'Gerenciar Banco de Dados'."""
        self.container_insercao.pack_forget() 
        self.container_gerenciamento.pack(fill="both", expand=True) 
        self.atualizar_tabela_dados()

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        btn_deletar = ctk.CTkButton(self.sidebar, text="❌ Apagar Registro", font=("Arial Black", 12), fg_color="#a82b2b", hover_color="#7a1f1f", command=self.ao_clicar_deletar)
        btn_deletar.pack(pady=15, fill="x", padx=20)
        
        self.vm.registrar_botoes([btn_deletar])

    def atualizar_tabela_dados(self):
        """Busca os dados atualizados na ViewModel e reconstrói as linhas da tabela."""
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        if hasattr(self.vm, "buscar_todas_tintas"):
            tintas = self.vm.buscar_todas_tintas()
            for idx, tinta in enumerate(tintas):
                counts = tinta.get("counts", [])
                total_canais = len(counts.split(',')) if isinstance(counts, str) else len(counts)
                item_id = tinta.get("id", idx + 1)
                self.tabela.insert("", "end", values=(item_id, tinta.get("nome", "Sem Nome"), f"{total_canais} Canais"))

    def ao_clicar_carregar(self):
        nome_arquivo = self.vm.selecionar_mca()
        if nome_arquivo:
            self.lbl_nome_arquivo.configure(text=f"{nome_arquivo}", font=("Arial", 13, "bold"), text_color="#ffffff")

    def ao_clicar_salvar(self):
        nome_digitado = self.txt_nome_tinta.get()
        sucesso, mensagem = self.vm.executar_salvamento(nome_digitado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.txt_nome_tinta.delete(0, 'end')
            self.lbl_nome_arquivo.configure(text="Nenhum arquivo selecionado. Vá em Arquivo > Abrir...", font=("Arial", 13, "italic"), text_color="#aaaaaa")
            self.atualizar_tabela_dados()
        else:
            messagebox.showerror("Erro", mensagem)

    def ao_clicar_deletar(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma assinatura na tabela para poder apagá-la.")
            return

        valores = self.tabela.item(selecionado[0], "values")
        nome_registro = valores[1]

        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja apagar permanentemente a assinatura '{nome_registro}' do banco de dados?")
        if confirmar:
            if hasattr(self.vm, "excluir_tinta"):
                sucesso = self.vm.excluir_tinta(nome_registro)
                if sucesso:
                    messagebox.showinfo("Sucesso", f"'{nome_registro}' removido!")
                    self.atualizar_tabela_dados()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o registro.")
            else:
                messagebox.showerror("Erro", "Método 'excluir_tinta' não localizado na ViewModel.")
