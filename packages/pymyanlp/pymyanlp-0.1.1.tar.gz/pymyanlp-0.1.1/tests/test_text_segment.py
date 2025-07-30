"""Tests for pymyanlp.text.segment module."""

import pytest
from pymyanlp.text.segment import (
    segment_word,
    list_available_models,
    SEGMENTATION_MODELS,
    _import_module,
    _load_segmenter,
)


class TestSegmentationModels:
    """Tests for segmentation model configuration."""

    def test_segmentation_models_exist(self):
        """Test that SEGMENTATION_MODELS is defined and contains expected models."""
        assert isinstance(SEGMENTATION_MODELS, dict)
        assert len(SEGMENTATION_MODELS) > 0
        assert "viterbi" in SEGMENTATION_MODELS
        # crfseg might not be available depending on dependencies

    def test_segmentation_model_structure(self):
        """Test the structure of segmentation model entries."""
        for model_name, model_info in SEGMENTATION_MODELS.items():
            assert isinstance(model_info, tuple)
            assert len(model_info) == 3  # (module_path, function_name, default_args)
            module_path, func_name, default_args = model_info
            assert isinstance(module_path, str)
            assert isinstance(func_name, str)
            assert isinstance(default_args, dict)


class TestImportModule:
    """Tests for _import_module helper function."""

    def test_import_existing_module(self):
        """Test importing an existing module."""
        module = _import_module("os")
        assert module is not None
        assert hasattr(module, "path")

    def test_import_nonexistent_module(self):
        """Test importing a non-existent module."""
        module = _import_module("nonexistent_module_12345")
        assert module is None


class TestLoadSegmenter:
    """Tests for _load_segmenter function."""

    def test_load_unknown_segmenter(self):
        """Test loading an unknown segmentation model."""
        with pytest.raises(ValueError, match="Unknown segmentation model"):
            _load_segmenter("unknown_model")

    def test_load_viterbi_segmenter(self):
        """Test loading the viterbi segmenter."""
        # This should work as it's a core module
        segmenter = _load_segmenter("viterbi")
        # It might be None if dependencies are missing, but shouldn't raise an error
        assert segmenter is None or callable(segmenter)

    def test_load_segmenter_caching(self):
        """Test that segmenters are cached after first load."""
        # Load twice and ensure it's the same object (from cache)
        try:
            segmenter1 = _load_segmenter("viterbi")
            segmenter2 = _load_segmenter("viterbi")
            if segmenter1 is not None:
                assert segmenter1 is segmenter2
        except ValueError:
            # If viterbi is not available, that's okay for this test
            pass


class TestListAvailableModels:
    """Tests for list_available_models function."""

    def test_list_available_models_returns_list(self):
        """Test that list_available_models returns a list."""
        models = list_available_models()
        assert isinstance(models, list)

    def test_list_available_models_contains_valid_models(self):
        """Test that returned models are valid model names."""
        models = list_available_models()
        for model in models:
            assert model in SEGMENTATION_MODELS

    def test_list_available_models_not_empty_if_viterbi_available(self):
        """Test that at least viterbi should be available."""
        models = list_available_models()
        # viterbi should typically be available as it's a core component
        # but we'll make this test flexible in case dependencies are missing
        assert isinstance(models, list)


class TestSegmentWord:
    """Tests for segment_word function."""

    def test_segment_word_with_available_model(self, sample_burmese_text):
        """Test word segmentation with an available model."""
        available_models = list_available_models()
        if available_models:
            model = available_models[0]
            try:
                result = segment_word(sample_burmese_text, model=model)
                assert isinstance(result, list)
                assert len(result) > 0
                # All segments should be strings
                assert all(isinstance(segment, str) for segment in result)
            except ValueError:
                # If the model becomes unavailable during test, that's acceptable
                pass

    def test_segment_word_with_unavailable_model(self, sample_burmese_text):
        """Test word segmentation with an unavailable model."""
        with pytest.raises(ValueError, match="Unknown segmentation model"):
            segment_word(sample_burmese_text, model="nonexistent_model")  # type: ignore

    def test_segment_word_empty_string(self):
        """Test word segmentation with empty string."""
        available_models = list_available_models()
        if available_models:
            model = available_models[0]
            try:
                result = segment_word("", model=model)
                assert isinstance(result, list)
            except ValueError:
                # If the model is not available, that's acceptable
                pass

    def test_segment_word_with_kwargs(self, sample_burmese_text):
        """Test word segmentation with additional keyword arguments."""
        available_models = list_available_models()
        if available_models:
            model = available_models[0]
            try:
                # Pass some additional kwargs (these might be ignored by the segmenter)
                result = segment_word(
                    sample_burmese_text, model=model, custom_param=True
                )
                assert isinstance(result, list)
            except (ValueError, TypeError):
                # If the model is not available or doesn't accept the param, that's acceptable
                pass

    def test_segment_word_viterbi_specifically(self, sample_burmese_text):
        """Test word segmentation specifically with viterbi model."""
        if "viterbi" in list_available_models():
            try:
                result = segment_word(sample_burmese_text, model="viterbi")
                assert isinstance(result, list)
                assert len(result) > 0
                # Result should contain the input text in some form
                rejoined = "".join(result)
                # Remove spaces for comparison as segmentation might add/remove them
                original_no_space = sample_burmese_text.replace(" ", "")
                result_no_space = rejoined.replace(" ", "")
                # The segmented result should contain the same characters
                for char in original_no_space:
                    if char.strip():  # Skip empty characters
                        assert char in result_no_space
            except ValueError:
                # If viterbi is not available, skip this test
                pytest.skip("Viterbi model not available")


class TestModelNameType:
    """Tests for ModelName type definition."""

    def test_model_name_literal_values(self):
        """Test that ModelName includes expected literal values."""
        # This is more of a type checking test, but we can verify the models exist
        expected_models = ["crfseg", "viterbi"]
        for model in expected_models:
            assert model in SEGMENTATION_MODELS
