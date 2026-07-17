import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargamos la API Key desde el archivo .env
load_dotenv()
clave_api = os.getenv("GROQ_API_KEY")

# Inicializamos el cliente de Groq
client = OpenAI(
    api_key=clave_api,
    base_url="https://api.groq.com/openai/v1",
)

def cargar_torneos():
    """Lee el archivo JSON de torneos."""
    if not os.path.exists("torneos.json"):
        return []
    with open("torneos.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)

def guardar_torneos(datos):
    """Guarda los datos actualizados en el archivo JSON."""
    with open("torneos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

def generar_reporte_ia(datos_torneo):
    """Envía los datos avanzados a la IA para generar el resumen deportivo."""
    instrucciones = (
        "Actúa como un periodista deportivo experto y analista táctico de EA FC 24.\n"
        "Te voy a proporcionar los datos en formato JSON de un torneo, que incluyen partidos, "
        "goleadores, asistentes y calificaciones de jugadores.\n\n"
        "Quiero que generes un reporte con secciones claras usando títulos llamativos:\n"
        "1. RESUMEN DEL TORNEO: Cómo va la competición, la gran sorpresa y el gigante dormido.\n"
        "2. ANÁLISIS DEL CLUB Y RENDIMIENTO: Evaluación detallada del desempeño de mi equipo.\n"
        "3. GALARDONES DEL CLUB: Quién es el MVP indiscutible, el jugador que necesita banquillo y la revelación basándote en goles, asistencias y notas.\n"
        "4. EL ONCE IDEAL Y RECOMENDACIONES TÁCTICAS: Sugiere alineaciones según el rendimiento actual.\n"
        "5. PLANIFICACIÓN DE FICHAJES BOMBA: Qué jugador del mercado real de FC 24 debería fichar para solucionar los puntos débiles.\n\n"
        f"Datos del Torneo:\n{json.dumps(datos_torneo, indent=2, ensure_ascii=False)}"
    )

    print("\n[IA pensando...] Analizando datos de tu campaña...")
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "Eres un analista de fútbol con un estilo dinámico, divertido y experto."},
                {"role": "user", "content": instrucciones}
            ],
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Hubo un error al conectar con la IA: {e}"

def registrar_partido(torneos):
    """Permite ingresar un nuevo partido con goleadores, asistentes y notas."""
    print("\n--- REGISTRAR NUEVO PARTIDO ---")
    for i, t in enumerate(torneos):
        print(f"[{i + 1}] - {t['nombre_torneo']} ({t['mi_club']})")
    
    try:
        opcion = int(input("\nSelecciona el número del torneo: ")) - 1
        if opcion < 0 or opcion >= len(torneos):
            print("Selección inválida.")
            return
    except ValueError:
        print("Por favor, ingresa un número válido.")
        return
    
    torneo_seleccionado = torneos[opcion]
    print(f"\nRegistrando partido para {torneo_seleccionado['mi_club']}:")
    
    try:
        jornada = int(input("Número de Jornada/Fecha: "))
        rival = input("¿Contra quién juegas? (Rival): ")
        goles_favor = int(input(f"Goles anotados por {torneo_seleccionado['mi_club']}: "))
        goles_contra = int(input(f"Goles anotados por {rival}: "))
        
        # --- NUEVO: Captura de Goleadores ---
        goleadores = []
        if goles_favor > 0:
            print(f"\n¿Quién anotó los {goles_favor} goles de tu equipo? (Presiona Enter después de cada nombre)")
            for i in range(goles_favor):
                jugador = input(f" Goleador {i+1}: ")
                if jugador: goleadores.append(jugador)
        
        # --- NUEVO: Captura de Asistentes ---
        asistentes = []
        if goles_favor > 0:
            print("\n¿Quién dio las asistencias? (Deja en blanco si fue jugada individual)")
            for i in range(goles_favor):
                jugador = input(f" Asistente para gol {i+1}: ")
                if jugador: asistentes.append(jugador)

        # --- NUEVO: Calificaciones de Rendimiento ---
        calificaciones = {}
        print("\n¿Quieres calificar el rendimiento de algún jugador clave en este partido? (ej: Isco: 8.5)")
        print("Escribe 'fin' para terminar de calificar.")
        while True:
            nom_jugador = input("Nombre del jugador: ")
            if nom_jugador.lower() == 'fin' or not nom_jugador:
                break
            try:
                nota = float(input(f"Nota para {nom_jugador} (1 al 10): "))
                calificaciones[nom_jugador] = nota
            except ValueError:
                print("Nota inválida, intenta de nuevo.")

        detalles = input("\nEscribe detalles clave (ej. cómo estuvo el partido, lesionados): ")
    except ValueError:
        print("Error en el formato de los datos ingresados. No se guardó el partido.")
        return

    # Estructura del partido enriquecida
    nuevo_partido = {
        "jornada": jornada,
        "rival": rival,
        "resultado_mi_club": goles_favor,
        "resultado_rival": goles_contra,
        "goleadores": goleadores,
        "asistentes": asistentes,
        "calificaciones_partido": calificaciones,
        "detalles": detalles
    }
    
    torneo_seleccionado["partidos"].append(nuevo_partido)
    guardar_torneos(torneos)
    print("\n¡Partido y estadísticas registrados con éxito! ⚽🔥")

