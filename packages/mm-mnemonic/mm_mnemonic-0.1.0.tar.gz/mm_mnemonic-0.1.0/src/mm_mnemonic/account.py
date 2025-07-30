from dataclasses import dataclass

from mm_mnemonic.types import Coin


@dataclass
class DerivedAccount:
    path: str
    address: str
    private: str


@dataclass
class DerivedAccounts:
    coin: Coin
    mnemonic: str
    passphrase: str
    derivation_path: str
    accounts: list[DerivedAccount]


def is_address_matched(address: str, search_pattern: str | None) -> bool:
    if search_pattern is None:
        return False
    address = address.lower()
    search_pattern = search_pattern.lower()

    if search_pattern.count("*") == 0:
        return address == search_pattern
    if search_pattern.startswith("*"):
        return address.endswith(search_pattern.removeprefix("*"))
    if search_pattern.endswith("*"):
        return address.startswith(search_pattern.removesuffix("*"))

    start_address, end_address = search_pattern.split("*")
    return address.startswith(start_address) and address.endswith(end_address)


def derive_accounts(coin: Coin, mnemonic: str, passphrase: str, derivation_path: str | None, limit: int) -> DerivedAccounts:
    if not derivation_path:
        derivation_path = get_default_derivation_path(coin)

    accounts = [derive_account(coin, mnemonic, passphrase, path=derivation_path.replace("{i}", str(i))) for i in range(limit)]
    return DerivedAccounts(
        coin=coin, mnemonic=mnemonic, passphrase=passphrase, derivation_path=derivation_path, accounts=accounts
    )


def derive_account(coin: Coin, mnemonic: str, passphrase: str, path: str) -> DerivedAccount:
    from mm_mnemonic.chains import btc, eth, sol, trx

    match coin:
        case Coin.BTC:
            return btc.derive_account(mnemonic, passphrase, path)
        case Coin.BTC_TESTNET:
            return btc.derive_account(mnemonic, passphrase, path, testnet=True)
        case Coin.ETH:
            return eth.derive_account(mnemonic, passphrase, path)
        case Coin.SOL:
            return sol.derive_account(mnemonic, passphrase, path)
        case Coin.TRX:
            return trx.derive_account(mnemonic, passphrase, path)
        case _:
            raise NotImplementedError


def get_default_derivation_path(coin: Coin) -> str:
    from mm_mnemonic.chains import btc, eth, sol, trx

    match coin:
        case Coin.BTC:
            return btc.DEFAULT_DERIVATION_PATH
        case Coin.BTC_TESTNET:
            return btc.DEFAULT_DERIVATION_PATH_TESTNET
        case Coin.ETH:
            return eth.DEFAULT_DERIVATION_PATH
        case Coin.SOL:
            return sol.DEFAULT_DERIVATION_PATH
        case Coin.TRX:
            return trx.DEFAULT_DERIVATION_PATH
        case _:
            raise NotImplementedError
