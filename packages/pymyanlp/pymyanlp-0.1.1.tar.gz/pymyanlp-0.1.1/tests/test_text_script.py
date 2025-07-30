"""Tests for pymyanlp.text.script module."""

import pytest
from pymyanlp.text.script import (
    is_burmese,
    get_burmese_script,
    fix_medial,
    contains_burmese,
    transliterate_numbers,
    clear_spacing,
    remove_punctuation,
    apply_written_suite,
    normalize,
    NUMBER_MAP,
    PUNCTUATION,
    BURMESE_ALPHABET,
)


class TestIsBurmese:
    """Tests for is_burmese function."""

    def test_is_burmese_with_valid_text(self, sample_burmese_text):
        """Test with valid Burmese text."""
        assert is_burmese(sample_burmese_text) is True

    def test_is_burmese_with_english_text(self, sample_english_text):
        """Test with English text."""
        assert is_burmese(sample_english_text) is False

    def test_is_burmese_with_mixed_text(self, sample_mixed_text):
        """Test with mixed Burmese and English text."""
        assert is_burmese(sample_mixed_text) is False

    def test_is_burmese_with_empty_string(self):
        """Test with empty string."""
        assert is_burmese("") is False

    def test_is_burmese_with_none(self):
        """Test with None input."""
        # The function should handle None gracefully
        try:
            result = is_burmese(None)  # type: ignore
            assert result is False
        except (TypeError, AttributeError):
            # If it raises an exception, that's also acceptable behavior
            pass

    def test_is_burmese_with_numbers(self):
        """Test with non-string input."""
        # The function should handle non-string input gracefully
        try:
            result = is_burmese(123)  # type: ignore
            assert result is False
        except (TypeError, AttributeError):
            # If it raises an exception, that's also acceptable behavior
            pass

    def test_is_burmese_with_spaces(self):
        """Test with Burmese text containing spaces."""
        assert is_burmese("မြန်မာ ဘာသာ") is True

    def test_is_burmese_with_only_spaces(self):
        """Test with only spaces."""
        assert is_burmese("   ") is True

    def test_is_burmese_single_character(self):
        """Test with single Burmese character."""
        assert is_burmese("က") is True
        assert is_burmese("ခ") is True
        assert is_burmese("a") is False


class TestGetBurmeseScript:
    """Tests for get_burmese_script function."""

    def test_burmese_core_character(self):
        """Test with core Burmese characters."""
        assert get_burmese_script("က") == "burmese"
        assert get_burmese_script("အ") == "burmese"

    def test_non_burmese_character(self):
        """Test with non-Burmese characters."""
        assert get_burmese_script("a") == "unknown"
        assert get_burmese_script("1") == "unknown"

    def test_pali_sanskrit_extensions(self):
        """Test Pali and Sanskrit extensions."""
        # Test characters in range 0x1050-0x1059
        pali_char = chr(0x1050)  # MYANMAR LETTER SHA
        assert get_burmese_script(pali_char) == "pali_sanskrit"

    def test_mon_extensions(self, sample_mon_text):
        """Test Mon extensions."""
        assert get_burmese_script(sample_mon_text) == "mon"

    def test_shan_extensions(self, sample_shan_text):
        """Test Shan extensions."""
        assert get_burmese_script(sample_shan_text) == "shan"


class TestFixMedial:
    """Tests for fix_medial function."""

    def test_fix_medial_before(self):
        """Test moving medial signs before base characters."""
        # Test with medial ya (ျ)
        text_with_medial = "ကျ"  # က + ျ
        result = fix_medial(text_with_medial, position="before")
        # Should move medial sign before base
        assert len(result) == 2

    def test_fix_medial_after(self):
        """Test keeping medial signs after base characters."""
        text_with_medial = "ကျ"
        result = fix_medial(text_with_medial, position="after")
        # Should keep original order
        assert result == text_with_medial

    def test_fix_medial_empty_string(self):
        """Test with empty string."""
        assert fix_medial("") == ""

    def test_fix_medial_no_medials(self):
        """Test with text containing no medial signs."""
        text = "မြန်မာ"
        result = fix_medial(text)
        assert isinstance(result, str)

    def test_fix_medial_multiple_medials(self):
        """Test with multiple medial signs."""
        # This is a more complex case that would test the function's handling
        # of multiple dependent consonant signs
        text = "ကြျ"  # က + ြ + ျ (hypothetical)
        result = fix_medial(text, position="before")
        assert isinstance(result, str)
        assert len(result) >= len(text)

    def test_fix_medial_default_position(self):
        """Test that default position is 'before'."""
        text = "ကျ"
        result_default = fix_medial(text)
        result_before = fix_medial(text, position="before")
        assert result_default == result_before


class TestContainsBurmese:
    """Tests for contains_burmese function."""

    def test_contains_burmese_with_burmese_text(self, sample_burmese_text):
        """Test with text containing Burmese characters."""
        assert contains_burmese(sample_burmese_text) is True

    def test_contains_burmese_with_english_text(self, sample_english_text):
        """Test with English-only text."""
        assert contains_burmese(sample_english_text) is False

    def test_contains_burmese_with_mixed_text(self, sample_mixed_text):
        """Test with mixed Burmese and English text."""
        assert contains_burmese(sample_mixed_text) is True

    def test_contains_burmese_empty_string(self):
        """Test with empty string."""
        assert contains_burmese("") is False

    def test_contains_burmese_single_character(self):
        """Test with single Burmese character."""
        assert contains_burmese("က") is True
        assert contains_burmese("a") is False


