"""Tests for configuration merging in layered_settings."""

from layered_settings.merger import ConfigMerger


class TestConfigMergerBasics:
    """Test basic merge operations."""

    def test_merge_empty_dicts(self):
        """Merging two empty dicts should return an empty dict."""
        result = ConfigMerger.merge({}, {})
        assert result == {}

    def test_merge_empty_base_with_override(self):
        """Merging empty base with override should return override content."""
        result = ConfigMerger.merge({}, {"key": "value"})
        assert result == {"key": "value"}

    def test_merge_base_with_empty_override(self):
        """Merging base with empty override should return base content."""
        result = ConfigMerger.merge({"key": "value"}, {})
        assert result == {"key": "value"}

    def test_adding_new_keys(self):
        """Override should add new keys to base."""
        base = {"existing": "value"}
        override = {"new": "data"}
        result = ConfigMerger.merge(base, override)
        assert result == {"existing": "value", "new": "data"}

    def test_adding_multiple_new_keys(self):
        """Override should add multiple new keys to base."""
        base = {"a": 1}
        override = {"b": 2, "c": 3}
        result = ConfigMerger.merge(base, override)
        assert result == {"a": 1, "b": 2, "c": 3}


class TestConfigMergerScalars:
    """Test merging scalar values."""

    def test_replacing_scalar_with_scalar(self):
        """Override should replace base scalar values."""
        base = {"key": "old"}
        override = {"key": "new"}
        result = ConfigMerger.merge(base, override)
        assert result == {"key": "new"}

    def test_replacing_integer(self):
        """Override should replace integer values."""
        base = {"count": 10}
        override = {"count": 20}
        result = ConfigMerger.merge(base, override)
        assert result == {"count": 20}

    def test_replacing_boolean(self):
        """Override should replace boolean values."""
        base = {"enabled": True}
        override = {"enabled": False}
        result = ConfigMerger.merge(base, override)
        assert result == {"enabled": False}

    def test_replacing_none(self):
        """Override should replace None values."""
        base = {"value": None}
        override = {"value": "something"}
        result = ConfigMerger.merge(base, override)
        assert result == {"value": "something"}


class TestConfigMergerLists:
    """Test merging list values (atomic replacement)."""

    def test_replacing_list_atomically(self):
        """Lists should be replaced entirely, not merged element-wise."""
        base = {"items": [1, 2]}
        override = {"items": [3]}
        result = ConfigMerger.merge(base, override)
        assert result == {"items": [3]}

    def test_replacing_empty_list_with_values(self):
        """Override should replace empty list with values."""
        base = {"items": []}
        override = {"items": [1, 2, 3]}
        result = ConfigMerger.merge(base, override)
        assert result == {"items": [1, 2, 3]}

    def test_replacing_list_with_empty_list(self):
        """Override should replace list with empty list."""
        base = {"items": [1, 2, 3]}
        override = {"items": []}
        result = ConfigMerger.merge(base, override)
        assert result == {"items": []}

    def test_list_not_merged_element_wise(self):
        """Verify lists are NOT merged element by element."""
        base = {"items": [1, 2]}
        override = {"items": [3, 4]}
        result = ConfigMerger.merge(base, override)
        # Should be [3, 4], NOT [1, 2, 3, 4]
        assert result == {"items": [3, 4]}
        assert result != {"items": [1, 2, 3, 4]}


class TestConfigMergerDicts:
    """Test merging nested dictionary values."""

    def test_recursively_merging_nested_dicts(self):
        """Nested dicts should be merged recursively."""
        base = {"db": {"host": "localhost", "port": 5432}}
        override = {"db": {"port": 3306}}
        result = ConfigMerger.merge(base, override)
        assert result == {"db": {"host": "localhost", "port": 3306}}

    def test_merging_deeply_nested_dicts(self):
        """Deep nesting should be merged recursively."""
        base = {"level1": {"level2": {"level3": {"a": 1, "b": 2}}}}
        override = {"level1": {"level2": {"level3": {"b": 99, "c": 3}}}}
        result = ConfigMerger.merge(base, override)
        assert result == {"level1": {"level2": {"level3": {"a": 1, "b": 99, "c": 3}}}}

    def test_adding_new_nested_dict(self):
        """Override should add new nested dicts."""
        base = {"existing": {"key": "value"}}
        override = {"new": {"nested": {"data": 123}}}
        result = ConfigMerger.merge(base, override)
        assert result == {
            "existing": {"key": "value"},
            "new": {"nested": {"data": 123}},
        }

    def test_merging_nested_dicts_with_multiple_keys(self):
        """Nested dicts with multiple keys should merge correctly."""
        base = {"database": {"host": "localhost", "port": 5432}, "cache": {"ttl": 3600}}
        override = {"database": {"port": 3306, "user": "admin"}, "cache": {"ttl": 7200}}
        result = ConfigMerger.merge(base, override)
        assert result == {
            "database": {"host": "localhost", "port": 3306, "user": "admin"},
            "cache": {"ttl": 7200},
        }


