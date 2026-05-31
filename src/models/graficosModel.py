# models/graficosModel.py
import re
import numpy as np
import matplotlib.pyplot as plt

def parse_mca(path):
    """Lê arquivos .mca (Pocket MCA / Amptek) e .spe (Ortec) de forma cirúrgica."""
    channels = []
    header_info = {}
    calibration_points = []
    
    try:
        with open(path, "r", encoding="latin-1") as f:
            lines = f.readlines()
        
        in_data_block = False
        in_calib_block = False
        
        for line in lines:
            line_strip = line.strip()
            if not line_strip: continue
                
            if line_strip in ["<<DATA>>", "$DATA:"]:
                in_data_block = True
                in_calib_block = False
                continue
            elif line_strip == "<<CALIBRATION>>":
                in_calib_block = True
                in_data_block = False
                continue
            elif line_strip.startswith("<<") or line_strip.startswith("$") or line_strip.startswith("ROI"):
                in_data_block = False
                in_calib_block = False
            
            if in_calib_block:
                parts = line_strip.split()
                if len(parts) >= 2:
                    try: calibration_points.append((float(parts[0]), float(parts[1])))
                    except ValueError: pass
                continue
            
            if in_data_block:
                parts = re.split(r"[,\s]+", line_strip)
                for p in parts:
                    if p != '':
                        try: channels.append(float(p))
                        except ValueError: pass
                continue
                
            if " - " in line_strip:
                key, val = line_strip.split(" - ", 1)
                header_info[key.strip()] = val.strip()
            elif ":" in line_strip and not line_strip.startswith("$"):
                parts = line_strip.split(":", 1)
                header_info[parts[0].strip()] = parts[1].strip()

        if len(channels) < 50:
            return _parse_mca_fallback(lines)
            
        return {
            "channels": np.array(channels, dtype=float),
            "header": header_info,
            "calibration": calibration_points
        }
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        return {"channels": np.array([], dtype=float), "header": {}, "calibration": []}

def _parse_mca_fallback(lines):
    blocks = []
    current = []
    for line in lines:
        parts = re.split(r"[,\s]+", line.strip())
        ok = True
        nums = []
        for p in parts:
            if p == '': continue
            try: nums.append(float(p))
            except: ok = False; break
        if ok and nums: current.extend(nums)
        else:
            if current and len(current) > len(blocks): blocks = current[:]
            current = []
    if current and len(current) > len(blocks): blocks = current[:]
    return {"channels": np.array(blocks, dtype=float), "header": {"info": "Parsed via fallback"}, "calibration": []}

def calcular_eixo_energia(num_canais, pontos_calibracao):
    if len(pontos_calibracao) >= 2:
        ch_elements = [p[0] for p in pontos_calibracao]
        en_elements = [p[1] for p in pontos_calibracao]
        m, b = np.polyfit(ch_elements, en_elements, 1)
        return m * np.arange(num_canais) + b
    return np.arange(num_canais)

def gerar_figura_espectro(parsed_data, titulo_grafico):
    """Gera e estiliza o gráfico do Matplotlib retornando o objeto Figure."""
    ch = parsed_data.get("channels")
    
    # 🌟 NOVO: Verifica se o eixo X já veio calculado e calibrado (visto na ComparacaoView/MainView)
    if "canais" in parsed_data and parsed_data.get("calibrado") == True:
        eixo_x = parsed_data.get("canais")
        label_x = "Energia (keV)"
    else:
        # Fallback para arquivos novos abertos diretamente do arquivo local
        calib = parsed_data.get("calibration", [])
        eixo_x = calcular_eixo_energia(ch.size, calib)
        label_x = "Energia (keV)" if len(calib) >= 2 else "Canal (Sem Calibração)"

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    # 1. Desenha a linha do gráfico
    ax.plot(eixo_x, ch, color='white', linewidth=1.5)
    
    # 2. Desenha a área preenchida abaixo do espectro
    ax.fill_between(eixo_x, ch, color='red', alpha=0.3)
    
    ax.set_title(titulo_grafico, fontdict={'fontsize': 12, 'fontweight': 'bold'})
    ax.set_xlabel(label_x)
    ax.set_ylabel("Contagens")
    ax.grid(True, linestyle='--', alpha=0.3)
    
    return fig

def aplicar_filtro_ruido(vetor_contagens, canal_inicial=20, threshold_percentual=0.02):
    """
    Aplica filtros para eliminar ruídos eletrônicos e de fundo.
    - canal_inicial: Corta os primeiros N canais (ruído eletrônico de baixa energia).
    - threshold_percentual: Zera canais com contagens menores que X% do pico máximo.
    """
    if vetor_contagens.size == 0:
        return np.zeros_like(vetor_contagens)
        
    # Faz uma cópia para não alterar o vetor original que será plotado no gráfico
    vetor_filtrado = np.copy(vetor_contagens)
    
    # 1. Corte de Canais Iniciais (Ruído Eletrônico de Fundo)
    if canal_inicial > 0 and canal_inicial < len(vetor_filtrado):
        vetor_filtrado[:canal_inicial] = 0
        
    # 2. Threshold de Intensidade Mínima (Ignora flutuações irrelevantes)
    max_contagem = np.max(vetor_filtrado)
    if max_contagem > 0:
        limite_corte = max_contagem * threshold_percentual
        # Zera tudo o que estiver abaixo do limite de corte estabelecido
        vetor_filtrado[vetor_filtrado < limite_corte] = 0
        
    return vetor_filtrado

def calcular_similaridade_cosseno(vetor_a, vetor_b, canal_inicial=20, threshold_percentual=0.02):
    """
    Calcula a similaridade de cosseno aplicando previamente o filtro de ruído 
    em ambos os vetores para aumentar a precisão do algoritmo.
    """
    # Aplica a limpeza matemática antes do cálculo do produto escalar
    a_limpo = aplicar_filtro_ruido(vetor_a, canal_inicial, threshold_percentual)
    b_limpo = aplicar_filtro_ruido(vetor_b, canal_inicial, threshold_percentual)

    tamanho_minimo = min(len(a_limpo), len(b_limpo))
    if tamanho_minimo == 0:
        return 0.0
        
    a = a_limpo[:tamanho_minimo]
    b = b_limpo[:tamanho_minimo]
    
    produto_escalar = np.dot(a, b)
    norma_a = np.linalg.norm(a)
    norma_b = np.linalg.norm(b)
    
    if norma_a == 0 or norma_b == 0:
        return 0.0
        
    return float(produto_escalar / (norma_a * norma_b))

def buscar_e_rankear_espectros(espectro_alvo, lista_banco, canal_inicial=20, threshold_percentual=0.02):
    """
    Compara o espectro alvo filtrado contra a lista do banco de dados.
    """
    ranking = []
    ch_alvo = espectro_alvo.get("channels", np.array([]))
    
    if ch_alvo.size == 0:
        return []

    for item in lista_banco:
        ch_banco = item.get("channels", np.array([]))
        
        # Passa os parâmetros de corte de ruído adiante
        similarity = calcular_similaridade_cosseno(
            ch_alvo, 
            ch_banco, 
            canal_inicial=canal_inicial, 
            threshold_percentual=threshold_percentual
        )
        
        ranking.append({
            "nome": item.get("nome", "Desconhecido"),
            "porcentagem": similarity * 100
        })
    
    ranking.sort(key=lambda x: x["porcentagem"], reverse=True)
    return ranking
