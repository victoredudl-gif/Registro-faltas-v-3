

import streamlit as st
import pandas as pd
from datetime import datetime
import os
try:
    import openpyxl
    st.success("✅ openpyxl está instalado correctamente.")
except ImportError:
    st.error("❌ openpyxl NO está instalado en el entorno.")
try:
    import subprocess
    import sys

    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl



st.set_page_config(page_title="Registro de Faltas", layout="centered")
st.title("📋 Registro de Faltas Escolares")

archivo = "nomina.xlsx"

# Mostrar archivos disponibles (diagnóstico)
st.write("📁 Archivos disponibles en la app:", os.listdir())

# Verificar si el archivo existe
if not os.path.exists(archivo):
    st.error(f"❌ El archivo '{archivo}' no se encuentra en la carpeta.")
    st.stop()

# Intentar leer las hojas disponibles
try:
    xls = pd.ExcelFile(archivo, engine="openpyxl")
    st.write("📄 Hojas disponibles en el archivo:", xls.sheet_names)
except Exception as e:
    st.error(f"❌ No se pudo leer el archivo Excel: {e}")
    st.stop()

# Cargar hoja de estudiantes
try:
    df_estudiantes = pd.read_excel(xls, sheet_name="Estudiantes", engine="openpyxl")
except:
    st.warning("⚠️ No se encontró la hoja 'Estudiantes'. Se usará una tabla vacía.")
    df_estudiantes = pd.DataFrame(columns=["Cédula", "Nombre", "Apellido", "Año", "Mención"])

# Cargar hoja de faltas
try:
    df_faltas = pd.read_excel(xls, sheet_name="Faltas", engine="openpyxl")
except:
    st.warning("⚠️ No se encontró la hoja 'Faltas'. Se usará una tabla vacía.")
    df_faltas = pd.DataFrame(columns=["Cédula", "Nombre", "Apellido", "Año", "Mención", "Fecha", "Semana", "Falta", "Mes"])

# 🔍 Buscar estudiante por cédula, nombre o apellido
st.subheader("🔎 Buscar estudiante")
busqueda = st.text_input("Escribe cédula, nombre o apellido")

if busqueda:
    busqueda = busqueda.lower()
    filtrados = df_estudiantes[
        df_estudiantes.apply(lambda row: busqueda in str(row["Cédula"]).lower()
                             or busqueda in str(row.get("Nombre", "")).lower()
                             or busqueda in str(row.get("Apellido", "")).lower(), axis=1)
    ]
else:
    filtrados = df_estudiantes

# Mostrar resultados y permitir selección
if not filtrados.empty:
    opciones = filtrados.apply(lambda row: f"{row['Cédula']} - {row['Nombre']} {row['Apellido']}", axis=1).tolist()
    seleccion = st.selectbox("Selecciona el estudiante", opciones)

    # Extraer datos del estudiante seleccionado
    cedula_seleccionada = seleccion.split(" - ")[0]
    estudiante = df_estudiantes[df_estudiantes["Cédula"].astype(str) == cedula_seleccionada].iloc[0]

    nombre = estudiante["Nombre"]
    apellido = estudiante["Apellido"]
    año = estudiante["Año"]
    mencion = estudiante["Mención"]

    st.write(f"**Nombre:** {nombre}")
    st.write(f"**Apellido:** {apellido}")
    st.write(f"**Año:** {año}")
    st.write(f"**Mención:** {mencion}")

    # 📅 Datos de la falta
    fecha = st.date_input("Fecha de la falta", value=datetime.today())
    semana = st.selectbox("Semana del mes", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"])
    faltas = st.multiselect("Tipo de falta", [
        "Retardo injustificado",
        "Daños a las instalaciones",
        "Irrespeto a los símbolos patrios",
        "Retiro del plantel sin permiso",
        "Uso del teléfono"
    ])

    # ✅ Registrar faltas
    if st.button("Registrar faltas"):
        mes = fecha.strftime("%B")
        nuevas_faltas = pd.DataFrame([{
            "Cédula": cedula_seleccionada,
            "Nombre": nombre,
            "Apellido": apellido,
            "Año": año,
            "Mención": mencion,
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Semana": semana,
            "Falta": falta,
            "Mes": mes
        } for falta in faltas])

        df_faltas = pd.concat([df_faltas, nuevas_faltas], ignore_index=True)

        try:



            # 🧩 Reordenar columnas antes de guardar
            columnas_ordenadas = ["Cédula", "Nombre", "Apellido", "Año", "Mención", "Fecha", "Semana", "Falta", "Mes"]

            # Asegurar que todas las columnas estén presentes
            for col in columnas_ordenadas:
                if col not in df_faltas.columns:
                    df_faltas[col] = ""

            # Reordenar
            df_faltas = df_faltas[columnas_ordenadas]
            with pd.ExcelWriter(archivo, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df_estudiantes.to_excel(writer, sheet_name="Estudiantes", index=False)
                df_faltas.to_excel(writer, sheet_name="Faltas", index=False)
            st.success("✅ Faltas registradas correctamente.")
        except Exception as e:
            st.error(f"Error al guardar el archivo: {e}")

        # 🚨 Verificar reincidencias
        alertas = []
        for falta in faltas:
            conteo = df_faltas[
                (df_faltas["Cédula"] == cedula_seleccionada) &
                (df_faltas["Falta"] == falta) &
                (df_faltas["Mes"] == mes)
            ].shape[0]
            if conteo >= 3:
                alertas.append(f"⚠️ Alerta: {cedula_seleccionada} tiene {conteo} faltas de tipo '{falta}' en {mes}.")

        if alertas:
            st.error("\n".join(alertas))
else:
    st.info("No hay coincidencias con la búsqueda.")

#Reconstrucion forzada para instalar openpyxl






