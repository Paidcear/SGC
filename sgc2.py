import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="SGC - Sistema Global de Control", layout="wide")
st.title("🔧 Sistema Global de Control (SGC)")

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
    return [f for f in os.listdir() if f.endswith(".json")]

def mostrar_campos_para_llenar(plantilla):
    st.subheader(f"📝 Llenar Plantilla: {plantilla['nombre']}")
    respuestas = {}
    total = 0

    for campo in plantilla["campos"]:
        nombre = campo["nombre"]
        tipo = campo["tipo"]
        obligatorio = campo.get("obligatorio", False)

        if tipo == "Texto":
            respuestas[nombre] = st.text_input(nombre)
        elif tipo == "Número":
            respuestas[nombre] = st.number_input(nombre, step=1.0)
            if campo.get("incluir_total"):
                total += respuestas[nombre]
        elif tipo == "Fecha":
            respuestas[nombre] = st.date_input(nombre)
        elif tipo == "Hora":
            respuestas[nombre] = st.time_input(nombre)
        elif tipo == "Opción múltiple":
            opciones = campo.get("opciones", "").split(",")
            respuestas[nombre] = st.selectbox(nombre, opciones)

    if total:
        st.markdown(f"**Total calculado:** {total}")

    if st.button("Guardar respuestas"):
        st.success("Datos guardados correctamente (simulado).")

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
                st.session_state.form_data = []  # Aquí se guardan todos los registros

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

            #st.markdown("---")
            #col_guardar, col_limpiar = st.columns(2)

            #with col_guardar:
            if st.button("💾 Guardar Datos"):
                st.session_state.form_data.append(datos_ingresados.copy())
                st.success("✅ Datos registrados exitosamente.")

            #with col_limpiar:
            if st.button("🧹 Limpiar Campos"):
                for campo in campos:
                    key_name = f"campo_{campo['nombre']}"
                    if key_name in st.session_state:
                        del st.session_state[key_name]
                st.rerun()

            st.markdown("---")
            # Mostrar DataFrame si hay datos
            if st.session_state.form_data:
                st.markdown("### 📊 Datos Registrados")
                df = pd.DataFrame(st.session_state.form_data)

                # Usar el primer campo como índice (solo si existe)
                primer_campo = campos[0]["nombre"]
                if primer_campo in df.columns:
                    df.set_index(primer_campo, inplace=True)

                st.dataframe(df)

                # Sumar valores numéricos
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

# --- Consultar Plantilla ---
if menu == "Gestión de Plantillas" and sub_menu_plantillas == "Consultar Plantilla":
    st.subheader("🔍 Consultar Plantilla")
    archivos = cargar_plantillas()
    if archivos:
        seleccion = st.selectbox("Selecciona una plantilla para consultar", archivos)
        if seleccion:
            with open(seleccion, "r", encoding="utf-8") as f:
                plantilla = json.load(f)
            st.json(plantilla)
    else:
        st.info("No hay plantillas disponibles para consultar.")

# --- Editar Plantilla ---
if menu == "Gestión de Plantillas" and sub_menu_plantillas == "Editar Plantilla":
    st.subheader("✏️ Editar Plantilla")
    archivos = cargar_plantillas()
    if archivos:
        seleccion = st.selectbox("Selecciona una plantilla para editar", archivos)
        if seleccion:
            with open(seleccion, "r", encoding="utf-8") as f:
                plantilla = json.load(f)

            st.text_input("Nombre de la plantilla", value=plantilla["nombre"], key="editar_nombre")

            for i, campo in enumerate(plantilla["campos"]):
                st.markdown(f"**Campo {i+1}:**")
                campo["nombre"] = st.text_input(f"Nombre del campo {i+1}", campo["nombre"], key=f"edit_nombre_{i}")
                campo["tipo"] = st.selectbox(f"Tipo {i+1}", ["Texto", "Número", "Fecha", "Hora", "Opción múltiple"], index=["Texto", "Número", "Fecha", "Hora", "Opción múltiple"].index(campo["tipo"]), key=f"edit_tipo_{i}")
                campo["obligatorio"] = st.checkbox(f"¿Obligatorio?", value=campo["obligatorio"], key=f"edit_obligatorio_{i}")
                if campo["tipo"] == "Opción múltiple":
                    campo["opciones"] = st.text_input(f"Opciones {i+1}", value=campo.get("opciones", ""), key=f"edit_opciones_{i}")
                if campo["tipo"] == "Número":
                    campo["incluir_total"] = st.checkbox(f"¿Incluir en total?", value=campo.get("incluir_total", False), key=f"edit_incluir_total_{i}")
                st.markdown("---")

            if st.button("Guardar Cambios"):
                with open(seleccion, "w", encoding="utf-8") as f:
                    json.dump(plantilla, f, ensure_ascii=False, indent=4)
                st.success("Cambios guardados exitosamente.")
    else:
        st.info("No hay plantillas disponibles para editar.")