class TestConfigMergerTypeReplacement:
    """Test replacing values with different types."""

    def test_replacing_dict_with_scalar(self):
        """Override should replace dict with scalar."""
        base = {"config": {"nested": "value"}}
        override = {"config": "simple"}
        result = ConfigMerger.merge(base, override)
        assert result == {"config": "simple"}

    def test_replacing_scalar_with_dict(self):
        """Override should replace scalar with dict."""
        base = {"config": "simple"}
        override = {"config": {"nested": "value"}}
        result = ConfigMerger.merge(base, override)
        assert result == {"config": {"nested": "value"}}

    def test_replacing_list_with_dict(self):
        """Override should replace list with dict."""
        base = {"data": [1, 2, 3]}
        override = {"data": {"items": [1, 2, 3]}}
        result = ConfigMerger.merge(base, override)
        assert result == {"data": {"items": [1, 2, 3]}}

    def test_replacing_dict_with_list(self):
        """Override should replace dict with list."""
        base = {"data": {"items": [1, 2, 3]}}
        override = {"data": [1, 2, 3]}
        result = ConfigMerger.merge(base, override)
        assert result == {"data": [1, 2, 3]}


class TestConfigMergerImmutability:
    """Test that merge does not mutate input dicts."""

    def test_does_not_mutate_base(self):
        """Merge should not mutate the base dict."""
        base = {"key": "value", "nested": {"data": 1}}
        original_base = {"key": "value", "nested": {"data": 1}}
        override = {"key": "new", "nested": {"data": 2}}

        ConfigMerger.merge(base, override)

        assert base == original_base

    def test_does_not_mutate_override(self):
        """Merge should not mutate the override dict."""
        base = {"key": "value"}
        override = {"key": "new", "nested": {"data": 2}}
        original_override = {"key": "new", "nested": {"data": 2}}

        ConfigMerger.merge(base, override)

        assert override == original_override

    def test_result_is_independent_copy(self):
        """Modifying result should not affect inputs."""
        base = {"nested": {"value": 1}}
        override = {"nested": {"value": 2}}

        result = ConfigMerger.merge(base, override)
        result["nested"]["value"] = 999

        assert base == {"nested": {"value": 1}}
        assert override == {"nested": {"value": 2}}

    def test_modifying_base_after_merge(self):
        """Modifying base after merge should not affect result."""
        base = {"nested": {"value": 1}}
        override = {"nested": {"value": 2}}

        result = ConfigMerger.merge(base, override)
        base["nested"]["value"] = 999

        assert result == {"nested": {"value": 2}}

    def test_modifying_override_after_merge(self):
        """Modifying override after merge should not affect result."""
        base = {"nested": {"value": 1}}
        override = {"nested": {"value": 2}}

        result = ConfigMerger.merge(base, override)
        override["nested"]["value"] = 999

        assert result == {"nested": {"value": 2}}


class TestConfigMergerMultipleSequentialMerges:
    """Test performing multiple sequential merges."""

    def test_sequential_merges_build_up(self):
        """Multiple sequential merges should build up configuration."""
        layer1 = {"a": 1, "b": 2}
        layer2 = {"b": 20, "c": 3}
        layer3 = {"c": 30, "d": 4}

        result1 = ConfigMerger.merge(layer1, layer2)
        result2 = ConfigMerger.merge(result1, layer3)

        assert result2 == {"a": 1, "b": 20, "c": 30, "d": 4}

    def test_sequential_merges_with_nested_dicts(self):
        """Multiple sequential merges should work with nested dicts."""
        layer1 = {"db": {"host": "localhost", "port": 5432}}
        layer2 = {"db": {"port": 3306, "user": "user1"}}
        layer3 = {"db": {"user": "admin"}}

        result1 = ConfigMerger.merge(layer1, layer2)
        result2 = ConfigMerger.merge(result1, layer3)

        assert result2 == {"db": {"host": "localhost", "port": 3306, "user": "admin"}}

    def test_three_layer_merge(self):
        """Three-layer merge should work correctly."""
        defaults = {"server": {"host": "0.0.0.0", "port": 8000}, "debug": False}
        user_config = {
            "server": {"port": 9000},
            "debug": True,
            "logging": {"level": "INFO"},
        }
        cli_args = {"server": {"host": "127.0.0.1"}, "logging": {"level": "DEBUG"}}

        result1 = ConfigMerger.merge(defaults, user_config)
        result2 = ConfigMerger.merge(result1, cli_args)

        assert result2 == {
            "server": {"host": "127.0.0.1", "port": 9000},
            "debug": True,
            "logging": {"level": "DEBUG"},
        }
