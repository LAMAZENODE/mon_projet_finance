import os
import streamlit as st
import stripe
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Configuration sécurisée via les Secrets de Streamlit
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ID_PRIX_STRIPE = os.environ.get("STRIPE_PRICE_ID")

# Configuration de la page Premium
st.set_page_config(page_title="Calculateur Financier Premium", page_icon="💰", layout="wide")

# CSS Custom de l'interface de vente et design Premium
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

# --- MOTEUR FINANCIER AVANCÉ AVEC INFLATION ---
def simuler_scenario_inflation(initial, mensuel, taux_nominal, inflation, annees):
    capital_nominal = initial
    capital_reel = initial
    
    taux_mensuel_nominal = (taux_nominal / 100) / 12
    # Formule du taux d'intérêt réel net d'inflation (Fisher)
    taux_reel_annuel = ((1 + taux_nominal/100) / (1 + inflation/100) - 1) * 100
    taux_mensuel_reel = (taux_reel_annuel / 100) / 12
    
    historique = []
    for mois in range(1, (annees * 12) + 1):
        # Calcul de la valeur brute (Nominale)
        capital_nominal += mensuel
        capital_nominal += capital_nominal * taux_mensuel_nominal
        
        # Calcul de la valeur ajustée du pouvoir d'achat (Réelle)
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

# --- FONCTION DE GÉNÉRATION DU RAPPORT PDF ---
def generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation):
    buffer = BytesIO()
    plt.figure(figsize=(10, 6))
    
    # On trace les courbes réelles (ajustées de l'inflation) pour le PDF
    plt.plot(df_a.index, df_a["Pouvoir d'Achat Réel (€)"], label="Scénario A (Réel)", color="#ff4b4b", linewidth=2)
    plt.plot(df_b.index, df_b["Pouvoir d'Achat Réel (€)"], label="Scénario B (Réel)", color="#ffa500", linewidth=2)
    plt.plot(df_c.index, df_c["Pouvoir d'Achat Réel (€)"], label="Scénario C (Réel)", color="#00d4b2", linewidth=2)
    
    plt.title(f"Rapport de Performance Financière (Ajusté de l'inflation : {inflation}%)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Années", fontsize=11)
    plt.ylabel("Valeur de l'épargne (€)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    
    # Ajout des métadonnées en texte sur le graphique
    texte_info = f"Capital Initial : {initial} €\nEffort Mensuel : {mensuel} €\nInflation annuelle : {inflation}%"
    plt.gcf().text(0.15, 0.2, texte_info, fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#e9ecef'))
    
    plt.tight_layout()
    plt.savefig(buffer, format="pdf", dpi=300)
    plt.close()
    buffer.seek(0)
    return buffer

# --- INTERFACE UTILISATEUR ---

st.markdown('<div class="premium-badge">✨ VERSION 2.0 ULTIME</div>', unsafe_allow_html=True)
st.title("Simulateur d'Épargne Haute Précision 🧠")
st.subheader("Analysez la perte de pouvoir d'achat liée à l'inflation et téléchargez votre rapport.")

st.divider()

if st.session_state["est_abonne"]:
    # --- INTERFACE DÉBLOQUÉE (MEMBRES) ---
    st.success("🔓 Accès Premium Activé — Rapports PDF et Inflation débloqués")
    
    # Paramètres macro-économiques globaux
    col_g, col_m, col_d = st.columns(3)
    with col_g:
        initial = st.number_input("Capital Initial (€)", value=10000, min_value=0, step=1000)
    with col_m:
        mensuel = st.number_input("Versement Mensuel (€)", value=250, min_value=0, step=50)
    with col_d:
        # L'argument massue : l'inflation ajustable
        inflation = st.number_input("Taux d'Inflation Annuel Estimé (%)", value=2.5, step=0.1, min_value=0.0)
    
    annees = st.slider("Horizon d'investissement (Années)", min_value=2, max_value=40, value=15)
    
    st.markdown("### 📊 Configuration des stratégies et rendements nominaux")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<h5 style='color:#ff4b4b;'>📉 Scénario A (Prudent)</h5>", unsafe_allow_html=True)
        taux_a = st.number_input("Rendement Annuel A (%)", value=3.0, step=0.1, key="t_a")
    with c2:
        st.markdown("<h5 style='color:#ffa500;'>⚖️ Scénario B (Équilibré)</h5>", unsafe_allow_html=True)
        taux_b = st.number_input("Rendement Annuel B (%)", value=5.5, step=0.1, key="t_b")
    with c3:
        st.markdown("<h5 style='color:#00d4b2;'>📈 Scénario C (Dynamique)</h5>", unsafe_allow_html=True)
        taux_c = st.number_input("Rendement Annuel C (%)", value=8.5, step=0.1, key="t_c")
    
    # Génération des DataFrames individuels
    df_a = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_a, inflation, annees)).set_index("Année")
    df_b = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_b, inflation, annees)).set_index("Année")
    df_c = pd.DataFrame(simuler_scenario_inflation(initial, mensuel, taux_c, inflation, annees)).set_index("Année")
    
    # Fusion des données pour l'affichage graphique global du Pouvoir d'Achat Réel
    df_comparatif_reel = pd.DataFrame({
        "Année": list(range(1, annees + 1)),
        "Scénario A (Pouvoir d'achat réel)": df_a["Pouvoir d'Achat Réel (€)"],
        "Scénario B (Pouvoir d'achat réel)": df_b["Pouvoir d'Achat Réel (€)"],
        "Scénario C (Pouvoir d'achat réel)": df_c["Pouvoir d'Achat Réel (€)"]
    }).set_index("Année")
    
    # Rendu du graphique Principal
    st.markdown("### 📈 Trajectoire de votre Pouvoir d'Achat Réel (Net d'Inflation)")
    st.line_chart(df_comparatif_reel)
    
    # SECTION D'EXPORT EXCLUSIVE
    st.markdown("### 📥 Outils d'export professionnels")
    pdf_file = generer_pdf(df_a, df_b, df_c, initial, mensuel, inflation)
    
    st.download_button(
        label="📥 Télécharger le Rapport d'Analyse au format PDF",
        data=pdf_file,
        file_name="rapport_simulation_premium.pdf",
        mime="application/pdf",
        type="primary"
    )
    
    # Affichage technique détaillé sous forme d'onglets
    st.markdown("### 📋 Tableaux de bord détaillés par stratégie")
    tab1, tab2, tab3 = st.tabs(["📉 Prudent (A)", "⚖️ Équilibré (B)", "📈 Dynamique (C)"])
    with tab1:
        st.dataframe(df_a, use_container_width=True)
    with tab2:
        st.dataframe(df_b, use_container_width=True)
    with tab3:
        st.dataframe(df_c, use_container_width=True)

