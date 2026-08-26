import os
import streamlit as st
import stripe
import pandas as pd

# Configuration sécurisée via les Secrets de Streamlit
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ID_PRIX_STRIPE = os.environ.get("STRIPE_PRICE_ID")

# Configuration de la page avec un style Premium
st.set_page_config(page_title="Calculateur Financier Premium", page_icon="💰", layout="wide")

# CSS Custom pour injecter du design haut de gamme
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
    }
    .blur-preview {
        filter: blur(6px);
        opacity: 0.35;
        pointer-events: none;
        user-select: none;
    }
    .feature-box {
        padding: 12px;
        border-left: 4px solid #635bff;
        background: #ffffff;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stripe-button {
        display: inline-block;
        background: linear-gradient(135deg, #635bff, #00d4b2);
        color: white !important;
        font-weight: bold;
        padding: 14px 28px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(99, 91, 255, 0.3);
    }
    .security-banner {
        margin-top: 15px;
        font-size: 13px;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

# Simulation de la session utilisateur
if "est_abonne" not in st.session_state:
    st.session_state["est_abonne"] = False
if "email" not in st.session_state:
    st.session_state["email"] = "client@exemple.com"

# Gestion du retour de paiement Stripe
query_params = st.query_params
if "success" in query_params and query_params["success"] == "true":
    st.session_state["est_abonne"] = True
    st.success("🎉 Votre abonnement a bien été activé ! Merci pour votre confiance.")
    st.query_params.clear()

# Barre latérale
st.sidebar.markdown("### 🔒 Espace Client")
if st.session_state["est_abonne"]:
    st.sidebar.success("🟢 Membre Pro Actif")
else:
    st.sidebar.warning("⚡ Version Gratuite / Limitée")

# Moteur de calcul financier capitalisé
def simuler_scenario(initial, mensuel, taux, annees):
    capital = initial
    taux_mensuel = (taux / 100) / 12
    historique = []
    for mois in range(1, (annees * 12) + 1):
        capital += mensuel
        capital += capital * taux_mensuel
        if mois % 12 == 0:
            historique.append(round(capital, 2))
    return historique

# --- INTERFACE UTILISATEUR ---

st.markdown('<div class="premium-badge">✨ MODE COMPARATEUR AVANCÉ</div>', unsafe_allow_html=True)
st.title("Simulateur Multi-Scénarios Professionnel 📊")
st.subheader("Comparez instantanément jusqu'à 3 stratégies d'investissement différentes.")

st.divider()

if st.session_state["est_abonne"]:
    # --- INTERFACE DEBLOQUEE (MEMBRES) ---
    st.success("🔓 Accès Premium Activé — Simulations Illimitées")
    
    # Paramètres globaux communs
    col_g, col_d = st.columns(2)
    with col_g:
        initial = st.number_input("Capital Initial global (€)", value=5000, min_value=0, step=500)
    with col_d:
        mensuel = st.number_input("Effort d'Épargne Mensuel (€)", value=300, min_value=0, step=50)
    
    annees = st.slider("Durée de la projection (Années)", min_value=2, max_value=40, value=20)
    
    st.markdown("### 🛠 Configurer vos 3 scénarios à comparer")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📉 Scénario A (Ex: Livret A)")
        taux_a = st.number_input("Taux Annuel A (%)", value=3.0, step=0.1, key="t_a")
    with c2:
        st.warning("⚖️ Scénario B (Ex: Assurance Vie)")
        taux_b = st.number_input("Taux Annuel B (%)", value=5.5, step=0.1, key="t_b")
    with c3:
        st.success("📈 Scénario C (Ex: ETF / PEA)")
        taux_c = st.number_input("Taux Annuel C (%)", value=8.5, step=0.1, key="t_c")
    
    # Calculs et construction du DataFrame pour affichage graphique
    data_scenarios = {
        "Année": list(range(1, annees + 1)),
        "Scénario A": simuler_scenario(initial, mensuel, taux_a, annees),
        "Scénario B": simuler_scenario(initial, mensuel, taux_b, annees),
        "Scénario C": simuler_scenario(initial, mensuel, taux_c, annees)
    }
    df = pd.DataFrame(data_scenarios).set_index("Année")
    
    # Rendu visuel Premium
    st.markdown("### 📈 Graphique comparatif des performances")
    st.line_chart(df)
    
    st.markdown("### 📋 Tableau de données détaillées")
    st.dataframe(df, use_container_width=True)

else:
    # --- INTERFACE TEASER PRO (PAYWALL) ---
    col_gauche, col_droite = st.columns([1.2, 1], gap="large")
    
    with col_gauche:
        st.markdown("### 👀 Aperçu du graphique comparatif multi-scénarios")
        
        # Effet frustration psychologique : Affichage d'un faux graphique flouté
        st.markdown('<div class="blur-preview">', unsafe_allow_html=True)
        # Données fictives fixes juste pour générer un beau graphique flou en arrière-plan
        preview_df = pd.DataFrame({
            "Année": list(range(1, 16)),
            "Livret Classique": [10000 + (i*1200)*1.02 for i in range(1, 16)],
            "Portefeuille Optimisé Pro": [10000 + (i*1200)*1.08**i for i in range(1, 16)]
        }).set_index("Année")
        st.line_chart(preview_df)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 💡 Pourquoi comparer vos scénarios ?")
        st.markdown("Une différence de seulement **2% de rendement** sur 15 ans peut représenter plus de **24 500 € de gains manqués**. Ne laissez plus votre argent dormir sans stratégie.")

    with col_droite:
        st.markdown('<div class="paywall-container">', unsafe_allow_html=True)
        st.markdown("### 🚀 Accédez au Comparateur Premium")
        st.markdown("<h2 style='color:#635bff; margin:0;'>9,00 € <span style='font-size:16px; color:#6c757d;'>/ mois</span></h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#495057; font-size:14px; margin-bottom:20px;'>Sans engagement. Résiliation en 1 clic.</p>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-box" style="text-align:left;">📊 <b>Superposition de 3 Scénarios</b> simultanés</div>
            <div class="feature-box" style="text-align:left;">🎛 <b>Curseur de Durée Dynamique</b> de 2 à 40 ans</div>
            <div class="feature-box" style="text-align:left;">📥 <b>Export des données</b> au format Excel/CSV</div>
            <div class="feature-box" style="text-align:left;">🔒 <b>Garantie Stripe Secure</b> : Zéro friction</div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Débloquer le Graphique Comparatif", use_container_width=True, type="primary"):
            try:
                session_checkout = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price': ID_PRIX_STRIPE, 'quantity': 1}],
                    mode='subscription',
                    success_url="http://localhost:8501/?success=true",
                    cancel_url="http://localhost:8501/?success=false",
                    customer_email=st.session_state["email"]
                )
                st.markdown(f'<div style="text-align:center; margin-top:15px;"><a class="stripe-button" href="{session_checkout.url}" target="_blank">💳 Finaliser sur Stripe Secure</a></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Erreur d'initialisation Stripe. Vérifiez vos clés d'API.")
        
        st.markdown("""
            <div class="security-banner">
                🔒 Technologie de paiement sécurisée par <b>Stripe</b><br>
                Conforme aux normes bancaires PCI-DSS.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)













