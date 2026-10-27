import datetime
import warnings
from urllib.parse import urlencode

from stripe._stripe_object import StripeObject
from stripe._encode import _api_encode


class TestApiEncode:
    def test_encode_stripe_object_without_id_no_deprecation_warning(self):
        """
        Test that encoding a StripeObject without an id (like metadata)
        does not trigger a deprecation warning.
        Regression test for issue #1651.
        """
        metadata = StripeObject()
        metadata["key1"] = "value1"
        metadata["key2"] = "value2"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(_api_encode({"metadata": metadata}))

            # Check no deprecation warnings were raised
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) == 0, (
                f"Expected no deprecation warnings, but got {len(deprecation_warnings)}"
            )

        # Verify the metadata was encoded correctly as nested dict
        assert result == [
            ("metadata[key1]", "value1"),
            ("metadata[key2]", "value2"),
        ]

    def test_encode_stripe_object_with_id_extracts_id(self):
        """
        Test that encoding a StripeObject with an id (like a customer reference)
        correctly extracts just the id value.
        """
        customer = StripeObject()
        customer["id"] = "cus_123"
        customer["name"] = "Test Customer"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(_api_encode({"customer": customer}))

            # Check no deprecation warnings were raised
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) == 0, (
                f"Expected no deprecation warnings, but got {len(deprecation_warnings)}"
            )

        # Should encode to just the ID
        assert result == [("customer", "cus_123")]

    def test_encode_regular_dict(self):
        """Test that regular dicts are encoded as nested dicts."""
        regular_dict = {"key1": "value1", "key2": "value2"}
        result = list(_api_encode({"data": regular_dict}))

        assert result == [
            ("data[key1]", "value1"),
            ("data[key2]", "value2"),
        ]

    def test_encode_none_value_skipped(self):
        """Test that None values are skipped during encoding."""
        result = list(_api_encode({"field": None}))
        assert result == []

    def test_encode_string_value(self):
        """Test that string values are encoded directly."""
        result = list(_api_encode({"name": "John Doe"}))
        assert result == [("name", "John Doe")]

    def test_encode_boolean_value(self):
        """Test that boolean values are encoded as lowercase strings."""
        result = list(_api_encode({"active": True, "deleted": False}))
        assert result == [("active", "true"), ("deleted", "false")]

    def test_encode_list_value(self):
        """Test that list values are encoded with indexed keys."""
        result = list(_api_encode({"items": ["item1", "item2", "item3"]}))
        assert result == [
            ("items[0]", "item1"),
            ("items[1]", "item2"),
            ("items[2]", "item3"),
        ]

    def test_encode_nested_list_value(self):
        """Test that nested lists (2D arrays) are encoded with double indices."""
        result = list(_api_encode({"items": [[1, 2], [3, 4]]}))
        assert result == [
            ("items[0][0]", 1),
            ("items[0][1]", 2),
            ("items[1][0]", 3),
            ("items[1][1]", 4),
        ]

    def test_encode_mixed_nested_list_value(self):
        """Test that lists with mixed element types (dicts and nested lists) encode correctly."""
        result = list(
            _api_encode({"items": [{"foo": "bar", "baz": "qux"}, [3, 4]]})
        )
        assert result == [
            ("items[0][foo]", "bar"),
            ("items[0][baz]", "qux"),
            ("items[1][0]", 3),
            ("items[1][1]", 4),
        ]

    def test_encode_boolean_list_and_tuple_values(self):
        """Booleans that are direct list or tuple elements encode as lowercase strings."""
        for value in ([True, False], (True, False)):
            result = list(_api_encode({"flags": value}))
            assert result == [
                ("flags[0]", "true"),
                ("flags[1]", "false"),
            ]

    def test_encode_datetime_list_and_tuple_values(self):
        """Datetimes that are direct list or tuple elements encode as unix timestamps."""
        dt = datetime.datetime(
            2024, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc
        )
        for value in ([dt], (dt,)):
            result = list(_api_encode({"created": value}))
            assert result == [("created[0]", 1704164645)]

    def test_encode_nested_boolean_list_value(self):
        """Booleans inside nested lists still encode as lowercase strings."""
        result = list(_api_encode({"flags": [[True], [False]]}))
        assert result == [
            ("flags[0][0]", "true"),
            ("flags[1][0]", "false"),
        ]

    def test_urlencode_boolean_and_datetime_list_items(self):
        """List items match the form encoding used for top-level bools and datetimes."""
        dt = datetime.datetime(
            2024, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc
        )
        flags = urlencode(list(_api_encode({"flags": [True, False]})))
        created = urlencode(list(_api_encode({"created": [dt]})))
        assert flags == "flags%5B0%5D=true&flags%5B1%5D=false"
        assert created == "created%5B0%5D=1704164645"
