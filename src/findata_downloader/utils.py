# src/findata_downloader/utils.py
import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    return {
        'raw_dir': 'data/raw',
        'processed_dir': 'data/processed',
        'quantile_threshold': 0.99
    }

def fetch_stock_data(ticker: str, years: int = 5) -> pd.DataFrame | None:
    try:
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - years)
        logger.info(f"Scaricando dati per {ticker}...")
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True
        )
        if data.empty:
            logger.warning(f"Nessun dato trovato per {ticker}")
            return None
        return data.reset_index()[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        logger.error(f"Errore durante il download di {ticker}: {str(e)}")
        return None

def process_data(raw_df: pd.DataFrame, ticker: str) -> pd.DataFrame | None:
    try:
        df = raw_df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['log_returns'] = np.log(df['Close']).diff()
        threshold = df['log_returns'].quantile(0.99)
        filtered = df[df['log_returns'].abs() < threshold]
        return filtered.dropna()
    except Exception as e:
        logger.error(f"Errore elaborazione {ticker}: {str(e)}")
        return None

def save_data(df: pd.DataFrame, path: Path, ticker: str, file_format: str):
    try:
        path.mkdir(parents=True, exist_ok=True)
        if file_format == "csv":
            output_path = path / f"{ticker}.csv"
            df.to_csv(output_path, index=False)
        elif file_format == "parquet":
            output_path = path / f"{ticker}.parquet"
            df.to_parquet(output_path, index=False)
        else:
            logger.warning(f"Formato {file_format} non riconosciuto. Salvataggio in CSV di default.")
            output_path = path / f"{ticker}.csv"
            df.to_csv(output_path, index=False)

        logger.info(f"Dati salvati in {output_path}")
    except Exception as e:
        logger.error(f"Errore salvataggio {ticker}: {str(e)}")
