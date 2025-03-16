```markdown
# 📈 Findata Downloader

Una potente CLI professionale per scaricare dati finanziari da Yahoo Finance

## 📥 Installazione

### Prerequisiti
- Python 3.8+
- pip aggiornato

### Metodi di installazione

**1. Da PyPI (raccomandato):**
```bash
pip install findata-downloader
```

**2. Da repository Git:**
```bash
pip install git+https://github.com/tuo-repo/findata-downloader.git
```

**3. Sviluppo locale:**
```bash
git clone https://github.com/tuo-repo/findata-downloader
cd findata-downloader
pip install -e .
```

## 🚀 Utilizzo Base

### Comando minimo:
```bash
findata TICKER --period INTERVALLO
```
Esempio per scaricare 1 anno di dati Apple:
```bash
findata AAPL --period 1y
```

### Esempi avanzati:

**1. Dati intraday con intervallo 15 minuti:**
```bash
findata TSLA --period 5d --interval 15m --format csv
```

**2. Dati storici con compressione:**
```bash
findata MSFT --period 10y --interval 1d --compress --format parquet
```

**3. Output personalizzato:**
```bash
findata BTC-USD -p max -i 1d -o ~/financial_data -fn bitcoin_full_history.feather
```

**4. Con proxy e verbose mode:**
```bash
findata AMZN -p 1y -i 1wk --proxy socks5://localhost:9050 -v
```

## 🔧 Opzioni Principali

| Flag               | Descrizione                                  | Valori Accettati               |
|---------------------|----------------------------------------------|---------------------------------|
| `-p/--period`       | Periodo storico                             | 1d, 5d, 1mo, 1y, max          |
| `-i/--interval`     | Frequenza dati                              | 1m, 15m, 1h, 1d, 1wk          |
| `-f/--format`       | Formato output                              | csv, json, parquet, feather    |
| `-o/--output`       | Directory di output                         | Percorso assoluto/relativo     |
| `--compress`        | Abilita compressione gzip                  | Flag booleano                  |
| `-v/--verbose`      | Output dettagliato                         | Flag booleano                  |

## 🛠 Troubleshooting Comune

### Errore 429 (Too Many Requests)
```bash
# Soluzione 1: Usa un proxy
findata AAPL --period 1y --proxy http://proxy-server:port

# Soluzione 2: Aumenta timeout e retries
findata TSLA --timeout 60 --retries 10
```

### Dati Mancanti
```bash
# Verifica la validità del ticker
findata CHECK_TICKER --period 1d

# Prova con intervalli diversi
findata PROBLEMATIC_TICKER --interval 1h
```

### Problemi Dipendenze
```bash
# Aggiorna pacchetti chiave
pip install --upgrade yfinance pandas requests
```

## 📚 Intervalli Supportati

| Intervallo | Periodo Massimo | Note                           |
|------------|-----------------|--------------------------------|
| 1m         | 7 giorni        | Richiede dati recenti         |
| 15m        | 60 giorni       |                                |
| 1h         | 730 giorni      |                                |
| 1d         | Max storico     |                                |
| 1wk        | Max storico     |                                |

## 📦 Formati Supportati

| Formato   | Compressione | Dimensioni Tipiche | Velocità |
|-----------|--------------|--------------------|----------|
| CSV       | gzip         | Medio              | 🟢🟢🟢     |
| Parquet   | Snappy       | Piccolo            | 🟢🟢🟢🟢   |
| Feather   | Non support. | Grande             | 🟢🟢🟢🟢🟢 |
| JSON      | gzip         | Grande             | 🟢        |

## 📜 License
MIT License - [Dettagli Licenza](LICENSE)

## 👥 Contribuire
1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/awesome-feature`)
3. Commit dei cambiamenti (`git commit -am 'Add awesome feature'`)
4. Push del branch (`git push origin feature/awesome-feature`)
5. Apri una Pull Request

**Happy data mining!** 🚀
