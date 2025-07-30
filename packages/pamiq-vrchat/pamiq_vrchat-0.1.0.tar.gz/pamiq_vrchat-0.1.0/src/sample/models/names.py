from enum import StrEnum


class ModelName(StrEnum):
    """Enumerates all model names in experiments."""

    IMAGE_JEPA_CONTEXT_ENCODER = "image_jepa_context_encoder"
    IMAGE_JEPA_TARGET_ENCODER = "image_jepa_target_encoder"
    IMAGE_JEPA_PREDICTOR = "image_jepa_predictor"

    AUDIO_JEPA_CONTEXT_ENCODER = "audio_jepa_context_encoder"
    AUDIO_JEPA_TARGET_ENCODER = "audio_jepa_target_encoder"
    AUDIO_JEPA_PREDICTOR = "audio_jepa_predictor"

    TEMPORAL_ENCODER = "temporal_encoder"

    FORWARD_DYNAMICS = "forward_dynamics"

    POLICY_VALUE = "policy_value"
