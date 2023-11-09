import click

from games.manager import Manager


@click.command()
@click.argument('game', required=False)
@click.option('--fps', type=int, default=30, help='Set the frames per second to render')
@click.option('--debug', is_flag=True, help='Turn on debug mode')
def main(game, fps, debug):
    Manager().start(game_filter=game, fps=fps, debug=debug)
