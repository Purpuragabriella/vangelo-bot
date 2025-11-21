import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
BOT_TOKEN = "6152033559:AAENgTWUcMIJ9X_0Pd3tDljOJyeUJiQpkLk"
CHAT_ID = "@Innamorati_della_lode" 

RSS_URL = "http://feed.evangelizo.org/rss/v2/reading_gospel-it.xml"

def clean_html(html_text):
    # Pulisce i tag HTML per rendere il testo leggibile
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator="\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def job():
    print(f"--- Avvio script: {datetime.now()} ---")
    
    # 1. Scarica il Feed
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        print(f"Errore connessione RSS: {e}")
        return

    if not feed.entries:
        print("Nessun vangelo trovato nel feed.")
        return

    # 2. Prende il primo elemento (di solito è quello di oggi o domani)
    # Evangelizo a volte mette prima le letture, poi il vangelo. 
    # Cerchiamo specificamente il vangelo se ci sono più voci, o prendiamo il primo.
    entry = feed.entries[0]
    
    # 3. CONTROLLO DATA (Anti-Duplicati)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # La data del feed viene convertita in stringa per il confronto
    if hasattr(entry, 'published_parsed'):
        entry_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
    else:
        # Fallback se non c'è la data parsata
        entry_date = today_str 

    print(f"Data Vangelo nel feed: {entry_date}")
    print(f"Data di oggi: {today_str}")

    if entry_date != today_str:
        print("⚠️ ATTENZIONE: La data del feed non corrisponde a oggi. Potrebbe essere il vangelo di ieri o domani.")
        print("Per sicurezza, procedo solo se le date coincidono. (Blocco invio)")
        # Se vuoi forzare l'invio anche se la data è diversa, metti un # davanti alla riga sotto (return)
        return

    # 4. Preparazione Messaggio
    title = entry.title
    raw_content = entry.description
    clean_text = clean_html(raw_content)
    
    # Tagliamo il testo se è troppo lungo per Telegram (max 4096 caratteri)
    if len(clean_text) > 3800:
        clean_text = clean_text[:3800] + "..."

    message = f"📖 *Vangelo del Giorno*\n_{entry_date}_\n\n*{title}*\n\n{clean_text}"
    
    # 5. Invio
    print("Invio a Telegram...")
    result = send_telegram_message(message)
    
    if result.get("ok"):
        print("✅ Messaggio inviato con successo!")
    else:
        print(f"❌ Errore invio Telegram: {result}")

if __name__ == "__main__":
    job()
