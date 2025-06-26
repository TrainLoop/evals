"""Constants for benchmark command."""

# ANSI helpers for console output
OK = "\033[32m✓\033[0m"
BAD = "\033[31m✗\033[0m"
INFO_COLOR = "\033[94m"
HEADER_COLOR = "\033[95m"
EMPHASIS_COLOR = "\033[93m"
RESET_COLOR = "\033[0m"

# Emojis
EMOJI_ROCKET = "🚀"
EMOJI_GRAPH = "📊"
EMOJI_SAVE = "💾"
EMOJI_CHECK = "✅"
EMOJI_WARNING = "⚠️"

# Provider key mapping
PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "cohere": "COHERE_API_KEY",
    "google": "GEMINI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "together": "TOGETHER_API_KEY",
    "anyscale": "ANYSCALE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "deepinfra": "DEEPINFRA_API_KEY",
    "replicate": "REPLICATE_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "azure": "AZURE_API_KEY",
    "bedrock": "AWS_ACCESS_KEY_ID",  # Also needs AWS_SECRET_ACCESS_KEY
}

# Default providers
DEFAULT_PROVIDERS = [
    "openai/gpt-4o",
    "anthropic/claude-3-sonnet-20240229",
    "gemini/gemini-2.0-flash",
]
