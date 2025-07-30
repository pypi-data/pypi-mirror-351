import importlib.util
from typing import List, Dict, Any, Callable, Optional, Literal


# Dictionary of available segmentation models
# Keys are model names, values are (module_path, function_name, default_args) tuples
SEGMENTATION_MODELS = {
    "crfseg": ("pymyanlp.lib.mmcrfseg", "segment_word", {}),
    "viterbi": ("pymyanlp.lib.myword", "segment_text", {})
}

# Define a type for model names
ModelName = Literal["crfseg", "viterbi"]

# Keep track of loaded segmentation functions
_loaded_segmenters: Dict[str, Callable] = {}

# Default segmentation model
_default_model: ModelName = "viterbi"


def _import_module(module_path: str) -> Optional[Any]:
    """
    Safely import a module without raising an exception if it's not available.

    Args:
        module_path: The module path to import.

    Returns:
        The imported module or None if not available.
    """
    try:
        return importlib.import_module(module_path)
    except ImportError:
        return None


def _load_segmenter(model_name: str) -> Optional[Callable]:
    """
    Load a segmentation function by model name.

    Args:
        model_name: Name of the segmentation model to load.

    Returns:
        The segmentation function or None if not available.
    """
    if model_name in _loaded_segmenters:
        return _loaded_segmenters[model_name]

    if model_name not in SEGMENTATION_MODELS:
        raise ValueError(f"Unknown segmentation model: {model_name}. Available models: {list(SEGMENTATION_MODELS.keys())}")

    module_path, func_name, _ = SEGMENTATION_MODELS[model_name]
    module = _import_module(module_path)

    if module is None:
        return None

    func = getattr(module, func_name, None)
    if func is not None:
        _loaded_segmenters[model_name] = func

    return func


def list_available_models() -> List[ModelName]:
    """
    List names of available segmentation models.

    Returns:
        List of model names that are currently available (dependencies installed).
    """
    available = []
    for model_name in SEGMENTATION_MODELS:
        if _load_segmenter(model_name) is not None:
            available.append(model_name)
    return available


def set_default_model(model_name: ModelName) -> None:
    """
    Set the default segmentation model.

    Args:
        model_name: Name of the model to use as default.

    Raises:
        ValueError: If the model is not available.
    """
    global _default_model

    if _load_segmenter(model_name) is None:
        raise ValueError(f"Model '{model_name}' is not available. Make sure its dependencies are installed.")

    _default_model = model_name


def segment_word(
    text: str,
    model: ModelName = "viterbi",
    **kwargs
) -> List[str]:
    """
    Segment text into words using the specified segmentation model.

    Args:
        text: The text to segment.
        model: Name of the segmentation model to use. If None, the default model is used.
              Valid values are: "crfseg", "viterbi"
        **kwargs: Additional arguments passed to the segmentation function.

    Returns:
        List of segmented words or original text if segmentation failed.

    Raises:
        ValueError: If the specified model is not recognized.
    """
    # Use default model if none specified
    model_name = model or _default_model

    # Load the segmentation function
    segmenter = _load_segmenter(model_name)
    if segmenter is None:
        # If the model is not available, return the original text
        raise ValueError(f"Model '{model_name}' is not available. Make sure its dependencies are installed.")

    default_args = SEGMENTATION_MODELS[model_name][2]
    args = {**default_args, **kwargs}

    return segmenter(text, **args)
