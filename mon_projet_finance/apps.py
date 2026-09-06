import os
import streamlit as st
import stripe
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import time
import re
from datetime import datetime

# ============================================
# CONFIGURATION STRIPE
# ============================================

try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    ID_PRIX_MENSUEL = st.secrets["STRIPE_PRICE_ID_MONTHLY"]
    URL_APP = st.secrets["MON_URL_STREAMLIT"]
except KeyError as e:
    st.error(f"❌ Erreur de configuration : La clé `{e.args[0]}` est manquante dans `.streamlit/secrets.toml`")
    st.stop()

st.set_page_config(
    page_title="Simulateur d'Épargne Premium",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - SUPPRESSION TOTALE DES ESPACES
# ============================================

st.markdown("""
<style>
    /* SUPPRESSION TOTALE DES ESPACES */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Supprimer les marges des colonnes */
    .row-widget.stColumns {
        gap: 0px !important;
        margin: 0px !important;
    }
    
    .stColumn {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Supprimer les espaces des éléments Streamlit */
    .stMarkdown {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    .stDivider {
        margin: 6px 0px !important;
        padding: 0px !important;
    }
    
    .stSpacer {
        display: none !important;
    }
    
    .element-container {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    .stAlert {
        margin: 4px 0px !important;
        padding: 8px !important;
    }
    
    /* Supprimer les marges des vides */
    .stVerticalBlock {
        gap: 0px !important;
    }
    
    /* Styles personnalisés */
    .premium-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 14px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .free-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 3px 12px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    
    .paywall-premium {
        background: linear-gradient(145deg, #ffffff, #f8f9fe);
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.12);
        border: 1px solid rgba(102, 126, 234, 0.08);
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 100%;
        margin: 0px;
    }
    
    .pricing-card-premium {
        background: linear-gradient(145deg, #667eea, #764ba2);
        border-radius: 14px;
        padding: 14px 18px;
        color: white;
        margin: 8px 0 10px 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.35);
        position: relative;
    }
    
    .pricing-price-premium {
        font-size: 34px;
        font-weight: 800;
        margin: 2px 0;
    }
    
    .pricing-price-premium span {
        font-size: 16px;
        font-weight: 400;
        opacity: 0.8;
    }
    
    .pricing-features-premium {
        text-align: left;
        margin: 8px 0 2px 0;
        padding: 0;
        list-style: none;
    }
    
    .pricing-features-premium li {
        padding: 3px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        color: rgba(255,255,255,0.95);
        font-size: 12px;
    }
    
    .pricing-features-premium li::before {
        content: "✦";
        color: #ffd700;
        font-weight: 700;
        font-size: 14px;
    }
    
    .preview-container {
        border-radius: 14px;
        overflow: hidden;
        background: #f8f9fe;
        border: 2px solid #e0e4f0;
        position: relative;
        min-height: 380px;
        height: 100%;
        margin: 0px;
    }
    
    .preview-content {
        padding: 10px 14px 14px 14px;
        background: white;
        border-radius: 12px;
    }
    
    .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.85) 55%, rgba(255,255,255,0.95) 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        border-radius: 14px;
        padding: 15px;
    }
    
    .preview-overlay .lock-icon {
        font-size: 40px;
        margin-bottom: 4px;
    }
    
    .preview-overlay h3 {
        margin: 0 0 2px 0;
        color: #1a1a2e;
        font-size: 20px;
        font-weight: 700;
    }
    
    .preview-overlay p {
        margin: 0 0 8px 0;
        color: #6c757d;
        font-size: 13px;
        text-align: center;
    }
    
    .preview-overlay .price-tag {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .preview-overlay .price-tag span {
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 700;
    }
    
    .testimonial-card {
        background: white;
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 6px;
        border-left: 3px solid #667eea;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .testimonial-card .stars {
        color: #ffd700;
        font-size: 12px;
        letter-spacing: 2px;
    }
    
    .testimonial-card .author {
        font-weight: 600;
        color: #1a1a2e;
        margin-top: 2px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
    }
    
    .testimonial-card .author .role {
        font-weight: 400;
        color: #6c757d;
        font-size: 11px;
    }
    
    .security-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-size: 11px;
        color: #6c757d;
        margin-top: 6px;
        flex-wrap: wrap;
    }
    
    .security-badge span {
        display: flex;
        align-items: center;
        gap: 3px;
    }
    
    .metric-preview {
        background: white;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .metric-preview .value {
        font-size: 20px;
        font-weight: 800;
        color: #dc3545;
    }
    
    .metric-preview .label {
        font-size: 10px;
        color: #6c757d;
        font-weight: 500;
    }
    
    .metric-preview.green .value {
        color: #28a745;
    }
    
    .sidebar-status {
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    .sidebar-status.free {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffc107;
    }
    
    .sidebar-status.premium {
        background: #d4edda;
        color: #155724;
        border: 1px solid #28a745;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .btn-pulse {
        animation: pulse 2s infinite;
    }
    
    /* Réduire les marges des titres */
    h1, h2, h3, h4, h5, h6 {
        margin: 4px 0 !important;
    }
    
    p {
        margin: 2px 0 !important;
    }
    
    .stTextInput > div {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Supprimer les marges des conteneurs */
    .st-emotion-cache-1r4qj8v {
        padding: 0px !important;
    }
    
    .st-emotion-cache-1v0mbdj {
        margin: 0px !important;
        padding: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================

if "est_abonne" not in st.session_state:
    st.session_state["est_abonne"] = False
if "email" not in st.session_state:
    st.session_state["email"] = ""

# ============================================
# FONCTIONS
# ============================================

def valider_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def simuler_scenario_inflation(initial, mensuel, taux_nominal, inflation, annees):
    capital_nominal = initial
    capital_reel = initial
    taux_mensuel_nominal = (taux_nominal / 100) / 12
    taux_reel_annuel = ((1 + taux_nominal/100) / (1 + inflation/100) - 1) * 100
    taux_mensuel_reel = (taux_reel_annuel / 100) / 12
    historique = []
    for mois in range(1, (annees * 12) + 1):
        capital_nominal += mensuel
        capital_nominal += capital_nominal * taux_mensuel_nominal
        capital_reel += mensuel
        capital_reel += capital_reel * taux_mensuel_reel
        if mois % 12 == 0:
            annee_actuelle = mois // 12
            historique.append({
                "Année": annee_actuelle,
                "Valeur Brute (€)": round(capital_nominal, 2),
                "Pouvoir d'Achat Réel (€)": round(capital_reel, 2)
            })
    return historique

def generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation):
    buffer = BytesIO()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Standard", color="#4b7bec", linewidth=2)
    ax1.plot(df_b.index, df_b["Pouvoir d'Achat Réel (€)"], label="Optimise", color="#ffa502", linewidth=2)
    ax1.plot(df_c.index, df_c["Pouvoir d'Achat Réel (€)"], label="Premium", color="#00d4b2", linewidth=2)
    ax1.set_title(f"Inflation: {inflation}%", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Annees", fontsize=10)
    ax1.set_ylabel("Valeur (€)", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc='upper left', fontsize=9)
    
    ax2.plot(df_a.index, df_a["Valeur Brute (€)"], label="Brute", color="#4b7bec", linewidth=1.5, linestyle='--')
    ax2.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Reel", color="#ff4757", linewidth=2)
    ax2.fill_between(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], df_a["Valeur Brute (€)"], alpha=0.1, color='#ff4757')
    ax2.set_title("Impact de l'inflation", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Annees", fontsize=10)
    ax2.set_ylabel("Valeur (€)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(buffer, format="pdf", dpi=300, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer

def creer_session_paiement():
    try:
        email = st.session_state.get("email", "").strip()
        if not email or not valider_email(email):
            st.error("❌ Email invalide")
            return None
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": ID_PRIX_MENSUEL, "quantity": 1}],
            mode="subscription",
            success_url=f"{URL_APP}?success=true",
            cancel_url=f"{URL_APP}?cancel=true",
            customer_email=email
        )
        return session.url
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return None

# ============================================
# GESTION DU RETOUR DE PAIEMENT
# ============================================

query_params = st.query_params
if "success" in query_params:
    st.session_state["est_abonne"] = True
    st.success("🎉 Abonnement actif !")
    st.balloons()
    st.query_params.clear()
    st.rerun()

if "cancel" in query_params:
    st.warning("ℹ️ Annule")
    st.query_params.clear()

# ============================================
# BARRE LATÉRALE
# ============================================

with st.sidebar:
    st.markdown("### 🚀 Premium")
    st.markdown("---")
    
    if st.session_state["est_abonne"]:
        st.markdown('<div class="sidebar-status premium">🟢 Premium Actif</div>', unsafe_allow_html=True)
        if st.button("🚪 Deconnexion", use_container_width=True):
            st.session_state["est_abonne"] = False
            st.session_state["email"] = ""
            st.rerun()
    else:
        st.markdown('<div class="sidebar-status free">⚡ Version Gratuite</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Premium :")
        st.markdown("✅ Simulations\n✅ Multi-scenarios\n✅ Graphiques\n✅ Export PDF")
        if st.button("🔥 S'abonner", use_container_width=True, type="primary"):
            st.rerun()

# ============================================
# INTERFACE PRINCIPALE - HEADER
# ============================================

col_logo, col_right = st.columns([3, 1])
with col_logo:
    st.markdown('<span class="premium-badge">✨ V2</span>', unsafe_allow_html=True)
    st.title("🧠 Simulateur Épargne")
    st.caption("Analyse inflation + optimisation")

with col_right:
    if not st.session_state["est_abonne"]:
        st.markdown("""
        <div style="text-align:right;">
            <span style="background:#fff3cd;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">👀 7 jours essai</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# ESPACE MEMBRE VS PAYWALL
# ============================================

if st.session_state["est_abonne"]:
    # ESPACE MEMBRE
    st.success("🔓 Premium debloque !")
    
    st.markdown("### 📊 Parametres")
    col1, col2, col3 = st.columns(3)
    with col1:
        initial = st.number_input("Capital (€)", value=10000, step=1000)
    with col2:
        mensuel = st.number_input("Mensuel (€)", value=250, step=50)
    with col3:
        inflation = st.number_input("Inflation %", value=2.5, step=0.1)
    
    annees = st.slider("Horizon", 2, 40, 15)
    
    st.markdown("### 📈 Scenarios")
    c1, c2, c3 = st.columns(3)
    with c1:
        taux_a = st.number_input("Standard %", value=3.0, step=0.1)
    with c2:
        taux_b = st.number_input("Optimise %", value=5.5, step=0.1)
    with c3:
        taux_c = st.number_input("Premium %", value=8.5, step=0.1)
    
    with st.spinner("..."):
        df_a = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_a, inflation, annees)).set_index("Année")
        df_b = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_b, inflation, annees)).set_index("Année")
        df_c = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_c, inflation, annees)).set_index("Année")
    
    st.markdown("### 📊 Comparatif")
    df_compare = pd.DataFrame({
        "Standard": df_a["Pouvoir d'Achat Réel (€)"],
        "Optimise": df_b["Pouvoir d'Achat Réel (€)"],
        "Premium": df_c["Pouvoir d'Achat Réel (€)"]
    })
    st.line_chart(df_compare)
    
    st.markdown("### 📥 PDF")
    pdf = generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation)
    st.download_button("📥 Telecharger", data=pdf, file_name=f"rapport_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)

else:
    # ==========================================
    # PAYWALL SANS ESPACES VIDES
    # ==========================================
    
    # Bannière - COMPACTE
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f8f9fe,#eef1ff);padding:10px 18px;border-radius:14px;border:1px solid #d0d3e0;margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;">
            <div>
                <span class="free-badge">🔓 APERCU</span>
                <h3 style="margin:2px 0;font-size:16px;">Decouvrez Premium</h3>
                <p style="margin:0;font-size:12px;color:#6c757d;">Testez et voyez la valeur</p>
            </div>
            <div style="display:flex;gap:6px;">
                <span style="background:#ffd700;padding:2px 10px;border-radius:20px;font-weight:600;font-size:11px;">⭐ 5</span>
                <span style="background:#28a745;color:#fff;padding:2px 10px;border-radius:20px;font-weight:600;font-size:11px;">✅ Satisfait</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Colonnes SANS ESPACE
    col_pay, col_prev = st.columns([1, 1.3], gap="small")
    
    with col_pay:
        st.markdown("""
        <div class="paywall-premium">
            <h2 style="font-size:22px;margin:0;">🔒 Premium</h2>
            <p style="font-size:13px;margin:2px 0 8px 0;">Debloquez la puissance totale</p>
            
            <div class="pricing-card-premium">
                <div style="font-size:11px;background:rgba(255,255,255,0.2);padding:2px 10px;border-radius:20px;display:inline-block;">⭐ OFFRE POPULAIRE</div>
                <div class="pricing-price-premium">9,00€ <span>/ mois</span></div>
                <div style="font-size:12px;opacity:0.8;margin:-2px 0 6px 0;">0,30€/jour</div>
                <ul class="pricing-features-premium">
                    <li>Simulations illimitees</li>
                    <li>Comparaison multi-scenarios</li>
                    <li>Graphiques avances</li>
                    <li>Exports PDF haute res</li>
                    <li>Analyse personnalisee</li>
                    <li>Annulation 1 clic</li>
                </ul>
            </div>
            
            <div style="margin-top:8px;">
                <div style="background:white;border-radius:12px;padding:12px 14px;box-shadow:0 2px 12px rgba(0,0,0,0.04);">
                    <label style="font-weight:600;font-size:12px;display:block;text-align:left;margin-bottom:4px;">📧 Email :</label>
                    <input type="email" id="email_input_paywall" placeholder="vous@exemple.com" style="width:100%;padding:8px 12px;border:2px solid #e0e0e0;border-radius:8px;font-size:13px;margin-bottom:8px;">
                    <button onclick="document.getElementById('stButton_subscribe').click()" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:10px;border:none;border-radius:50px;font-weight:700;font-size:14px;cursor:pointer;width:100%;box-shadow:0 4px 20px rgba(102,126,234,0.35);" class="btn-pulse">
                        🔓 DEBLOQUER
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        email_input = st.text_input("", placeholder="vous@exemple.com", key="email_paywall", label_visibility="collapsed")
        if email_input:
            st.session_state["email"] = email_input
        
        if st.button("🔓 DEBLOQUER", use_container_width=True, key="stButton_subscribe"):
            if not valider_email(st.session_state.get("email", "")):
                st.error("Email invalide")
            else:
                checkout_url = creer_session_paiement()
                if checkout_url:
                    st.markdown(f'<a href="{checkout_url}" target="_blank" style="display:block;text-align:center;background:#28a745;color:#fff;padding:8px;border-radius:50px;text-decoration:none;font-weight:700;margin-top:6px;font-size:13px;">💳 Stripe</a>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="security-badge">
            <span>🔒 Secure</span>
            <span>🔄 Annulation</span>
            <span>💳 Stripe</span>
            <span>📱 7j/7</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 💬 Témoignages")
        st.markdown("""
        <div class="testimonial-card">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-size:12px;margin:2px 0;">"9€ rentabilises au centuple !"</p>
            <div class="author">Thomas R. <span class="role">Entrepreneur</span></div>
        </div>
        <div class="testimonial-card">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-size:12px;margin:2px 0;">"Graphiques ultra clairs"</p>
            <div class="author">Sarah M. <span class="role">Cadre</span></div>
        </div>
        <div class="testimonial-card" style="margin-bottom:0;">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-size:12px;margin:2px 0;">"Enfin la verite sur l'epargne !"</p>
            <div class="author">David L. <span class="role">Ingenieur</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prev:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <h3 style="margin:0;font-size:18px;">🔍 Apercu</h3>
            <span style="background:#ff4757;color:#fff;padding:1px 8px;border-radius:20px;font-size:9px;font-weight:700;">DEMO</span>
        </div>
        <p style="font-size:12px;color:#6c757d;margin:0 0 8px 0;">👆 Apercu de l'analyse</p>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        st.markdown('<div class="preview-content">', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2, gap="small")
        with col_m1:
            st.markdown("""
            <div class="metric-preview">
                <div class="value">-2,3%</div>
                <div class="label">Perte / an</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown("""
            <div class="metric-preview green">
                <div class="value">+15 400€</div>
                <div class="label">Gain 10 ans</div>
            </div>
            """, unsafe_allow_html=True)
        
        data_preview = pd.DataFrame({
            "Années": list(range(1, 16)),
            "Livret A": [10000 * (1.03**i) for i in range(1, 16)],
            "Premium": [10000 * (1.085**i) for i in range(1, 16)]
        }).set_index("Années")
        
        st.line_chart(data_preview, use_container_width=True)
        
        st.dataframe(
            data_preview.round(0).head(4),
            use_container_width=True,
            column_config={
                "Livret A": st.column_config.NumberColumn("Livret A", format="%.0f €"),
                "Premium": st.column_config.NumberColumn("Premium", format="%.0f €")
            }
        )
        
        st.markdown("""
        <div style="background:#fff3cd;padding:6px 12px;border-radius:6px;margin-top:4px;border-left:3px solid #ffc107;">
            <span style="font-size:11px;"><strong>💡</strong> Inflation reduit de 20% en 10 ans</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="preview-overlay">
            <span class="lock-icon">🔒</span>
            <h3>Version Premium</h3>
            <p>Abonnez-vous pour debloquer<br>l'integralite</p>
            <div class="price-tag">
                <span style="background:#667eea;color:#fff;">9€/mois</span>
                <span style="background:#28a745;color:#fff;">⭐ 5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f8f9fa,#e9ecef);padding:10px;border-radius:10px;text-align:center;">
        <div style="display:flex;justify-content:center;gap:20px;flex-wrap:wrap;">
            <span style="font-weight:600;font-size:12px;">🔒 100% securise</span>
            <span style="font-weight:600;font-size:12px;">🔄 Annulation</span>
            <span style="font-weight:600;font-size:12px;">💳 Stripe</span>
            <span style="font-weight:600;font-size:12px;">📱 7j/7</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