else:
    # --- INTERFACE TEASER PRO (PAYWALL MARKETING) ---
    col_gauche, col_droite = st.columns([1.2, 1], gap="large")
    
    with col_gauche:
        st.markdown("### 👀 Aperçu du moteur d'impact de l'inflation")
        
        # Teaser flouté montrant le split entre Valeur brute et Pouvoir d'Achat Réel
        st.markdown('<div class="blur-preview">', unsafe_allow_html=True)
        preview_df = pd.DataFrame({
            "Année": list(range(1, 11)),
            "Capital Brute (Fictif)": [10000 + (i*3000)*1.06**i for i in range(1, 11)],
            "Pouvoir d'Achat Réel détruit par l'Inflation": [10000 + (i*3000)*1.02**i for i in range(1, 11)]
        }).set_index("Année")
        st.line_chart(preview_df)
        st.button("Générer le Rapport PDF", disabled=True, key="btn_pdf_dis")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### ⚠️ Le piège invisible de l'inflation")
        st.markdown("Avec une inflation moyenne à **2.5%**, un capital de **50 000 €** laissé sur un compte mal rémunéré perd plus de **13 500 € de pouvoir d'achat** en 10 ans. Notre outil calcule l'impact exact mois par mois pour vous éviter cela.")

    with col_droite:
        st.markdown('<div class="paywall-container">', unsafe_allow_html=True)











