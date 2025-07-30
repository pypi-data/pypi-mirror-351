from .hivetrace import (
    HivetraceSDK,
    InvalidParameterError,
    MissingConfigError,
    UnauthorizedError,
)

try:
    from hivetrace.crewai_adapter import CrewAIAdapter, trace

    __all__ = ["CrewAIAdapter", "trace"]


except ImportError:
    __all__ = [
        "HivetraceSDK",
        "InvalidParameterError",
        "MissingConfigError",
        "UnauthorizedError",
    ]
