from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import tomlkit
from typer.testing import CliRunner

from mm_mnemonic.cli import app
from mm_mnemonic.commands.derive import Params
from mm_mnemonic.types import Coin


class TestDeriveDefaults:
    """Test default behavior when no parameters provided."""

    def test_shows_examples_by_default(self, runner: CliRunner) -> None:
        """When no parameters provided, should show usage examples."""
        result = runner.invoke(app, ["derive"])

        assert result.exit_code == 1  # Main task (deriving accounts) was not completed
        assert "USAGE EXAMPLES:" in result.stdout
        assert "mm-mnemonic derive --prompt" in result.stdout
        assert "mm-mnemonic derive --generate" in result.stdout
        assert "mm-mnemonic derive --generate --generate-passphrase" in result.stdout
        assert "For detailed help: mm-mnemonic derive --help" in result.stdout


class TestDeriveGenerate:
    """Test derive command with --generate mode."""

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_generate_basic(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test basic generate mode with real generation."""
        mock_typer_prompt.return_value = "test123"

        result = runner.invoke(app, ["derive", "--generate", "--limit", "1"])

        assert result.exit_code == 0
        assert "Coin: ETH" in result.stdout
        assert "test123" in result.stdout

        # Verify mnemonic format (should be 24 words by default)
        mnemonic_line = next(line for line in result.stdout.split("\n") if "Mnemonic:" in line)
        mnemonic = mnemonic_line.split("Mnemonic: ")[1]
        words = mnemonic.split()
        assert len(words) == 24
        assert all(len(word) >= 3 for word in words)  # BIP39 words are at least 3 chars

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_generate_with_custom_words(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test generate with custom word count."""
        mock_typer_prompt.return_value = ""

        result = runner.invoke(app, ["derive", "--generate", "--words", "12", "--limit", "1"])

        assert result.exit_code == 0

        # Verify mnemonic has correct word count
        mnemonic_line = next(line for line in result.stdout.split("\n") if "Mnemonic:" in line)
        mnemonic = mnemonic_line.split("Mnemonic: ")[1]
        words = mnemonic.split()
        assert len(words) == 12

    def test_generate_with_auto_passphrase(self, runner: CliRunner) -> None:
        """Test generate with automatic passphrase generation."""
        result = runner.invoke(app, ["derive", "--generate", "--generate-passphrase", "--limit", "1"])

        assert result.exit_code == 0

        # Verify passphrase was generated (not empty)
        passphrase_line = next(line for line in result.stdout.split("\n") if "Passphrase:" in line)
        passphrase = passphrase_line.split("Passphrase: ")[1]
        assert passphrase != ""
        assert len(passphrase) > 5  # Generated passphrase should be reasonably long

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_generate_deterministic_behavior(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test that different generations produce different results."""
        mock_typer_prompt.return_value = "same_pass"

        result1 = runner.invoke(app, ["derive", "--generate", "--limit", "1"])
        result2 = runner.invoke(app, ["derive", "--generate", "--limit", "1"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Different generations should produce different mnemonics
        assert result1.stdout != result2.stdout

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_generate_with_different_coins(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test generate with different coin types."""
        mock_typer_prompt.return_value = ""

        for coin in ["BTC", "ETH", "SOL", "TRX"]:
            result = runner.invoke(app, ["derive", "--generate", "--coin", coin, "--limit", "1"])
            assert result.exit_code == 0
            assert f"Coin: {coin}" in result.stdout


class TestDeriveMnemonic:
    """Test derive command with --mnemonic mode using known test vectors."""

    def test_mnemonic_basic(self, runner: CliRunner, mnemonic: str) -> None:
        """Test basic mnemonic mode with known mnemonic."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--limit", "1"])

        assert result.exit_code == 0
        assert "Coin: ETH" in result.stdout
        assert mnemonic in result.stdout
        assert "Passphrase:" in result.stdout

    def test_mnemonic_with_passphrase(self, runner: CliRunner, mnemonic: str, passphrase: str) -> None:
        """Test mnemonic with passphrase."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--passphrase", passphrase, "--limit", "1"])

        assert result.exit_code == 0
        assert mnemonic in result.stdout
        assert passphrase in result.stdout

    def test_mnemonic_deterministic(self, runner: CliRunner) -> None:
        """Test that same mnemonic produces same results."""
        test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result1 = runner.invoke(app, ["derive", "--mnemonic", test_mnemonic, "--limit", "2"])
        result2 = runner.invoke(app, ["derive", "--mnemonic", test_mnemonic, "--limit", "2"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout  # Should be identical

    def test_different_mnemonics_different_results(self, runner: CliRunner) -> None:
        """Test that different mnemonics produce different accounts."""
        mnemonic1 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mnemonic2 = "legal winner thank year wave sausage worth useful legal winner thank yellow"

        result1 = runner.invoke(app, ["derive", "--mnemonic", mnemonic1, "--limit", "1"])
        result2 = runner.invoke(app, ["derive", "--mnemonic", mnemonic2, "--limit", "1"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout != result2.stdout  # Should produce different accounts

    def test_mnemonic_with_custom_derivation_path(self, runner: CliRunner, mnemonic: str) -> None:
        """Test mnemonic with custom derivation path."""
        custom_path = "m/44'/3'/0'/0/{i}"
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--derivation-path", custom_path, "--limit", "1"])

        assert result.exit_code == 0
        assert custom_path in result.stdout


class TestDerivePrompt:
    """Test derive command with --prompt mode."""

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_prompt_basic(self, mock_typer_prompt: Mock, runner: CliRunner, mnemonic: str) -> None:
        """Test basic prompt mode with valid mnemonic."""
        mock_typer_prompt.side_effect = [mnemonic, "test_passphrase"]

        result = runner.invoke(app, ["derive", "--prompt", "--limit", "1"])

        assert result.exit_code == 0
        assert mnemonic in result.stdout
        assert "test_passphrase" in result.stdout

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_prompt_invalid_mnemonic_retry(self, mock_typer_prompt: Mock, runner: CliRunner, mnemonic: str) -> None:
        """Test prompt mode with invalid mnemonic that requires retry."""
        # First invalid mnemonic, then valid one
        mock_typer_prompt.side_effect = ["invalid mnemonic", mnemonic, "test_pass"]

        result = runner.invoke(app, ["derive", "--prompt", "--limit", "1"])

        assert result.exit_code == 0
        assert mnemonic in result.stdout


class TestDeriveFileOutput:
    """Test derive command file output functionality."""

    def test_save_to_file_basic(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test saving accounts to files."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(tmp_path), "--limit", "2"])

        assert result.exit_code == 0

        # Check files are created
        keys_file = tmp_path / "keys.toml"
        addresses_file = tmp_path / "addresses.txt"
        assert keys_file.exists()
        assert addresses_file.exists()

        # Check file contents
        keys_data = tomlkit.loads(keys_file.read_text())
        assert keys_data["coin"] == "ETH"
        assert keys_data["mnemonic"] == mnemonic
        accounts = keys_data["accounts"]
        assert isinstance(accounts, list)
        assert len(accounts) == 2

        addresses = addresses_file.read_text().strip().split("\n")
        assert len(addresses) == 2

    @patch("mm_mnemonic.passphrase.typer.prompt")
    def test_save_encrypted(self, mock_typer_prompt: Mock, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test saving encrypted files."""
        mock_typer_prompt.return_value = "encryption_password"

        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(tmp_path), "--encrypt", "--limit", "1"]
        )

        assert result.exit_code == 0

        # Check encrypted file is created
        encrypted_file = tmp_path / "keys.toml.enc"
        assert encrypted_file.exists()
        assert not (tmp_path / "keys.toml").exists()  # unencrypted file should not exist

    def test_file_output_hides_sensitive_info(self, runner: CliRunner, mnemonic: str, passphrase: str, tmp_path: Path) -> None:
        """Test that sensitive information is hidden when saving to files."""
        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--passphrase", passphrase, "--output-dir", str(tmp_path), "--limit", "1"]
        )

        assert result.exit_code == 0

        # Check that sensitive info is hidden in console output
        assert mnemonic not in result.stdout  # actual mnemonic should be hidden
        assert passphrase not in result.stdout  # actual passphrase should be hidden
        assert "words (saved to file)" in result.stdout
        assert "yes (saved to file)" in result.stdout
        assert "Private Key" not in result.stdout  # private key column should be hidden

    def test_file_output_no_passphrase(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test file output display when no passphrase is used."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(tmp_path), "--limit", "1"])

        assert result.exit_code == 0
        assert "Passphrase: no" in result.stdout


class TestDeriveValidation:
    """Test parameter validation for derive command."""

    def test_conflicting_input_methods(self, runner: CliRunner, mnemonic: str) -> None:
        """Test that conflicting input methods are rejected."""
        # generate + mnemonic
        result = runner.invoke(app, ["derive", "--generate", "--mnemonic", mnemonic])
        assert result.exit_code == 2
        assert "Cannot use multiple input methods simultaneously" in result.stdout

        # generate + prompt
        result = runner.invoke(app, ["derive", "--generate", "--prompt"])
        assert result.exit_code == 2
        assert "Cannot use multiple input methods simultaneously" in result.stdout

        # mnemonic + prompt
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--prompt"])
        assert result.exit_code == 2
        assert "Cannot use multiple input methods simultaneously" in result.stdout

    def test_generate_passphrase_without_generate(self, runner: CliRunner) -> None:
        """Test that --generate-passphrase without --generate is rejected."""
        result = runner.invoke(app, ["derive", "--generate-passphrase", "--prompt"])
        assert result.exit_code == 2
        assert "--generate-passphrase can only be used with --generate" in result.stdout

    def test_words_without_generate(self, runner: CliRunner) -> None:
        """Test that --words without --generate is rejected."""
        result = runner.invoke(app, ["derive", "--words", "12", "--prompt"])
        assert result.exit_code == 2
        assert "--words can only be used with --generate" in result.stdout

    def test_encrypt_without_output_dir(self, runner: CliRunner, mnemonic: str) -> None:
        """Test that --encrypt without --output-dir is rejected."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--encrypt"])
        assert result.exit_code == 2
        assert "Cannot use --encrypt without --output-dir" in result.stdout

    def test_passphrase_with_prompt(self, runner: CliRunner) -> None:
        """Test that --passphrase with --prompt is rejected."""
        result = runner.invoke(app, ["derive", "--prompt", "--passphrase", "test"])
        assert result.exit_code == 2
        assert "Cannot use --passphrase with --prompt" in result.stdout


class TestDeriveParams:
    """Test Params class validation."""

    def test_params_validation_encrypt_without_output_dir(self) -> None:
        """Test Params validation for encrypt without output_dir."""
        params = Params(
            coin=Coin.ETH,
            mnemonic="test",
            passphrase=None,
            generate=False,
            generate_passphrase=False,
            prompt=False,
            words=24,
            derivation_path=None,
            limit=10,
            output_dir=None,
            encrypt=True,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()
        assert "Cannot use --encrypt without --output-dir" in str(exc_info.value)

    def test_params_validation_conflicting_methods(self) -> None:
        """Test Params validation for conflicting input methods."""
        params = Params(
            coin=Coin.ETH,
            mnemonic="test",
            passphrase=None,
            generate=True,  # conflict with mnemonic
            generate_passphrase=False,
            prompt=False,
            words=24,
            derivation_path=None,
            limit=10,
            output_dir=None,
            encrypt=False,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()
        assert "Cannot use multiple input methods simultaneously" in str(exc_info.value)


class TestDeriveEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_coin_type(self, runner: CliRunner, mnemonic: str) -> None:
        """Test that invalid coin types are rejected."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--coin", "INVALID"])
        assert result.exit_code == 2

    def test_invalid_words_count(self, runner: CliRunner) -> None:
        """Test that invalid word counts are rejected."""
        result = runner.invoke(app, ["derive", "--generate", "--words", "13"])  # invalid count
        assert result.exit_code == 2  # Parameter validation error
        assert "Words must be one of: 12, 15, 21, 24" in result.stdout

    def test_empty_output_directory_error(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test error when output directory is not empty."""
        # Create a non-empty directory
        test_dir = tmp_path / "not_empty"
        test_dir.mkdir()
        (test_dir / "existing_file.txt").write_text("test")

        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(test_dir)])
        assert result.exit_code == 1
        assert "is not empty" in result.stdout

    def test_invalid_mnemonic(self, runner: CliRunner) -> None:
        """Test that invalid mnemonic is rejected."""
        result = runner.invoke(app, ["derive", "--mnemonic", "invalid mnemonic phrase", "--limit", "1"])
        assert result.exit_code == 1  # Should fail validation

    def test_empty_mnemonic(self, runner: CliRunner) -> None:
        """Test that empty mnemonic is rejected."""
        result = runner.invoke(app, ["derive", "--mnemonic", "", "--limit", "1"])
        assert result.exit_code == 1


class TestDeriveIntegration:
    """Integration tests for derive command."""

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    @patch("mm_mnemonic.passphrase.typer.prompt")
    def test_full_workflow_generate_and_save(
        self, mock_passphrase_prompt: Mock, mock_derive_prompt: Mock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test complete workflow: generate, save, encrypt."""
        mock_derive_prompt.return_value = "test_passphrase"
        mock_passphrase_prompt.return_value = "encryption_password"

        result = runner.invoke(
            app, ["derive", "--generate", "--coin", "BTC", "--limit", "3", "--output-dir", str(tmp_path), "--encrypt"]
        )

        assert result.exit_code == 0

        # Verify encrypted file exists
        assert (tmp_path / "keys.toml.enc").exists()
        assert (tmp_path / "addresses.txt").exists()

        # Verify console output hides sensitive info
        assert "words (saved to file)" in result.stdout
        assert "yes (saved to file)" in result.stdout
        assert "Private Key" not in result.stdout

    def test_complete_deterministic_workflow(self, runner: CliRunner) -> None:
        """Test that complete workflow is deterministic with same inputs."""
        test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result1 = runner.invoke(
            app, ["derive", "--mnemonic", test_mnemonic, "--passphrase", "test", "--coin", "ETH", "--limit", "2"]
        )
        result2 = runner.invoke(
            app, ["derive", "--mnemonic", test_mnemonic, "--passphrase", "test", "--coin", "ETH", "--limit", "2"]
        )

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout  # Should be identical

    def test_cross_coin_different_addresses(self, runner: CliRunner) -> None:
        """Test that same mnemonic produces different addresses for different coins."""
        test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        eth_result = runner.invoke(app, ["derive", "--mnemonic", test_mnemonic, "--coin", "ETH", "--limit", "1"])
        btc_result = runner.invoke(app, ["derive", "--mnemonic", test_mnemonic, "--coin", "BTC", "--limit", "1"])

        assert eth_result.exit_code == 0
        assert btc_result.exit_code == 0
        assert eth_result.stdout != btc_result.stdout  # Different coins should produce different addresses
