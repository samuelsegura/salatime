#!/usr/bin/env python3
"""
Système de notifications pour horaires de prière - CCIQ
Envoie une notification Telegram 10 minutes avant chaque Iqama
"""

import requests
import schedule 
import time
import re
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
os.environ['TZ'] = 'America/Montreal'
time.tzset()

# Charger les variables d'environnement
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ============================================
# FONCTION 1 : Récupérer les horaires
# ============================================
def get_prayer_times():
    """Scrape les horaires depuis mosqueprayertimes.com"""
    try:
        print('📡 Récupération des horaires depuis mosqueprayertimes.com...')
        
        response = requests.get('https://mosqueprayertimes.com/cciq2', timeout=10)
        html = response.text
        
        # Extraire la variable MPT avec regex
        mpt_match = re.search(r'MPT=\{([^}]+)\}', html)
        
        if not mpt_match:
            print('❌ Impossible de trouver les horaires dans la page')
            return None
        
        # Parser les données MPT
        mpt_data = {}
        entries = re.findall(r'(\d{8}):"([^"]+)"', mpt_match.group(1))
        
        for date_key, times_str in entries:
            mpt_data[date_key] = times_str
        
        # Obtenir les horaires d'aujourd'hui
        today = datetime.now()
        date_key = today.strftime('%Y%m%d')
        
        if date_key not in mpt_data:
            print(f'❌ Pas de données pour aujourd\'hui: {date_key}')
            return None
        
        # Décoder les horaires
        times = decode_prayer_times(mpt_data[date_key])
        
        print('✅ Horaires récupérés avec succès !')
        return times
        
    except Exception as e:
        print(f'❌ Erreur lors de la récupération: {e}')
        return None

# ============================================
# FONCTION 2 : Décoder la chaîne d'horaires
# ============================================
def decode_prayer_times(data):
    """Decode la chaîne encodée d'horaires"""
    def format_time(time_str):
        if not time_str or time_str == '0000':
            return None
        return f"{time_str[:2]}:{time_str[2:]}"
    
    return {
        'fajr': {
            'start': format_time(data[8:12]),
            'iqama': format_time(data[12:16])
        },
        'zuhr': {
            'start': format_time(data[20:24]),
            'iqama': format_time(data[24:28])
        },
        'asr': {
            'start': format_time(data[28:32]),
            'iqama': format_time(data[32:36])
        },
        'maghrib': {
            'start': format_time(data[36:40]),
            'iqama': format_time(data[40:44])
        },
        'isha': {
            'start': format_time(data[44:48]),
            'iqama': format_time(data[48:52])
        }
    }

# ============================================
# FONCTION 3 : Afficher les horaires
# ============================================
def display_prayer_times(times):
    """Affiche les horaires de manière lisible"""
    print('\n📅 Horaires du jour (CCIQ):')
    print(f"🌙 Fajr: {times['fajr']['start']} (Athan) → {times['fajr']['iqama']} (Iqama)")
    print(f"☀️ Zuhr: {times['zuhr']['start']} (Athan) → {times['zuhr']['iqama']} (Iqama)")
    print(f"🌤️ Asr: {times['asr']['start']} (Athan) → {times['asr']['iqama']} (Iqama)")
    print(f"🌆 Maghrib: {times['maghrib']['start']} (Athan) → {times['maghrib']['iqama']} (Iqama)")
    print(f"🌙 Isha: {times['isha']['start']} (Athan) → {times['isha']['iqama']} (Iqama)\n")

# ============================================
# FONCTION 4 : Envoyer notification Telegram
# ============================================
def send_telegram_notification(prayer_name, prayer_time):
    """Envoie une notification via Telegram"""
    try:
        message = f"🕌 Prière de {prayer_name}\n⏰ L'Iqama commence dans 10 minutes à {prayer_time}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Notification envoyée pour {prayer_name} à {prayer_time}")
        else:
            print(f"❌ Erreur envoi notification: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur envoi notification: {e}")

