# verificar_banco.py
import sqlite3
import numpy as np
import sys

# Força o terminal a aceitar caracteres universais se suportado, 
# ou substitui os que não conseguir exibir sem quebrar o programa.
sys.stdout.reconfigure(errors='replace')

DB_NAME = "banco/banco_tintas.db"

def consultar_tintas_cadastradas():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, live_time, data_aquisicao, espectro_normalizado FROM tintas")
        linhas = cursor.fetchall()
        
        if not linhas:
            print("\n O banco de dados esta vazio! Nenhuma tinta foi cadastrada ainda.")
            conn.close()
            return

        print(f"\n=== Tintas Encontradas no Banco de Dados ({len(linhas)}) ===")
        
        for linha in linhas:
            tinta_id = linha[0]
            nome = linha[1]
            live_time = linha[2]
            data_aquisicao = linha[3]
            espectro_str = linha[4]
            
            # Reconverte a string de texto de volta para um array do numpy
            espectro_array = np.fromstring(espectro_str, sep=",")
            
            # Trocado os caracteres especiais por marcadores simples (->) para evitar erros no Windows
            print(f"\n[ID {tinta_id}] Tinta: {nome}")
            print(f"  -> Data de Aquisicao: {data_aquisicao}")
            print(f"  -> Tempo Ativo (Live Time): {live_time}s")
            print(f"  -> Tamanho do Vetor (Canais): {espectro_array.size}")
            print(f"  -> Soma das Contagens Norm.: {espectro_array.sum():.4f}")
            print(f"  -> Amostra dos Primeiros Canais Norm.: {espectro_array[:5]}")
            print("-" * 50)
            
        conn.close()
        
    except sqlite3.OperationalError:
        print(f"\n Erro: O arquivo '{DB_NAME}' nao foi encontrado ou a tabela nao existe.")
    except Exception as e:
        print(f"\n Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    consultar_tintas_cadastradas()
