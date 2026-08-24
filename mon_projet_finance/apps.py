import os
from flask import Flask, redirect, render_template_string, request

import stripe

app = Flask(__name__)

# Configuration 100% sécurisée pour GitHub public
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ID_PRIX_STRIPE = os.environ.get("STRIPE_PRICE_ID")


# Simulation Base de Données
utilisateur_connecte = {
    "email": "test@exemple.com",
    "est_abonne": False
}

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

PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Calculateur Financier Premium</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; }
        .container { max-width: 500px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        .badge { color: white; padding: 5px 10px; border-radius: 4px; font-size: 14px; float: right; }
        .badge.bloque { background: #e74c3c; }
        .badge.actif { background: #2ecc71; }
        label { display: block; margin-top: 10px; font-weight: bold; }
        input { width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; }
        button { background-color: #2ecc71; color: white; border: none; padding: 10px 15px; margin-top: 15px; width: 100%; cursor: pointer; font-size: 16px; border-radius: 5px; }
        .pay-box { background-color: #ebf5fb; border: 2px dashed #3498db; padding: 15px; border-radius: 5px; margin-top: 20px; text-align: center; }
        .btn-pay { background-color: #3498db; }
        .resultats { margin-top: 20px; background: #f9f9f9; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>
            Calculateur Premium
            {% if abonne %}
                <span class="badge actif">Abonnement Actif</span>
            {% else %}
                <span class="badge bloque">Accès Bloqué</span>
            {% endif %}
        </h2>

        {% if abonne %}
            <form method="POST" action="/calculer">
                <label>Capital Initial (€) :</label>
                <input type="number" name="initial" value="1000" required>
                
                <label>Versement Mensuel (€) :</label>
                <input type="number" name="mensuel" value="1000" required>
                
                <label>Taux Annuel (%) :</label>
                <input type="number" step="0.1" name="taux" value="3.5" required>
                
                <label>Durée (Années) :</label>
                <input type="number" name="annees" value="10" required>
                
                <button type="submit">Calculer l'Épargne</button>
            </form>

            {% if resultats %}
                <div class="resultats">
                    <h3>Vos Résultats :</h3>
                    <ul>
                    {% for r in resultats %}
                        <li>Année {{ r.annee }} : <strong>{{ r.total }} €</strong></li>
                    {% endfor %}
                    </ul>
                </div>
            {% endif %}
        {% else %}
            <div class="pay-box">
                <p>Débloquez cet outil pour tester vos simulations financières.</p>
                <form method="POST" action="/creer-session-paiement">
                    <button type="submit" class="btn-pay">S'abonner maintenant</button>
                </form>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(PAGE_HTML, abonne=utilisateur_connecte["est_abonne"], resultats=None)

@app.route('/calculer', methods=['POST'])
def calculer():
    if not utilisateur_connecte["est_abonne"]:
        return redirect('/')
    
    initial = float(request.form['initial'])
    mensuel = float(request.form['mensuel'])
    taux = float(request.form['taux'])
    annees = int(request.form['annees'])
    
    res = calculer_epargne(initial, mensuel, taux, annees)
    return render_template_string(PAGE_HTML, abonne=True, resultats=res)

@app.route('/creer-session-paiement', methods=['POST'])
def creer_session():
    # URL de votre site (s'adapte automatiquement une fois en ligne)
    domaine = request.url_root
    try:
        session_checkout = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': ID_PRIX_STRIPE,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=domaine + 'succes?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domaine,
            customer_email=utilisateur_connecte["email"]
        )
        return redirect(session_checkout.url, code=303)
    except Exception as e:
        return str(e), 400

@app.route('/succes')
def succes():
    # Ici, Stripe a validé le paiement. On passe l'utilisateur en abonné.
    utilisateur_connecte["est_abonne"] = True
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)







