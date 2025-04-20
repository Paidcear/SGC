import streamlit as st
import json
import os
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="SGC - Sistema Global de Control", layout="wide")
st.title("🔧 Sistema Global de Control (SGC)")

# --- Funciones de persistencia de datos ---
def ruta_datos(plantilla_nombre):
    os.makedirs("registros", exist_ok=True)
    return os.path.join("registros", f"{plantilla_nombre}_datos.json")

def cargar_datos_plantilla(plantilla_nombre):
    ruta = ruta_datos(plantilla_nombre)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos_plantilla(plantilla_nombre, datos):
    ruta = ruta_datos(plantilla_nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# --- Menú lateral ---
with st.sidebar:
    st.header("📋 Menú Principal")
    menu = st.selectbox("Selecciona una opción", [
        "Panel Principal",
        "Gestión de Plantillas",
        "Importar/Exportar Datos"
    ])

    if menu == "Gestión de Plantillas":
        sub_menu_plantillas = st.selectbox("Plantillas", [
            "Crear Plantilla",
            "Consultar Plantilla",
            "Editar Plantilla"
        ])
    else:
        sub_menu_plantillas = None

    if menu == "Importar/Exportar Datos":
        sub_menu_datos = st.selectbox("Importar/Exportar", [
            "Importar desde JSON",
            "Exportar Plantillas/Reportes"
        ])
    else:
        sub_menu_datos = None

    if menu == "Panel Principal":
        st.button("✨ Ejecutar Acción Principal")

# Función para cargar plantillas disponibles
def cargar_plantillas():
    return [f for f in os.listdir() if f.endswith(".json") and not f.startswith("registros")]  # evitar cargar registros

# --- Panel Principal ---
if menu == "Panel Principal":
    st.subheader("🏠 Bienvenido al Sistema Global de Control")

    archivos = cargar_plantillas()
    if archivos:
        plantilla_sel = st.selectbox("📦 Selecciona una plantilla para llenar datos:", archivos, key="plantilla_panel")
        if plantilla_sel:
            with open(plantilla_sel, "r", encoding="utf-8") as f:
                plantilla = json.load(f)

            st.markdown("### ✏️ Ingreso de Datos")
            campos = plantilla.get("campos", [])

            if "form_data" not in st.session_state:
                st.session_state.form_data = {}

            if plantilla_sel not in st.session_state.form_data:
                st.session_state.form_data[plantilla_sel] = cargar_datos_plantilla(plantilla_sel)

            datos_ingresados = {}

            for i, campo in enumerate(campos):
                nombre = campo["nombre"]
                tipo = campo["tipo"]
                key_name = f"campo_{nombre}"

                if key_name not in st.session_state:
                    if tipo == "Texto":
                        st.session_state[key_name] = ""
                    elif tipo == "Número":
                        st.session_state[key_name] = float(campo.get("valor_default", 0.0))
                    elif tipo == "Fecha":
                        st.session_state[key_name] = date.today()
                    elif tipo == "Hora":
                        st.session_state[key_name] = datetime.now().time()
                    elif tipo == "Opción múltiple":
                        opciones = campo.get("opciones", "").split(",")
                        st.session_state[key_name] = opciones[0] if opciones else ""

                if tipo == "Texto":
                    datos_ingresados[nombre] = st.text_input(nombre, key=key_name)
                elif tipo == "Número":
                    datos_ingresados[nombre] = st.number_input(nombre, key=key_name)
                elif tipo == "Fecha":
                    datos_ingresados[nombre] = st.date_input(nombre, key=key_name)
                elif tipo == "Hora":
                    datos_ingresados[nombre] = st.time_input(nombre, key=key_name)
                elif tipo == "Opción múltiple":
                    opciones = campo.get("opciones", "").split(",")
                    datos_ingresados[nombre] = st.selectbox(nombre, opciones, key=key_name)

            if st.button("💾 Guardar Datos"):
                st.session_state.form_data[plantilla_sel].append(datos_ingresados.copy())
                guardar_datos_plantilla(plantilla_sel, st.session_state.form_data[plantilla_sel])
                st.success("✅ Datos registrados exitosamente.")

            if st.button("🧹 Limpiar Campos"):
                for campo in campos:
                    key_name = f"campo_{campo['nombre']}"
                    if key_name in st.session_state:
                        del st.session_state[key_name]
                st.rerun()

            st.markdown("---")
            if plantilla_sel in st.session_state.form_data and st.session_state.form_data[plantilla_sel]:
                st.markdown("### 📊 Datos Registrados")
                df = pd.DataFrame(st.session_state.form_data[plantilla_sel])

                primer_campo = campos[0]["nombre"]
                if primer_campo in df.columns:
                    df.set_index(primer_campo, inplace=True)

                st.dataframe(df)

                suma_numeros = df.select_dtypes(include=["number"]).sum().sum()
                st.markdown(f"### 🔢 Suma Total de Valores Numéricos: **{suma_numeros}**")
    else:
        st.info("Aún no hay plantillas guardadas.")

# --- Importar / Exportar Datos ---
eliminar = False
if menu == "Importar/Exportar Datos":
    if sub_menu_datos == "Importar desde JSON":
        archivo = st.file_uploader("Selecciona un archivo .json", type=["json"])
        if archivo:
            datos = json.load(archivo)
            st.write("📂 Datos importados:", datos)

    elif sub_menu_datos == "Exportar Plantillas/Reportes":
        archivos = cargar_plantillas()
        if archivos:
            seleccion = st.selectbox("Selecciona qué deseas exportar", archivos)
            with open(seleccion, "r", encoding="utf-8") as f:
                contenido = json.load(f)
            st.json(contenido)
        else:
            st.info("No hay archivos exportables disponibles.")

# --- Crear Plantilla ---
if menu == "Gestión de Plantillas" and sub_menu_plantillas == "Crear Plantilla":
    st.subheader("🧹 Crear Nueva Plantilla")

    nombre_plantilla = st.text_input("Nombre de la plantilla")
    num_campos = st.number_input("¿Cuántos campos deseas agregar?", min_value=1, max_value=50, step=1, value=1)

    if "campos" not in st.session_state or len(st.session_state.campos) != num_campos:
        st.session_state.campos = [
            {"nombre": "", "tipo": "Texto", "obligatorio": False, "opciones": "", "incluir_total": False}
            for _ in range(num_campos)
        ]

    st.markdown("---")

    for i, campo in enumerate(st.session_state.campos):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            campo["nombre"] = st.text_input(f"Nombre del campo {i+1}", campo.get("nombre", ""), key=f"nombre_{i}")
        with col2:
            campo["tipo"] = st.selectbox(
                f"Tipo de dato {i+1}",
                ["Texto", "Número", "Fecha", "Hora", "Opción múltiple"],
                index=["Texto", "Número", "Fecha", "Hora", "Opción múltiple"].index(campo.get("tipo", "Texto")),
                key=f"tipo_{i}"
            )
        with col3:
            campo["obligatorio"] = st.checkbox(f"¿Obligatorio?", campo.get("obligatorio", False), key=f"obligatorio_{i}")
        with col4:
            pass

        if campo["tipo"] == "Opción múltiple":
            campo["opciones"] = st.text_input(
                f"Opciones para el campo {i+1} (separadas por coma)",
                value=campo.get("opciones", ""),
                key=f"opciones_{i}"
            )

        if campo["tipo"] == "Número":
            campo["incluir_total"] = st.checkbox(
                f"¿Incluir en total?",
                campo.get("incluir_total", False),
                key=f"incluir_total_{i}"
            )

        st.markdown("---")

    if nombre_plantilla and st.session_state.campos:
        if st.button("Guardar Plantilla"):
            plantilla = {
                "nombre": nombre_plantilla,
                "campos": st.session_state.campos
            }
            with open(f"{nombre_plantilla}.json", "w", encoding="utf-8") as f:
                json.dump(plantilla, f, ensure_ascii=False, indent=4)
            st.success(f"Plantilla '{nombre_plantilla}' guardada correctamente.")
            st.session_state.campos = []
    else:
        st.info("Introduce un nombre para la plantilla y configura al menos un campo para poder guardar.")

        