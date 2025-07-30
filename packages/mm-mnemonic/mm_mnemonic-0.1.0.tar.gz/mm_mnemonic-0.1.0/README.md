# mm-mnemonic

A Python CLI tool for generating cryptocurrency accounts from BIP39 mnemonic phrases.

## Installation

```bash
uv tool install mm-mnemonic
```

## Usage

### `derive` - Generate Cryptocurrency Accounts

The `derive` command generates cryptocurrency accounts from BIP39 mnemonic phrases with support for multiple blockchains.

#### Basic Usage

```bash
# Interactive mode - prompts for mnemonic and passphrase
mm-mnemonic derive --prompt

# Generate new random mnemonic
mm-mnemonic derive --generate

# Use specific mnemonic
mm-mnemonic derive --mnemonic "abandon abandon abandon..." --passphrase "optional_passphrase"
```

#### Supported Cryptocurrencies

- **BTC** - Bitcoin (mainnet)
- **BTC_TESTNET** - Bitcoin (testnet)
- **ETH** - Ethereum
- **SOL** - Solana
- **TRX** - TRON

#### Input Methods

##### 1. Interactive Prompt (`--prompt`)
Securely prompts for mnemonic and passphrase with hidden input:

```bash
mm-mnemonic derive --prompt --coin BTC --limit 5
```

##### 2. Generate New Mnemonic (`--generate`)
Creates a new random mnemonic phrase:

```bash
# Generate 24-word mnemonic (default)
mm-mnemonic derive --generate

# Generate 12-word mnemonic
mm-mnemonic derive --generate --words 12

# Generate mnemonic with automatic passphrase
mm-mnemonic derive --generate --generate-passphrase
```

##### 3. Use Existing Mnemonic (`--mnemonic`)
Specify an existing mnemonic phrase:

```bash
mm-mnemonic derive --mnemonic "your twenty four word mnemonic phrase here..." --passphrase "optional_passphrase"
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--coin` | `-c` | Cryptocurrency type (BTC, ETH, SOL, TRX) | ETH |
| `--mnemonic` | `-m` | BIP39 mnemonic phrase (12-24 words) | None |
| `--passphrase` | `-p` | BIP39 passphrase (use with --mnemonic) | None |
| `--generate` | `-g` | Generate new random mnemonic | False |
| `--generate-passphrase` | `-gp` | Generate random passphrase (with --generate) | False |
| `--prompt` | | Interactive input mode | False |
| `--words` | `-w` | Word count for generated mnemonic (12,15,21,24) | 24 |
| `--derivation-path` | | Custom derivation path template | Auto |
| `--limit` | `-l` | Number of accounts to derive | 10 |
| `--output-dir` | `-o` | Save accounts to directory | None |
| `--encrypt` | `-e` | Encrypt saved files (requires --output-dir) | False |

#### Examples

##### Generate Bitcoin Accounts
```bash
# Generate 5 Bitcoin accounts
mm-mnemonic derive --generate --coin BTC --limit 5

# Save to encrypted files
mm-mnemonic derive --generate --coin BTC --limit 5 --output-dir ./btc-keys --encrypt
```

##### Use Custom Derivation Path
```bash
# Custom Ethereum derivation path
mm-mnemonic derive --prompt --derivation-path "m/44'/60'/0'/0/{i}"

# Ledger-style Bitcoin path
mm-mnemonic derive --generate --coin BTC --derivation-path "m/44'/0'/{i}'/0/0"
```

##### File Output
When using `--output-dir`, two files are created:

- **`keys.toml`** - Complete account information (mnemonic, passphrase, private keys, addresses)
- **`addresses.txt`** - Address list only (one per line)

```bash
# Save to files (plain text)
mm-mnemonic derive --generate --output-dir ./my-accounts

# Save encrypted (prompts for encryption password)
mm-mnemonic derive --generate --output-dir ./my-accounts --encrypt
```

#### Security Features

- **Hidden Input**: All sensitive input (mnemonics, passphrases, passwords) is hidden during typing
- **Automatic Confirmation**: Password/passphrase entries require confirmation to prevent typos
- **Console Privacy**: When saving to files, sensitive information is hidden from console output
- **File Encryption**: Optional AES-256-CBC encryption for saved key files

#### Sample Output

```bash
$ mm-mnemonic derive --generate --coin ETH --limit 2

Coin: ETH
Mnemonic: abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
Passphrase: 
Derivation Path: m/44'/60'/0'/0/{i}

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Path             ┃ Address                                    ┃ Private Key                                                        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ m/44'/60'/0'/0/0 │ 0x9858EfFD232B4033E47d90003D41EC34EcaEda94 │ 0x1ab42cc412b618bdea3a599e3c9bae199ebf030895b039e9db1e30dafb12b727 │
│ m/44'/60'/0'/0/1 │ 0x6Fac4D18c912343BF86fa7049364Dd4E424Ab9C0 │ 0x9a983cb3d832fbde5ab49d692b7a8bf5b5d232479c99333d0fc8e1d21f1b55b6 │
└──────────────────┴────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────┘
```

#### Default Derivation Paths

| Coin | Default Path |
|------|--------------|
| BTC | `m/84'/0'/0'/0/{i}` (Native SegWit) |
| BTC_TESTNET | `m/84'/1'/0'/0/{i}` |
| ETH | `m/44'/60'/0'/0/{i}` |
| SOL | `m/44'/501'/0'/0/{i}` |
| TRX | `m/44'/195'/0'/0/{i}` |

#### Error Handling

The tool validates all inputs and provides helpful error messages:

- Invalid mnemonic phrases are rejected with retry prompts
- Conflicting options are detected (e.g., `--generate` with `--mnemonic`)
- Missing required combinations are flagged (e.g., `--encrypt` without `--output-dir`)
- Non-empty output directories are rejected to prevent accidental overwrites 