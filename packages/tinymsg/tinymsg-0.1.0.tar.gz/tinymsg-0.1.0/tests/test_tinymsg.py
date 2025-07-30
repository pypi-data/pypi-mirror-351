from typing import Any, Dict, List, Optional

import pytest

from tinymsg import Message


class SimpleMessage(Message):
    """Test message with basic types."""

    name: str
    age: int
    active: bool


class NestedMessage(Message):
    """Test message with nested objects."""

    id: int
    data: SimpleMessage
    tags: List[str]


class ComplexMessage(Message):
    """Test message with complex nested structures."""

    users: List[SimpleMessage]
    metadata: Dict[str, Any]
    config: Optional[dict] = None


class EmptyMessage(Message):
    """Test message with no fields."""

    pass


class DefaultFieldsMessage(Message):
    """Test message with default values."""

    name: str
    count: int = 0
    enabled: bool = True
    items: List[str] = []


class TestBasicSerialization:
    """Test basic pack/unpack functionality."""

    def test_simple_message_roundtrip(self):
        """Test basic serialization and deserialization."""
        original = SimpleMessage(name="Alice", age=30, active=True)
        packed = original.pack()
        unpacked = SimpleMessage.unpack(packed)

        assert unpacked.name == "Alice"
        assert unpacked.age == 30
        assert unpacked.active is True
        assert unpacked == original

    def test_empty_message(self):
        """Test serialization of message with no fields."""
        original = EmptyMessage()
        packed = original.pack()
        unpacked = EmptyMessage.unpack(packed)

        assert unpacked == original

    def test_message_with_defaults(self):
        """Test serialization with default field values."""
        original = DefaultFieldsMessage(name="test")
        packed = original.pack()
        unpacked = DefaultFieldsMessage.unpack(packed)

        assert unpacked.name == "test"
        assert unpacked.count == 0
        assert unpacked.enabled is True
        assert unpacked.items == []

    def test_override_defaults(self):
        """Test serialization when overriding default values."""
        original = DefaultFieldsMessage(name="test", count=5, enabled=False, items=["a", "b"])
        packed = original.pack()
        unpacked = DefaultFieldsMessage.unpack(packed)

        assert unpacked.name == "test"
        assert unpacked.count == 5
        assert unpacked.enabled is False
        assert unpacked.items == ["a", "b"]


class TestNestedSerialization:
    """Test serialization with nested objects."""

    def test_nested_message(self):
        """Test serialization with nested Message objects."""
        simple = SimpleMessage(name="Bob", age=25, active=False)
        nested = NestedMessage(id=123, data=simple, tags=["tag1", "tag2"])

        packed = nested.pack()
        unpacked = NestedMessage.unpack(packed)

        assert unpacked.id == 123
        assert unpacked.data.name == "Bob"
        assert unpacked.data.age == 25
        assert unpacked.data.active is False
        assert unpacked.tags == ["tag1", "tag2"]

    def test_complex_nested_structure(self):
        """Test serialization with lists of objects and complex structures."""
        users = [
            SimpleMessage(name="Alice", age=30, active=True),
            SimpleMessage(name="Bob", age=25, active=False),
        ]
        metadata = {
            "version": "1.0",
            "created": "2024-01-01",
            "stats": {"count": 2, "active": 1},
        }

        complex_msg = ComplexMessage(users=users, metadata=metadata, config={"debug": True})

        packed = complex_msg.pack()
        unpacked = ComplexMessage.unpack(packed)

        assert len(unpacked.users) == 2
        assert unpacked.users[0].name == "Alice"
        assert unpacked.users[1].name == "Bob"
        assert unpacked.metadata["version"] == "1.0"
        assert unpacked.metadata["stats"]["count"] == 2
        assert unpacked.config["debug"] is True


class TestDataTypes:
    """Test various data types and edge cases."""

    def test_unicode_strings(self):
        """Test serialization with unicode strings."""
        msg = SimpleMessage(name="José María", age=30, active=True)
        packed = msg.pack()
        unpacked = SimpleMessage.unpack(packed)

        assert unpacked.name == "José María"

    def test_large_numbers(self):
        """Test serialization with large numbers."""
        msg = SimpleMessage(name="test", age=2147483647, active=True)
        packed = msg.pack()
        unpacked = SimpleMessage.unpack(packed)

        assert unpacked.age == 2147483647

    def test_empty_collections(self):
        """Test serialization with empty lists and dicts."""
        msg = ComplexMessage(users=[], metadata={})
        packed = msg.pack()
        unpacked = ComplexMessage.unpack(packed)

        assert unpacked.users == []
        assert unpacked.metadata == {}

    def test_none_values(self):
        """Test serialization with None values in optional fields."""
        msg = ComplexMessage(users=[], metadata={}, config=None)
        packed = msg.pack()
        unpacked = ComplexMessage.unpack(packed)

        assert unpacked.config is None


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_data_type(self):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SimpleMessage(name="test", age="not_a_number", active=True)

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SimpleMessage(age=30, active=True)  # missing name

    def test_corrupted_data_unpacking(self):
        """Test that corrupted data raises appropriate error."""
        with pytest.raises(Exception):  # msgpack or validation error
            SimpleMessage.unpack(b"corrupted_data")

    def test_wrong_message_type_unpacking(self):
        """Test unpacking with wrong message type."""
        simple = SimpleMessage(name="test", age=30, active=True)
        packed = simple.pack()

        # This should raise a validation error since NestedMessage expects different fields
        with pytest.raises(Exception):
            NestedMessage.unpack(packed)


class TestPerformance:
    """Basic performance and stress tests."""

    def test_large_list_serialization(self):
        """Test serialization with large lists."""
        users = [
            SimpleMessage(name=f"user_{i}", age=20 + i % 50, active=i % 2 == 0) for i in range(1000)
        ]

        msg = ComplexMessage(users=users, metadata={"count": 1000})
        packed = msg.pack()
        unpacked = ComplexMessage.unpack(packed)

        assert len(unpacked.users) == 1000
        assert unpacked.users[0].name == "user_0"
        assert unpacked.users[999].name == "user_999"

    def test_deep_nesting(self):
        """Test with deeply nested structures."""
        # Create nested structure: metadata with nested dicts
        metadata = {
            "level1": {
                "level2": {"level3": {"level4": {"data": "deep_value", "numbers": [1, 2, 3, 4, 5]}}}
            }
        }

        msg = ComplexMessage(users=[], metadata=metadata)
        packed = msg.pack()
        unpacked = ComplexMessage.unpack(packed)

        assert unpacked.metadata["level1"]["level2"]["level3"]["level4"]["data"] == "deep_value"


class TestEquality:
    """Test object equality after serialization."""

    def test_message_equality(self):
        """Test that messages are equal after round-trip serialization."""
        msg1 = SimpleMessage(name="test", age=30, active=True)
        msg2 = SimpleMessage(name="test", age=30, active=True)

        assert msg1 == msg2

        packed = msg1.pack()
        unpacked = SimpleMessage.unpack(packed)

        assert msg1 == unpacked
        assert msg2 == unpacked

    def test_complex_message_equality(self):
        """Test equality with complex nested structures."""
        users = [SimpleMessage(name="Alice", age=30, active=True)]
        msg1 = ComplexMessage(users=users, metadata={"test": True})

        packed = msg1.pack()
        msg2 = ComplexMessage.unpack(packed)

        assert msg1 == msg2
