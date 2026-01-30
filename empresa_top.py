import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURACIÓN DE BASE DE DATOS ---
conn = sqlite3.connect('gestion_empresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS proyectos 
             (id INTEGER PRIMARY KEY, cliente TEXT, nombre TEXT, valor REAL, estado TEXT, fecha TEXT)''')
conn.commit()

# --- INTERFAZ ---
st.set_page_config(page_title="ERP Industrial Top", layout="wide")
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["Dashboard", "Nueva Cotización", "Gestión de Proyectos", "Facturación"])

# --- MÓDULO 1: DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Control de Mando - Proyectos")
    data = pd.read_sql("SELECT * FROM proyectos", conn)
    
    if not data.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(data, names='estado', values='valor', title="Distribución de Presupuesto por Estado")
            st.plotly_chart(fig_pie)
        with col2:
            fig_bar = px.bar(data, x='nombre', y='valor', color='estado', title="Valor por Proyecto")
            st.plotly_chart(fig_bar)
    else:
        st.info("No hay proyectos registrados aún.")

# --- MÓDULO 2: COTIZADOR ---
elif menu == "Nueva Cotización":
    st.title("📝 Desarrollador de Propuestas Técnicas")
    with st.form("form_cotizacion"):
        c_cliente = st.text_input("Cliente")
        c_proyecto = st.text_input("Nombre del Proyecto (ej. Ducto VR30)")
        
        st.subheader("Ingeniería de Materiales")
        col_m1, col_m2 = st.columns(2)
        laminas = col_m1.number_input("Cantidad de Láminas 3CR12 (4x8)", min_value=1)
        precio_lam = col_m2.number_input("Precio por lámina", value=4000000)
        
        st.subheader("Mano de Obra y AIU")
        cuadrilla = st.number_input("Nº de personas", value=3)
        dias = st.number_input("Días de ejecución", value=12)
        utilidad_p = st.slider("% Utilidad Sugerida", 5, 30, 15)
        
        btn_calc = st.form_submit_button("Calcular y Guardar")
        
        if btn_calc:
            costo_directo = (laminas * precio_lam) + (cuadrilla * dias * 150000) # Ejemplo pago dia
            total = costo_directo * (1 + (utilidad_p/100) + 0.15) # +15% Admin/Imprevistos
            
            c.execute("INSERT INTO proyectos (cliente, nombre, valor, estado, fecha) VALUES (?,?,?,?,?)",
                      (c_cliente, c_proyecto, total, "En Desarrollo", "2026-01-30"))
            conn.commit()
            st.success(f"Propuesta Generada por ${total:,.0f}. Proyecto guardado en base de datos.")

# --- MÓDULO 3: GESTIÓN ---
elif menu == "Gestión de Proyectos":
    st.title("⚙️ Control de Proyectos en Curso")
    data = pd.read_sql("SELECT * FROM proyectos", conn)
    
    for index, row in data.iterrows():
        with st.expander(f"{row['nombre']} - {row['cliente']}"):
            nuevo_estado = st.selectbox("Cambiar Estado", ["En Desarrollo", "Aprobado", "Finalizado", "Cobrado"], key=row['id'])
            if st.button("Actualizar", key=f"btn_{row['id']}"):
                c.execute("UPDATE proyectos SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                conn.commit()
                st.rerun()

# --- MÓDULO 4: FACTURACIÓN ---
elif menu == "Facturación":
    st.title("🧾 Facturación y Cobros")
    st.warning("⚠️ La Facturación Electrónica requiere integración con API de la DIAN (ej: Siigo o Alegra).")
    data = pd.read_sql("SELECT * FROM proyectos WHERE estado = 'Aprobado'", conn)
    st.write("Proyectos listos para facturar:")
    st.table(data)