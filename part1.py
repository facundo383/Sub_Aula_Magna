import pandas as pd
import streamlit as st
import io
import os
import re
from PIL import Image, ImageOps

carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(carpeta_actual, "python.xlsx")
CARPETA_IMAGENES = os.path.join(carpeta_actual, "CARPETA_IMAGENES")

st.title("Eleccion para el cartel del Aula Magna")

nombre_usuario = st.text_input("Por favor, ingresa tu nombre:")
documento_texto = st.text_input("Por favor, ingrese su DNI:", max_chars=8)

if documento_texto and not documento_texto.isdigit():
    st.error("El DNI solo debe contener números.")

# Cargar histórico si existe
if os.path.exists(ruta):
    try:
        df_historico = pd.read_excel(ruta, sheet_name='equipo')
        df_historico['Nombre'] = df_historico['Nombre'].astype(str).str.strip()
        df_historico['Equipo'] = df_historico['Equipo'].astype(str).str.strip()
    except Exception:
        df_historico = pd.DataFrame(columns=["Nombre", "Equipo", "DNI"])
else:
    df_historico = pd.DataFrame(columns=["Nombre", "Equipo", "DNI"])

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

equipo_elegido = st.selectbox("¿Cual te gusta mas?", list(opciones_equipos.keys()))
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
            
        nombres_existentes = df_historico['Nombre'].str.lower().values
        if nombre_usuario.lower() in nombres_existentes:
            st.error(f"El nombre '{nombre_usuario}' ya se encuentra registrado.")
            st.stop()
            
        df_nuevo = pd.DataFrame({
            "Nombre": [nombre_usuario],
            "Equipo": [equipo_elegido],   
            "DNI": [documento_texto],
        })
        df_final = pd.concat([df_historico, df_nuevo], ignore_index=True)

        # Guardar en Excel localmente para la sesión
        try:
            with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
                df_final.to_excel(writer, index=False, sheet_name='equipo')
            st.success(f"¡Excelente! '{nombre_usuario}' se guardó correctamente.")
        except Exception as e:
            st.error(f"No se pudo guardar en el archivo local: {e}")

        # Generar archivo en memoria para descarga directa del usuario
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='equipo')
        buffer_excel.seek(0)
        
        st.download_button(
            label="Descargar datos en Excel actualizado",
            data=buffer_excel,
            file_name="registro_usuarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Por favor, completa todos los campos (nombre y DNI).")
