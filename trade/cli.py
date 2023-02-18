import pkg_resources
from trade import pymt5, pygarch, settings, core
import rich_click as click
from rich.console import Console
# from rich import print
from rich.table import Table


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True



@click.group()
@click.version_option(pkg_resources.get_distribution("trade").version)
def main():
    """Roger's Trade System.

    This cli application controls Trade System.
    """


@main.command()
def options():
    """Starts MetaTrader5 and set market watch"""
    core.start_options()


@main.command()
def garch():
    """Starts volatility stimation by GARCH"""
    pymt5.conecta_mt5("BTG")
    while True:
        df = pygarch.volatilitys_df(settings.GARCH_WATHC)
        df = df.astype(str)

        table = Table(title="GARCH Volatility")
        for column in df.columns:
            table.add_column(column.title(), style="bold blue")

        for i, row in df.iterrows():
            table.add_row(*[row[0], row[1], row[2], row[3], row[4]])

        console = Console()
        console.print(table)
