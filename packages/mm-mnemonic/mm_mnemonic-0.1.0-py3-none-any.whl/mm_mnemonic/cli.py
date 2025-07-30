import importlib.metadata
from pathlib import Path
from typing import Annotated

import typer

from mm_mnemonic import commands
from mm_mnemonic.types import Coin

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, add_completion=False)


def mnemonic_words_callback(value: int) -> int:
    if value not in [12, 15, 21, 24]:
        raise typer.BadParameter("Words must be one of: 12, 15, 21, 24")
    return value


@app.command(name="derive")
def derive_command(
    coin: Annotated[Coin, typer.Option("--coin", "-c", help="Cryptocurrency to derive accounts for")] = Coin.ETH,
    # Input methods (mutually exclusive)
    mnemonic: Annotated[str | None, typer.Option("--mnemonic", "-m", help="BIP39 mnemonic phrase (12-24 words)")] = None,
    passphrase: Annotated[
        str | None,
        typer.Option("--passphrase", "-p", help="BIP39 passphrase (optional, use with --mnemonic)"),
    ] = None,
    generate: Annotated[bool, typer.Option("--generate", "-g", help="Generate a new random mnemonic phrase")] = False,
    generate_passphrase: Annotated[
        bool, typer.Option("--generate-passphrase", "-gp", help="Also generate a random passphrase (use with --generate)")
    ] = False,
    prompt: Annotated[bool, typer.Option("--prompt", help="Interactively prompt for mnemonic and passphrase")] = False,
    # Generation options
    words: Annotated[
        int,
        typer.Option(
            "--words", "-w", help="Number of words for generated mnemonic (use with --generate)", callback=mnemonic_words_callback
        ),
    ] = 24,
    # Derivation options
    derivation_path: Annotated[
        str | None,
        typer.Option(
            "--derivation-path",
            help="Custom derivation path template (e.g., m/44'/0'/0'/0/{i}). Default paths used if not specified.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Number of accounts to derive")] = 10,
    # Output options
    output_dir: Annotated[
        Path | None, typer.Option("--output-dir", "-o", help="Directory to save account files (keys.toml and addresses.txt)")
    ] = None,
    encrypt: Annotated[
        bool,
        typer.Option("--encrypt", "-e", help="Encrypt saved keys with AES-256-CBC (requires --output-dir)"),
    ] = False,
) -> None:
    """
    Derive cryptocurrency accounts from BIP39 mnemonic phrases.

    USAGE MODES:

    --prompt                         Interactive input

    --generate                       Generate new mnemonic

    --generate --generate-passphrase Generate mnemonic + passphrase

    --mnemonic="..." --passphrase="..." Use existing credentials

    SUPPORTED COINS: BTC, BTC_TESTNET, ETH, SOL, TRX
    """
    commands.derive.run(
        commands.derive.Params(
            coin=coin,
            limit=limit,
            derivation_path=derivation_path,
            mnemonic=mnemonic,
            passphrase=passphrase,
            generate=generate,
            generate_passphrase=generate_passphrase,
            prompt=prompt,
            words=words,
            output_dir=output_dir,
            encrypt=encrypt,
        )
    )


@app.command(name="search", help="Search addresses in the derived accounts")
def search_command() -> None:
    raise typer.BadParameter("not implemented yet")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mm-mnemonic version: {importlib.metadata.version('mm-mnemonic')}")
        raise typer.Exit


@app.callback()
def main(
    _version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Print the version and exit"),
) -> None:
    pass


if __name__ == "__main__":
    app()
