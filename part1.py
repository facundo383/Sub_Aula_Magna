import streamlit as st
import os
import re
import sqlite3
import pandas as pd
from PIL import Image, ImageOps

carpeta_actual = os.path.dirname(os.path.abspath(__file__))
CARPETA_IMAGENES = os.path.join(carpeta_actual, "CARPETA_IMAGENES")
DB_PATH = os.path.join(carpeta_actual, "votos.db")

# --- FUNCIÓN PARA CARGAR CSS EXTERNO (Silenciosa) ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar los estilos al inicio
local_css("style.css")

# --- CONFIGURACIÓN DE BASE DE DATOS SQLITE (Autocreadora) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            equipo TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- MENÚ DE NAVEGACIÓN EN LA BARRA LATERAL ---
menu = st.sidebar.selectbox("Menú de Navegación", ["Votación", "Administración"])

if menu == "Votación":
    st.markdown('<h1 class="titulo-principal">Elección para el cartel<br>del Aula Magna</h1>', unsafe_allow_html=True)

    nombre_usuario = st.text_input("Por favor, ingresa tu nombre:")
    documento_texto = st.text_input("Por favor, ingrese su DNI:", max_chars=8)

    if documento_texto and not documento_texto.isdigit():
        st.error("El DNI solo debe contener números.")

    opciones_equipos = {
        "Cartel numero 1": ("FOTO1.jpeg", 0),
        "Cartel numero 2": ("FOTO2.jpeg", 0),
        "Cartel numero 3": ("FOTO3.jpeg", 0),
        "Cartel numero 4": ("FOTO4.jpeg", 0),
        "Cartel numero 5": ("FOTO5.jpeg", 0),
        "Cartel numero 6": ("FOTO6.jpeg", 0),
        "Cartel numero 7": ("FOTO7.jpeg", 0),
        "Cartel numero 8": ("FOTO8.jpeg", 0),
        "Cartel numero 9": ("FOTO9.jpeg", 0),
        "Cartel numero 10": ("FOTO10.jpeg", 0),
        "Cartel numero 11": ("FOTO11.jpeg", 0),
        "Cartel numero 12": ("FOTO12.jpeg", 0),
        "Cartel numero 13": ("FOTO13.jpeg", 0),
        "Cartel numero 14": ("FOTO14.jpeg", 0)
    }

    equipo_elegido = st.selectbox("¿Cuál te gusta más?", list(opciones_equipos.keys()))
    archivo_imagen = opciones_equipos[equipo_elegido][0]
    ruta_imagen_completa = os.path.join(CARPETA_IMAGENES, archivo_imagen)

    if os.path.exists(ruta_imagen_completa):
        imagen_pil = Image.open(ruta_imagen_completa)
        imagen_corregida = ImageOps.exif_transpose(imagen_pil)  
        st.image(
            imagen_corregida, caption=f"Emblema de {equipo_elegido}", width=300
        )
    else:
        st.warning(f"No se encontró la imagen '{archivo_imagen}' en la carpeta '{CARPETA_IMAGENES}'.")

    if st.button("Guardar Todo"):
        if nombre_usuario and documento_texto:
            patron_letras = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$"
            if not re.match(patron_letras, nombre_usuario):
                st.error("Error: El nombre solo puede contener letras.")
                st.stop()
                
            if not documento_texto.isdigit():
                st.error("Error: El DNI solo debe contener números.")
                st.stop()

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM votos WHERE LOWER(nombre) = ?", (nombre_usuario.strip().lower(),))
                if cursor.fetchone():
                    st.error(f"El nombre '{nombre_usuario}' ya se encuentra registrado.")
                    conn.close()
                    st.stop()

                cursor.execute("SELECT id FROM votos WHERE dni = ?", (documento_texto.strip(),))
                if cursor.fetchone():
                    st.error(f"El DNI '{documento_texto}' ya ha emitido un voto.")
                    conn.close()
                    st.stop()

                cursor.execute(
                    "INSERT INTO votos (nombre, dni, equipo) VALUES (?, ?, ?)",
                    (nombre_usuario.strip(), documento_texto.strip(), equipo_elegido)
                )
                conn.commit()
                conn.close()

                st.success(f"¡Excelente! Su voto por '{equipo_elegido}' fue guardado correctamente en la base de datos.")

            except sqlite3.IntegrityError:
                st.error("Error: Ya existe un registro con esos datos en la base de datos.")
            except Exception as e:
                st.error(f"No se pudo guardar en la base de datos: {e}")
                
        else:
            st.warning("Por favor, completa todos los campos (nombre y DNI).")

elif menu == "Administración":
    st.markdown('<h1 class="titulo-principal">Panel de Administración</h1>', unsafe_allow_html=True)
    
    PASSWORD_ADMIN = "admin123"
    password_ingresada = st.text_input("Ingrese la contraseña de administrador:", type="password")

    if password_ingresada == PASSWORD_ADMIN:
        st.success("Acceso concedido.")
        
        conn = sqlite3.connect(DB_PATH)
        df_votos = pd.read_sql_query("SELECT id, nombre AS Nombre, dni AS DNI, equipo AS Equipo, fecha AS Fecha FROM votos", conn)
        conn.close()
        
        st.subheader("Registros de Votos Guardados")
        if not df_votos.empty:
            st.dataframe(df_votos, use_container_width=True)
            
            if os.path.exists(DB_PATH):
                with open(DB_PATH, "rb") as f:
                    db_bytes = f.read()
                
                st.download_button(
                    label="📥 Descargar Base de Datos (.db)",
                    data=db_bytes,
                    file_name="votos.db",
                    mime="application/octet-stream"
                )
        else:
            st.info("Aún no hay votos registrados en la base de datos.")
            
    elif password_ingresada != "":
        st.error("Contraseña incorrecta. Inténtelo de nuevo.")