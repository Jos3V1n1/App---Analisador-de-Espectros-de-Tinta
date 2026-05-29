# views/comparacaoView.py
import customtkinter as ctk
import os
import numpy as np

class ComparacaoView(ctk.CTkFrame):
    def __init__(self, master, viewmodel, sidebar):
        super().__init__(master, fg_color="transparent")
        self.vm = viewmodel  
        self.sidebar = sidebar 
        
        self.configurar_layout_centro()
        self.criar_painel_inferior_dados()
        self.criar_e_enviar_botoes_esquerda()

    def configurar_layout_centro(self):
        """Estrutura o centro da tela para mostrar o ranking de forma imponente."""
        lbl_tit = ctk.CTkLabel(self, text="📊 Módulo de Comparação e Match Estatístico", font=("Arial Black", 16))
        lbl_tit.pack(anchor="w", padx=20, pady=15)
        
        self.frame_ranking_centro = ctk.CTkFrame(self, fg_color="#18191b", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.frame_ranking_centro.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.lbl_status = ctk.CTkLabel(
            self.frame_ranking_centro, 
            text="Nenhum arquivo comparado.\nVá em 'Arquivo > Abrir Arquivo (.mca)' no topo para carregar uma amostra.", 
            font=("Arial", 13, "italic"),
            text_color="#666666"
        )
        self.lbl_status.pack(expand=True)

    def criar_painel_inferior_dados(self):
        """Tabela de diagnóstico na parte inferior para logs analíticos de rotina."""
        self.frame_diagnostico_inferior = ctk.CTkFrame(self, fg_color="#18191b", height=140, corner_radius=4)
        self.frame_diagnostico_inferior.pack(fill="x", side="bottom", pady=(5, 20), padx=20)
        self.frame_diagnostico_inferior.pack_propagate(False)
        
        frame_cabecalho = ctk.CTkFrame(self.frame_diagnostico_inferior, fg_color="#212224", height=25)
        frame_cabecalho.pack(fill="x")
        
        ctk.CTkLabel(frame_cabecalho, text="📋 Logs de Execução e Diagnóstico Analítico", font=("Arial", 11, "bold"), text_color="#aaaaaa").pack(side="left", padx=20)
        
        self.container_linhas = ctk.CTkScrollableFrame(self.frame_diagnostico_inferior, fg_color="transparent")
        self.container_linhas.pack(fill="both", expand=True, padx=5, pady=2)
        
        self.lbl_status_interno = ctk.CTkLabel(self.container_linhas, text="Nenhum log gerado. Sistema aguardando processamento.", font=("Arial", 12, "italic"), text_color="#555555")
        self.lbl_status_interno.pack(pady=15)

    def criar_e_enviar_botoes_esquerda(self):
        """Instancia e renderiza os botões de comparação diretamente na sidebar."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # 🌟 REMOVIDO: O botão btn_abrir foi retirado daqui
        btn_comparar = ctk.CTkButton(self.sidebar, text="Executar Comparação", font=("Arial", 12, "bold"), fg_color="#2da44e", hover_color="#22863a", command=self.ao_clicar_comparar)
        btn_comparar.pack(pady=10, fill="x", padx=20)
        
        self.vm.registrar_botoes([btn_comparar])

    def atualizar_status_arquivo_carregado(self, nome_arquivo):
        """Método chamado externamente quando um arquivo é aberto pelo menu superior."""
        for w in self.frame_ranking_centro.winfo_children(): 
            w.destroy()
        
        ctk.CTkLabel(
            self.frame_ranking_centro, 
            text=f"📁 Amostra Pronta para Análise!\n\nArquivo: {nome_arquivo}\n\nO vetor de contagens está pronto na memória.\nClique em 'Executar Match' para processar contra o banco.", 
            font=("Arial", 13, "bold"), 
            text_color="#ffffff"
        ).pack(expand=True)

    def ao_clicar_comparar(self):
        """Busca no banco e executa o algoritmo de cosseno com os filtros da VM."""
        main_view = self.winfo_toplevel()
        
        for w in self.frame_ranking_centro.winfo_children(): w.destroy()
        for w in self.container_linhas.winfo_children(): w.destroy()
            
        if not self.vm.dados_espectro_atual:
            ctk.CTkLabel(self.frame_ranking_centro, text="⚠️ Abra um espectro em 'Arquivo > Abrir...' antes de tentar comparar!", text_color="orange", font=("Arial", 13, "bold")).pack(expand=True)
            return

        dados_reais_banco = []
        if hasattr(main_view, "database_vm"):
            tintas_do_banco = main_view.database_vm.buscar_todas_tintas()
            try:
                for tinta in tintas_do_banco:
                    nome_tinta = tinta.get("nome")
                    dados_espectro = tinta.get("counts")
                    
                    if isinstance(dados_espectro, str):
                        dados_reais = np.fromstring(dados_espectro, sep=',')
                    else:
                        dados_reais = np.array(dados_espectro, dtype=float)
                    
                    dados_reais_banco.append({"nome": nome_tinta, "channels": dados_reais})
            except Exception as e:
                print(f"Erro no mapeamento do banco: {e}")

        if not dados_reais_banco:
            ctk.CTkLabel(self.frame_ranking_centro, text="📭 Banco de dados vazio. Cadastre espectros antes de comparar.", text_color="yellow", font=("Arial", 13)).pack(expand=True)
            return

        canal_corte = getattr(main_view.subtela_graficos, 'canal_corte_ruido', 20)
        thresh_pct = getattr(main_view.subtela_graficos, 'threshold_percentual', 0.02)
        
        ranking = self.vm.realizar_comparacao(dados_reais_banco, canal_inicial=canal_corte, threshold_percentual=thresh_pct)
        
        if ranking:
            lbl_tit_rank = ctk.CTkLabel(self.frame_ranking_centro, text="🏆 Ranking de Similaridade Encontrado:", font=("Arial Black", 14))
            lbl_tit_rank.pack(anchor="w", padx=25, pady=(20, 15))
            
            for i, item in enumerate(ranking[:5], start=1):
                texto = f"{i}º Lugar: {item['nome']} ➔ {item['porcentagem']:.2f}% de compatibilidade"
                cor = "#2da44e" if i == 1 and item['porcentagem'] > 85 else "#ffffff"
                
                lbl = ctk.CTkLabel(self.frame_ranking_centro, text=texto, font=("Arial", 13, "bold" if i==1 else "normal"), text_color=cor)
                lbl.pack(anchor="w", padx=45, pady=6)
                
            ctk.CTkLabel(self.container_linhas, text=f"✅ Match executado com sucesso! Maior similaridade: {ranking[0]['nome']} ({ranking[0]['porcentagem']:.2f}%)", font=("Arial", 12), text_color="#2da44e").pack(anchor="w", padx=15, pady=5)
            
            # 🌟 NOVA LINHA: Força o gráfico a aparecer no result_frame assim que o Match roda
            dados_grafico = self.vm.obter_dados_espectro()
            if dados_grafico and hasattr(main_view, "plotar_no_app"):
                main_view.plotar_no_app(dados_grafico, titulo_grafico=f"Espectro Analisado: {os.path.basename(self.vm.caminho_mca)}")
        else:
            ctk.CTkLabel(self.frame_ranking_centro, text="❌ Nenhuma correlação estatística pôde ser calculada para esta amostra.", text_color="crimson").pack(expand=True)
