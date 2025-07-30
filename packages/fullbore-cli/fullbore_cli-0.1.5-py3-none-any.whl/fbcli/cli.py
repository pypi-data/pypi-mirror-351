# fbcli/cli.py

import typer
from fbcli.commands import servers
import subprocess

app = typer.Typer(
    help="Full Bore CLI — manage servers and operations from the terminal.",
    invoke_without_command=True
)

@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

@app.command()
def list_servers():
    """List all configured servers."""
    servers.list()

@app.command()
def ssh(server: str):
    """SSH into a server by name."""
    servers.ssh(server)

@app.command()
def redeploy(server: str, repo_path: str):
    """Redeploy a repo by server repo_name"""
    servers.redeploy(server, repo_path)

if __name__ == "__main__":
    app()
