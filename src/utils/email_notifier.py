import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


def send_price_alert(
    card_name: str,
    cardmarket_price: float,
    vinted_price: float,
    vinted_url: str,
    difference: float,
) -> bool:
    """
    Envoie une alerte par email quand un prix Vinted est inférieur au prix Cardmarket
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_from_email
        msg["To"] = settings.notification_email
        msg["Subject"] = f"🎴 Alerte prix Lorcana - {card_name}"

        body = f"""
        <html>
        <body>
            <h2>Alerte de prix pour {card_name}</h2>
            <p>Une offre moins chère a été trouvée sur Vinted !</p>
            <ul>
                <li>Prix Cardmarket : {cardmarket_price:.2f}€</li>
                <li>Prix Vinted : {vinted_price:.2f}€</li>
                <li>Différence : {difference:.2f}€ ({(difference/cardmarket_price*100):.1f}%)</li>
            </ul>
            <p><a href="{vinted_url}">Voir l'annonce sur Vinted</a></p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port) as server:
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        logger.info(f"Email d'alerte envoyé pour {card_name}")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        return False
