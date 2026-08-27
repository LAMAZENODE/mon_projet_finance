# --- INTERFACE UTILISATEUR ---

# Cas 1 : Utilisateur remboursé -> BLOQUÉ
if est_rembourse:
    st.error("❌ Accès révoqué.")
    st.subheader(f"L'adresse e-mail {email_eleve} a été définitivement bloquée.")
    st.write("Suite à votre demande de remboursement, votre accès au Tuteur IA a été clôturé.")
    st.stop()

# Cas 2 : Utilisateur non payé -> PAGE DE VENTE
elif not est_abonne:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📐 Tuteur Privé de Mathématiques IA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #4B5563;'>Progressez en maths 10x plus vite avec votre coach disponible 24h/24.</p>", unsafe_allow_html=True)
    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🎯 **Précision 99%**")
        st.caption("Corrections étape par étape adaptées à votre niveau scolaire.")
    with col2:
        st.markdown("⚡ **Instantané**")
        st.caption("Plus besoin d'attendre. Réponses claires en moins de 3 secondes.")
    with col3:
        st.markdown("🔒 **Accès Unique**")
        st.caption("Un seul paiement de 5€. Aucun abonnement, aucun frais caché.")

    st.write("---")

    # Affichage des informations du produit
    with st.expander("🔍 Détails du paiement (mode test)"):
        st.info(f"""
        **Produit**: prod_V4aMSxA92kIcCt
        **Tarif**: price_1U4RBaAGivtq6O4IE1gyxeyt
        **Prix**: 5,00 €
        **Mode**: {'TEST' if MODE_TEST else 'PRODUCTION'}
        """)

    # ✅ CORRECTION ICI - Utilisation de guillemets simples pour éviter les conflits
    st.markdown(
        '<div style="background-color: #F3F4F6; padding: 20px; border-radius: 10px; border-left: 5px solid #10B981; margin-bottom: 20px;">'
        '<h4 style="margin: 0; color: #111827;">🚀 Offre Spéciale d\'Accès Unique</h4>'
        '<p style="font-size: 1.8em; font-weight: bold; margin: 10px 0; color: #10B981;">5,00 € <span style="font-size: 0.5em; color: #6B7280; font-weight: normal;">paiement unique (accès immédiat)</span></p>'
        '<ul style="margin-bottom: 0; padding-left: 20px; color: #374151;">'
        '<li>Accès complet au tuteur IA 24h/24 et 7j/7</li>'
        '<li>Explications détaillées de TOUS vos exercices de maths</li>'
        '<li>Garantie satisfait ou remboursé sous 14 jours (si non utilisé)</li>'
        '<li><b>Nouveau :</b> Téléchargement des corrections au format PDF</li>'
        '</ul>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("💳 Débloquer mon Tuteur IA (Paiement unique 5€)", use_container_width=True, type="primary"):
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[{'price': ID_PRIX_UNIQUE, 'quantity': 1}],
                mode='payment',
                success_url=f"{URL_APP}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=URL_APP,
            )
            
            st.markdown(f"### [🔗 Cliquez ici pour finaliser le paiement sécurisé]({checkout_session.url})")
            st.caption("🔒 Transaction 100% sécurisée par Stripe. Vos données bancaires sont cryptées.")
            
            # Afficher l'URL de la session pour débogage
            if MODE_TEST:
                with st.expander("🔧 Informations de débogage"):
                    st.code(f"""
                    Session ID: {checkout_session.id}
                    URL de paiement: {checkout_session.url}
                    Price ID utilisé: {ID_PRIX_UNIQUE}
                    Mode: TEST
                    """)
            
            # ✅ CORRECTION ICI - Même problème avec les guillemets
            st.markdown(
                '<p style="font-size: 0.8em; color: #9CA3AF; text-align: center; margin-top: 10px;">'
                'Conformément à la loi sur les contenus numériques, en soumettant votre premier exercice, '
                'vous demandez l\'exécution immédiate du service et renoncez expressément à votre droit de rétractation.'
                '</p>', 
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la création du paiement : {e}")
            if MODE_TEST:
                st.error(f"Détails de l'erreur : {str(e)}")

    st.write("---")
    st.markdown("##### ⭐ Ce que disent nos étudiants :")
    st.info('"Grâce à cette IA, je suis passé de 9 à 14 de moyenne en maths en seulement un mois. Les explications sont hyper claires !" – Thomas, élève de Première.')

# Cas 3 : Utilisateur payé -> ACCÈS DÉBLOQUÉ
else:
    if MODE_TEST:
        st.info("🔬 **MODE TEST** - Les paiements sont simulés")
    
    st.markdown("<h1 style='text-align: center; color: #10B981;'>🎓 Votre Espace Tuteur Privé</h1>", unsafe_allow_html=True)
    
    if MODE_TEST:
        st.success(f"✅ Accès Test Activé pour **{email_eleve}**")
        st.caption("💡 En mode test, vous pouvez utiliser toutes les fonctionnalités gratuitement")
    else:
        st.success(f"✨ Accès Premium Activé pour **{email_eleve}**. Posez toutes vos questions ici.")
    
    exercice = st.text_area("✍️ Soumettez votre exercice et votre niveau scolaire (ex: 3ème, Terminale, etc.) :", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        bouton_correction = st.button("🚀 Obtenir la correction détaillée", type="primary", use_container_width=True)
    
    if bouton_correction and exercice.strip():
        with st.spinner("🔮 Votre tuteur IA analyse le problème et rédige la correction étape par étape..."):
            try:
                instructions = (
                    "Tu es un tuteur privé de mathématiques hautement qualifié, pédagogue et bienveillant. "
                    "Ton but est d'aider l'élève à comprendre son exercice, pas seulement de lui donner la réponse brute. "
                    "1. Salue brièvement l'élève de manière encourageante.\n"
                    "2. Rappelle brièvement les propriétés ou formules mathématiques nécessaires pour résoudre le problème.\n"
                    "3. Propose une correction extrêmement détaillée, rédigée étape par étape.\n"
                    "4. Utilise un langage clair, accessible et structure tes calculs avec une mise en forme soignée.\n"
                    "5. Termine par un petit conseil ou un mot d'encouragement pour ses révisions."
                )
                
                reponse_ia = client_ia.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=exercice,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.3
                    )
                )
                
                st.session_state['derniere_correction'] = reponse_ia.text
                st.session_state['dernier_enonce'] = exercice
                
                st.success("✅ Correction générée avec succès !")
                st.markdown(reponse_ia.text)
                
                # Bouton de téléchargement PDF
                pdf_buffer = generer_pdf(reponse_ia.text, exercice)
                st.download_button(
                    label="📥 Télécharger la correction en PDF",
                    data=pdf_buffer,
                    file_name="correction_maths.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as api_error:
                st.error(f"❌ Erreur lors de l'appel à l'IA : {api_error}")
    elif bouton_correction:
        st.warning("⚠️ Veuillez écrire ou coller un énoncé d'exercice avant de lancer l'analyse.")










