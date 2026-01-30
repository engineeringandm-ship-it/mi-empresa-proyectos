import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema de Gestión Universal", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stHeader { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("💼 Generador de Cotizaciones Profesional")

# --- 1. DATOS DEL CLIENTE ---
with st.expander("👤 Información del Cliente y Proyecto", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        cliente = st.text_input("Cliente / Empresa", placeholder="Ej: Alcaldía de Cúcuta")
    with col2:
        proyecto = st.text_input("Referencia del Proyecto", placeholder="Ej: Mantenimiento General")
    with col3:
        fecha = st.date_input("Fecha", datetime.now())

st.markdown("---")

# --- 2. TABLA DE SERVICIOS (EL CORAZÓN DEL SISTEMA) ---
st.subheader("📝 Detalle de Servicios o Productos")
st.info("Puedes agregar servicios, repuestos, horas de mano de obra o materiales. ¡Lo que necesites!")

# Creamos una estructura vacía para empezar
if 'filas' not in st.session_state:
    st.session_state.filas = pd.DataFrame([
        {"Descripción": "Servicio de diagnóstico técnico", "Unidad": "Global", "Cantidad": 1.0, "Valor Unitario": 0.0}
    ])

# Editor de datos potente
df_editor = st.data_editor(
    st.session_state.filas,
    num_rows="dynamic", # Permite añadir y borrar filas con el botón (+)
    column_config={
        "Descripción": st.column_config.TextColumn("Descripción del Servicio", width="large", required=True),
        "Unidad": st.column_config.SelectboxColumn("Unidad", options=["Und", "Global", "Hora", "Día", "Mts", "Kg"], default="Und"),
        "Cantidad": st.column_config.NumberColumn("Cant.", min_value=0.1, format="%.1f"),
        "Valor Unitario": st.column_config.NumberColumn("V. Unitario ($)", min_value=0.0, format="$%d")
    },
    use_container_width=True,
    key="tabla_principal"
)

# --- 3. CÁLCULOS ---
df_editor["Subtotal"] = df_editor["Cantidad"] * df_editor["Valor Unitario"]
total_neto = df_editor["Subtotal"].sum()

col_res1, col_res2 = st.columns([2,1])
with col_res2:
    iva_pct = st.number_input("% IVA (Si aplica)", value=0)
    valor_iva = total_neto * (iva_pct / 100)
    total_final = total_neto + valor_iva
    
    st.markdown(f"### Subtotal: **${total_neto:,.0f}**")
    st.markdown(f"### IVA ({iva_pct}%): **${valor_iva:,.0f}**")
    st.markdown(f"## **TOTAL: ${total_final:,.0f}**")

# --- 4. GENERACIÓN DE PDF PROFESIONAL ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'COTIZACIÓN COMERCIAL', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Fecha: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'R')
        self.ln(10)

def generar_pdf(df, cliente, proyecto, total):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {proyecto}", 0, 1)
    pdf.ln(5)
    
    # Encabezados de tabla
    pdf.set_fill_color(30, 58, 138) # Azul oscuro
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, " Descripción", 1, 0, 'L', True)
    pdf.cell(20, 10, " Cant.", 1, 0, 'C', True)
    pdf.cell(35, 10, " V. Unit", 1, 0, 'C', True)
    pdf.cell(45, 10, " Subtotal", 1, 1, 'C', True)
    
    # Filas de la tabla
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 9)
    for index, row in df.iterrows():
        pdf.cell(90, 8, f" {row['Descripción']}", 1)
        pdf.cell(20, 8, f" {row['Cantidad']}", 1, 0, 'C')
        pdf.cell(35, 8, f" ${row['Valor Unitario']:,.0f}", 1, 0, 'R')
        pdf.cell(45, 8, f" ${row['Subtotal']:,.0f}", 1, 1, 'R')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(145, 10, "TOTAL FINAL:", 0, 0, 'R')
    pdf.cell(45, 10, f" ${total:,.0f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

if st.button("📥 Descargar Cotización en PDF"):
    if cliente and not df_editor.empty:
        pdf_bytes = generar_pdf(df_editor, cliente, proyecto, total_final)
        st.download_button(label="Click aquí para descargar", data=pdf_bytes, file_name=f"Cotizacion_{cliente}.pdf", mime="application/pdf")
    else:
        st.error("Por favor llena el nombre del cliente y agrega al menos un servicio.")
  
