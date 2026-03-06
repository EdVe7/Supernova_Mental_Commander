import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import datetime
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF 

# ==========================================
# 1. CONFIGURAZIONE E DESIGN (Oro, Nero, Bianco)
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
        background-color: #ffffff;
        border: 1px solid #D4AF37; /* Bordo Oro */
        padding: 5% 10% 5% 10%;
        border-radius: 0px; /* Squadrato, più formale */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Stile Mission Box (Nero e Oro) */
    .vision-box {
        background: #000000;
        color: #D4AF37;
        padding: 20px;
        border: 2px solid #D4AF37;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Bottoni Oro */
    div.stButton > button:first-child {
        background-color: #D4AF37;
        color: #000000;
        border: None;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #000000;
        color: #D4AF37;
        border: 1px solid #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True) 

# NUOVE COLONNE PER IL FOGLIO EXCEL/GSHEETS
COLUMNS = ["Data", "Torneo", "Score", "Pre_Shot_Routine", "Post_Shot_Routine", "Gestione_Stress", "Focus", "Accettazione", "Strategia", "Pensieri_Mentali", "Takeaway_Tecnico"] 

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
            st.markdown("<h1 style='text-align:center; color:#D4AF37; font-size:4rem; letter-spacing: 4px;'>SUPERNOVA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:1.5rem; color:#000000; font-weight:bold;'>DATA OVER TALENT</p>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='text-align:center; color:#000000; text-transform:uppercase;'>Accesso Tour</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci Password Master", type="password")
        if st.button("ENTRA NEL LAB", use_container_width=True):
            if pwd == "supernova26":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Credenziali respinte. Riprova.")
    st.stop() 

# ==========================================
# 4. DATA ENGINE (Google Sheets) -> INVARIATO
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
# 5. GENERATORE PDF PREMIUM (Oro/Nero, Focus sulle Note)
# ==========================================
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(212, 175, 55) # Oro
        self.cell(0, 10, 'SUPERNOVA - TOUR PERFORMANCE REPORT', 0, 1, 'C')
        self.set_draw_color(0, 0, 0) # Linea Nera
        self.line(10, 22, 200, 22)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'DATA OVER TALENT', 0, 0, 'L')
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
        skills = ['Pre_Shot_Routine', 'Post_Shot_Routine', 'Gestione_Stress', 'Focus', 'Accettazione', 'Strategia']
        media_globale = df_filtered[skills].mean().mean()
        media_score = df_filtered[df_filtered['Score'] > 0]['Score'].mean() 

        # Box Riassuntivo
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(0, 0, 0) # Sfondo Nero
        pdf.set_text_color(212, 175, 55) # Testo Oro
        pdf.cell(0, 10, f" Indice Mentale Globale: {media_globale:.2f} / 5.0  |  Media Score: {media_score:.1f}", 0, 1, 'C', fill=True)
        pdf.ln(8) 

        # Analisi Dettagliata Medie (Parametri Tecnici/Mentali)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "MEDIE PARAMETRI (Scala 1-5)", 0, 1, 'L', fill=False)
        self_draw_color = (212, 175, 55)
        pdf.set_draw_color(*self_draw_color)
        pdf.line(10, pdf.get_y(), 100, pdf.get_y())
        pdf.ln(2)
        
        for skill in skills:
            media = df_filtered[skill].mean()
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"{skill.replace('_', ' ')}: {media:.1f}", ln=True)
        
        pdf.ln(10)
        
        # Storico Tornei e LOG DETTAGLIATO (Molto spazio alle note)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 8, " DIARIO POST-GARA E PENSIERI ", 0, 1, 'L', fill=True)
        pdf.ln(3)
        
        for _, row in df_filtered.iterrows():
            d_str = row['Data'].strftime('%d/%m/%Y') if pd.notnull(row['Data']) else "N/A"
            
            # Intestazione Gara
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, f"[{d_str}] - {row['Torneo']} (Score: {row['Score']})", ln=True)
            
            # Pulizia e inserimento Note Mentali
            mentali_str = str(row['Pensieri_Mentali']) if pd.notnull(row['Pensieri_Mentali']) else "Nessuna nota."
            mentali_clean = mentali_str.encode('latin-1', 'ignore').decode('latin-1')
            pdf.set_font('Arial', 'I', 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, f"Pensieri Mentali & Stress: {mentali_clean}")
            
            # Pulizia e inserimento Takeaway Tecnico
            tecnici_str = str(row['Takeaway_Tecnico']) if pd.notnull(row['Takeaway_Tecnico']) else "Nessuna nota."
            tecnici_clean = tecnici_str.encode('latin-1', 'ignore').decode('latin-1')
            pdf.set_font('Arial', '', 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, f"Takeaway Tecnico (Routine/Strategia): {tecnici_clean}")
            
            pdf.ln(4)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

    return pdf.output(dest='S').encode('latin-1') 

