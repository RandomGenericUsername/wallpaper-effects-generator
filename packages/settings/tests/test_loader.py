"""Tests for file loader functionality."""

from pathlib import Path

import pytest

from layered_settings.errors import SettingsFileError
from layered_settings.loader import FileLoader


class TestFormatDetection:
    """Test format detection from file extensions."""

    def test_detect_toml_format(self, tmp_path: Path) -> None:
        """Test detection of .toml files."""
        filepath = tmp_path / "config.toml"
        filepath.touch()

        assert FileLoader.detect_format(filepath) == "toml"

    def test_detect_yaml_format(self, tmp_path: Path) -> None:
        """Test detection of .yaml files."""
        filepath = tmp_path / "config.yaml"
        filepath.touch()

        assert FileLoader.detect_format(filepath) == "yaml"

    def test_detect_yml_format(self, tmp_path: Path) -> None:
        """Test detection of .yml files."""
        filepath = tmp_path / "config.yml"
        filepath.touch()

        assert FileLoader.detect_format(filepath) == "yaml"

    def test_detect_unsupported_format(self, tmp_path: Path) -> None:
        """Test error for unsupported file extensions."""
        filepath = tmp_path / "config.json"
        filepath.touch()

        with pytest.raises(SettingsFileError, match="Unsupported file format"):
            FileLoader.detect_format(filepath)

    def test_detect_no_extension(self, tmp_path: Path) -> None:
        """Test error for files without extensions."""
        filepath = tmp_path / "config"
        filepath.touch()

        with pytest.raises(SettingsFileError, match="Unsupported file format"):
            FileLoader.detect_format(filepath)


class TestTOMLLoading:
    """Test loading TOML files."""

    @pytest.fixture
    def toml_file(self, tmp_path: Path) -> Path:
        """Create a valid TOML file for testing."""
        filepath = tmp_path / "config.toml"
        content = """
# Test configuration
[database]
host = "localhost"
port = 5432
enabled = true

[database.credentials]
username = "admin"
password = "secret"

[features]
items = ["item1", "item2", "item3"]
count = 42
ratio = 3.14
"""
        filepath.write_text(content)
        return filepath

    def test_load_valid_toml(self, toml_file: Path) -> None:
        """Test loading a valid TOML file."""
        result = FileLoader.load(toml_file)

        assert isinstance(result, dict)
        assert "database" in result
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        assert result["database"]["enabled"] is True
        assert result["database"]["credentials"]["username"] == "admin"
        assert result["features"]["items"] == ["item1", "item2", "item3"]
        assert result["features"]["count"] == 42
        assert result["features"]["ratio"] == 3.14

    def test_load_empty_toml(self, tmp_path: Path) -> None:
        """Test loading an empty TOML file."""
        filepath = tmp_path / "empty.toml"
        filepath.write_text("")

        result = FileLoader.load(filepath)
        assert result == {}

    def test_load_invalid_toml_syntax(self, tmp_path: Path) -> None:
        """Test error for invalid TOML syntax."""
        filepath = tmp_path / "invalid.toml"
        filepath.write_text("[section\ninvalid = syntax")

        with pytest.raises(SettingsFileError, match="Failed to parse TOML file"):
            FileLoader.load(filepath)

    def test_load_toml_with_nested_tables(self, tmp_path: Path) -> None:
        """Test loading TOML with complex nested structures."""
        filepath = tmp_path / "nested.toml"
        content = """
[section.subsection.deep]
value = "nested"

[[array_of_tables]]
name = "first"

[[array_of_tables]]
name = "second"
"""
        filepath.write_text(content)

        result = FileLoader.load(filepath)
        assert result["section"]["subsection"]["deep"]["value"] == "nested"
        assert len(result["array_of_tables"]) == 2
        assert result["array_of_tables"][0]["name"] == "first"
        assert result["array_of_tables"][1]["name"] == "second"


