# models/databaseModel.py
import sqlite3
import numpy as np

DB_NAME = "banco/banco_tintas.db"

class Tinta:
    """Classe de Modelo que representa uma Tinta no domínio do negócio."""
    def __init__(self, nome, channels, live_time=None, data_aquisicao=None, arquivo_origem=None, canal_corte=20, threshold_utilizado=0.02, id=None):
        self.id = id
        self.nome = nome
        self.channels = np.array(channels)
        self.live_time = live_time
        self.data_aquisicao = data_aquisicao
        # 🌟 NOVOS ATRIBUTOS DE CONTEXTO
        self.arquivo_origem = arquivo_origem
        self.canal_corte = canal_corte
        self.threshold_utilizado = threshold_utilizado

    def obter_espectro_normalizado(self):
        """Aplica a normalização L2 (Regra de negócio pura)."""
        if self.channels.size == 0:
            return None
        norma = np.linalg.norm(self.channels)
        if norma == 0:
            return np.zeros_like(self.channels)
        return self.channels / norma

def inicializar_banco():
    """Cria a tabela se não existir com as novas colunas de metadados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tintas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            espectro_normalizado TEXT NOT NULL,
            live_time REAL,
            data_aquisicao TEXT,
            arquivo_origem TEXT,
            canal_corte INTEGER,
            threshold_utilizado REAL
        )
    """)
    conn.commit()
    conn.close()

def salvar_tinta_no_banco(tinta: Tinta):
    """Recebe um objeto Tinta do Model e persiste-o no SQLite com metadados."""
    espectro_norm = tinta.obter_espectro_normalizado()
    if espectro_norm is None:
        return False, "O espectro está vazio."
        
    if np.linalg.norm(tinta.channels) == 0:
        return False, "Espectro com contagens zeradas."

    # Converte o array para string
    espectro_string = ",".join(map(str, espectro_norm))
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # 🌟 UPDATE: Query alterada para incluir as novas colunas
        cursor.execute("""
            INSERT INTO tintas (nome, espectro_normalizado, live_time, data_aquisicao, arquivo_origem, canal_corte, threshold_utilizado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            tinta.nome, 
            espectro_string, 
            tinta.live_time, 
            tinta.data_aquisicao,
            tinta.arquivo_origem,
            tinta.canal_corte,
            tinta.threshold_utilizado
        ))
        conn.commit()
        conn.close()
        return True, "Tinta salva com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"Já existe uma tinta cadastrada com o nome '{tinta.nome}'."
    except Exception as e:
        return False, f"Erro ao salvar: {e}"

def buscar_todas_tintas_do_banco():
    """Conecta ao banco de dados e retorna todas as tintas cadastradas com filtros."""
    tintas = []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 🌟 MODIFICADO: Adicionamos as novas colunas no SELECT
        cursor.execute("SELECT id, nome, espectro_normalizado, arquivo_origem, canal_corte, threshold_utilizado FROM tintas")
        rows = cursor.fetchall()
        
        for row in rows:
            # 🌟 MODIFICADO: Mapeia cada coluna para o dicionário correspondente
            tintas.append({
                "id": row[0],
                "nome": row[1],
                "counts": row[2],
                "arquivo_origem": row[3],
                "canal_corte": row[4],
                "threshold_utilizado": row[5]
            })
            
        conn.close()
    except Exception as e:
        print(f"Erro ao ler banco de dados em databaseModel: {e}")
        
    return tintas

def deletar_tinta_do_banco(nome_tinta):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tintas WHERE nome = ?", (nome_tinta,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao deletar no banco: {e}")
        return False