def crear_nuevo_torneo(torneos):
    """Permite al usuario crear un torneo desde cero."""
    print("\n--- CREAR NUEVO TORNEO ---")
    nombre = input("Nombre del Torneo: ")
    club = input("¿Qué club vas a dirigir?: ")
    alineacion = input("Alineación inicial (ej. 4-3-3): ")
    puntos_debiles = input("Puntos débiles iniciales: ")
    
    nuevo = {
        "id_torneo": len(torneos) + 1,
        "nombre_torneo": nombre,
        "mi_club": club,
        "alineacion_actual": alineacion,
        "puntos_debiles_observados": puntos_debiles,
        "partidos": []
    }
    
    torneos.append(nuevo)
    guardar_torneos(torneos)
    print(f"\n¡Torneo '{nombre}' creado con éxito! 🎉")

def main():
    while True:
        torneos = cargar_torneos()
        print("\n" + "="*45)
        print("   🏆 MÁNAGER ANALÍTICO FC 24 - AVANZADO 🏆   ")
        print("="*45)
        print("[1] Ver mis torneos activos")
        print("[2] Registrar nuevo partido (Con Stats)")
        print("[3] Generar reporte táctico de IA")
        print("[4] Crear un nuevo torneo desde cero")
        print("[5] Salir")
        print("="*45)
        
        opcion = input("Elige una opción (1-5): ")
        
        if opcion == "1":
            if not torneos:
                print("\nNo hay torneos registrados todavía.")
            for t in torneos:
                print(f"\n- {t['nombre_torneo']} ({t['mi_club']}) | Partidos: {len(t['partidos'])}")
        
        elif opcion == "2":
            if not torneos:
                print("\nPrimero debes crear un torneo (Opción 4).")
            else:
                registrar_partido(torneos)
                
        elif opcion == "3":
            if not torneos:
                print("\nNo tienes torneos para analizar.")
                continue
            for i, t in enumerate(torneos):
                print(f"[{i + 1}] - {t['nombre_torneo']}")
            try:
                sel = int(input("\nSelecciona el número: ")) - 1
                if 0 <= sel < len(torneos):
                    reporte = generar_reporte_ia(torneos[sel])
                    print("\n================ REPORTAJE DEPORTIVO ================")
                    print(reporte)
                    print("=====================================================")
                else:
                    print("Selección inválida.")
            except ValueError:
                print("Número inválido.")
                
        elif opcion == "4":
            crear_nuevo_torneo(torneos)
            
        elif opcion == "5":
            print("\n¡Gracias por usar Mánager Analítico FC! ¡A ganar la liga! 🎮⚽")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main()