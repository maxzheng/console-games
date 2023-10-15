import click

from games.manager import Manager


@click.command()
def main():
    Manager().start()
