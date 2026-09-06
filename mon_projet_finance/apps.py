import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import re

st.set_page_config(
    page_title="Simulateur d'Épargne",
    page_icon="🧠",
    layout="wide"
)

# ============================================
# CSS
# ============================================

st.markdown("""
<style>
    .premium-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    
    .pricing-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .pricing-price {
        font-size: 40px;
        font-weight: 800;
        margin: 8px 0;
    }
    
    .pricing-price span {
        font-size: 16px;
        font-weight: 400;
        opacity: 0.8;
    }
    
    .features {
        text-align: left;
        margin: 16px 0;
        padding: 0;
        list-style: none;
    }
    
    .features li {
        padding: 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .features li::before {
        content: "✅";
    }
    
    .testimonial {
        background: white;
        padding: 14px 16px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .testimonial .author {
        font-weight: 600;
        margin-top: 4px;
        font-size: 14px;
    }
    
    .testimonial .role {
        font-weight: 400;
        color: #6c757d;
        font-size: 13px;
    }
    
    .preview-box {
        border: 2px dashed #d0d3e0;
        border-radius: 12px;
        padding: 20px;
        background: #f8f9fe;
        position: relative;
    }
    
    .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.9) 70%, rgba(255,255,255,0.95) 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        z-index: 10;
    }
    
    .preview-overlay .lock {
        font-size: 40px;
        margin-bottom: 8px;
    }
    
    .preview-overlay h3 {
        margin: 0;
        color: #1a1a2e;
    }
    
    .preview-overlay p {
        color: #6c757d;
        font-size: 14px;
        margin: 4px 0 12px 0;
    }
    
    .btn-premium {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 12px 32px;
        border: none;
        border-radius: 50px;
        font-weight: 700;
        font-size: 16px;
        cursor: pointer;
        width: 100%;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.35);
    }
    
    .btn-premium:hover {
        transform: translateY(-2px);
    }
    
    .security-badge {
        display: flex;
        justify-content: center;
        gap: 16px;
        font-size: 12px;
        color: #6c757d;
        margin-top: 12px;
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

def simuler(initial, mensuel, taux, inflation, annees):
    capital = initial
    taux_mensuel = (taux / 100) / 12
    historique = []
    for mois in range(1, (annees * 12) + 1):
        capital += mensuel
        capital += capital * taux_mensuel
        if mois % 12 == 0:
            historique.append(round(capital, 2))
    return historique

def generer_pdf():
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(8, 5))
    
    annees = list(range(1, 16))
    standard = simuler(10000, 250, 3, 2.5, 15)
    dynamique = simuler(10000, 250, 6, 2.5, 15)
    inflation_impact = [10000 * (0.975**i) for i in range(1, 16)]
    
    ax.plot(annees, standard, label="Scénario Standard (3%)", color="#4b7bec", linewidth=2)
    ax.plot(annees, dynamique, label="Scénario Dynamique (6%)", color="#00d4b2", linewidth=2)
    ax.plot(annees, inflation_impact, label="Inflation Réelle", color="#ff4757", linewidth=2, linestyle='--')
    
    ax.set_title("Évolution de l'Épargne", fontsize=14, fontweight='bold')
    ax.set_xlabel("Années")
    ax.set_ylabel("Valeur (€)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(buffer, format="pdf", dpi=300)
    plt.close()
    buffer.seek(0)
    return buffer

def creer_paiement():
    # Simulation de paiement - À remplacer par Stripe
    st.session_state["est_abonne"] = True
    st.success("🎉 Abonnement activé !")
    st.balloons()
    st.rerun()

# ============================================
# GESTION DU PAIEMENT
# ============================================

query_params = st.query_params
if "success" in query_params:
    st.session_state["est_abonne"] = True
    st.success("🎉 Abonnement activé !")
    st.balloons()
    st.query_params.clear()
    st.rerun()

# ============================================
# INTERFACE PRINCIPALE
# ============================================

st.markdown('<span class="premium-badge">✨ VERSION 2.0</span>', unsafe_allow_html=True)
st.title("🧠 Simulateur d'Épargne")
st.caption("Analysez l'impact de l'inflation")

st.divider()

# ============================================
# ESPACE MEMBRE VS PAYWALL
# ============================================

if st.session_state["est_abonne"]:
    # ==========================================
    # VERSION PREMIUM DÉBLOQUÉE
    # ==========================================
    
    st.success("🔓 Accès Premium débloqué !")
    
    st.markdown("### 📊 Paramètres de simulation")
    col1, col2, col3 = st.columns(3)
    with col1:
        capital = st.number_input("Capital initial (€)", value=10000, step=1000)
    with col2:
        mensuel = st.number_input("Versement mensuel (€)", value=250, step=50)
    with col3:
        inflation = st.number_input("Inflation (%)", value=2.5, step=0.1)
    
    annees = st.slider("Horizon (années)", 2, 40, 15)
    
    st.markdown("### 📈 Scénarios")
    c1, c2, c3 = st.columns(3)
    with c1:
        taux_a = st.number_input("Standard (%)", value=3.0, step=0.1)
    with c2:
        taux_b = st.number_input("Dynamique (%)", value=6.0, step=0.1)
    with c3:
        taux_c = st.number_input("Premium (%)", value=8.5, step=0.1)
    
    # Calculs
    data_a = simuler(capital, mensuel, taux_a, inflation, annees)
    data_b = simuler(capital, mensuel, taux_b, inflation, annees)
    data_c = simuler(capital, mensuel, taux_c, inflation, annees)
    
    df = pd.DataFrame({
        "Standard": data_a,
        "Dynamique": data_b,
        "Premium": data_c
    }, index=range(1, annees + 1))
    
    st.markdown("### 📈 Évolution")
    st.line_chart(df)
    
    st.markdown("### 📥 Export PDF")
    st.caption("Téléchargez votre rapport complet en PDF")
    
    pdf = generer_pdf()
    st.download_button(
        "📥 Télécharger le rapport PDF",
        data=pdf,
        file_name="rapport_epargne.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    # ==========================================
    # VERSION GRATUITE AVEC APERÇU
    # ==========================================
    
    # Colonnes : Offre à gauche, Aperçu à droite
    col_left, col_right = st.columns([1, 1.2], gap="medium")
    
    with col_left:
        st.markdown("### 🔒 Accès Premium")
        st.caption("Débloquez la puissance totale de notre simulateur financier.")
        
        # Carte de prix
        st.markdown("""
        <div class="pricing-card">
            <h3 style="margin:0;">Abonnement Mensuel</h3>
            <div class="pricing-price">9.00€ <span>/ mois</span></div>
            <ul class="features">
                <li>Simulations illimitées</li>
                <li>Graphes comparatifs avancés</li>
                <li>Exports PDF haute résolution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulaire email
        email = st.text_input("📧 Saisissez votre adresse email pour commencer :", placeholder="vous@exemple.com", key="email_input")
        if email:
            st.session_state["email"] = email
        
        if st.button("🔓 DÉBLOQUER MAINTENANT", use_container_width=True):
            if not valider_email(email):
                st.error("⚠️ Veuillez entrer un email valide.")
            else:
                creer_paiement()
        
        st.markdown("""
        <div class="security-badge">
            <span>🔒 100% sécurisé</span>
            <span>🔄 Annulation facile</span>
            <span>💳 Stripe</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Témoignages
        st.markdown("### 💬 Ce qu'en disent nos utilisateurs")
        st.markdown("""
        <div class="testimonial">
            <p style="font-style:italic;margin:0;">"Cet outil m'a fait réaliser l'impact réel de l'inflation sur mon livret A. J'ai réajusté mes investissements immédiatement. Les 9€ sont rentabilisés au centuple !"</p>
            <div class="author">Thomas R. <span class="role">— Entrepreneur</span></div>
        </div>
        <div class="testimonial">
            <p style="font-style:italic;margin:0;">"Les graphiques comparatifs sont ultra clairs. L'export PDF est parfait pour faire des points financiers en famille."</p>
            <div class="author">Sarah M. <span class="role">— Cadre Financier</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 🔍 Aperçu de votre espace Premium")
        st.caption("Abonnez-vous pour interagir avec ce graphique et modifier les données.")
        
        # Conteneur d'aperçu
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        
        # Graphique d'aperçu (visible)
        st.info("💡 Exemple d'analyse générée pour un capital de 10 000 €")
        
        data_preview = pd.DataFrame({
            "Standard": [10000 * (1.03**i) for i in range(1, 16)],
            "Dynamique": [10000 * (1.06**i) for i in range(1, 16)],
            "Inflation Réelle": [10000 * (0.975**i) for i in range(1, 16)]
        }, index=range(1, 16))
        
        st.line_chart(data_preview)
        
        # Overlay avec CTA
        st.markdown("""
        <div class="preview-overlay">
            <span class="lock">🔒</span>
            <h3>Contenu Premium</h3>
            <p>Abonnez-vous pour débloquer<br>toutes les fonctionnalités</p>
            <div style="display:flex;gap:10px;">
                <span style="background:#667eea;color:#fff;padding:4px 16px;border-radius:50px;font-weight:700;font-size:13px;">9€/mois</span>
                <span style="background:#ffd700;padding:4px 16px;border-radius:50px;font-weight:700;font-size:13px;">⭐ 5/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("🔒 Paiement sécurisé - 7 jours d'essai inclus - Satisfait ou remboursé")
