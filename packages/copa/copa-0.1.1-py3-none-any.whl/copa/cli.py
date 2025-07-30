"""Console script for copa"""
import sys
import typer

app = typer.Typer()

@app.command()
def main():
    """Console script for copa."""
    typer.echo("Replace this message by putting your code into "
               "copa.cli.main")
    typer.echo("See typer documentation at https://typer.tiangolo.com/")

if __name__ == "__main__":
    app()