class TestYAMLLoading:
    """Test loading YAML files."""

    @pytest.fixture
    def yaml_file(self, tmp_path: Path) -> Path:
        """Create a valid YAML file for testing."""
        filepath = tmp_path / "config.yaml"
        content = """
# Test configuration
database:
  host: localhost
  port: 5432
  enabled: true
  credentials:
    username: admin
    password: secret

features:
  items:
    - item1
    - item2
    - item3
  count: 42
  ratio: 3.14
"""
        filepath.write_text(content)
        return filepath

    def test_load_valid_yaml(self, yaml_file: Path) -> None:
        """Test loading a valid YAML file."""
        result = FileLoader.load(yaml_file)

        assert isinstance(result, dict)
        assert "database" in result
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        assert result["database"]["enabled"] is True
        assert result["database"]["credentials"]["username"] == "admin"
        assert result["features"]["items"] == ["item1", "item2", "item3"]
        assert result["features"]["count"] == 42
        assert result["features"]["ratio"] == 3.14

    def test_load_yaml_with_yml_extension(self, tmp_path: Path) -> None:
        """Test loading YAML file with .yml extension."""
        filepath = tmp_path / "config.yml"
        filepath.write_text("key: value\nnumber: 123")

        result = FileLoader.load(filepath)
        assert result["key"] == "value"
        assert result["number"] == 123

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        """Test loading an empty YAML file."""
        filepath = tmp_path / "empty.yaml"
        filepath.write_text("")

        result = FileLoader.load(filepath)
        assert result is None or result == {}

    def test_load_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        """Test error for invalid YAML syntax."""
        filepath = tmp_path / "invalid.yaml"
        filepath.write_text("key: value\n  invalid: indentation\n back: here")

        with pytest.raises(SettingsFileError, match="Failed to parse YAML file"):
            FileLoader.load(filepath)

    def test_load_yaml_with_complex_types(self, tmp_path: Path) -> None:
        """Test loading YAML with various data types."""
        filepath = tmp_path / "types.yaml"
        content = """
null_value: null
bool_true: true
bool_false: false
integer: 42
float: 3.14
string: "hello"
list: [1, 2, 3]
nested:
  deep:
    value: "found"
"""
        filepath.write_text(content)

        result = FileLoader.load(filepath)
        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False
        assert result["integer"] == 42
        assert result["float"] == 3.14
        assert result["string"] == "hello"
        assert result["list"] == [1, 2, 3]
        assert result["nested"]["deep"]["value"] == "found"


class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test error when file does not exist."""
        filepath = tmp_path / "nonexistent.toml"

        with pytest.raises(SettingsFileError, match="File not found"):
            FileLoader.load(filepath)

    def test_load_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test error when path is a directory."""
        dirpath = tmp_path / "directory.toml"
        dirpath.mkdir()

        with pytest.raises(SettingsFileError, match="is not a file"):
            FileLoader.load(dirpath)

    def test_load_unsupported_format(self, tmp_path: Path) -> None:
        """Test error for unsupported file format."""
        filepath = tmp_path / "config.ini"
        filepath.write_text("[section]\nkey=value")

        with pytest.raises(SettingsFileError, match="Unsupported file format"):
            FileLoader.load(filepath)

    def test_load_unreadable_file(self, tmp_path: Path) -> None:
        """Test error for file read permission issues."""
        filepath = tmp_path / "protected.toml"
        filepath.write_text("key = 'value'")
        filepath.chmod(0o000)

        try:
            with pytest.raises(SettingsFileError, match="Failed to read file"):
                FileLoader.load(filepath)
        finally:
            # Restore permissions for cleanup
            filepath.chmod(0o644)


class TestIntegration:
    """Integration tests for complete loading workflows."""

    def test_load_multiple_formats(self, tmp_path: Path) -> None:
        """Test loading different formats with same data."""
        # Create TOML file
        toml_file = tmp_path / "config.toml"
        toml_file.write_text('[section]\nkey = "value"\ncount = 42')

        # Create YAML file
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("section:\n  key: value\n  count: 42")

        # Load both and verify structure
        toml_result = FileLoader.load(toml_file)
        yaml_result = FileLoader.load(yaml_file)

        assert toml_result["section"]["key"] == yaml_result["section"]["key"]
        assert toml_result["section"]["count"] == yaml_result["section"]["count"]

    def test_load_realistic_config(self, tmp_path: Path) -> None:
        """Test loading a realistic configuration file."""
        filepath = tmp_path / "app_config.toml"
        content = """
[app]
name = "MyApp"
version = "1.0.0"
debug = false

[app.logging]
level = "INFO"
file = "/var/log/app.log"

[database]
host = "db.example.com"
port = 5432
name = "production"

[database.pool]
min_connections = 5
max_connections = 20
timeout = 30.0

[features]
enabled = ["auth", "api", "admin"]
experimental = []
"""
        filepath.write_text(content)

        result = FileLoader.load(filepath)

        assert result["app"]["name"] == "MyApp"
        assert result["app"]["version"] == "1.0.0"
        assert result["app"]["debug"] is False
        assert result["app"]["logging"]["level"] == "INFO"
        assert result["database"]["port"] == 5432
        assert result["database"]["pool"]["max_connections"] == 20
        assert "auth" in result["features"]["enabled"]
        assert result["features"]["experimental"] == []
