import requests
import time
import telegram

# --- تنظیمات ربات ---
BOT_TOKEN = "8423597712:AAGRD85JKMeqDuTwyrJsX-i06NNL-P19gG4"
CHAT_ID = "7211246146"

bot = telegram.Bot(token=BOT_TOKEN)

# توکن‌ها از 3 شبکه: Solana, BSC, ETH
def fetch_birdeye_sol():
    try:
        url = "https://public-api.birdeye.so/public/token/moving?direction=up&sort_by=volume_24h&limit=5"
        response = requests.get(url)
        tokens = response.json().get("data", [])
        result = []
        for token in tokens:
            symbol = token.get("symbol")
            address = token.get("address")
            price = float(token.get("price_usd", 0))
            change = float(token.get("price_change_24h", 0))
            volume = float(token.get("volume_24h_quote", 0))
            if change > 10 and volume > 50000:
                result.append({
                    "symbol": symbol,
                    "address": address,
                    "price": price,
                    "change": change,
                    "volume": volume,
                    "chain": "Solana",
                    "dex": "Jupiter/Birdeye",
                    "chart": f"https://birdeye.so/token/{address}?chain=solana"
                })
        return result
    except:
        return []

def fetch_gecko_terminal(chain):
    try:
        url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/pools?page=1"
        response = requests.get(url)
        data = response.json().get("data", [])
        result = []
        for pool in data:
            attr = pool.get("attributes", {})
            token_name = attr.get("token_symbol")
            price_usd = float(attr.get("base_token_price_usd", 0))
            volume_usd = float(attr.get("volume_usd", 0))
            change = float(attr.get("price_percent_change_24h", 0))
            address = pool.get("id")
            if change > 10 and volume_usd > 50000:
                result.append({
                    "symbol": token_name,
                    "address": address,
                    "price": price_usd,
                    "change": change,
                    "volume": volume_usd,
                    "chain": "BSC" if chain == "bsc" else "ETH",
                    "dex": "PancakeSwap" if chain == "bsc" else "Uniswap",
                    "chart": f"https://www.geckoterminal.com/{chain}/pools/{address}"
                })
        return result
    except:
        return []

def calculate_zones(price):
    buy_low = round(price * 0.92, 6)
    buy_high = round(price * 0.97, 6)
    sell_low = round(price * 1.10, 6)
    sell_high = round(price * 1.25, 6)
    return buy_low, buy_high, sell_low, sell_high

def format_message(token):
    buy_low, buy_high, sell_low, sell_high = calculate_zones(token['price'])
    return f'''
🚀 پامپ جدید شناسایی شد!

🪙 توکن: ${token['symbol']}
📊 رشد 24h: +{round(token['change'], 2)}%
💰 حجم 24h: ${int(token['volume']):,}
📉 Buy Zone: ${buy_low} ~ ${buy_high}
📈 Sell Zone: ${sell_low} ~ ${sell_high}

🌐 شبکه: {token['chain']}
🛒 خرید/فروش در: {token['dex']}
📊 چارت: {token['chart']}
'''

def main():
    sent = set()
    while True:
        sol_tokens = fetch_birdeye_sol()
        bsc_tokens = fetch_gecko_terminal("bsc")
        eth_tokens = fetch_gecko_terminal("eth")
        all_tokens = sol_tokens + bsc_tokens + eth_tokens

        for token in all_tokens:
            uid = token['address']
            if uid not in sent:
                msg = format_message(token)
                try:
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    sent.add(uid)
                except:
                    pass

        time.sleep(300)  # هر 5 دقیقه
            
if __name__ == "__main__":
    main()