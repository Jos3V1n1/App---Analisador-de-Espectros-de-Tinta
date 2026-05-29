# viewmodels/databaseVM.py
import os
from tkinter import filedialog
from models.graficosModel import parse_mca
from models.databaseModel import Tinta, inicializar_banco, salvar_tinta_no_banco, buscar_todas_tintas_do_banco

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
            filetypes=[("Arquivos de Espectro", "*.mca *.spe"), ("Todos os arquivos", "*.*")]
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

    def executar_salvamento(self, nome_tinta: str):
        """Valida as entradas, monta o Model 'Tinta' e solicita a gravação."""
        if self.dados_espectro_atual is None:
            return False, "Gere o gráfico do espectro antes de tentar salvar!"
            
        nome_limpo = nome_tinta.strip()
        if not nome_limpo:
            return False, "Por favor, digite um nome/identificação para esta tinta!"
            
        channels = self.dados_espectro_atual.get("channels")
        header = self.dados_espectro_atual.get("header", {})
        live_time = header.get("LIVE_TIME")
        data_aquisicao = header.get("START_TIME")
        
        # Instancia o objeto do Model
        nova_tinta = Tinta(
            nome=nome_limpo, 
            channels=channels, 
            live_time=live_time, 
            data_aquisicao=data_aquisicao
        )
        
        # Executa a ação através do Model
        sucesso, mensagem = salvar_tinta_no_banco(nova_tinta)
        return sucesso, mensagem
    
    def buscar_todas_tintas(self):
        """Busca todas as assinaturas guardadas no banco de dados."""
        return buscar_todas_tintas_do_banco()
