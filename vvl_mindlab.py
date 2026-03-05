import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import datetime
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Supernova Fatigue Lab", page_icon="🚀")

# CSS per pulizia interfaccia
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# SPLASH SCREEN SUPERNOVA
if 'splash_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='text-align:center; color:#FF9800;'>SUPERNOVA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Powered by Supernova Sport Science</p>", unsafe_allow_html=True)
    time.sleep(5) 
    placeholder.empty()
    st.session_state['splash_done'] = True # Segna lo splash come fatto

# SISTEMA DI LOGIN
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align:center;'>Accesso Riservato</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Inserisci la Password", type="password")
    if st.button("ENTRA NEL LAB"):
        if pwd == "supernova26":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password errata.")
    st.stop()

COLUMNS = ["Data", "Torneo", "Score", "Accettazione", "Routine", "Decisione", "Focus", "Energia", "Tensione", "Note"]

# ==============================================================================
# 2. SPLASH SCREEN & LOGIN
# ==============================================================================
if "mind_splash" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; font-size:4rem; color:{COLORS['Teal']};'>V.V.L. MIND LAB</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-weight:bold;'>Mental Performance Training - Road to 2040</p>", unsafe_allow_html=True)
    time.sleep(2)
    placeholder.empty()
    st.session_state["mind_splash"] = True

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown(f"<h3 style='text-align:center; color:{COLORS['Teal']}'>Area Riservata Performance</h3>", unsafe_allow_html=True)
    pwd = st.text_input("Inserisci Password Olimpica", type="password")
    if st.button("ACCEDI"):
        if pwd == "olimpiadi2040":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Credenziali respinte.")
    st.stop()

# ==============================================================================
# 3. DATA ENGINE (Google Sheets)
# ==============================================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.date
        return df
    except Exception as e:
        return pd.DataFrame(columns=COLUMNS)

def save_data(new_data):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existing = load_data()
    df_new = pd.DataFrame([new_data])
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    conn.update(data=df_final)
    st.cache_data.clear()

# ==============================================================================
# 4. GENERATORE PDF PROFESSIONALE
# ==============================================================================
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(58, 180, 184) # Teal VVL
        self.cell(0, 8, 'V.V.L. MIND LAB - PERFORMANCE REPORT', 0, 1, 'C')
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(8)

def create_pdf_report(df_filtered, period_name):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Periodo Analizzato: {period_name} | Data Generazione: {datetime.date.today()}", ln=True)
    pdf.ln(5)

    if not df_filtered.empty:
        # Analisi Medie
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(58, 180, 184)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, " PROFILO MENTALE MEDIO (Scala 1-5) ", 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        skills = ['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia', 'Tensione']
        for skill in skills:
            media = df_filtered[skill].mean()
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"> {skill}: {media:.1f} / 5.0", ln=True)
        
        pdf.ln(5)
        # Storico Tornei
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(58, 180, 184)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, " STORICO COMPETIZIONI ", 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)
        
        for _, row in df_filtered.iterrows():
            d_str = row['Data'].strftime('%d/%m/%Y') if pd.notnull(row['Data']) else "N/A"
            note_str = str(row['Note'])[:80] + "..." if pd.notnull(row['Note']) and len(str(row['Note'])) > 80 else str(row['Note'])
            # Pulizia caratteri speciali per FPDF
            note_clean = note_str.encode('latin-1', 'ignore').decode('latin-1')
            
            pdf.cell(0, 6, f"{d_str} | {row['Torneo']} | Score: {row['Score']}", ln=True)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 5, f"   Note: {note_clean}", ln=True)
            pdf.set_font('Arial', '', 9)
            pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# 5. INTERFACCIA PRINCIPALE
# ==============================================================================
st.markdown("<div class='vision-box'><strong>🎯 MISSIONE 2040:</strong> Diventare il giocatore più resiliente del Tour.<br><em>Il processo batte il risultato.</em></div>", unsafe_allow_html=True)

tab_in, tab_an = st.tabs(["📝 REGISTRO POST-GARA", "📊 ANALISI RADAR"])

with tab_in:
    st.subheader("Analisi della Prestazione")
    with st.form("mind_review", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            torneo = st.text_input("Torneo o Campo Pratica")
            score = st.number_input("Punteggio Finale (Lascia 0 se allenamento)", min_value=0, value=72)
        with col2:
            acc = st.slider("Accettazione dell'Errore", 1, 5, 3)
            rou = st.slider("Costanza della Routine", 1, 5, 3)
        
        col3, col4 = st.columns(2)
        with col3:
            dec = st.slider("Qualità Decisione/Immagine", 1, 5, 3)
            foc = st.slider("Focus nel Presente", 1, 5, 3)
        with col4:
            ene = st.slider("Gestione Energia", 1, 5, 3)
            ten = st.slider("Tensione (1=Rilassato, 5=Bloccato)", 1, 5, 2)

        note = st.text_area("Cosa porti a casa da questa sessione? (Key Takeaway)")
        
        if st.form_submit_button("SALVA VALUTAZIONE MENTALE"):
            if torneo:
                new_entry = {
                    "Data": datetime.date.today(), "Torneo": torneo, "Score": score,
                    "Accettazione": acc, "Routine": rou, "Decisione": dec,
                    "Focus": foc, "Energia": ene, "Tensione": ten, "Note": note
                }
                save_data(new_entry)
                st.success("✅ Dati acquisiti. Ogni analisi ti avvicina all'obiettivo.")
            else:
                st.error("Inserisci il nome del Torneo o Campo.")

with tab_an:
    df_all = load_data()
    
    if df_all.empty:
        st.info("Nessun dato registrato. Inserisci la prima valutazione per sbloccare i grafici.")
    else:
        periodo = st.selectbox("Seleziona Arco Temporale:", ["Ultimi 7 giorni", "Ultimo Mese", "Ultimi 6 Mesi", "Lifelong (Tutto)"])
        oggi = datetime.date.today()
        
        if periodo == "Ultimi 7 giorni": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=7))]
        elif periodo == "Ultimo Mese": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=30))]
        elif periodo == "Ultimi 6 Mesi": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=182))]
        else: df_f = df_all

        if not df_f.empty:
            # Creazione Radar Chart
            medie_f = df_f[['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']].mean()
            
            fig = go.Figure(go.Scatterpolar(
                r=medie_f.values,
                theta=medie_f.index,
                fill='toself',
                fillcolor='rgba(58, 180, 184, 0.5)', # Teal semitrasparente
                line_color='#3AB4B8',
                name='Skill Mentali'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                title=f"Profilo Radar delle Competenze ({periodo})"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Bottone PDF
            pdf_bytes = create_pdf_report(df_f, periodo)
            st.download_button(label="📄 SCARICA REPORT MENTALE (PDF)", data=pdf_bytes, file_name=f"VVL_MindLab_{periodo.replace(' ', '')}.pdf", mime="application/pdf")
            
            with st.expander("📖 Esplora Diario Storico"):
                st.dataframe(df_f.sort_values(by="Data", ascending=False), hide_index=True)
        else:
            st.warning("Nessun dato trovato per il periodo selezionato.")

