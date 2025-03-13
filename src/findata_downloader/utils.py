import os
import logging
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
    retries: int = 3,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Scarica dati storici utilizzando Yahoo Finance
    """
    try:
        session = requests.Session()
        if proxy:
            session.proxies = {
                "http": proxy,
                "https": proxy
            }
            if verbose:
                logger.info(f"Using proxy: {proxy}")

        retry_strategy = Retry(
            total=retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.timeout = timeout

        yf_ticker = yf.Ticker(ticker, session=session)
        
        kwargs = {
            "interval": interval,
            "prepost": prepost,
            "auto_adjust": adjust,
        }

        if period:
            kwargs["period"] = period
        else:
            kwargs["start"] = start
            kwargs["end"] = end

        if verbose:
            logger.info(f"Downloading data with parameters: {kwargs}")

        data = yf_ticker.history(**kwargs)
        
        if data.empty:
            raise ValueError("No data returned for the given parameters")

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
    """Verifica la validità del ticker"""
    try:
        yf.Ticker(ticker).info
        return True
    except:
        return False

def get_formats() -> list:
    """Restituisce la lista dei formati supportati"""
    return ['csv', 'json', 'parquet', 'feather', 'xlsx']