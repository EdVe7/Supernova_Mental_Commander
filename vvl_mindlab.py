import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import datetime
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAZIONE E DESIGN (Stile PGA Tour)
# ==========================================
st.set_page_config(page_title="Supernova Mind Lab", page_icon="🧠", layout="wide")

# CSS per pulizia totale e design premium
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 2rem;}
    
    /* Stile per le metriche (KPI) */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 5% 10% 5% 10%;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Stile Mission Box */
    .vision-box {
        background: linear-gradient(135deg, #1f2937 0%, #3AB4B8 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

COLUMNS = ["Data", "Torneo", "Score", "Accettazione", "Routine", "Decisione", "Focus", "Energia", "Tensione", "Note"]

# ==========================================
# 2. SPLASH SCREEN SUPERNOVA
# ==========================================
if 'splash_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", use_container_width=False, width=300)
        except:
            st.markdown("<h1 style='text-align:center; color:#3AB4B8; font-size:4rem;'>SUPERNOVA MIND LAB</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:1.2rem;'>Advanced Mental Performance Tracking</p>", unsafe_allow_html=True)
    time.sleep(3) 
    placeholder.empty()
    st.session_state['splash_done'] = True

# ==========================================
# 3. SISTEMA DI LOGIN
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align:center; color:#1f2937;'>Accesso Area Tour</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci Password Master", type="password")
        if st.button("ENTRA NEL LAB", use_container_width=True):
            if pwd == "supernova26":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Credenziali respinte. Riprova.")
    st.stop()

# ==========================================
# 4. DATA ENGINE (Google Sheets)
# ==========================================
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

# ==========================================
# 5. GENERATORE PDF PREMIUM
# ==========================================
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(58, 180, 184) # Teal Supernova
        self.cell(0, 10, 'SUPERNOVA MIND LAB - PERFORMANCE REPORT', 0, 1, 'C')
        self.set_draw_color(200, 200, 200)
        self.line(10, 22, 200, 22)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Powered by Supernova Sport Science', 0, 0, 'L')
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'R')

def create_pdf_report(df_filtered, period_name):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Periodo di Riferimento: {period_name} | Generato il: {datetime.date.today()}", ln=True)
    pdf.ln(5)

    if not df_filtered.empty:
        # Calcolo KPI Globali
        skills = ['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']
        media_globale = df_filtered[skills].mean().mean()
        media_score = df_filtered[df_filtered['Score'] > 0]['Score'].mean()

        # Box Riassuntivo
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f" Indice Mentale Globale: {media_globale:.2f} / 5.0  |  Media Score: {media_score:.1f}", 0, 1, 'C', fill=True)
        pdf.ln(5)

        # Analisi Dettagliata Medie
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(58, 180, 184)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, " PROFILO MENTALE DETTAGLIATO ", 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        for skill in skills + ['Tensione']:
            media = df_filtered[skill].mean()
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"> {skill}: {media:.1f} / 5.0", ln=True)
        
        pdf.ln(8)
        
        # Storico Tornei
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(58, 180, 184)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, " LOG COMPETIZIONI ", 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)
        
        for _, row in df_filtered.iterrows():
            d_str = row['Data'].strftime('%d/%m/%Y') if pd.notnull(row['Data']) else "N/A"
            note_str = str(row['Note'])[:90] + "..." if pd.notnull(row['Note']) and len(str(row['Note'])) > 90 else str(row['Note'])
            note_clean = note_str.encode('latin-1', 'ignore').decode('latin-1')
            
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(0, 6, f"{d_str} - {row['Torneo']} (Score: {row['Score']})", ln=True)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 5, f"   Takeaway: {note_clean}", ln=True)
            pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 6. INTERFACCIA PRINCIPALE
# ==========================================
st.markdown("<div class='vision-box'><h3>🎯 ROAD TO 2040</h3><p>Diventare il giocatore più resiliente del Tour. Il processo batte il risultato.</p></div>", unsafe_allow_html=True)

tab_in, tab_an = st.tabs(["📝 REGISTRO POST-GARA", "📊 DASHBOARD PERFORMANCE"])

