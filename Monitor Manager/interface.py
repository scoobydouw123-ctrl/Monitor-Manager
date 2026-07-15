import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. CONFIGURACIÓN Y ESTILO VISUAL (Look Neón/Gradiente Ajustado)
st.set_page_config(page_title="FC 24 AI Tracker", page_icon="⚽", layout="centered")

def apply_custom_design():
    st.markdown(
        """
        <style>
        /* Fondo degradado basado en tu imagen */
        .stApp {
            background: linear-gradient(135deg, #cc00cc, #6600cc, #008080);
            color: #FFFFFF !important;
        }
        
        /* Forzar que TODOS los textos comunes y textos de listas sean blancos y legibles */
        .stApp p, .stApp span, .stApp label, .stApp li, .stApp div {
            color: #FFFFFF !important;
        }

        /* Arreglo específico para los textos grises dentro de los expanders (historial de partidos) */
        .stMarkdown div p, .stText {
            color: #FFFFFF !important;
            font-weight: 500 !important;
            font-size: 16px !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
        }
        
        /* Ocultar barra lateral por completo si está vacía */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        /* Contenedor personalizado para el menú horizontal inferior */
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            border: 1px solid #FF00FF;
        }
        
        /* Estilos para inputs: Fondo oscuro y letras blancas para que se lea perfecto lo que escribes */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div {
            background-color: rgba(0, 0, 0, 0.5) !important;
            color: #00FFFF !important; /* Texto celeste neón para que resalte al escribir */
            border: 1px solid #FF00FF !important;
            font-weight: bold !important;
        }
        
        /* Estilos para los BOTONES (como "Crear Torneo"): Fondo degradado neón con letras negras bien marcadas */
        .stButton>button {
            background: linear-gradient(90deg, #FF00FF, #00FFFF) !important;
            color: #000000 !important; /* Letras negras para máximo contraste */
            font-weight: 900 !important;
            border-radius: 10px !important;
            border: 2px solid #FFFFFF !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Títulos principales */
        h1, h2, h3 {
            color: #FFFFFF !important;
            text-shadow: 2px 2px 5px #000000 !important;
        }
        
        /* Cajas desplegables de torneos */
        .stExpander {
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid #FF00FF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_design()

# 2. LÓGICA DE DATOS E IA
load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

def cargar_torneos():
    if not os.path.exists("torneos.json"): return []
    with open("torneos.json", "r", encoding="utf-8") as f: return json.load(f)

def guardar_torneos(datos):
    with open("torneos.json", "w", encoding="utf-8") as f: json.dump(datos, f, indent=2, ensure_ascii=False)

def generar_reporte_ia(datos_torneo):
    instrucciones = (
        "Eres un analista TÁCTICO REAL de EA FC 24. Tu objetivo es analizar SOLO los datos proporcionados.\n"
        "REGLAS CRÍTICAS:\n"
        "1. NO INVENTES datos, equipos o ligas que no estén en el JSON.\n"
        "2. Céntrate exclusivamente en el rendimiento del club del usuario.\n"
        "3. Si el club es un equipo (ej. Newcastle), no hables de selecciones nacionales.\n"
        "4. Sugiere fichajes REALISTAS para el mercado de EA FC 24 basados en las posiciones débiles.\n"
        "5. Sé crítico pero profesional. Si el equipo pierde mucho, exige cambios tácticos.\n\n"
        f"DATOS DEL TORNEO:\n{json.dumps(datos_torneo, indent=2, ensure_ascii=False)}\n\n"
        "GENERA EL REPORTE CON ESTA ESTRUCTURA:\n"
        "A) RENDIMIENTO DEL CLUB: Análisis de los resultados registrados.\n"
        "B) NOTAS INDIVIDUALES: Quién está rindiendo según las calificaciones dadas.\n"
        "C) RECOMENDACIÓN TÁCTICA: Formación sugerida y estilo de juego.\n"
        "D) PLAN DE FICHAJES: 2 nombres reales de jugadores de FC 24 para mejorar el equipo."
    )
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "system", "content": "Eres un analista técnico de fútbol serio y preciso."},
                      {"role": "user", "content": instrucciones}],
            temperature=0.3
        )
        return res.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# 3. INTERFAZ PRINCIPAL
st.title("🎮 FC 24 AI ANALYST")

torneos = cargar_torneos()

# Inicializar estado de navegación si no existe
if "menu_sel" not in st.session_state:
    st.session_state.menu_sel = "Mis Torneos"

# Renderizado de la pestaña seleccionada
menu = st.session_state.menu_sel

if menu == "Mis Torneos":
    st.header("🏆 Torneos Registrados")
    if not torneos: 
        st.info("No hay nada aquí aún. ¡Crea un torneo abajo!")
    for t in torneos:
        with st.expander(f"{t.get('nombre_torneo', 'Torneo')} ({t.get('mi_club', 'Club')})"):
            st.write(f"**Tipo:** {t.get('tipo', 'Liga')} | **Alineación:** {t.get('alineacion_actual', '4-3-3')}")
            if "partidos" in t:
                for p in t['partidos']:
                    # SOLUCIÓN AL ERROR ROJO: Usamos .get() para evitar el KeyError si el partido es viejo
                    fase_partido = p.get('fase', p.get('jornada', 'N/A'))
                    st.text(f"{fase_partido} vs {p.get('rival', 'Desconocido')} | Resultado: {p.get('resultado_mi_club', 0)}-{p.get('resultado_rival', 0)}")

elif menu == "Añadir Partido":
    st.header("⚽ Registrar Resultado")
    if not torneos: st.warning("Crea un torneo primero.")
    else:
        t_nombres = [t['nombre_torneo'] for t in torneos]
        t_sel = st.selectbox("Torneo", t_nombres)
        torneo = next(t for t in torneos if t['nombre_torneo'] == t_sel)
        
        with st.form("partido"):
            fase = st.text_input("Fase o Jornada (ej: Grupo A, Octavos, Fecha 1)")
            rival = st.text_input("Rival")
            g_f = st.number_input(f"Goles de {torneo.get('mi_club', 'Mi Club')}", min_value=0, step=1)
            g_c = st.number_input(f"Goles de {rival}", min_value=0, step=1)
            
            st.write("---")
            goleadores = st.text_input("Goleadores (separados por coma)")
            calif = st.text_input("Calificaciones (Ej: Isco=9, Pope=7)")
            detalles = st.text_area("Notas tácticas")
            
            if st.form_submit_button("Guardar Partido"):
                notas = {}
                if calif:
                    for i in calif.split(","):
                        if "=" in i:
                            k, v = i.split("=")
                            notas[k.strip()] = v.strip()
                
                nuevo_p = {
                    "fase": fase, "rival": rival,
                    "resultado_mi_club": int(g_f), "resultado_rival": int(g_c),
                    "goleadores": [g.strip() for g in goleadores.split(",")] if goleadores else [],
                    "calificaciones": notas, "detalles": detalles
                }
                if "partidos" not in torneo: torneo["partidos"] = []
                torneo["partidos"].append(nuevo_p)
                guardar_torneos(torneos)
                st.success("¡Partido guardado con éxito!")

elif menu == "Reporte IA":
    st.header("🧠 Análisis Táctico")
    if not torneos: st.warning("Sin datos.")
    else:
        t_sel = st.selectbox("Elegir Torneo", [t['nombre_torneo'] for t in torneos])
        torneo = next(t for t in torneos if t['nombre_torneo'] == t_sel)
        
        if st.button("Generar Informe"):
            with st.spinner("Analizando datos reales..."):
                reporte = generar_reporte_ia(torneo)
                st.markdown(reporte)

elif menu == "Nuevo Torneo":
    st.header("🆕 Crear Torneo")
    nombre = st.text_input("Nombre (ej: Champions League 2024)")
    tipo = st.selectbox("Tipo de torneo", ["Liga (Jornadas)", "Copa (Fases/Grupos)", "Amistosos"])
    club = st.text_input("Tu equipo")
    ali = st.text_input("Formación base (ej: 4-2-3-1)")
    
    if st.button("Crear Torneo"):
        nuevo = {
            "nombre_torneo": nombre, "tipo": tipo, "mi_club": club,
            "alineacion_actual": ali, "partidos": []
        }
        torneos.append(nuevo)
        guardar_torneos(torneos)
        st.success("¡Torneo creado con éxito!")

# --- 4. BOTONES CENTRALES / INFERIORES DE NAVEGACIÓN ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.write("### 🧭 Navegación Principal")

# Usamos columnas para colocar los botones en fila horizontal (abajo en el centro)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 Torneos", use_container_width=True):
        st.session_state.menu_sel = "Mis Torneos"
        st.rerun()
with col2:
    if st.button("⚽ + Partido", use_container_width=True):
        st.session_state.menu_sel = "Añadir Partido"
        st.rerun()
with col3:
    if st.button("🧠 Info IA", use_container_width=True):
        st.session_state.menu_sel = "Reporte IA"
        st.rerun()
with col4:
    if st.button("🆕 + Torneo", use_container_width=True):
        st.session_state.menu_sel = "Nuevo Torneo"
        st.rerun()