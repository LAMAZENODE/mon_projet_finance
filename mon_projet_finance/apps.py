import os
import streamlit as st
import stripe

# Configuration sécurisée via les Secrets de Streamlit
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ID_PRIX_STRIPE = os.environ.get("STRIPE_PRICE_ID")

# Configuration de la page avec un style Premium
st.set_page_config(page_title="Calculateur Financier Premium", page_icon="💰", layout="wide")

# CSS Custom pour injecter du design haut de gamme (Effet flou, badges, cartes)
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
        filter: blur(5px);
        opacity: 0.4;
        pointer-events: none;
        user-select: none;
    }
    .feature-box {
        padding: 15px;
        border-left: 4px solid #00D4B2;
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
        transition: transform 0.2s;
    }
    .stripe-button:hover {
        transform: translateY(-2px);
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

# Barre latérale - Statut pro
st.sidebar.markdown("### 🔒 Espace Client")
if st.session_state["est_abonne"]:
    st.sidebar.success("🟢 Membre Pro Actif")
else:
    st.sidebar.warning("⚡ Version Gratuite / Limitée")

# Logique de calcul
def calculer_epargne(capital_initial, versement_mensuel, taux_annuel, annees):
    capital = capital_initial
    taux_mensuel = (taux_annuel / 100) / 12
    historique = []
    for mois in range(1, (annees * 12) + 1):
        capital += versement_mensuel
        capital += capital * taux_mensuel
        if mois % 12 == 0:
            historique.append({"Année": mois // 12, "Capital Cumulé (€)": round(capital, 2)})
    return historique

# --- INTERFACE UTILISATEUR ---

# En-tête de marque
st.markdown('<div class="premium-badge">✨ ACCÈS PRIVÉ</div>', unsafe_allow_html=True)
st.title("Calculateur Financier Premium 🧠")
st.subheader("Optimisez vos investissements et simulez vos intérêts composés en temps réel.")

st.divider()

if st.session_state["est_abonne"]:
    # Interface Débloquée
    st.success("🔓 Contenu Premium Débloqué")
    with st.form("form_calcul"):
        col1, col2 = st.columns(2)
        with col1:
            initial = st.number_input("Capital Initial (€)", value=5000, min_value=0)
            mensuel = st.number_input("Versement Mensuel (€)", value=200, min_value=0)
        with col2:
            taux = st.number_input("Taux Annuel Estimé (%)", value=5.0, step=0.1, min_value=0.0)
            annees = st.number_input("Durée de la simulation (Années)", value=15, min_value=1, max_value=50)
        
        bouton_calcul = st.form_submit_button("Lancer la simulation haute précision")

    if bouton_calcul:
        resultats = calculer_epargne(initial, mensuel, taux, annees)
        st.write("### 📈 Votre trajectoire financière")
        st.line_chart(data=[r["Capital Cumulé (€)"] for r in resultats])
        st.dataframe(resultats, use_container_width=True)

else:
    # PAGE DE VENTE & TEASER (PAYWALL PREMIUM)
    col_gauche, col_droite = st.columns([3, 2], gap="large")
    
    with col_gauche:
        st.markdown("### 👀 Aperçu de l'outil")
        # On simule l'interface floutée derrière pour créer de la frustration positive
        st.markdown('<div class="blur-preview">', unsafe_allow_html=True)
        st.number_input("Capital Initial (€)", value=10000, disabled=True, key="preview_1")
        st.number_input("Versement Mensuel (€)", value=500, disabled=True, key="preview_2")
        st.button("Lancer la simulation", disabled=True, key="preview_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### ⭐ Témoignages de nos membres")
        st.caption("« Grâce à la précision de l'outil, j'ai pu restructurer mon épargne mensuelle et identifier 340€ de gains passifs cachés par an. » — *Thomas D., Investisseur Particulier*")

    with col_droite:
        st.markdown('<div class="paywall-container">', unsafe_allow_html=True)
        st.markdown("### 🚀 Débloquez la Version Pro")
        st.markdown("<h2 style='color:#635bff; margin:0;'>9,00 € <span style='font-size:16px; color:#6c757d;'>/ mois</span></h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#495057; font-size:14px; margin-bottom:20px;'>Sans engagement. Annulez à tout moment.</p>", unsafe_allow_html=True)
        
        # Liste des bénéfices bien marketée
        st.markdown("""
            <div class="feature-box" style="text-align:left;">🎯 <b>Simulations Précises</b> au mois près</div>
            <div class="feature-box" style="text-align:left;">📈 <b>Graphiques Interactifs</b> d'intérêts composés</div>
            <div class="feature-box" style="text-align:left;">💎 <b>Zéro Publicité</b>, code ultra-rapide</div>
            <div class="feature-box" style="text-align:left;">🛠 <b>Support Prioritaire</b> sous 24h</div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Génération du bouton Stripe de manière sécurisée
        if st.button("S'abonner et Accéder Immédiatement", use_container_width=True, type="primary"):
            try:
                session_checkout = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price': ID_PRIX_STRIPE, 'quantity': 1}],
                    mode='subscription',
                    success_url="http://localhost:8501/?success=true",
                    cancel_url="http://localhost:8501/?success=false",
                    customer_email=st.session_state["email"]
                )
                # Vrai bouton au style Stripe
                st.markdown(f'<div style="text-align:center; margin-top:15px;"><a class="stripe-button" href="{session_checkout.url}" target="_blank">💳 Continuer vers Stripe Secure</a></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Erreur de connexion avec Stripe. Vérifiez vos clés API.")
        
        st.markdown("""
            <div class="security-banner">
                🔒 Paiement 100% sécurisé via <b>Stripe</b><br>
                Chiffrement SSL 256 bits. Vos données bancaires ne sont jamais sauvegardées.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)











