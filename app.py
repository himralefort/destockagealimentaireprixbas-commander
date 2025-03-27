from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
import logging
import os 
# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'a0365944c4029819074695803944e2f2b05f0c17f10fa575eab73911fd885b83:'  # Clé secrète pour les sessions

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Fonction pour formater les montants en nombres flottants
def format_amount(amount):
    if isinstance(amount, str):
        amount = amount.replace('€', '').replace(' ', '').strip()
        amount = amount.replace(',', '.')
        if amount.endswith('.'):
            amount = amount[:-1]
        return float(amount)
    return float(amount)

# Fonction pour formater les montants en chaîne de caractères (format monétaire)
def format_amount_str(amount):
    return f"{amount:,.2f} €".replace(',', ' ').replace('.', ',').replace(' ', '.')

# Route pour la page d'accueil
@app.route('/')
def index():
    # Initialiser les données de commande dans la session
    session['order_data'] = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "billing_address": "",
        "quantity": 1,
        "subtotal": format_amount_str(257.00),  # Sous-total initial
        "delivery_cost": format_amount_str(59.99),  # Frais de livraison initiaux
        "discount": format_amount_str(0.00),  # Réduction initiale
        "final_total": format_amount_str(316.99),  # Total initial
        "montant_total": format_amount_str(316.99),  # Montant total initial
        "note": "",
        "payment_method": "",
        "cardholder_name": "",
        "card_number": "",
        "expiry_date": "",
        "cvv": "",
        "installment_plan": "",
        "product_name": "Lot de 10 unités de foie gras Labeyrie 285g",
        "payment_date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    logging.debug("Session initialisée : %s", session['order_data'])
    return render_template('validation.html', data=session.get('order_data'))

# Route pour traiter la commande (GET et POST)
@app.route('/commander', methods=['GET', 'POST'])
def commander():
    if request.method == 'POST':
        try:
            # Récupérer et mettre à jour les données du formulaire
            order_data = session.get('order_data', {})
            logging.debug("Données du formulaire reçues : %s", request.form)

            # Mettre à jour les données de la commande avec les valeurs du formulaire
            order_data.update({
                "first_name": request.form.get("first-name", ""),
                "last_name": request.form.get("last-name", ""),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
                "address": request.form.get("address", ""),
                "billing_address": request.form.get("billing-address", ""),
                "quantity": int(request.form.get("quantity", 1)),
                "subtotal": request.form.get("subtotal", "0,00 €"),
                "delivery_cost": request.form.get("delivery-cost", "0,00 €"),
                "discount": request.form.get("discount", "0,00 €"),
                "final_total": request.form.get("final-total", "0,00 €"),
                "note": request.form.get("note", ""),
                "payment_method": request.form.get("payment-method", ""),
            })

            # Convertir les montants en nombres pour les calculs
            order_data["subtotal"] = format_amount(order_data["subtotal"])
            order_data["delivery_cost"] = format_amount(order_data["delivery_cost"])
            order_data["discount"] = format_amount(order_data["discount"])
            order_data["final_total"] = format_amount(order_data["final_total"])

            # Recalculer le total si nécessaire
            order_data["final_total"] = order_data["subtotal"] + order_data["delivery_cost"] - order_data["discount"]

            # Synchroniser montant_total avec final_total
            order_data["montant_total"] = order_data["final_total"]

            # Mettre à jour les données dans la session
            session['order_data'] = order_data
            logging.debug("Données de commande mises à jour dans /commander : %s", session['order_data'])

            # Rediriger vers /confirmation après la mise à jour des données
            return redirect(url_for('confirmation'))

        except Exception as e:
            logging.error("Erreur lors de la mise à jour des données : %s", e)
            return "Une erreur s'est produite lors du traitement de votre demande.", 500

    return render_template('confirmation.html', data=session.get('order_data'))

# Route pour la page de confirmation
@app.route('/confirmation')
def confirmation():
    # Récupérer les données de la session
    order_data = session.get('order_data', {})
    logging.debug("Données de la session dans /confirmation : %s", order_data)

    if not order_data:
        logging.warning("Aucune donnée de commande trouvée dans la session. Redirection vers /commander.")
        return redirect(url_for('commander'))  # Rediriger vers /commander

    return render_template('confirmation.html', data=order_data)

# Route pour le paiement en plusieurs fois
@app.route('/jumeler', methods=['GET', 'POST'])
def jumeler():
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            order_data = {
                "first_name": request.form.get("first-name", ""),
                "last_name": request.form.get("last-name", ""),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
                "address": request.form.get("address", ""),
                "billing_address": request.form.get("billing-address", ""),
                "quantity": int(request.form.get("quantity", 1)),
                "subtotal": request.form.get("subtotal", "0,00 €"),
                "delivery_cost": request.form.get("delivery-cost", "0,00 €"),
                "discount": request.form.get("discount", "0,00 €"),
                "final_total": request.form.get("final-total", "0,00 €"),
                "montant_total": request.form.get("montant-total", "0,00 €"),
                "note": request.form.get("note", ""),
                "payment_method": request.form.get("payment-method", ""),
                "cardholder_name": request.form.get("cardholder-name", ""),
                "installment_plan": request.form.get("installment-plan", ""),
            }

            # Stocker les données dans la session
            session['order_data'] = order_data
            logging.debug("Données de commande mises à jour dans /jumeler : %s", session['order_data'])

            # Rediriger vers jumeler.html
            return redirect(url_for('jumeler'))

        except Exception as e:
            logging.error("Erreur lors de la récupération des données du formulaire : %s", e)
            return "Une erreur s'est produite lors du traitement de votre demande.", 500

    # Récupérer les données de la session
    order_data = session.get('order_data', {})
    return render_template('jumeler.html', data=order_data)

# Point d'entrée de l'application
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5015))  # Utilise le port de Render ou 5015 en local
    app.run(host='0.0.0.0', port=port, debug=True)
