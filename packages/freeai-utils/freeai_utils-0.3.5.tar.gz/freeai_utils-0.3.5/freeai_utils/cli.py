# freeai_utils/cli.py
import sys
import click
from ._setup import install_default_model

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        # no subcommand given: show help and exit with error
        click.echo(ctx.get_help())
        sys.exit(1)

@main.command()
def setup():
    install_default_model()

if __name__ == "__main__":
    main()
