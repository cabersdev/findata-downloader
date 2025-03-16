import os
import logging
import random
import time
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

import pandas as pd
import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomAdapter(HTTPAdapter):
    """Adapter personalizzato con delay random tra le richieste"""
    def send(self, request, **kwargs):
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        return super().send(request, **kwargs)

def fetch_stock_data(
    ticker: str,
    period: Optional[str] = None,
    interval: str = '1d',
    start: Optional[Union[datetime, str]] = None,
    end: Optional[Union[datetime, str]] = None,
    prepost: bool = False,
    adjust: bool = True,
    api_key: Optional[str] = None,
    proxy: Optional[str] = None,
    timeout: int = 30,
    retries: int = 5,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Scarica dati storici utilizzando Yahoo Finance con gestione avanzata degli errori
    """
    try:
        session = requests.Session()
        
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        if proxy:
            allowed_protocols = ('http://', 'https://', 'socks5://')
            if not proxy.startswith(allowed_protocols):
                proxy = 'http://' + proxy  # Default a HTTP se non specificato
            session.proxies = {'http': proxy, 'https': proxy}


            if verbose: 
                logger.info(f"Using proxy: {proxy}")


        retry_strategy = Retry(
            total=retries,
            backoff_factor=2.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(['GET', 'POST']),
            respect_retry_after_header=True
        )

        adapter = CustomAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        yf_ticker = yf.Ticker(
            ticker,
            session=session,
        )

        time.sleep(random.uniform(0.5, 1.0))

        kwargs = {
            "interval": interval,
            "prepost": prepost,
            "auto_adjust": adjust,
            "timeout": timeout
        }

        if period:
            kwargs["period"] = period
        else:
            kwargs["start"] = start
            kwargs["end"] = end

        if verbose:
            logger.info(f"Downloading data with parameters: {kwargs}")

        data = None
        try:
            data = yf.download(
                tickers=ticker,
                period=period,
                interval=interval,
                prepost=prepost,
                auto_adjust=adjust,
                threads=False,
                proxy=session.proxies.get('https') if session.proxies else None,
                timeout=timeout,
                retry=retries
            )
        except Exception as e:
            logger.warning(f"Metodo download fallito, tentativo con history: {str(e)}")
            data = yf_ticker.history(
                period=period,
                interval=interval,
                start=start,
                end=end,
                prepost=prepost,
                auto_adjust=adjust,
                timeout=timeout
            )

        if data is None:
            raise ValueError("Nessun dato ricevuto dal server")
            
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"Tipo dati non valido: {type(data)}")
        
        if data.empty:
            if not yf.Ticker(ticker).history(period="1d").empty:
                raise ValueError("Dati disponibili ma non per i parametri richiesti")
            raise ValueError(f"Ticker {ticker} non valido o delistato")

        return data

    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise

def save_data(
    data: pd.DataFrame,
    path: Union[str, Path],
    file_format: str = 'csv',
    compress: bool = False,
    overwrite: bool = False
) -> None:
    """
    Salva i dati in diversi formati con opzione di compressione
    """
    path = Path(path)
    compression = None
    
    try:
        if data is None:
            raise ValueError("Nessun dato da salvare")
        
        if path.exists() and not overwrite:
            raise FileExistsError(f"File {path} already exists")
        
        path.parent.mkdir(parents=True, exist_ok=True)

        if file_format == 'csv':
            compression = 'gzip' if compress else None
            data.to_csv(path, index=True, compression=compression)
        
        elif file_format == 'json':
            compression = 'gzip' if compress else None
            data.to_json(path, indent=4, compression=compression)
        
        elif file_format == 'parquet':
            compression = 'gzip' if compress else None
            data.to_parquet(path, compression=compression)
        
        elif file_format == 'feather':
            if compress:
                raise NotImplementedError("Feather format doesn't support compression in this implementation")
            data.reset_index().to_feather(path)
        
        elif file_format == 'xlsx':
            if compress:
                raise NotImplementedError("XLSX compression not supported. Use CSV/JSON/Parquet instead")
            data.to_excel(path, index=True)
        
        else:
            raise ValueError(f"Formato non supportato: {file_format}")

        logger.info(f"Dati salvati correttamente in: {path}")

    except Exception as e:
        logger.error(f"Salvataggio fallito: {str(e)}")
        raise

def validate_ticker(ticker: str) -> bool:
    """Verifica la validità del ticker usando fast_info"""
    try:
        return bool(yf.Ticker(ticker).fast_info.get('lastPrice', False))
    except Exception:
        return False

def get_formats() -> list:
    """Restituisce la lista dei formati supportati"""
    return ['csv', 'json', 'parquet', 'feather', 'xlsx']