# ============================================
# FONCTION 4B : Confirmation quotidienne
# ============================================
def send_confirmation_telegram(times):
    """Envoie une confirmation avec les horaires du jour"""
    try:
        today = datetime.now().strftime('%A %d %B %Y')
        
        message = f"""✅ Horaires récupérés - {today}

🌙 Fajr: {times['fajr']['iqama']}
☀️ Zuhr: {times['zuhr']['iqama']}
🌤️ Asr: {times['asr']['iqama']}
🌆 Maghrib: {times['maghrib']['iqama']}
🌙 Isha: {times['isha']['iqama']}

⏰ Notifications programmées 10 min avant chaque Iqama"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Confirmation envoyée sur Telegram")
        else:
            print(f"❌ Erreur envoi confirmation: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur envoi confirmation: {e}")

def send_error_telegram():
    """Envoie une alerte en cas d'échec de récupération"""
    try:
        message = "❌ ERREUR: Impossible de récupérer les horaires ce matin !\n\nVérifiez le système."
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        
        requests.post(url, data=data, timeout=10)
        print("✅ Alerte d'erreur envoyée sur Telegram")
        
    except Exception as e:
        print(f"❌ Erreur envoi alerte: {e}")


# ============================================
# FONCTION 5 : Programmer les notifications
# ============================================
def schedule_notifications(times):
    """Programme les notifications 10 minutes avant chaque Iqama"""
    
    prayers = [
        ('Fajr', times['fajr']['iqama']),
        ('Zuhr', times['zuhr']['iqama']),
        ('Asr', times['asr']['iqama']),
        ('Maghrib', times['maghrib']['iqama']),
        ('Isha', times['isha']['iqama'])
    ]
    
    print('\n⏰ Programmation des notifications (10 min avant Iqama):')
    
    for prayer_name, iqama_time in prayers:
        if not iqama_time:
            continue
        
        # Convertir l'heure en datetime
        hours, minutes = map(int, iqama_time.split(':'))
        iqama_datetime = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # Calculer l'heure de notification (10 minutes avant)
        notification_time = iqama_datetime - timedelta(minutes=10)
        
        # Vérifier si l'heure n'est pas déjà passée
        if notification_time > datetime.now():
            # Programmer la notification
            schedule.every().day.at(notification_time.strftime('%H:%M')).do(
                send_telegram_notification, prayer_name, iqama_time
            )
            
            print(f"   ✓ {prayer_name}: notification à {notification_time.strftime('%H:%M')} (Iqama à {iqama_time})")
        else:
            print(f"   ⊘ {prayer_name}: déjà passé (Iqama était à {iqama_time})")
    
    print('')

# ============================================
# FONCTION PRINCIPALE
# ============================================
def main():
    """Fonction principale - récupère et programme les horaires"""
    print('\n🕌 ════════════════════════════════════════════════')
    print('   Système de notifications - CCIQ')
    print('════════════════════════════════════════════════ 🕌\n')
    
    times = get_prayer_times()
    
    if times:
        display_prayer_times(times)
        schedule.clear()
        schedule_notifications(times)
        
        # Envoyer confirmation Telegram
        send_confirmation_telegram(times)
        
        print('✅ Système actif ! Les notifications seront envoyées 10 min avant chaque Iqama.')
        print('⌨️  Appuyez sur Ctrl+C pour arrêter\n')
    else:
        # Envoyer alerte d'échec
        send_error_telegram()
        print('❌ Impossible de récupérer les horaires\n')

# ============================================
# LANCEMENT DU PROGRAMME
# ============================================
if __name__ == '__main__':
    # Exécuter immédiatement au démarrage
    main()
    
    # Programmer la mise à jour quotidienne à 5h du matin
    schedule.every().day.at("05:00").do(main)
    
    print('🔄 En attente du prochain événement...\n')
    
    # Boucle infinie pour exécuter les tâches programmées
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes
