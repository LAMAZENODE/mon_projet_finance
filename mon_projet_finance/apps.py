import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import re
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Simulateur d'Épargne",
    page_icon="🧠",
    layout="wide"
)

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

def simuler_epargne(initial, mensuel, taux, inflation, annees):
    capital_nominal = initial
    capital_reel = initial
    taux_mensuel_nominal = (taux / 100) / 12
    taux_reel_annuel = ((1 + taux/100) / (1 + inflation/100) - 1) * 100
    taux_mensuel_reel = (taux_reel_annuel / 100) / 12
    
    historique = []
    for mois in range(1, (annees * 12) + 1):
        capital_nominal += mensuel
        capital_nominal += capital_nominal * taux_mensuel_nominal
        capital_reel += mensuel
        capital_reel += capital_reel * taux_mensuel_reel
        if mois % 12 == 0:
            annee = mois // 12
            historique.append({
                "Année": annee,
                "Valeur Nominale (€)": round(capital_nominal, 2),
                "Pouvoir d'Achat Réel (€)": round(capital_reel, 2)
            })
    return pd.DataFrame(historique)

def generer_pdf(initial, mensuel, inflation, taux_a, taux_b, taux_c, annees, email):
    """Génère un PDF complet pour les membres premium"""
    buffer = BytesIO()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    df_a = simuler_epargne(initial, mensuel, taux_a, inflation, annees)
    df_b = simuler_epargne(initial, mensuel, taux_b, inflation, annees)
    df_c = simuler_epargne(initial, mensuel, taux_c, inflation, annees)
    
    # Graph 1 - Comparaison
    ax1.plot(df_a["Année"], df_a["Pouvoir d'Achat Réel (€)"], label=f"Scénario {taux_a}%", color="#4b7bec", linewidth=2.5)
    ax1.plot(df_b["Année"], df_b["Pouvoir d'Achat Réel (€)"], label=f"Scénario {taux_b}%", color="#ffa502", linewidth=2.5)
    ax1.plot(df_c["Année"], df_c["Pouvoir d'Achat Réel (€)"], label=f"Scénario {taux_c}%", color="#00d4b2", linewidth=2.5)
    ax1.set_title(f"📈 ÉVOLUTION DU POUVOIR D'ACHAT", fontsize=16, fontweight='bold')
    ax1.set_xlabel("Années", fontsize=12)
    ax1.set_ylabel("Valeur Réelle (€)", fontsize=12)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11)
    
    # Graph 2 - Impact inflation
    ax2.plot(df_a["Année"], df_a["Valeur Nominale (€)"], label="Valeur Nominale", color="#4b7bec", linewidth=2, linestyle='--')
    ax2.plot(df_a["Année"], df_a["Pouvoir d'Achat Réel (€)"], label="Pouvoir d'Achat Réel", color="#ff4757", linewidth=2.5)
    ax2.fill_between(df_a["Année"], df_a["Pouvoir d'Achat Réel (€)"], df_a["Valeur Nominale (€)"], alpha=0.2, color='#ff4757')
    ax2.set_title("📉 IMPACT DE L'INFLATION SUR VOTRE ÉPARGNE", fontsize=16, fontweight='bold')
    ax2.set_xlabel("Années", fontsize=12)
    ax2.set_ylabel("Valeur (€)", fontsize=12)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(loc='upper left', fontsize=11)
    
    plt.figtext(0.5, 0.01, f"Rapport personnalisé pour : {email} | {datetime.now().strftime('%d/%m/%Y')}", 
                ha="center", fontsize=10, style='italic', color='#6c757d')
    
    plt.tight_layout()
    plt.savefig(buffer, format="pdf", dpi=300, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer

def creer_paiement():
    # Simulation paiement - À remplacer par Stripe
    st.session_state["est_abonne"] = True
    st.success("🎉 Félicitations ! Votre abonnement Premium est activé.")
    st.balloons()
    st.rerun()

# ============================================
# CSS
# ============================================

st.markdown("""
<style>
    .premium-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 6px 18px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .pricing-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 16px;
        padding: 28px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.35);
    }
    
    .pricing-price {
        font-size: 44px;
        font-weight: 800;
        margin: 6px 0;
    }
    
    .pricing-price span {
        font-size: 18px;
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
        padding: 8px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
    }
    
    .features li::before {
        content: "✅";
    }
    
    .btn-payer {
        background: linear-gradient(135deg, #00d4b2, #28a745);
        color: white;
        padding: 16px 32px;
        border: none;
        border-radius: 50px;
        font-weight: 800;
        font-size: 20px;
        cursor: pointer;
        width: 100%;
        box-shadow: 0 6px 30px rgba(40, 167, 69, 0.4);
        transition: all 0.3s;
        animation: pulse 2s infinite;
    }
    
    .btn-payer:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 40px rgba(40, 167, 69, 0.5);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .testimonial {
        background: white;
        padding: 16px 18px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .testimonial p {
        font-style: italic;
        margin: 0;
        font-size: 14px;
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
        border: 2px solid #d0d3e0;
        border-radius: 12px;
        padding: 20px;
        background: #f8f9fe;
        position: relative;
        min-height: 350px;
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
        border-radius: 12px;
        z-index: 10;
        padding: 20px;
    }
    
    .preview-overlay .lock {
        font-size: 48px;
        margin-bottom: 8px;
    }
    
    .preview-overlay h3 {
        margin: 0;
        color: #1a1a2e;
        font-size: 22px;
    }
    
    .preview-overlay p {
        color: #6c757d;
        font-size: 14px;
        margin: 4px 0 12px 0;
        text-align: center;
    }
    
    .security-badge {
        display: flex;
        justify-content: center;
        gap: 20px;
        font-size: 12px;
        color: #6c757d;
        margin-top: 12px;
    }
    
    .feature-highlight {
        background: #fff3cd;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 12px 0;
    }
    
    .pdf-lock {
        text-align: center;
        padding: 16px;
        background: #f8f9fa;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
    }
    
    .badge-popular {
        background: rgba(255,255,255,0.2);
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
    }
    
    .price-small {
        font-size: 14px;
        opacity: 0.8;
        margin: -4px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# GESTION DU PAIEMENT
# ============================================

query_params = st.query_params
if "success" in query_params:
    st.session_state["est_abonne"] = True
    st.query_params.clear()
    st.rerun()

# ============================================
# INTERFACE PRINCIPALE
# ============================================

st.markdown('<span class="premium-badge">✨ VERSION 2.0</span>', unsafe_allow_html=True)
st.title("🧠 Simulateur d'Épargne Intelligent")
st.caption("Analysez l'impact de l'inflation sur votre épargne")

st.divider()

# ============================================
# ESPACE MEMBRE VS PAYWALL
# ============================================

if st.session_state["est_abonne"]:
    # ==========================================
    # ESPACE PREMIUM DÉBLOQUÉ
    # ==========================================
    
    st.success("🔓 Accès Premium débloqué !")
    
    st.markdown("### 📊 Paramètres de simulation")
    col1, col2, col3 = st.columns(3)
    with col1:
        capital = st.number_input("💰 Capital Initial (€)", value=10000, step=1000)
    with col2:
        mensuel = st.number_input("📆 Versement Mensuel (€)", value=250, step=50)
    with col3:
        inflation = st.number_input("📉 Inflation annuelle (%)", value=2.5, step=0.1)
    
    annees = st.slider("⏳ Horizon d'investissement (années)", 2, 40, 15)
    
    st.markdown("### 📈 Scénarios d'investissement")
    c1, c2, c3 = st.columns(3)
    with c1:
        taux_a = st.number_input("📊 Standard (%)", value=3.0, step=0.1)
    with c2:
        taux_b = st.number_input("📈 Dynamique (%)", value=6.0, step=0.1)
    with c3:
        taux_c = st.number_input("🚀 Premium (%)", value=8.5, step=0.1)
    
    with st.spinner("Calcul en cours..."):
        df_a = simuler_epargne(capital, mensuel, taux_a, inflation, annees)
        df_b = simuler_epargne(capital, mensuel, taux_b, inflation, annees)
        df_c = simuler_epargne(capital, mensuel, taux_c, inflation, annees)
    
    st.markdown("### 🎯 Synthèse comparative")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📊 Standard", f"{df_a['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €")
    with col_m2:
        st.metric("📈 Dynamique", f"{df_b['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €")
    with col_m3:
        st.metric("🚀 Premium", f"{df_c['Pouvoir d\'Achat Réel (€)'].iloc[-1]:,.0f} €")
    
    st.markdown("### 📈 Évolution du pouvoir d'achat")
    df_compare = pd.DataFrame({
        f"Standard {taux_a}%": df_a["Pouvoir d'Achat Réel (€)"],
        f"Dynamique {taux_b}%": df_b["Pouvoir d'Achat Réel (€)"],
        f"Premium {taux_c}%": df_c["Pouvoir d'Achat Réel (€)"]
    }, index=df_a["Année"])
    st.line_chart(df_compare)
    
    st.markdown("### 📥 Export PDF personnalisé")
    pdf = generer_pdf(capital, mensuel, inflation, taux_a, taux_b, taux_c, annees, st.session_state.get("email", "Utilisateur"))
    st.download_button(
        "📥 Télécharger mon rapport PDF personnalisé",
        data=pdf,
        file_name=f"rapport_epargne_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    # ==========================================
    # VERSION GRATUITE - LE CLIENT VOIT LE BOUTON PAYER
    # ==========================================
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fe, #eef1ff); padding: 12px 20px; border-radius: 12px; border: 1px solid #d0d3e0; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div>
                <span style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 2px 12px; border-radius: 50px; font-weight: 600; font-size: 11px;">👀 APERÇU</span>
                <h3 style="margin: 4px 0 2px 0; font-size: 18px;">Visualisez l'impact de l'inflation</h3>
                <p style="margin: 0; color: #6c757d; font-size: 13px;">Découvrez les graphiques et titres explicatifs</p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: #ffd700; padding: 3px 10px; border-radius: 20px; font-weight: 600; font-size: 11px;">⭐ 5/5</span>
                <span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 20px; font-weight: 600; font-size: 11px;">✅ Satisfait</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.2], gap="medium")
    
    with col_left:
        st.markdown("### 🔒 Accès Premium")
        st.caption("Débloquez la puissance totale de notre simulateur financier.")
        
        st.markdown("""
        <div class="pricing-card">
            <div style="display: flex; justify-content: center; margin-bottom: 4px;">
                <span class="badge-popular">⭐ OFFRE POPULAIRE</span>
            </div>
            <h3 style="margin: 0;">Abonnement Mensuel</h3>
            <div class="pricing-price">9.00€ <span>/ mois</span></div>
            <div class="price-small">soit seulement 0,30€ par jour</div>
            <ul class="features">
                <li>Simulations illimitées</li>
                <li>Graphiques comparatifs avancés</li>
                <li>Exports PDF haute résolution</li>
                <li>Analyse personnalisée</li>
                <li>Annulation en 1 clic</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulaire email
        email = st.text_input("📧 Saisissez votre adresse email pour commencer :", 
                             placeholder="vous@exemple.com", 
                             key="email_input")
        if email:
            st.session_state["email"] = email
        
        # 🔴 BOUTON PAYER TRÈS VISIBLE !
        if st.button("💳 PAYER 9,00€ ET DÉBLOQUER", use_container_width=True, type="primary"):
            if not valider_email(email):
                st.error("⚠️ Veuillez entrer une adresse email valide.")
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
        
        st.markdown("### 💬 Ce qu'en disent nos utilisateurs")
        st.markdown("""
        <div class="testimonial">
            <p>"Cet outil m'a fait réaliser l'impact réel de l'inflation sur mon livret A. J'ai réajusté mes investissements immédiatement. Les 9€ sont rentabilisés au centuple !"</p>
            <div class="author">Thomas R. <span class="role">— Entrepreneur</span></div>
        </div>
        <div class="testimonial">
            <p>"Les graphiques comparatifs sont ultra clairs. L'export PDF est parfait pour faire des points financiers en famille."</p>
            <div class="author">Sarah M. <span class="role">— Cadre Financier</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <h3 style="margin: 0; font-size: 18px;">🔍 Aperçu du rapport Premium</h3>
            <span style="background: #ff4757; color: white; padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: 700;">DÉMO</span>
        </div>
        <p style="font-size: 13px; color: #6c757d; margin: 0 0 10px 0;">👆 Visualisez les grands titres et graphiques</p>
        """, unsafe_allow_html=True)
        
        # Conteneur d'aperçu
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        
        st.caption("💡 Exemple d'analyse générée pour un capital de 10 000 €")
        
        data_preview = pd.DataFrame({
            "📊 Livret A (3%)": [10000 * (1.03**i) for i in range(1, 16)],
            "🚀 Stratégie Premium (6%)": [10000 * (1.06**i) for i in range(1, 16)],
            "📉 Pouvoir d'achat réel": [10000 * (0.975**i) for i in range(1, 16)]
        }, index=range(1, 16))
        
        st.line_chart(data_preview)
        
        # Overlay avec message incitatif
        st.markdown("""
        <div class="preview-overlay">
            <span class="lock">📄</span>
            <h3>Rapport complet verrouillé</h3>
            <p>Abonnez-vous pour débloquer :</p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin: 4px 0 10px 0;">
                <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px; font-size: 12px;">📊 Graphiques interactifs</span>
                <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px; font-size: 12px;">📥 Export PDF</span>
                <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px; font-size: 12px;">🎯 Analyse personnalisée</span>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 4px;">
                <span style="background: #667eea; color: white; padding: 4px 16px; border-radius: 50px; font-weight: 700; font-size: 13px;">9€/mois</span>
                <span style="background: #ffd700; padding: 4px 16px; border-radius: 50px; font-weight: 700; font-size: 13px;">⭐ 5/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 🔒 Bloc PDF verrouillé - PAS DE TÉLÉCHARGEMENT GRATUIT !
        st.markdown("""
        <div class="pdf-lock" style="margin-top: 12px;">
            <span style="font-size: 28px;">🔒</span>
            <p style="margin: 4px 0 0 0; font-weight: 700; color: #6c757d; font-size: 15px;">
                PDF disponible uniquement en version Premium
            </p>
            <p style="margin: 2px 0 0 0; font-size: 13px; color: #adb5bd;">
                Payer 9€ pour débloquer votre rapport personnalisé
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Liste des fonctionnalités
        st.markdown("""
        <div style="background: white; padding: 12px 16px; border-radius: 10px; border: 1px solid #e9ecef; margin-top: 12px;">
            <strong>📋 Ce que vous obtiendrez en Premium :</strong>
            <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 13px; color: #6c757d;">
                <li>📊 <strong>Grands titres</strong> explicatifs sur chaque graphique</li>
                <li>📈 Comparaison de <strong>3 scénarios</strong> personnalisés</li>
                <li>💰 Impact visuel de <strong>l'inflation</strong> sur votre capital</li>
                <li>🎯 Synthèse des <strong>gains potentiels</strong></li>
                <li>📄 Format professionnel <strong>haute résolution</strong></li>
                <li>🔐 Rapport <strong>personnalisé</strong> avec votre email</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("🔒 Paiement sécurisé - 7 jours d'essai inclus - Satisfait ou remboursé")
