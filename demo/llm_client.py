"""Minimal LLM provider wrapper. Default provider: Anthropic (Claude).

A thin seam so a second model can be slotted in later for the proposal's
required >=2-model comparison. For this demo only Anthropic is wired up.
"""
import os

DEFAULT_MODEL = "claude-sonnet-4-6"


class LLMError(RuntimeError):
    pass


class AnthropicClient:
    def __init__(self, model=DEFAULT_MODEL, temperature=0.0, max_tokens=4000):
        try:
            import anthropic
        except ImportError as e:  # spec 3.4 analog: missing dependency, clear message
            raise LLMError("anthropic SDK not installed. Run: py -m pip install anthropic") from e
        if not os.environ.get("ANTHROPIC_API_KEY"):  # spec 3.3: key checked up-front
            raise LLMError("ANTHROPIC_API_KEY is not set in the environment.")
        self._anthropic = anthropic
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic()

    def generate(self, system, user):
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,  # 0 = reproducible (valid on Sonnet 4.6)
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except self._anthropic.APIError as e:  # spec 3.3: no raw stack trace to user
            raise LLMError(f"Anthropic API call failed: {e}") from e
        return "".join(b.text for b in resp.content if b.type == "text")

    def validate_credentials(self):
        """Reject invalid credentials before the task batch starts."""
        try:
            self.client.models.list(limit=1, timeout=10.0)
        except (
            self._anthropic.AuthenticationError,
            self._anthropic.PermissionDeniedError,
        ) as e:
            raise LLMError("ANTHROPIC_API_KEY was rejected by Anthropic.") from e
        except self._anthropic.APIError as e:
            return f"credential check unavailable ({type(e).__name__}); continuing"
        return "Anthropic credentials accepted"


def make_client(provider="anthropic", model=DEFAULT_MODEL, temperature=0.0):
    if provider != "anthropic":
        raise LLMError(f"Unknown provider '{provider}'. Only 'anthropic' is wired up for the demo.")
    return AnthropicClient(model=model, temperature=temperature)
