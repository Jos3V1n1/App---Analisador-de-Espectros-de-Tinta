# viewmodels/graficosVM.py
import os
from tkinter import filedialog
from models.graficosModel import parse_mca

class GraficosVM:
    def __init__(self):
        self.caminho_mca = None
        self.dados_espectro_atual = None
        self.botoes_da_view = []

    def registrar_botoes(self, lista_botoes):
        """Armazena os botões físicos que vieram da GraficosView."""
        self.botoes_da_view = lista_botoes

    def obter_botoes_registrados(self):
        """Disponibiliza os botões dinâmicos para a MainView colher."""
        return self.botoes_da_view

    def selecionar_mca(self) -> str:
        """Dispara a janela de busca por arquivo e faz o parse através do Model."""
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
        """Retorna os metadados e contagens estruturados para a View renderizar."""
        if not self.dados_espectro_atual:
            return None
        return self.dados_espectro_atual

    def realizar_comparacao(self, dados_do_banco, canal_inicial=20, threshold_percentual=0.02):
        """
        Pega o espectro atual e solicita o ranking aplicando os filtros de tolerância.
        """
        if not self.dados_espectro_atual:
            return []
            
        from models.graficosModel import buscar_e_rankear_espectros
        
        # Repassa os parâmetros de ruído para o motor do Model
        ranking = buscar_e_rankear_espectros(
            self.dados_espectro_atual, 
            dados_do_banco,
            canal_inicial=canal_inicial,
            threshold_percentual=threshold_percentual
        )
        return ranking
