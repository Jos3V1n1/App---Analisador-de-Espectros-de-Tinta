# viewmodels/databaseVM.py
import os
from tkinter import filedialog
from models.graficosModel import parse_mca
from models.databaseModel import Tinta, inicializar_banco, salvar_tinta_no_banco, buscar_todas_tintas_do_banco, deletar_tinta_do_banco

class DatabaseVM:
    def __init__(self):
        self.caminho_mca = None
        self.dados_espectro_atual = None  # Dados brutos em cache na VM
        self.botoes_da_view = []          # Cache dos botões enviados pela View
        
        # Garante a infraestrutura de dados ativa
        inicializar_banco()

    def registrar_botoes(self, lista_botoes):
        """Recebe os botões físicos gerados pela DatabaseView."""
        self.botoes_da_view = lista_botoes

    def obter_botoes_registrados(self):
        """Retorna os botões guardados para a MainView poder renderizá-los."""
        return self.botoes_da_view

    def selecionar_mca(self) -> str:
        """Abre o seletor de ficheiros e armazena o caminho selecionado."""
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de Espectro",
            filetypes=[("Arquivos de Espectro", "*.mca")]
        )
        if caminho:
            self.caminho_mca = caminho
            self.dados_espectro_atual = parse_mca(caminho)
            return os.path.basename(caminho)
        return ""

    def obter_dados_espectro(self):
        """Retorna os dados do arquivo atual para plotagem."""
        if not self.dados_espectro_atual:
            return None
        return self.dados_espectro_atual

# 🌟 ALTERE PARA (com "c"):
    def executar_salvamento(self, nome_tinta: str, canal_corte: int = 20, threshold_pct: float = 0.02):
        """Valida as entradas, monta o Model 'Tinta' e solicita a gravação."""
        if self.dados_espectro_atual is None:
            return False, "Abra um arquivo de espectro antes de tentar salvar!"
        # ... o resto do código do método continua exatamente igual ...
            
        nome_limpo = nome_tinta.strip()
        if not nome_limpo:
            return False, "Por favor, digite um nome/identificação para esta tinta!"
            
        channels = self.dados_espectro_atual.get("channels")
        header = self.dados_espectro_atual.get("header", {})
        live_time = header.get("LIVE_TIME")
        data_aquisicao = header.get("START_TIME")
        
        # 🌟 NOVO: Extrai apenas o nome do ficheiro (ex: "tintapreta.mca") do caminho completo
        nome_arquivo_mca = os.path.basename(self.caminho_mca) if self.caminho_mca else "Desconhecido"
        
        # 🌟 MODIFICADO: Instancia o objeto do Model com todos os novos parâmetros
        nova_tinta = Tinta(
            nome=nome_limpo, 
            channels=channels, 
            live_time=live_time, 
            data_aquisicao=data_aquisicao,
            arquivo_origem=nome_arquivo_mca,
            canal_corte=canal_corte,
            threshold_utilizado=threshold_pct
        )
        
        # Executa a ação através do Model
        sucesso, mensagem = salvar_tinta_no_banco(nova_tinta)
        return sucesso, mensagem
    
    def buscar_todas_tintas(self):
        """Busca todas as assinaturas guardadas no banco de dados."""
        return buscar_todas_tintas_do_banco()
    
    def excluir_tinta(self, nome_tinta: str) -> bool:
        """
        Recebe o nome da tinta da View, chama o Model para remover do SQLite
        e retorna True se o processo foi concluído com sucesso.
        """
        try:
            sucesso = deletar_tinta_do_banco(nome_tinta)
            return sucesso
        except Exception as e:
            print(f"Erro na ViewModel ao tentar deletar: {e}")
            return False

    def filtrar_tintas_por_nome(self, texto_busca: str):
        """Retorna apenas as tintas que contêm o termo buscado no nome."""
        # 1. Pega a lista completa direto do banco
        todas_tintas = self.buscar_todas_tintas()
        
        texto_limpo = texto_busca.strip().lower()
        if not texto_limpo:
            return todas_tintas
            
        # 2. Filtra em memória as que dão "match" com o nome digitado
        tintas_filtradas = [
            tinta for tinta in todas_tintas 
            if texto_limpo in tinta.get("nome", "").lower()
        ]
        
        return tintas_filtradas
