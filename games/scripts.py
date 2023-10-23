import click

from games.manager import Manager


@click.command()
@click.option('--fps', type=int, default=30, help='Set the frames per second to render')
@click.option('--debug', is_flag=True, help='Turn on debug mode')
def main(fps, debug):
    Manager().start(fps=fps, debug=debug)