# --- TAB 1: INPUT DATI ---
with tab_in:
    st.subheader("Inserimento Dati Sessione")
    with st.form("mind_review", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            torneo = st.text_input("Torneo o Campo Pratica")
        with col2:
            score = st.number_input("Punteggio Finale (0 se allenamento)", min_value=0, value=72)
        with col3:
            st.write("") # Spaziatura
            st.caption("Valuta ogni parametro con sincerità radicale.")
            
        st.divider()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            acc = st.slider("Accettazione dell'Errore", 1, 5, 3)
            rou = st.slider("Costanza della Routine", 1, 5, 3)
        with c2:
            dec = st.slider("Qualità Decisione/Immagine", 1, 5, 3)
            foc = st.slider("Focus nel Presente", 1, 5, 3)
        with c3:
            ene = st.slider("Gestione Energia", 1, 5, 3)
            ten = st.slider("Tensione (1=Rilassato, 5=Bloccato)", 1, 5, 2)

        note = st.text_area("Key Takeaway (Cosa ha funzionato? Cosa va migliorato?)")
        
        submit = st.form_submit_button("REGISTRA SCORE MENTALE 🚀", use_container_width=True)
        if submit:
            if torneo:
                new_entry = {
                    "Data": datetime.date.today(), "Torneo": torneo, "Score": score,
                    "Accettazione": acc, "Routine": rou, "Decisione": dec,
                    "Focus": foc, "Energia": ene, "Tensione": ten, "Note": note
                }
                save_data(new_entry)
                st.success("✅ Dati acquisiti con successo al database centrale.")
            else:
                st.error("Inserisci il nome del Torneo o Campo per procedere.")

# --- TAB 2: DASHBOARD ANALITICA ---
with tab_an:
    df_all = load_data()
    
    if df_all.empty:
        st.info("📊 Nessun dato registrato. Inserisci la prima valutazione per sbloccare l'Analytics Center.")
    else:
        # Selettore periodo e filtri
        col_filt1, col_filt2 = st.columns([1, 3])
        with col_filt1:
            periodo = st.selectbox("Arco Temporale:", ["Ultimi 7 giorni", "Ultimo Mese", "Ultimi 6 Mesi", "Lifelong (Tutto)"])
        
        oggi = datetime.date.today()
        if periodo == "Ultimi 7 giorni": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=7))]
        elif periodo == "Ultimo Mese": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=30))]
        elif periodo == "Ultimi 6 Mesi": df_f = df_all[df_all['Data'] >= (oggi - datetime.timedelta(days=182))]
        else: df_f = df_all

        if not df_f.empty:
            # --- KPI METRICS ---
            st.markdown("### KPI Sintetici")
            kpi1, kpi2, kpi3 = st.columns(3)
            
            # Calcolo Indice Mentale (Media delle 5 skill positive)
            mental_index = df_f[['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']].mean().mean()
            # Calcolo Score Medio (escludendo gli allenamenti a score 0)
            df_scores = df_f[df_f['Score'] > 0]
            avg_score = df_scores['Score'].mean() if not df_scores.empty else 0
            
            kpi1.metric("Rounds Registrati", len(df_f))
            kpi2.metric("Indice Mentale Globale", f"{mental_index:.2f} / 5")
            kpi3.metric("Scoring Average", f"{avg_score:.1f}" if avg_score > 0 else "N/A")
            
            st.divider()
            
            # --- GRAFICI ---
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                # RADAR CHART
                medie_f = df_f[['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']].mean()
                fig_radar = go.Figure(go.Scatterpolar(
                    r=medie_f.values,
                    theta=medie_f.index,
                    fill='toself',
                    fillcolor='rgba(58, 180, 184, 0.4)',
                    line_color='#3AB4B8',
                    name='Skill Mentali'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=False,
                    title="Profilo Radar Competenze",
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            with g_col2:
                # LINE CHART (Trend Score)
                if not df_scores.empty:
                    fig_line = px.line(df_scores, x='Data', y='Score', markers=True, 
                                     title="Scoring Trend (Solo Tornei/Giri completi)",
                                     color_discrete_sequence=['#1f2937'])
                    fig_line.update_layout(yaxis_title="Punteggio Finale", xaxis_title="")
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Nessun punteggio di gara registrato nel periodo per tracciare il trend.")

            st.divider()
            
            # --- ESPORTAZIONE E TABELLA ---
            col_pdf, col_space = st.columns([1, 2])
            with col_pdf:
                pdf_bytes = create_pdf_report(df_f, periodo)
                st.download_button(label="📄 SCARICA REPORT (PDF)", data=pdf_bytes, file_name=f"Supernova_MindLab_{periodo.replace(' ', '')}.pdf", mime="application/pdf", use_container_width=True)
            
            with st.expander("📖 Consulta Raw Data (Diario Storico)"):
                st.dataframe(df_f.sort_values(by="Data", ascending=False), hide_index=True, use_container_width=True)
        else:
            st.warning("Nessun dato trovato per l'arco temporale selezionato.")
