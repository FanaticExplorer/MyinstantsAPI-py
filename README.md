# 🎵 MyInstants Unofficial API

**FastAPI-based unofficial API for accessing and scraping the [MyInstants](https://www.myinstants.com/) soundboard website.**

> 🛠️ Originally based on [abdipr/myinstants-api](https://github.com/abdipr/myinstants-api), this version is fully rewritten in Python, powered by FastAPI, updated and fixed.

---

## ✨ Features

- 🔍 Search for sounds by keyword
- 📈 Get trending and all-time best sounds by locale
- 🆕 Browse recently added sounds
- 👤 Retrieve a user's favorite or uploaded sounds
- 📄 Get detailed info about any individual sound

---

## 🚀 API Endpoints

Base URL: `http://localhost:8000/` (or your deployed host)

Swagger documentation is available at root after running the server.

### 🔸 `GET /search?q=<query>`
Search for sounds.

### 🔸 `GET /trending?locale=us`
Get trending sounds for a specific country.

### 🔸 `GET /recent`
Latest added sounds.

### 🔸 `GET /best?locale=fr`
All-time best sounds for a locale.

### 🔸 `GET /favorites?username=<user>`
Get a user's favorited sounds.

### 🔸 `GET /uploaded?username=<user>`
Get sounds uploaded by a user.

### 🔸 `GET /detail?id=<sound_id>`
Get full detail of a specific sound.

---

## 📦 Installation & Usage

- Clone the repository
```bash
git clone https://github.com/FanaticExplorer/MyinstantsAPI-py
cd MyinstantsAPI-py
```
- Install dependencies
```bash
pip install -r requirements.txt
```

- Run the FastAPI server
```bash
python main.py
```

- Access the API (and docs) at `http://localhost:8000/`
---

## 💖 Support the Developer

If you find this tool useful, consider supporting my work:

[![Buy me a coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/FanaticExplorer)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/FanaticExplorer)
[![Monobank Card](https://img.shields.io/badge/Monobank_Card-000000?style=flat&logo=visa&logoColor=white)](https://send.monobank.ua/3KAPtPvd4a)

You can also support me with cryptocurrency:

**Binance Pay ID:** `780389392`

[![Binance Pay QR code](https://img.shields.io/badge/Binance_Pay_QR_code-F0B90B?style=flat&logo=binance&logoColor=black)](https://i.imgur.com/WEYYdTn.png)

**Direct Wallet Addresses:**
- **BTC:** `1ksLDnSTekh9kdQcgeqtbdZtxKuLtDobC`
- **ETH (ERC20):** `0xef174683a9ca0cc6065bb8de433188bb1767b631`
- **USDT (TRC20):** `TC3SSLB1cyD1PEugufHF5zUv3sVpFhCi7z`
- **SOL (Solana):** `4ZZhbfJMevkg3x9W8KQiBsdFLz5NAkKMm7takXi2Lz8i`

Every donation helps me create and maintain more useful tools!

---

## 📄 License

[MIT License](https://opensource.org/license/mit/)

---

## 🗒️ Notes

⚠️ This API uses web scraping — it may break if the original website changes its structure.