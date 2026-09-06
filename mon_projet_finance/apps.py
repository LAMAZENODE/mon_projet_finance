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
# CSS MODERNE
# ============================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Suppression des marges et espaces */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    .premium-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .free-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 4px 14px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    
    .paywall-premium {
        background: linear-gradient(145deg, #ffffff, #f8f9fe);
        border-radius: 20px;
        padding: 30px 25px 20px 25px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.12);
        border: 1px solid rgba(102, 126, 234, 0.08);
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    
    .paywall-premium::before {
        content: "★";
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 120px;
        color: rgba(102, 126, 234, 0.04);
    }
    
    .paywall-premium h2 {
        margin-top: 0;
        margin-bottom: 8px;
    }
    
    .paywall-premium p {
        margin-bottom: 15px;
    }
    
    .pricing-card-premium {
        background: linear-gradient(145deg, #667eea, #764ba2);
        border-radius: 16px;
        padding: 20px 25px;
        color: white;
        margin: 10px 0 15px 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.35);
        position: relative;
    }
    
    .pricing-price-premium {
        font-size: 42px;
        font-weight: 800;
        margin: 5px 0;
    }
    
    .pricing-price-premium span {
        font-size: 18px;
        font-weight: 400;
        opacity: 0.8;
    }
    
    .pricing-features-premium {
        text-align: left;
        margin: 15px 0 5px 0;
        padding: 0;
        list-style: none;
    }
    
    .pricing-features-premium li {
        padding: 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        color: rgba(255,255,255,0.95);
        font-size: 14px;
    }
    
    .pricing-features-premium li::before {
        content: "✦";
        color: #ffd700;
        font-weight: 700;
        font-size: 18px;
    }
    
    .preview-container {
        border-radius: 16px;
        overflow: hidden;
        background: #f8f9fe;
        border: 2px solid #e0e4f0;
        position: relative;
        min-height: 400px;
        height: 100%;
    }
    
    .preview-content {
        padding: 15px 20px 20px 20px;
        background: white;
        border-radius: 12px;
    }
    
    .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.85) 60%, rgba(255,255,255,0.95) 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        border-radius: 16px;
        padding: 20px;
    }
    
    .preview-overlay .lock-icon {
        font-size: 48px;
        margin-bottom: 8px;
    }
    
    .preview-overlay h3 {
        margin: 0 0 4px 0;
        color: #1a1a2e;
        font-size: 22px;
        font-weight: 700;
    }
    
    .preview-overlay p {
        margin: 0 0 12px 0;
        color: #6c757d;
        font-size: 14px;
        text-align: center;
    }
    
    .preview-overlay .price-tag {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    .preview-overlay .price-tag span {
        padding: 5px 16px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 700;
    }
    
    .testimonial-card {
        background: white;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .testimonial-card .stars {
        color: #ffd700;
        font-size: 13px;
        letter-spacing: 2px;
    }
    
    .testimonial-card .author {
        font-weight: 600;
        color: #1a1a2e;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    .testimonial-card .author .role {
        font-weight: 400;
        color: #6c757d;
        font-size: 12px;
    }
    
    .security-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        font-size: 12px;
        color: #6c757d;
        margin-top: 10px;
        flex-wrap: wrap;
    }
    
    .security-badge span {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .metric-preview {
        background: white;
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .metric-preview .value {
        font-size: 22px;
        font-weight: 800;
        color: #dc3545;
    }
    
    .metric-preview .label {
        font-size: 11px;
        color: #6c757d;
        font-weight: 500;
    }
    
    .metric-preview.green .value {
        color: #28a745;
    }
    
    .sidebar-status {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
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
    
    /* Supprimer les marges des colonnes */
    .row-widget.stColumns {
        gap: 0px;
    }
    
    .stColumn {
        padding: 0 !important;
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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    ax1.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Scenario Standard", color="#4b7bec", linewidth=2.5)
    ax1.plot(df_b.index, df_b["Pouvoir d'Achat Réel (€)"], label="Scenario Optimise", color="#ffa502", linewidth=2.5)
    ax1.plot(df_c.index, df_c["Pouvoir d'Achat Réel (€)"], label="Scenario Premium", color="#00d4b2", linewidth=2.5)
    ax1.set_title(f"Evolution du Pouvoir d'Achat (Inflation: {inflation}%)", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Annees", fontsize=11)
    ax1.set_ylabel("Valeur Reelle (€)", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc='upper left', fontsize=10)
    
    ax2.plot(df_a.index, df_a["Valeur Brute (€)"], label="Valeur Nominale", color="#4b7bec", linewidth=2, linestyle='--')
    ax2.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Pouvoir d'Achat Reel", color="#ff4757", linewidth=2.5)
    ax2.fill_between(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], df_a["Valeur Brute (€)"], alpha=0.15, color='#ff4757')
    ax2.set_title("Impact de l'inflation sur votre epargne", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Annees", fontsize=11)
    ax2.set_ylabel("Valeur (€)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc='upper left', fontsize=10)
    
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
    st.success("🎉 Abonnement active avec succes !")
    st.balloons()
    st.query_params.clear()
    st.rerun()

if "cancel" in query_params:
    st.warning("ℹ️ Paiement annule.")
    st.query_params.clear()

# ============================================
# BARRE LATÉRALE
# ============================================

with st.sidebar:
    st.markdown("### 🚀 Simulateur Premium")
    st.markdown("---")
    
    if st.session_state["est_abonne"]:
        st.markdown('<div class="sidebar-status premium">🟢 Membre Premium Actif</div>', unsafe_allow_html=True)
        st.caption(f"📧 {st.session_state.get('email', '')}")
        if st.button("🚪 Se deconnecter", use_container_width=True):
            st.session_state["est_abonne"] = False
            st.session_state["email"] = ""
            st.rerun()
    else:
        st.markdown('<div class="sidebar-status free">⚡ Version Gratuite</div>', unsafe_allow_html=True)
        st.caption("🔓 Debloquez toutes les fonctionnalites")
        
        st.markdown("---")
        st.markdown("### 📊 Version Premium :")
        st.markdown("""
        ✅ Simulations illimitees  
        ✅ Comparaison multi-scenarios  
        ✅ Graphiques avances  
        ✅ Export PDF haute qualite  
        ✅ Analyses personnalisees  
        """)
        
        if st.button("🔥 S'abonner", use_container_width=True, type="primary"):
            st.rerun()

# ============================================
# INTERFACE PRINCIPALE
# ============================================

col_logo, col_right = st.columns([3, 1])
with col_logo:
    st.markdown('<span class="premium-badge">✨ VERSION 2.0</span>', unsafe_allow_html=True)
    st.title("🧠 Simulateur d'Épargne Intelligent")
    st.caption("Analysez en profondeur l'impact de l'inflation et optimisez votre strategie financiere.")

with col_right:
    if not st.session_state["est_abonne"]:
        st.markdown("""
        <div style="text-align: right; padding-top: 10px;">
            <span style="background: #fff3cd; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: #856404;">
                👀 7 jours d'essai inclus
            </span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ============================================
# ESPACE MEMBRE VS PAYWALL
# ============================================

if st.session_state["est_abonne"]:
    # ==========================================
    # INTERFACE MEMBRE (DÉBLOQUÉE)
    # ==========================================
    
    st.success("🔓 Acces Premium debloque !")
    
    st.markdown("### 📊 Parametres de simulation")
    col1, col2, col3 = st.columns(3)
    with col1:
        initial = st.number_input("💰 Capital Initial (€)", value=10000, step=1000)
    with col2:
        mensuel = st.number_input("📆 Versement Mensuel (€)", value=250, step=50)
    with col3:
        inflation = st.number_input("📉 Inflation annuelle (%)", value=2.5, step=0.1)
    
    annees = st.slider("⏳ Horizon (annees)", 2, 40, 15)
    
    st.markdown("### 📈 Scenarios d'investissement")
    c1, c2, c3 = st.columns(3)
    with c1:
        taux_a = st.number_input("🟦 Standard (%)", value=3.0, step=0.1)
    with c2:
        taux_b = st.number_input("🟧 Optimise (%)", value=5.5, step=0.1)
    with c3:
        taux_c = st.number_input("🟩 Premium (%)", value=8.5, step=0.1)
    
    with st.spinner("⏳ Calcul..."):
        df_a = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_a, inflation, annees)).set_index("Année")
        df_b = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_b, inflation, annees)).set_index("Année")
        df_c = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_c, inflation, annees)).set_index("Année")
    
    st.markdown("### 🎯 Synthese")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    gain_a = df_a["Pouvoir d'Achat Réel (€)"].iloc[-1] - initial
    gain_b = df_b["Pouvoir d'Achat Réel (€)"].iloc[-1] - initial
    gain_c = df_c["Pouvoir d'Achat Réel (€)"].iloc[-1] - initial
    
    with col_m1:
        st.metric("Standard", f"{df_a['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €", f"{gain_a:+,.0f} €")
    with col_m2:
        st.metric("Optimise", f"{df_b['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €", f"{gain_b:+,.0f} €")
    with col_m3:
        st.metric("Premium", f"{df_c['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €", f"{gain_c:+,.0f} €")
    
    st.markdown("### 📈 Evolution")
    df_compare = pd.DataFrame({
        "Standard": df_a["Pouvoir d'Achat Réel (€)"],
        "Optimise": df_b["Pouvoir d'Achat Réel (€)"],
        "Premium": df_c["Pouvoir d'Achat Réel (€)"]
    })
    st.line_chart(df_compare)
    
    st.markdown("### 📥 Export PDF")
    pdf = generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation)
    st.download_button(
        "📥 Telecharger le rapport (PDF)",
        data=pdf,
        file_name=f"rapport_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    # ==========================================
    # BLOC PAYWALL SANS ESPACES VIDES
    # ==========================================
    
    # Bannière d'aperçu gratuit
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fe, #eef1ff); padding: 15px 25px; border-radius: 16px; border: 1px solid #d0d3e0; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <span class="free-badge">🔓 APERCU GRATUIT</span>
                <h3 style="margin: 6px 0 2px 0; font-size: 18px;">Decouvrez ce que vous offre la version Premium</h3>
                <p style="margin: 0; color: #6c757d; font-size: 14px;">Testez le simulateur en apercu et voyez la valeur ajoutee</p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: #ffd700; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px;">⭐ 5 etoiles</span>
                <span style="background: #28a745; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px;">✅ Satisfait ou rembourse</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Colonnes collées sans espaces
    col_pay, col_prev = st.columns([1, 1.3], gap="small")
    
    with col_pay:
        st.markdown("""
        <div class="paywall-premium">
            <h2 style="font-size: 24px;">🔒 Acces Premium</h2>
            <p style="color: #6c757d; font-size: 14px; margin-bottom: 10px;">Debloquez la puissance totale<br>de notre simulateur financier.</p>
            
            <div class="pricing-card-premium">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 2px;">
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 20px; font-size: 11px;">⭐ OFFRE POPULAIRE</span>
                </div>
                <div class="pricing-price-premium" style="font-size: 36px; margin: 5px 0;">
                    9,00€ <span style="font-size: 16px;">/ mois</span>
                </div>
                <div style="margin: -5px 0 10px 0; font-size: 13px; opacity: 0.8;">
                    soit seulement 0,30€ par jour
                </div>
                <ul class="pricing-features-premium" style="margin: 10px 0 5px 0;">
                    <li style="font-size: 13px; padding: 4px 0;">Simulations illimitees</li>
                    <li style="font-size: 13px; padding: 4px 0;">Comparaison multi-scenarios</li>
                    <li style="font-size: 13px; padding: 4px 0;">Graphiques avances interactifs</li>
                    <li style="font-size: 13px; padding: 4px 0;">Exports PDF haute resolution</li>
                    <li style="font-size: 13px; padding: 4px 0;">Analyse personnalisee</li>
                    <li style="font-size: 13px; padding: 4px 0;">Annulation en 1 clic</li>
                </ul>
            </div>
            
            <div style="margin-top: 12px;">
                <div style="background: white; border-radius: 12px; padding: 14px 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.04);">
                    <label style="font-weight: 600; font-size: 13px; display: block; text-align: left; margin-bottom: 6px;">📧 Votre email :</label>
                    <input type="email" id="email_input_paywall" placeholder="vous@exemple.com" style="width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; margin-bottom: 10px;">
                    <button onclick="document.getElementById('stButton_subscribe').click()" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px; border: none; border-radius: 50px; font-weight: 700; font-size: 15px; cursor: pointer; width: 100%; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.35); transition: all 0.3s;" class="btn-pulse">
                        🔓 DEBLOQUER MAINTENANT
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        email_input = st.text_input("", placeholder="vous@exemple.com", key="email_paywall", label_visibility="collapsed")
        if email_input:
            st.session_state["email"] = email_input
        
        if st.button("🔓 DEBLOQUER MAINTENANT", use_container_width=True, key="stButton_subscribe"):
            if not valider_email(st.session_state.get("email", "")):
                st.error("⚠️ Veuillez entrer une adresse email valide.")
            else:
                checkout_url = creer_session_paiement()
                if checkout_url:
                    st.markdown(f'<a href="{checkout_url}" target="_blank" style="display: block; text-align: center; background: #28a745; color: white; padding: 10px; border-radius: 50px; text-decoration: none; font-weight: 700; margin-top: 8px; font-size: 14px;">💳 Payer securise via Stripe</a>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="security-badge" style="margin-top: 8px;">
            <span>🔒 100% securise</span>
            <span>🔄 Annulation facile</span>
            <span>💳 Stripe</span>
            <span>📱 Support 7j/7</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 💬 Ce qu'en disent nos utilisateurs")
        st.markdown("""
        <div class="testimonial-card" style="padding: 12px 14px; margin-bottom: 8px;">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-style: italic; margin: 4px 0; font-size: 13px;">"Cet outil m'a fait realiser l'impact reel de l'inflation. Les 9€ sont rentabilises au centuple !"</p>
            <div class="author" style="margin-top: 2px; font-size: 13px;">Thomas R. <span class="role">— Entrepreneur</span></div>
        </div>
        <div class="testimonial-card" style="padding: 12px 14px; margin-bottom: 8px;">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-style: italic; margin: 4px 0; font-size: 13px;">"Les graphiques comparatifs sont ultra clairs. L'export PDF est parfait."</p>
            <div class="author" style="margin-top: 2px; font-size: 13px;">Sarah M. <span class="role">— Cadre Financier</span></div>
        </div>
        <div class="testimonial-card" style="padding: 12px 14px; margin-bottom: 0;">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <p style="font-style: italic; margin: 4px 0; font-size: 13px;">"Enfin un simulateur qui montre la verite sur l'epargne !"</p>
            <div class="author" style="margin-top: 2px; font-size: 13px;">David L. <span class="role">— Ingenieur</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prev:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <h3 style="margin: 0; font-size: 20px;">🔍 Apercu interactif</h3>
            <span style="background: #ff4757; color: white; padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: 700;">DEMO</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("👆 Voici un apercu de ce que vous pourrez analyser en detail")
        
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        st.markdown('<div class="preview-content">', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2, gap="small")
        with col_m1:
            st.markdown("""
            <div class="metric-preview">
                <div class="value">-2,3%</div>
                <div class="label">📉 Perte de pouvoir d'achat / an</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown("""
            <div class="metric-preview green">
                <div class="value">+15 400€</div>
                <div class="label">🚀 Gain potentiel sur 10 ans</div>
            </div>
            """, unsafe_allow_html=True)
        
        data_preview = pd.DataFrame({
            "Années": list(range(1, 16)),
            "Livret A (3%)": [10000 * (1.03**i) for i in range(1, 16)],
            "Strategie Premium (8.5%)": [10000 * (1.085**i) for i in range(1, 16)]
        }).set_index("Années")
        
        st.line_chart(data_preview, use_container_width=True)
        
        st.dataframe(
            data_preview.round(0).head(5),
            use_container_width=True,
            column_config={
                "Livret A (3%)": st.column_config.NumberColumn("💰 Livret A", format="%.0f €"),
                "Strategie Premium (8.5%)": st.column_config.NumberColumn("🚀 Premium", format="%.0f €")
            }
        )
        
        st.markdown("""
        <div style="background: #fff3cd; padding: 10px 14px; border-radius: 8px; margin-top: 6px; border-left: 4px solid #ffc107;">
            <strong style="font-size: 13px;">💡 Le saviez-vous ?</strong>
            <span style="color: #6c757d; font-size: 13px;">En 10 ans, l'inflation peut reduire de 20% le pouvoir d'achat de votre epargne.</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="preview-overlay">
            <span class="lock-icon">🔒</span>
            <h3>Version Premium</h3>
            <p>Abonnez-vous pour debloquer<br>l'integralite des analyses</p>
            <div class="price-tag">
                <span style="background: #667eea; color: white;">9€/mois</span>
                <span style="background: #28a745; color: white;">⭐ 5/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 12px; text-align: center;">
        <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: center;">
            <div><span style="font-weight: 600; font-size: 13px;">🔒 Paiement 100% securise</span></div>
            <div><span style="font-weight: 600; font-size: 13px;">🔄 Annulation a tout moment</span></div>
            <div><span style="font-weight: 600; font-size: 13px;">💳 Stripe Certifie</span></div>
            <div><span style="font-weight: 600; font-size: 13px;">📱 Support 7j/7</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
