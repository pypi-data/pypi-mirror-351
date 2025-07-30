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

### `search` - Find Specific Addresses from Mnemonic

The `search` command allows you to find specific addresses derived from a BIP39 mnemonic phrase by providing partial address patterns with wildcard support.

#### Basic Usage

```bash
# Interactive mode - prompts for mnemonic and passphrase
mm-mnemonic search "0x1234*" --limit 100

# Use specific mnemonic  
mm-mnemonic search "*abcd" --mnemonic "abandon abandon abandon..." --passphrase "optional_passphrase"

# Search multiple patterns
mm-mnemonic search "0x1234*" "*5678*" "prefix*suffix" --limit 50
```

#### Wildcard Patterns

The search command supports flexible wildcard patterns:

- **`prefix*`** - Matches addresses starting with "prefix"
- **`*suffix`** - Matches addresses ending with "suffix"  
- **`*contains*`** - Matches addresses containing "contains" anywhere
- **`prefix*suffix`** - Matches addresses starting with "prefix" and ending with "suffix"
- **Exact match** - No wildcards for exact address matching
- **Case insensitive** - All pattern matching is case insensitive

#### Input Methods

##### 1. Command Line Patterns
Provide address patterns directly as arguments:

```bash
mm-mnemonic search "0xEd5308*" "*44fC" --mnemonic "your mnemonic..." --limit 20
```

##### 2. Patterns from File (`--addresses-file`)
Read patterns from a text file (one pattern per line):

```bash
# Create patterns file
echo -e "0x1234*\n*abcd\n*contains*\n# Comment lines start with #" > patterns.txt

# Search from file
mm-mnemonic search --addresses-file patterns.txt --limit 100
```

##### 3. Combined Approach
Use both command line patterns and file patterns together:

```bash
mm-mnemonic search "0x9999*" --addresses-file patterns.txt --limit 50
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--coin` | `-c` | Cryptocurrency type (BTC, ETH, SOL, TRX) | ETH |
| `--mnemonic` | `-m` | BIP39 mnemonic phrase (12-24 words) | Interactive prompt |
| `--passphrase` | `-p` | BIP39 passphrase | Interactive prompt |
| `--addresses-file` | `-f` | File containing address patterns to search | None |
| `--derivation-path` | | Custom derivation path template | Auto |
| `--limit` | `-l` | Maximum number of addresses to check | 1000 |

#### Examples

##### Search for Vanity Addresses
```bash
# Find addresses starting with "0x1234"
mm-mnemonic search "0x1234*" --limit 1000

# Find addresses containing "cafe"
mm-mnemonic search "*cafe*" --limit 500

# Multiple vanity patterns
mm-mnemonic search "0x1111*" "*2222*" "*3333*" --limit 2000
```

##### Search with Different Cryptocurrencies
```bash
# Search Bitcoin addresses
mm-mnemonic search "1BTC*" --coin BTC --limit 100

# Search Solana addresses  
mm-mnemonic search "*Sol*" --coin SOL --limit 200

# Search TRON addresses
mm-mnemonic search "T*" --coin TRX --limit 150
```

##### File-Based Search
```bash
# Create a patterns file
cat > my-patterns.txt << EOF
# Ethereum vanity patterns
0x1234*
*cafe*
*dead*
0xABCD*BEEF
# Bitcoin patterns  
1BTC*
*btc
EOF

# Search using the file
mm-mnemonic search --addresses-file my-patterns.txt --coin ETH --limit 500
```

##### Custom Derivation Paths
```bash
# Search with Ledger-style path
mm-mnemonic search "0x1234*" --derivation-path "m/44'/60'/0'/{i}/0" --limit 100

# Search different account branches
mm-mnemonic search "*cafe*" --derivation-path "m/44'/60'/1'/0/{i}" --limit 200
```

#### Sample Output

```bash
$ mm-mnemonic search "0xEd5308*" "*44fC" --limit 10

Coin: ETH
Derivation Path: m/44'/60'/0'/0/{i}

Searching for patterns: ['0xEd5308*', '*44fC']
Checking addresses...

Found 2 matches:

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern          ┃ Address                                    ┃ Private Key                                                        ┃ Path                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0xEd5308*        │ 0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537 │ 0x1ab42cc412b618bdea3a599e3c9bae199ebf030895b039e9db1e30dafb12b727 │ m/44'/60'/0'/0/0       │
│ *44fC            │ 0x85d8cd0Bf19132Dc0B2c92f80867a52BaeaB44fC │ 0x9a983cb3d832fbde5ab49d692b7a8bf5b5d232479c99333d0fc8e1d21f1b55b6 │ m/44'/60'/0'/0/1       │
└──────────────────┴────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────┴────────────────────────┘

Search completed. Checked 10 addresses.
```

#### Security Features

- **Interactive Input**: When mnemonic/passphrase are not provided via options, they are securely prompted with hidden input
- **Input Validation**: Mnemonic phrases are validated before starting the search
- **Console Privacy**: Private keys are displayed but can be hidden in future versions if needed

#### Performance Tips

- **Limit Setting**: Use `--limit` to control how many addresses to check (higher limits take longer)
- **Pattern Specificity**: More specific patterns (longer prefixes/suffixes) will be found faster
- **Multiple Patterns**: Searching multiple patterns simultaneously is more efficient than separate searches

#### Common Use Cases

1. **Vanity Address Search**: Find addresses with specific prefixes, suffixes, or patterns
2. **Address Recovery**: Locate a known partial address from your mnemonic 
3. **Pattern Collection**: Gather addresses matching specific themes or patterns
4. **Cross-Chain Search**: Find similar patterns across different cryptocurrencies

#### Error Handling

The search command provides helpful error messages for common issues:

- Invalid mnemonic phrases are rejected with retry prompts
- Missing address patterns (no arguments and no file) are detected  
- Non-existent pattern files are caught gracefully
- Empty pattern files (only comments/whitespace) are flagged
- File reading errors are handled with clear messages 