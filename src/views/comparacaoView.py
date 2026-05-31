# views/comparacaoView.py
import customtkinter as ctk
import os
import numpy as np
from tkinter import messagebox

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
            text="Nenhum arquivo comparado.\n\nEscolha uma Assinatura do Banco ao lado ou vá em 'Arquivo > Abrir Arquivo (.mca)' no topo.", 
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
        
        ctk.CTkLabel(frame_cabecalho, text="Logs de Execução e Diagnóstico Analítico", font=("Arial", 11, "bold"), text_color="#aaaaaa").pack(side="left", padx=20)
        
        self.container_linhas = ctk.CTkScrollableFrame(self.frame_diagnostico_inferior, fg_color="transparent")
        self.container_linhas.pack(fill="both", expand=True, padx=5, pady=2)
        
        self.lbl_status_interno = ctk.CTkLabel(self.container_linhas, text="Nenhum log gerado. Sistema aguardando processamento.", font=("Arial", 12, "italic"), text_color="#555555")
        self.lbl_status_interno.pack(pady=15)

    def criar_e_enviar_botoes_esquerda(self):
        """Instancia e renderiza os botões de comparação e o painel de resgate na sidebar."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()
       
        # Painel para selecionar e carregar uma tinta do banco diretamente pela aba comparar
        frame_resgate = ctk.CTkFrame(self.sidebar, fg_color="#1e1e1e", border_width=1, border_color="#2b2b2b", corner_radius=6)
        frame_resgate.pack(fill="x", padx=20, pady=5)
        
        lbl_painel = ctk.CTkLabel(frame_resgate, text="Referência do Banco", font=("Arial", 11, "bold"), text_color="#aaaaaa")
        lbl_painel.pack(pady=(5, 2), padx=10, anchor="w")
        
        # Dropdown para listar as assinaturas salvas
        self.opcoes_banco = ctk.CTkOptionMenu(frame_resgate, values=["Clique em Atualizar..."], font=("Arial", 11),
                                               text_color="#000000", 
                                               fg_color="#ffffff",
                                               button_color="#d1d1d1",
                                               button_hover_color="#a3a3a3")
        self.opcoes_banco.pack(fill="x", padx=10, pady=5)
        
        # Container para botões auxiliares do painel
        frame_botoes_resgate = ctk.CTkFrame(frame_resgate, fg_color="transparent")
        frame_botoes_resgate.pack(fill="x", padx=10, pady=(0, 8))
        
        btn_refresh = ctk.CTkButton(frame_botoes_resgate, text="Resetar", text_color="#000000", fg_color="#d1d1d1", hover_color="#a3a3a3", width=35, command=self.atualizar_dropdown_banco)
        btn_refresh.pack(side="left", padx=(0, 5))
        
        btn_carregar_banco = ctk.CTkButton(frame_botoes_resgate, text="Usar Tinta", font=("Arial", 12, "bold"), text_color="#000000", fg_color="#a3a3a3", hover_color="#7c7c7c", command=self.ao_escolher_tinta_banco)
        btn_carregar_banco.pack(side="left", fill="x", expand=True)

        # Botão padrão de processamento
        btn_comparar = ctk.CTkButton(self.sidebar, text="Executar Comparação", font=("Arial", 12, "bold"), fg_color="#2da44e", hover_color="#22863a", command=self.ao_clicar_comparar)
        btn_comparar.pack(pady=(10, 15), fill="x", padx=20)

        self.vm.registrar_botoes([btn_comparar, btn_carregar_banco])
        
        # Carrega a lista do banco inicialmente ao construir a tela
        self.atualizar_dropdown_banco()

    def atualizar_dropdown_banco(self):
        """Varre as assinaturas existentes na base de dados para atualizar as opções do menu."""
        main_view = self.winfo_toplevel()
        if hasattr(main_view, "database_vm"):
            try:
                tintas = main_view.database_vm.buscar_todas_tintas()
                nomes = [t.get("nome") for t in tintas if t.get("nome")]
                if nomes:
                    self.opcoes_banco.configure(values=nomes)
                    self.opcoes_banco.set(nomes[0])
                    return
            except Exception as e:
                print(f"Erro ao atualizar dropdown do comparador: {e}")
                
        self.opcoes_banco.configure(values=["Nenhuma tinta salva"])
        self.opcoes_banco.set("Nenhuma tinta salva")

    def ao_escolher_tinta_banco(self):
        """Busca a assinatura no banco e plota o gráfico garantindo o eixo X em keV 
        baseado na calibração do espectro atualmente carregado na MainView."""
        nome_selecionado = self.opcoes_banco.get()
        if nome_selecionado in ["Clique em Atualizar...", "Nenhuma tinta salva"]:
            messagebox.showwarning("Aviso", "Cadastre ou selecione uma assinatura válida do banco.")
            return
            
        main_view = self.winfo_toplevel()
        if hasattr(main_view, "database_vm"):
            tintas = main_view.database_vm.buscar_todas_tintas()
            tinta_alvo = next((t for t in tintas if t.get("nome") == nome_selecionado), None)
            
            if tinta_alvo:
                # 1. RECUPERAÇÃO DAS CONTAGENS DA TINTA
                espectro_dados = tinta_alvo.get("counts")
                if isinstance(espectro_dados, str):
                    vetor_counts = np.fromstring(espectro_dados, sep=',')
                else:
                    vetor_counts = np.array(espectro_dados, dtype=float)

                # 2. CAPTURA DOS FILTROS DA TINTA (Padrão inteligente)
                canal_corte = tinta_alvo.get("canal_corte", 0)
                thresh_banco = tinta_alvo.get("threshold_utilizado", 0.02)
                
                # Tratamento numérico do threshold
                valor_bruto = float(thresh_banco) if thresh_banco is not None else 0.02
                if valor_bruto >= 1.0:
                    thresh_pct = valor_bruto / 100.0
                elif 0.0 < valor_bruto < 1.0:
                    thresh_pct = valor_bruto
                else:
                    thresh_pct = 0.0

                # 3. CAPTURA INTELIGENTE DA CALIBRAÇÃO (Usa a do ficheiro aberto como referência)
                coef_a, coef_b, coef_c = 1.0, 0.0, 0.0
                
                # Tenta puxar os coeficientes ativos que vieram do ficheiro .mca na MainView
                if hasattr(main_view, "graficos_vm") and main_view.graficos_vm.dados_espectro_atual:
                    dados_ativos = main_view.graficos_vm.dados_espectro_atual
                    coef_a = float(dados_ativos.get("a", 1.0))
                    coef_b = float(dados_ativos.get("b", 0.0))
                    coef_c = float(dados_ativos.get("c", 0.0))
                
                # Se os coeficientes continuarem padrão (1, 0, 0), tenta procurar pontos de calibração brutos
                elif hasattr(main_view, "graficos_vm") and main_view.graficos_vm.dados_espectro_atual:
                    calib_pontos = main_view.graficos_vm.dados_espectro_atual.get("calibration", [])
                    if len(calib_pontos) >= 2:
                        ch_elements = [p[0] for p in calib_pontos]
                        en_elements = [p[1] for p in calib_pontos]
                        m, b = np.polyfit(ch_elements, en_elements, 1)
                        coef_a, coef_b = m, b

                # 4. APLICAÇÃO DO FILTRO DE CORTE DE CANAIS
                counts_filtrados = vetor_counts.copy()
                if canal_corte > 0 and canal_corte < len(counts_filtrados):
                    counts_filtrados[:canal_corte] = 0

                # 5. MATEMÁTICA DO EIXO X (Conversão de canais para keV)
                eixo_canais_puros = np.arange(len(counts_filtrados))
                if coef_c != 0.0:
                    vetor_energia_kev = (coef_c * (eixo_canais_puros ** 2)) + (coef_a * eixo_canais_puros) + coef_b
                else:
                    vetor_energia_kev = (eixo_canais_puros * coef_a) + coef_b

                # 6. MONTA O DICIONÁRIO COMPATIVEL COM O MODELO GRÁFICO
                dados_grafico = {ch: val for ch, val in tinta_alvo.items() if ch != 'counts'}
                dados_grafico.update({
                    "counts": counts_filtrados,
                    "channels": counts_filtrados,
                    "canais": vetor_energia_kev,       # Injeta o eixo X convertido para keV
                    "calibrado": True,                 # Força True para ativar a label "Energia (keV)"
                    "nome": nome_selecionado,
                    "canal_corte": canal_corte,
                    "threshold": thresh_pct,
                    "a": coef_a,
                    "b": coef_b,
                    "c": coef_c
                })

                # Sincroniza o estado da ViewModel
                self.vm.dados_espectro_atual = dados_grafico
                self.vm.caminho_mca = f"{nome_selecionado}"
                
                self.atualizar_status_arquivo_carregado(f"[Banco] {nome_selecionado}")
                
                # Limpa e atualiza os textos de aviso na tela
                for w in self.container_linhas.winfo_children(): w.destroy()
                ctk.CTkLabel(
                    self.container_linhas, 
                    text=f"Base Carregada -> Corte: {canal_corte}ch | Threshold: {thresh_pct*100:.1f}%", 
                    font=("Arial", 11), 
                    text_color="#2da44e"
                ).pack(anchor="w", padx=15, pady=2)
                
                # 7. ENVIA PARA A MAINVIEW PLOTAR EM REAL-TIME
                if hasattr(main_view, "plotar_no_app"):
                    main_view.plotar_no_app(dados_grafico, titulo_grafico=f"Espectro Alvo do Banco: {nome_selecionado}")

    def ao_clicar_comparar(self):
        """Busca no banco e executa o algoritmo de cosseno com os filtros reais vindos da aba FiltrosView."""
        main_view = self.winfo_toplevel()
        
        for w in self.frame_ranking_centro.winfo_children(): w.destroy()
        for w in self.container_linhas.winfo_children(): w.destroy()
            
        if self.vm.dados_espectro_atual is None or (isinstance(self.vm.dados_espectro_atual, np.ndarray) and self.vm.dados_espectro_atual.size == 0):
            ctk.CTkLabel(self.frame_ranking_centro, text="⚠️ Selecione uma assinatura do banco ou abra um arquivo externo antes de tentar comparar!", text_color="orange", font=("Arial", 13, "bold")).pack(expand=True)
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

        # Localiza dinamicamente a aba FiltrosView para capturar os filtros reais ativos
        aba_filtros = None
        for atributo in dir(main_view):
            obj = getattr(main_view, atributo, None)
            if obj and obj.__class__.__name__ == "FiltrosView":
                aba_filtros = obj
                break

        # Captura os parâmetros reais da aba de filtros (ou usa o fallback seguro caso ela não exista)
        if aba_filtros is not None:
            canal_corte = getattr(aba_filtros, 'canal_corte_ruido', 20)
            thresh_pct = getattr(aba_filtros, 'threshold_percentual', 0.02)
        else:
            canal_corte = getattr(main_view, 'canal_corte_ruido', 20)
            thresh_pct = getattr(main_view, 'threshold_percentual', 0.02)
        
        ranking = None
        try:
            ranking = self.vm.realizar_comparacao(dados_reais_banco, canal_inicial=canal_corte, threshold_percentual=thresh_pct)
        except ValueError:
            espectro_temp = self.vm.dados_espectro_atual
            self.vm.dados_espectro_atual = True  
            try:
                ranking = self.vm.realizar_comparacao(dados_reais_banco, canal_inicial=canal_corte, threshold_percentual=thresh_pct)
            except Exception:
                ranking = None
            finally:
                self.vm.dados_espectro_atual = espectro_temp  

        if ranking:
            lbl_tit_rank = ctk.CTkLabel(self.frame_ranking_centro, text="🏆 Ranking de Similaridade Encontrado:", font=("Arial Black", 14))
            lbl_tit_rank.pack(anchor="w", padx=25, pady=(20, 15))
            
            for i, item in enumerate(ranking[:5], start=1):
                texto = f"{i}º Lugar: {item['nome']} ➔ {item['porcentagem']:.2f}% de compatibilidade"
                cor = "#2da44e" if i == 1 and item['porcentagem'] > 85 else "#ffffff"
                
                lbl = ctk.CTkLabel(self.frame_ranking_centro, text=texto, font=("Arial", 13, "bold" if i==1 else "normal"), text_color=cor)
                lbl.pack(anchor="w", padx=45, pady=6)
                
            ctk.CTkLabel(self.container_linhas, text=f"✅ Match executado com sucesso! Maior similaridade: {ranking[0]['nome']} ({ranking[0]['porcentagem']:.2f}%)", font=("Arial", 12), text_color="#2da44e").pack(anchor="w", padx=15, pady=5)
            
            try:
                dados_grafico = self.vm.obter_dados_espectro()
            except ValueError:
                dados_grafico = {
                    "counts": self.vm.dados_espectro_atual, 
                    "canais": np.arange(len(self.vm.dados_espectro_atual))
                }
                
            if dados_grafico and hasattr(main_view, "plotar_no_app"):
                # 🌟 SEÇÃO CORRIGIDA: Identificação inteligente do título do gráfico 🌟
                caminho = getattr(self.vm, "caminho_mca", "")
                
                if not caminho:
                    titulo_final = "Espectro Analisado: Amostra"
                elif "/" in caminho or "\\" in caminho or caminho.lower().endswith(('.mca', '.spe')):
                    # Se possui barras de diretório ou extensão de arquivo, é um arquivo local externo
                    nome_limpo_arquivo = os.path.basename(caminho)
                    titulo_final = f"Espectro Comparado de Arquivo: {nome_limpo_arquivo}"
                else:
                    # Caso contrário, é o nome cru de uma assinatura carregada direto do Banco
                    titulo_final = f"Espectro Comparado do Banco: {caminho}"
                
                # Executa o plot com o título dinâmico corrigido
                main_view.plotar_no_app(dados_grafico, titulo_grafico=titulo_final)
        else:
            ctk.CTkLabel(self.frame_ranking_centro, text="❌ Nenhuma correlação estatística pôde ser calculada para esta amostra.\nVerifique se o banco possui registros com o mesmo tamanho de canais.", text_color="crimson", font=("Arial", 12, "bold")).pack(expand=True)

    def atualizar_status_arquivo_carregado(self, nome_arquivo):
        """Método chamado externamente (ou internamente) para sinalizar a prontidão da amostra."""
        for w in self.frame_ranking_centro.winfo_children(): 
            w.destroy()
        
        ctk.CTkLabel(
            self.frame_ranking_centro, 
            text=f"📁 Amostra Pronta para Análise!\n\nOrigem: {nome_arquivo}\n\nO vetor de contagens está pronto na memória.\nClique em 'Executar Comparação' para processar contra o banco.", 
            font=("Arial", 13, "bold"), 
            text_color="#ffffff"
        ).pack(expand=True)
