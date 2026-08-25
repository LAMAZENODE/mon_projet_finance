import os
import streamlit as st
import stripe

# Configuration sécurisée via les Secrets de Streamlit
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ID_PRIX_STRIPE = os.environ.get("STRIPE_PRICE_ID")

# Titre et style de la page
st.set_page_config(page_title="Calculateur Financier Premium", page_icon="💰")
st.title("Calculateur Financier Premium")

# Simulation de la session utilisateur
if "est_abonne" not in st.session_state:
    st.session_state["est_abonne"] = False
if "email" not in st.session_state:
    st.session_state["email"] = "test@exemple.com"

# Gestion du retour de paiement Stripe (Query Parameters)
query_params = st.query_params
if "success" in query_params and query_params["success"] == "true":
    st.session_state["est_abonne"] = True
    st.success("🎉 Votre abonnement a bien été activé ! Merci pour votre confiance.")
    st.query_params.clear()

# Affichage du statut de l'abonnement
if st.session_state["est_abonne"]:
    st.sidebar.success("🟢 Abonnement Actif")
else:
    st.sidebar.error("🔴 Accès Bloqué")

# Fonction de calcul financier
def calculer_epargne(capital_initial, versement_mensuel, taux_annuel, annees):
    capital = capital_initial
    taux_mensuel = (taux_annuel / 100) / 12
    mois_totaux = annees * 12
    historique = []
    for mois in range(1, mois_totaux + 1):
        capital += versement_mensuel
        interets_du_mois = capital * taux_mensuel
        capital += interets_du_mois
        if mois % 12 == 0:
            historique.append({"annee": mois // 12, "total": round(capital, 2)})
    return historique

# Interface conditionnelle
if st.session_state["est_abonne"]:
    st.subheader("Simulateur d'Épargne")
    
    # Formulaire Streamlit
    with st.form("form_calcul"):
        initial = st.number_input("Capital Initial (€)", value=1000, min_value=0)
        mensuel = st.number_input("Versement Mensuel (€)", value=1000, min_value=0)
        taux = st.number_input("Taux Annuel (%)", value=3.5, step=0.1, min_value=0.0)
        annees = st.number_input("Durée (Années)", value=10, min_value=1, max_value=50)
        
        soumis = st.form_submit_button("Calculer l'Épargne")
    
    if soumis:
        resultats = calculer_epargne(initial, mensuel, taux, annees)
        st.subheader("📊 Vos Résultats :")
        for r in resultats:
            st.write(f"📅 Année {r['annee']} : **{r['total']:,} €**")

else:
    st.info("💡 Débloquez cet outil pour tester vos simulations financières.")
    
    # Bouton de paiement Stripe
    if st.button("S'abonner maintenant", type="primary"):
        # Détection dynamique de l'URL de l'application en cours d'exécution
        # Pour Streamlit en production, l'idéal est de définir l'URL finale manuellement ou via les paramètres
        url_de_base = "https://streamlit.app" 
        
        try:
            session_checkout = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': ID_PRIX_STRIPE,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_de_base + "?success=true",
                cancel_url=url_de_base,
                customer_email=st.session_state["email"]
            )
            # Redirection vers la page de paiement Stripe
            st.link_button("Accéder au paiement sécurisé Stripe 💳", session_checkout.url)
        except Exception as e:
            st.error(f"Erreur lors de la création de la session Stripe : {e}")









