import pytest


@pytest.mark.asyncio
async def test_sample_function():
    """Sample test to verify pytest setup"""
    assert True


def test_basic_functionality():
    """Basic functionality test"""
    result = 1 + 1
    assert result == 2


class TestSampleClass:
    """Sample test class"""

    def test_method(self):
        """Test method in class"""
        assert "iTechSmart" in "iTechSmart Suite"

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            (1, 2),
            (2, 3),
            (3, 4),
        ],
    )
    def test_parametrized(self, input_value, expected):
        """Parametrized test example"""
        assert input_value + 1 == expected
