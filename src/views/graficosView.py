# views/graficosView.py
import customtkinter as ctk
import os
import numpy as np

class GraficosView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel  
        self.sidebar = sidebar 
        
        self.configurar_componentes_centro()
        self.criar_e_enviar_botoes()

    def configurar_componentes_centro(self):
        """Gera estritamente a linha de monitoramento com a label fixa na tela central."""
        frame_arquivo = ctk.CTkFrame(self, fg_color="transparent")
        frame_arquivo.pack(fill="x", expand=True, pady=15)
        
        # A label correta fixada no centro do frame dinâmico
        lbl_arq_txt = ctk.CTkLabel(frame_arquivo, text="> Assinatura Espectral: ", font=("Arial Black", 14))
        lbl_arq_txt.pack(side="left", padx=10)

        self.arquivo_em_destaque = ctk.CTkFrame(frame_arquivo, height=35, fg_color="#2b2b2b", corner_radius=6)
        self.arquivo_em_destaque.pack(side="left", fill="x", expand=True, padx=10)
        self.arquivo_em_destaque.pack_propagate(False)

        # 🔍 CORREÇÃO: Recria a label que vai de facto receber o nome do arquivo aberto
        self.lbl_nome_arquivo = ctk.CTkLabel(
            self.arquivo_em_destaque, 
            text="Nenhum arquivo selecionado para plotagem", 
            font=("Arial", 13, "italic"),
            text_color="#aaaaaa"
        )
        self.lbl_nome_arquivo.pack(fill="both", expand=True, padx=10)

        # Frame para exibir os rankings de comparação na interface central
        self.frame_ranking = ctk.CTkFrame(self, fg_color="black") # Mudei para transparent para alinhar com o fundo
        self.frame_ranking.pack(fill="x", pady=10)
           
    def criar_e_enviar_botoes(self):
        """Instancia os botões de controle apontando para a sidebar e registra na VM."""
        # 1. Injeta o botão de Abrir Espectro na Sidebar
        btn_abrir = ctk.CTkButton(
            self.sidebar, 
            text="Abrir Espectro", 
            font=("Arial Black", 12), 
            command=self.ao_clicar_abrir
        )

        # 2. Injeta o botão de Comparar Amostra na Sidebar
        btn_comparar = ctk.CTkButton(
            self.sidebar, 
            text="🔍 Comparar Amostra", 
            font=("Arial Black", 12), 
            fg_color="green", 
            command=self.ao_clicar_comparar
        )

        # Registra ambos na VM para a MainView poder recolher
        self.vm.registrar_botoes([btn_abrir, btn_comparar])

        # Se a MainView já existir no topo, força a atualização da sidebar de imediato
        main_view = self.winfo_toplevel()
        if hasattr(main_view, "atualizar_sidebar_com_botoes_da_vm"):
            main_view.atualizar_sidebar_com_botoes_da_vm()
        
    def ao_clicar_abrir(self):
        nome_arquivo = self.vm.selecionar_mca()
        if nome_arquivo:
            # Agora a label existe e vai mudar o texto dinamicamente!
            self.lbl_nome_arquivo.configure(
                text=f" {nome_arquivo}", 
                font=("Arial", 13, "bold"),
                text_color="#ffffff"
            )
            # Renderiza o gráfico automaticamente assim que o arquivo é escolhido
            self.ao_clicar_plotar()

    def ao_clicar_plotar(self):
        dados = self.vm.obter_dados_espectro()
        main_view = self.winfo_toplevel()
        
        if not dados:
            if hasattr(main_view, "result_frame"):
                for widget in main_view.result_frame.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(main_view.result_frame, text="Nenhum espectro aberto para plotar!", text_color="crimson").pack(pady=20)
            return
            
        if hasattr(main_view, "plotar_no_app"):
            main_view.plotar_no_app(dados, titulo_grafico=f"Gráfico: {os.path.basename(self.vm.caminho_mca)}")

    def ao_clicar_comparar(self):
        """Dispara a busca coletando dados REAIS do Banco pela MainView."""
        main_view = self.winfo_toplevel()
        
        # Limpa ranking anterior da tela
        for w in self.frame_ranking.winfo_children():
            w.destroy()
            
        if not self.vm.dados_espectro_atual:
            ctk.CTkLabel(self.frame_ranking, text="⚠️ Abra um arquivo de amostra primeiro!", text_color="orange").pack()
            return

        dados_banco = []
        
        if hasattr(main_view, "database_vm"):
            vm_banco = main_view.database_vm
            
            # Chama o método que acabamos de criar na sua DatabaseVM
            if hasattr(vm_banco, "buscar_todas_tintas"):
                tintas_do_banco = vm_banco.buscar_todas_tintas()
                
                try:
                    for tinta in tintas_do_banco:
                        nome_tinta = tinta.get("nome")
                        dados_espectro = tinta.get("counts")
                        
                        # Converte os canais salvos de string do banco para array NumPy
                        if isinstance(dados_espectro, str):
                            dados_reais = np.fromstring(dados_espectro, sep=',')
                        else:
                            dados_reais = np.array(dados_espectro, dtype=float)
                        
                        dados_banco.append({
                            "nome": nome_tinta,
                            "channels": dados_reais
                        })
                except Exception as e:
                    print(f"Erro ao reformatar dados do banco: {e}")
                    ctk.CTkLabel(self.frame_ranking, text="❌ Erro na estrutura dos dados salvos.", text_color="crimson").pack()
                    return

        if not dados_banco:
            ctk.CTkLabel(self.frame_ranking, text="Nenhuma tinta cadastrada no banco de dados.", text_color="yellow").pack()
            return

        # Executa a comparação por cosseno contra as assinaturas REAIS
        ranking = self.vm.realizar_comparacao(
            dados_banco, 
            canal_inicial=20,            # Ignora canais 0 a 19 (Ruído de baixa energia)
            threshold_percentual=0.02    # Filtra ruídos abaixo de 2% do pico principal
        )
        
        if ranking:
            lbl_tit = ctk.CTkLabel(self.frame_ranking, text="Ranking de Similaridade:", font=("Arial", 12, "bold"))
            lbl_tit.pack(anchor="w", padx=10)
            
            for item in ranking[:3]: 
                texto_rank = f"• {item['nome']}: {item['porcentagem']:.2f}% de match"
                lbl_item = ctk.CTkLabel(self.frame_ranking, text=texto_rank, font=("Arial", 12))
                lbl_item.pack(anchor="w", padx=25)
    
        # Para colocar temporariamente dentro de ao_clicar_comparar na views/graficosView.py:

        # Pega o vetor bruto da amostra aberta
        ch_brutos = self.vm.dados_espectro_atual.get("channels", np.array([]))

        # Importa a função de filtro para testar o resultado
        from models.graficosModel import aplicar_filtro_ruido
        ch_filtrados = aplicar_filtro_ruido(ch_brutos, canal_inicial=20, threshold_percentual=0.02)

        # Exibe o diagnóstico no terminal
        print("\n--- DIAGNÓSTICO DO FILTRO DE RUÍDO ---")
        print(f"Canais Totais do Arquivo: {len(ch_brutos)}")
        print(f"Soma das Contagens Brutas: {np.sum(ch_brutos)}")
        print(f"Soma das Contagens Após Filtro: {np.sum(ch_filtrados)}")
        print(f"Canais Zerados pelo Filtro: {np.count_nonzero(ch_brutos) - np.count_nonzero(ch_filtrados)}")
        print("---------------------------------------\n")
