# models/databaseModel.py
import sqlite3
import numpy as np

DB_NAME = "banco/banco_tintas.db"

class Tinta:
    """Classe de Modelo que representa uma Tinta no domínio do negócio."""
    def __init__(self, nome, channels, live_time=None, data_aquisicao=None, id=None):
        self.id = id
        self.nome = nome
        self.channels = np.array(channels)
        self.live_time = live_time
        self.data_aquisicao = data_aquisicao

    def obter_espectro_normalizado(self):
        """Aplica a normalização L2 (Regra de negócio pura)."""
        if self.channels.size == 0:
            return None
        norma = np.linalg.norm(self.channels)
        if norma == 0:
            return np.zeros_like(self.channels)
        return self.channels / norma

def inicializar_banco():
    """Cria a tabela se não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tintas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            espectro_normalizado TEXT NOT NULL,
            live_time REAL,
            data_aquisicao TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_tinta_no_banco(tinta: Tinta):
    """Recebe um objeto Tinta do Model e persiste-o no SQLite."""
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
        cursor.execute("""
            INSERT INTO tintas (nome, espectro_normalizado, live_time, data_aquisicao)
            VALUES (?, ?, ?, ?)
        """, (tinta.nome, espectro_string, tinta.live_time, tinta.data_aquisicao))
        conn.commit()
        conn.close()
        return True, "Tinta salva com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"Já existe uma tinta cadastrada com o nome '{tinta.nome}'."
    except Exception as e:
        return False, f"Erro ao salvar: {e}"

def buscar_todas_tintas_do_banco():
    """Conecta ao banco de dados e retorna todas as tintas cadastradas."""
    tintas = []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 🔍 CORREÇÃO: Aponta exatamente para a coluna 'espectro_normalizado'
        cursor.execute("SELECT nome, espectro_normalizado FROM tintas")
        rows = cursor.fetchall()
        
        for row in rows:
            tintas.append({
                "nome": row[0],
                "counts": row[1]  # Retorna a string de dados que a GraficosView já sabe converter
            })
            
        conn.close()
    except Exception as e:
        print(f"Erro ao ler banco de dados em databaseModel: {e}")
        
    return tintas

# Dentro do seu models/databaseModel.py

def deletar_tinta_do_banco(nome_tinta):
    try:
        conn = sqlite3.connect(DB_NAME) # Ajuste para o nome do seu arquivo
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tintas WHERE nome = ?", (nome_tinta,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao deletar no banco: {e}")
        return False
