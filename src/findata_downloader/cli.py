import click
from pathlib import Path
from .utils import fetch_stock_data, process_data, save_data

@click.command()
@click.argument('ticker')
@click.option('--years', deafault=1, type=int, help='Number of years of data to download')
@click.option('--csv', "file_format", flag_value='csv', default=True, help='Download data in CSV format')
@click.option('--json', "file_format", flag_value='json', help='Download data in JSON format')
@click.option('--parquet', "file_format", flag_value='parquet', help='Download data in Parquet format')
@click.option('--output', default='.', help='Output directory')
def main(ticker, years, file_format, output):
    click.echo(f'Downloading {years} years of data for {ticker} in {file_format} format to {output}')    