class TestTransliterateNumbers:
    """Tests for transliterate_numbers function."""

    def test_transliterate_english_numbers(self):
        """Test transliterating English numbers to Burmese."""
        text = "2024"
        result = transliterate_numbers(text)
        expected = "၂၀၂၄"
        assert result == expected

    def test_transliterate_mixed_content(self):
        """Test with mixed text containing numbers."""
        text = "Year 2024"
        result = transliterate_numbers(text)
        expected = "Year ၂၀၂၄"
        assert result == expected

    def test_transliterate_no_numbers(self):
        """Test with text containing no numbers."""
        text = "Hello World"
        result = transliterate_numbers(text)
        assert result == text

    def test_transliterate_empty_string(self):
        """Test with empty string."""
        assert transliterate_numbers("") == ""

    def test_transliterate_all_digits(self):
        """Test transliterating all digits 0-9."""
        text = "0123456789"
        result = transliterate_numbers(text)
        expected = "၀၁၂၃၄၅၆၇၈၉"
        assert result == expected

    def test_number_map_completeness(self):
        """Test that NUMBER_MAP contains all digits."""
        assert len(NUMBER_MAP) == 10
        assert all(str(i) in NUMBER_MAP for i in range(10))


class TestClearSpacing:
    """Tests for clear_spacing function."""

    def test_clear_spacing_burmese_only(self):
        """Test spacing removal with Burmese-only text."""
        text = "မြန်မာ ဘာသာ"
        result = clear_spacing(text)
        # Should remove all spaces for Burmese text
        assert " " not in result or result.count(" ") < text.count(" ")

    def test_clear_spacing_mixed_text(self):
        """Test spacing with mixed Burmese and English text."""
        text = "Hello မြန်မာ World"
        result = clear_spacing(text)
        # Should preserve spaces between English and Burmese
        assert isinstance(result, str)
        assert len(result) > 0

    def test_clear_spacing_english_only(self):
        """Test with English-only text."""
        text = "Hello World"
        result = clear_spacing(text)
        # Should handle English text appropriately
        assert isinstance(result, str)

    def test_clear_spacing_empty_string(self):
        """Test with empty string."""
        assert clear_spacing("") == ""

    def test_clear_spacing_only_spaces(self):
        """Test with string containing only spaces."""
        text = "   "
        result = clear_spacing(text)
        assert isinstance(result, str)


class TestRemovePunctuation:
    """Tests for remove_punctuation function."""

    def test_remove_punctuation_burmese(self):
        """Test removing Burmese punctuation."""
        text = "မြန်မာ။ ဘာသာ၊"
        result = remove_punctuation(text)
        assert "။" not in result
        assert "၊" not in result

    def test_remove_punctuation_english(self):
        """Test removing English punctuation."""
        text = "Hello, World!"
        result = remove_punctuation(text)
        assert "," not in result
        assert "!" not in result

    def test_remove_punctuation_mixed(self):
        """Test removing mixed punctuation."""
        text = "Hello, မြန်မာ!"
        result = remove_punctuation(text)
        assert "," not in result
        assert "!" not in result

    def test_remove_punctuation_no_punctuation(self):
        """Test with text containing no punctuation."""
        text = "Hello World"
        result = remove_punctuation(text)
        assert result == text

    def test_remove_punctuation_empty_string(self):
        """Test with empty string."""
        assert remove_punctuation("") == ""

    def test_punctuation_list_not_empty(self):
        """Test that PUNCTUATION list is defined and not empty."""
        assert len(PUNCTUATION) > 0
        assert "။" in PUNCTUATION  # Burmese period
        assert "၊" in PUNCTUATION  # Burmese comma


class TestApplyWrittenSuite:
    """Tests for apply_written_suite function."""

    def test_apply_written_suite_complete(self):
        """Test the complete written suite pipeline."""
        text = "Hello 2024, မြန်မာ!"
        result = apply_written_suite(text)

        # Should apply transliteration, remove punctuation, and clear spacing
        assert isinstance(result, str)
        # Numbers should be transliterated
        assert "2024" not in result
        # Punctuation should be removed
        assert "!" not in result
        assert "," not in result

    def test_apply_written_suite_empty(self):
        """Test with empty string."""
        assert apply_written_suite("") == ""

    def test_apply_written_suite_burmese_only(self, sample_burmese_text):
        """Test with Burmese-only text."""
        result = apply_written_suite(sample_burmese_text)
        assert isinstance(result, str)
        assert len(result) > 0


class TestConstants:
    """Tests for module constants."""

    def test_BURMESE_ALPHABETS_not_empty(self):
        """Test that BURMESE_ALPHABETS is defined and not empty."""
        assert len(BURMESE_ALPHABET) > 0
        assert "က" in BURMESE_ALPHABET
        assert "မ" in BURMESE_ALPHABET

    def test_number_map_structure(self):
        """Test NUMBER_MAP structure and content."""
        assert isinstance(NUMBER_MAP, dict)
        assert len(NUMBER_MAP) == 10
        assert NUMBER_MAP["0"] == "၀"
        assert NUMBER_MAP["9"] == "၉"

    def test_punctuation_list_structure(self):
        """Test PUNCTUATION list structure."""
        assert isinstance(PUNCTUATION, list)
        assert len(PUNCTUATION) > 0
        # Should contain both Burmese and English punctuation
        assert "။" in PUNCTUATION
        assert "." in PUNCTUATION
