import click
from pathlib import Path
from datetime import datetime
from typing import Optional
from .utils import fetch_stock_data, save_data

@click.command()
@click.argument('ticker', type=str, required=True)
@click.option('--period', '-p', 
              type=str,
              help='Time period to download (e.g., 1d, 5y, max)')
@click.option('--interval', '-i',
              type=click.Choice(['1m', '2m', '5m', '15m', '30m', '60m', 
                               '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']),
              default='1d',
              help='Data frequency interval')
@click.option('--start-date', '-s',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              help='End date (YYYY-MM-DD)')
@click.option('--prepost/--no-prepost',
              default=False,
              help='Include pre/post market data')
@click.option('--adjust/--no-adjust',
              default=True,
              help='Adjust dividend and stock splits')
@click.option('--format', '-f', 'file_format',
              type=click.Choice(['csv', 'json', 'parquet', 'feather', 'xlsx']),
              default='csv',
              help='Output file format')
@click.option('--output', '-o',
              type=click.Path(exists=True, file_okay=False, writable=True),
              default='.',
              help='Output directory')
@click.option('--filename', '-fn',
              type=str,
              help='Custom output filename')
@click.option('--compress/--no-compress',
              default=False,
              help='Compress output file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output')
@click.option('--api-key', '-k',
              envvar='FINDATA_API_KEY',
              help='API key for premium data')
@click.option('--proxy',
              type=str,
              help='Proxy server (e.g., http://user:pass@host:port)')
@click.option('--threads', '-t',
              type=int,
              default=4,
              help='Number of download threads')
@click.option('--timeout',
              type=int,
              default=30,
              help='Request timeout in seconds')
@click.option('--retries',
              type=int,
              default=3,
              help='Number of download retries')
def main(
    ticker: str,
    period: Optional[str],
    interval: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    prepost: bool,
    adjust: bool,
    file_format: str,
    output: str,
    filename: Optional[str],
    compress: bool,
    verbose: bool,
    api_key: Optional[str],
    proxy: Optional[str],
    threads: int,
    timeout: int,
    retries: int
):
    """
    Download financial data for a given ticker
    """
    
    if not period and (not start_date or not end_date):
        raise click.UsageError("Must specify either --period or both --start-date and --end-date")
    
    if period and (start_date or end_date):
        raise click.UsageError("Cannot combine --period with --start-date/--end-date")

    if not filename:
        date_part = period if period else f"{start_date:%Y%m%d}-{end_date:%Y%m%d}"  # type: ignore
        filename = f"{ticker}_{date_part}_{interval}".replace(' ', '')
        filename += f".{file_format}"

    output_path = Path(output) / filename

    try:
        if verbose:
            click.echo(f"Starting download for {ticker}...")
        
        # Download dati
        data = fetch_stock_data(
            ticker=ticker,
            period=period,
            interval=interval,
            start=start_date,
            end=end_date,
            prepost=prepost,
            adjust=adjust,
            api_key=api_key,
            proxy=proxy,
            threads=threads,
            timeout=timeout,
            retries=retries,
            verbose=verbose
        )
        
        save_data(
            data=data,
            path=output_path,
            file_format=file_format,
            compress=compress
        )

        if verbose:
            click.echo(f"Data successfully saved to {output_path}")
            click.echo(f"File size: {output_path.stat().st_size / 1024:.2f} KB")

    except Exception as e:
        raise click.ClickException(f"Download error: {str(e)}")


if __name__ == "__main__":
    main()