import click

from games.manager import Manager


@click.command()
@click.option('--debug', is_flag=True, help='Turn on debug modoe')
def main(debug):
    Manager().start(debug=debug)