# ==========================================
# 6. INTERFACCIA PRINCIPALE
# ==========================================
st.markdown("<div class='vision-box'><h3>SUPERNOVA</h3><p>DATA OVER TALENT</p></div>", unsafe_allow_html=True) 

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
            st.write("") 
            st.caption("Valuta ogni parametro con sincerità radicale.")
            
        st.divider()
        st.markdown("**Dettagli Tecnici & Mentali (1 = Scarso, 5 = Eccellente)**")
        c1, c2, c3 = st.columns(3)
        with c1:
            pre_rou = st.slider("Pre-Shot Routine", 1, 5, 3)
            post_rou = st.slider("Post-Shot Routine", 1, 5, 3)
        with c2:
            stress = st.slider("Gestione Stress/Tensione", 1, 5, 3)
            foc = st.slider("Focus nel Presente", 1, 5, 3)
        with c3:
            acc = st.slider("Accettazione dell'Errore", 1, 5, 3)
            strat = st.slider("Esecuzione Strategia", 1, 5, 3) 

        st.divider()
        st.markdown("**Diario di Bordo (Spazio per l'analisi profonda)**")
        pensieri = st.text_area("Pensieri Post-Gara (Stato emotivo, dialoghi interni, gestione della pressione)", height=100)
        takeaway = st.text_area("Takeaway Tecnico (Cosa ha funzionato tecnicamente, efficacia della routine)", height=100)
        
        submit = st.form_submit_button("REGISTRA SCORE MENTALE", use_container_width=True)
        if submit:
            if torneo:
                new_entry = {
                    "Data": datetime.date.today(), "Torneo": torneo, "Score": score,
                    "Pre_Shot_Routine": pre_rou, "Post_Shot_Routine": post_rou, 
                    "Gestione_Stress": stress, "Focus": foc, "Accettazione": acc, 
                    "Strategia": strat, "Pensieri_Mentali": pensieri, "Takeaway_Tecnico": takeaway
                }
                save_data(new_entry)
                st.success("✅ Dati acquisiti con successo al database centrale.")
            else:
                st.error("Inserisci il nome del Torneo o Campo per procedere.") 

# --- TAB 2: DASHBOARD ANALITICA ---
with tab_an:
    df_all = load_data()
    
    if df_all.empty:
        st.info("📊 Nessun dato registrato. Inserisci la prima valutazione.")
    else:
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
            kpi1, kpi2, kpi3 = st.columns(3)
            
            skills = ['Pre_Shot_Routine', 'Post_Shot_Routine', 'Gestione_Stress', 'Focus', 'Accettazione', 'Strategia']
            mental_index = df_f[skills].mean().mean()
            
            df_scores = df_f[df_f['Score'] > 0]
            avg_score = df_scores['Score'].mean() if not df_scores.empty else 0
            
            kpi1.metric("Rounds Registrati", len(df_f))
            kpi2.metric("Indice Tour (Media Skill)", f"{mental_index:.2f} / 5")
            kpi3.metric("Scoring Average", f"{avg_score:.1f}" if avg_score > 0 else "N/A")
            
            st.divider()
            
            # --- GRAFICI (Design Oro/Nero) ---
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                # RADAR CHART (Skills Complete)
                medie_f = df_f[skills].mean()
                # Rinominiamo gli indici per pulizia nel grafico
                medie_f.index = [x.replace('_', ' ') for x in medie_f.index]
                
                fig_radar = go.Figure(go.Scatterpolar(
                    r=medie_f.values,
                    theta=medie_f.index,
                    fill='toself',
                    fillcolor='rgba(212, 175, 55, 0.4)', # Oro trasparente
                    line_color='#D4AF37', # Oro solido
                    name='Tour Skills'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=False,
                    title=dict(text="Radar Profilo Tecnico/Mentale", font=dict(color='#000000')),
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True) 

            with g_col2:
                # LINE CHART (Trend Score)
                if not df_scores.empty:
                    fig_line = px.line(df_scores, x='Data', y='Score', markers=True, 
                                     title="Scoring Trend Ufficiale",
                                     color_discrete_sequence=['#D4AF37']) # Linea Oro
                    fig_line.update_traces(marker=dict(color='#000000', size=8)) # Pallini Neri
                    fig_line.update_layout(yaxis_title="Punteggio Finale", xaxis_title="")
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Nessun punteggio di gara registrato.") 

            st.divider()
            
            # --- ESPORTAZIONE E TABELLA ---
            col_pdf, col_space = st.columns([1, 2])
            with col_pdf:
                pdf_bytes = create_pdf_report(df_f, periodo)
                st.download_button(label="📄 SCARICA REPORT TOUR (PDF)", data=pdf_bytes, file_name=f"Supernova_TourReport_{periodo.replace(' ', '')}.pdf", mime="application/pdf", use_container_width=True)
            
            with st.expander("📖 Consulta Raw Data (Diario Storico)"):
                st.dataframe(df_f.sort_values(by="Data", ascending=False), hide_index=True, use_container_width=True)
        else:
            st.warning("Nessun dato trovato per l'arco temporale selezionato.")
