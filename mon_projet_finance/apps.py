import os
import streamlit as st
import stripe
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import time
import re

# ============================================
# CONFIGURATION STRIPE
# ============================================

# Récupérer les secrets
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    # Changement du nom de la variable pour refléter l'abonnement mensuel
    ID_PRIX_MENSUEL = st.secrets["STRIPE_PRICE_ID_MONTHLY"]
    URL_APP = st.secrets["MON_URL_STREAMLIT"]
except KeyError as e:
    st.error(f"❌ Erreur de configuration : La clé `{e.args[0]}` est manquante dans `.streamlit/secrets.toml`")
    st.stop()

# Configuration de la page
st.set_page_config(page_title="Simulateur Financier", page_icon="💰", layout="wide")

# ============================================
# CSS
# ============================================

st.markdown("""
<style>
.premium-badge {
    background: linear-gradient(135deg, #ffd700, #ffa500);
    color: #111;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 12px;
    display: inline-block;
    margin-bottom: 10px;
}
.paywall-container {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 30px;
    text-align: center;
}
.blur-preview {
    filter: blur(6px);
    opacity: 0.35;
    pointer-events: none;
    user-select: none;
}
.pricing-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #e9ecef;
    text-align: center;
}
.pricing-price {
    font-size: 32px;
    font-weight: bold;
    color: #635bff;
    margin: 15px 0;
}
.pricing-features {
    text-align: left;
    margin: 20px 0;
    padding-left: 20px;
}
.pricing-features li {
    margin: 8px 0;
    list-style-type: none;
}
.pricing-features li::before {
    content: "✅ ";
}
.security-banner {
    margin-top: 15px;
    font-size: 13px;
    color: #6c757d;
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
    ax1.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Scénario A", color="#ff4b4b", linewidth=2)
    ax1.plot(df_b.index, df_b["Pouvoir d'Achat Réel (€)"], label="Scénario B", color="#ffa500", linewidth=2)
    ax1.plot(df_c.index, df_c["Pouvoir d'Achat Réel (€)"], label="Scénario C", color="#00d4b2", linewidth=2)
    ax1.set_title(f"Évolution du Pouvoir d'Achat Réel (Inflation: {inflation}%)")
    ax1.set_xlabel("Années")
    ax1.set_ylabel("Valeur (€)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend()
    ax2.plot(df_a.index, df_a["Valeur Brute (€)"], label="Valeur Brute", color="#4b7bec", linewidth=2, linestyle='--')
    ax2.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Pouvoir d'Achat Réel", color="#ff4b4b", linewidth=2)
    ax2.set_title("Impact de l'Inflation")
    ax2.set_xlabel("Années")
    ax2.set_ylabel("Valeur (€)")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend()
    plt.tight_layout()
    plt.savefig(buffer, format="pdf", dpi=300)
    plt.close()
    buffer.seek(0)
    return buffer

def creer_session_paiement():
    try:
        email = st.session_state.get("email", "").strip()
        if not email or not valider_email(email):
            st.error("❌ Email invalide")
            return None
        
        # Modifications pour l'abonnement récurrent
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": ID_PRIX_MENSUEL, "quantity": 1}], # Utilisation du prix mensuel
            mode="subscription", # Changement crucial ici
            success_url=f"{URL_APP}?success=true", # Corrigé : URL_APP au lieu de APP_URL
            cancel_url=f"{URL_APP}?cancel=true",   # Corrigé : URL_APP au lieu de APP_URL
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
    st.success("🎉 Abonnement activé !")
    st.balloons()
    st.query_params.clear()
    st.rerun()

if "cancel" in query_params:
    st.warning("Paiement annulé")
    st.query_params.clear()

# ============================================
# BARRE LATÉRALE
# ============================================

st.sidebar.markdown("### 🔒 Espace Client")
if st.session_state["est_abonne"]:
    st.sidebar.success("🟢 Membre Pro Actif")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["est_abonne"] = False
        st.rerun()
else:
    st.sidebar.warning("⚡ Version Gratuite")

# ============================================
# INTERFACE PRINCIPALE
# ============================================

st.markdown('<div class="premium-badge">✨ VERSION 2.0</div>', unsafe_allow_html=True)
st.title("Simulateur d'Épargne 🧠")
st.subheader("Analysez l'impact de l'inflation")

st.divider()

if st.session_state["est_abonne"]:
    # ==========================================
    # INTERFACE MEMBRE (DÉBLOQUÉE)
    # ==========================================
    st.success("🔓 Accès Premium Activé")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        initial = st.number_input("Capital Initial (€)", value=10000, step=1000)
    with col2:
        mensuel = st.number_input("Versement Mensuel (€)", value=250, step=50)
    with col3:
        inflation = st.number_input("Inflation (%)", value=2.5, step=0.1)
    
    annees = st.slider("Horizon (Années)", 2, 40, 15)
    
    st.markdown("### 📊 Scénarios")
    c1, c2, c3 = st.columns(3)
    with c1:
        taux_a = st.number_input("Scénario A (%)", value=3.0, step=0.1)
    with c2:
        taux_b = st.number_input("Scénario B (%)", value=5.5, step=0.1)
    with c3:
        taux_c = st.number_input("Scénario C (%)", value=8.5, step=0.1)
    
    with st.spinner("Calcul..."):
        df_a = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_a, inflation, annees)).set_index("Année")
        df_b = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_b, inflation, annees)).set_index("Année")
        df_c = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_c, inflation, annees)).set_index("Année")
    
    df_compare = pd.DataFrame({
        "Scénario A": df_a["Pouvoir d'Achat Réel (€)"],
        "Scénario B": df_b["Pouvoir d'Achat Réel (€)"],
        "Scénario C": df_c["Pouvoir d'Achat Réel (€)"]
    })
    
    st.markdown("### 📈 Évolution")
    st.line_chart(df_compare)
    
    st.markdown("### 📥 Export")
    pdf = generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation)
    st.download_button("📥 Télécharger le PDF", data=pdf, file_name="rapport.pdf", mime="application/pdf")



else:
    # ==========================================
    # BLOC PAYWALL SI NON ABONNÉ
    # ==========================================
    
    # 1. Grille principale : Formulaire d'achat à gauche, Aperçu & Avis à droite
    col_pay, col_prev = st.columns([1, 1.2], gap="large")
    
    with col_pay:
        st.markdown("""
        <div class="paywall-container">
            <h2>🔒 Accès Premium</h2>
            <p>Débloquez la puissance totale de notre simulateur financier.</p>
            <div class="pricing-card" style="margin: 20px 0;">
                <h3>Abonnement Mensuel</h3>
                <div class="pricing-price">9.00€ <span style="font-size: 16px; color: #6c757d;">/ mois</span></div>
                <ul class="pricing-features">
                    <li>Simulations illimitées</li>
                    <li>Graphes comparatifs avancés</li>
                    <li>Exports PDF haute résolution</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulaire de paiement
        email_input = st.text_input("📧 Saisissez votre adresse email pour commencer :", key="email_paywall")
        if email_input:
            st.session_state["email"] = email_input
            if valider_email(email_input):
                if st.button("💳 S'abonner et Débloquer maintenant"):
                    checkout_url = creer_session_paiement()
                    if checkout_url:
                        st.markdown(f'<a href="{checkout_url}" target="_blank"><button style="background-color: #635bff; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 16px;">Aller vers la page de paiement sécurisée 💳</button></a>', unsafe_allow_html=True)
                        st.caption("🔒 Paiement 100% sécurisé via Stripe. Facturation récurrente, annulation en 1 clic.")
            else:
                st.error("⚠️ Veuillez entrer une adresse email valide.")
                
        st.divider()
        
        # Section Témoignages
        st.markdown("### 💬 Ce qu'en disent nos utilisateurs")
        
        st.markdown("""
        <div style="background-color: #f1f3f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <p style="font-style: italic; margin-bottom: 5px;">"Cet outil m'a fait réaliser l'impact réel de l'inflation sur mon livret A. J'ai réajusté mes investissements immédiatement. Les 9€ sont rentabilisés au centuple !"</p>
            <strong style="color: #4b7bec;">— Thomas R., Entrepreneur</strong>
        </div>
        <div style="background-color: #f1f3f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <p style="font-style: italic; margin-bottom: 5px;">"Les graphiques comparatifs sont ultra clairs. L'export PDF est parfait pour faire des points financiers en famille."</p>
            <strong style="color: #00d4b2;">— Sarah M., Cadre Financier</strong>
        </div>
        """, unsafe_allow_html=True)

    with col_prev:
        st.markdown("### 🔍 Aperçu de votre espace Premium")
        st.caption("Abonnez-vous à gauche pour interagir avec ce graphique et modifier les données.")
        
        # Génération d'un graphique factice flouté pour donner envie
        data_preview = pd.DataFrame({
            "Année": list(range(1, 16)),
            "Scénario Standard (3%)": [10000 * (1.03**i) for i in range(1, 16)],
            "Scénario Dynamique (6%)": [10000 * (1.06**i) for i in range(1, 16)],
            "Inflation Réelle": [10000 * (0.975**i) for i in range(1, 16)]
        }).set_index("Année")
        
        # Conteneur flouté en CSS
        st.markdown('<div class="blur-preview">', unsafe_allow_html=True)
        
        # Rendu visuel de la simulation bloquée
        st.info("💡 Exemple d'analyse générée pour un capital de 10 000 €")
        st.line_chart(data_preview)
        
        # Simulation de tableau
        st.dataframe(data_preview.tail(5))
        
        st.markdown('</div>', unsafe_allow_html=True)











