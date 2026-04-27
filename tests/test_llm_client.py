from types import SimpleNamespace

import pytest

from src import llm_client


class FakeResponses:
    def __init__(self, output_text="openai output"):
        self.calls = []
        self.output_text = output_text

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeChatCompletions:
    def __init__(self, content="local output"):
        self.calls = []
        self.content = content

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content),
                )
            ]
        )


class FakeOpenAI:
    instances = []
    responses = FakeResponses()
    chat_completions = FakeChatCompletions()

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.responses = self.__class__.responses
        self.chat = SimpleNamespace(completions=self.__class__.chat_completions)
        self.__class__.instances.append(self)


def clear_backend_env(monkeypatch):
    for name in [
        "LLM_BACKEND",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "LOCAL_LLM_BASE_URL",
        "LOCAL_LLM_API_KEY",
        "LOCAL_LLM_MODEL",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_default_backend_is_openai(monkeypatch):
    clear_backend_env(monkeypatch)

    assert llm_client.get_backend() == "openai"


def test_openai_backend_uses_env_model(monkeypatch):
    clear_backend_env(monkeypatch)
    FakeOpenAI.instances = []
    FakeOpenAI.responses = FakeResponses("openai output")
    monkeypatch.setattr(llm_client, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("LLM_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-openai-model")

    output = llm_client.call_llm("hello")

    assert output == "openai output"
    assert FakeOpenAI.instances[0].kwargs == {"api_key": "test-key"}
    assert FakeOpenAI.responses.calls[0]["model"] == "test-openai-model"
    assert FakeOpenAI.responses.calls[0]["input"] == "hello"


def test_local_backend_uses_base_url_and_chat_completions(monkeypatch):
    clear_backend_env(monkeypatch)
    FakeOpenAI.instances = []
    FakeOpenAI.chat_completions = FakeChatCompletions("local output")
    monkeypatch.setattr(llm_client, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("LLM_BACKEND", "local")
    monkeypatch.setenv("LOCAL_LLM_BASE_URL", "http://localhost:8080/v1")
    monkeypatch.setenv("LOCAL_LLM_API_KEY", "local-key")
    monkeypatch.setenv("LOCAL_LLM_MODEL", "qwen-test")

    output = llm_client.call_llm("hello local")

    assert output == "local output"
    assert FakeOpenAI.instances[0].kwargs == {
        "base_url": "http://localhost:8080/v1",
        "api_key": "local-key",
    }
    call = FakeOpenAI.chat_completions.calls[0]
    assert call["model"] == "qwen-test"
    assert call["messages"] == [{"role": "user", "content": "hello local"}]
    assert call["temperature"] == 0


def test_local_backend_missing_base_url_raises_clear_error(monkeypatch):
    clear_backend_env(monkeypatch)
    monkeypatch.setenv("LLM_BACKEND", "local")
    monkeypatch.setenv("LOCAL_LLM_MODEL", "qwen-test")

    with pytest.raises(llm_client.LLMConfigError) as exc_info:
        llm_client.call_llm("hello")

    assert exc_info.value.error_type == "missing_local_base_url"


def test_local_backend_missing_model_raises_clear_error(monkeypatch):
    clear_backend_env(monkeypatch)
    monkeypatch.setenv("LLM_BACKEND", "local")
    monkeypatch.setenv("LOCAL_LLM_BASE_URL", "http://localhost:8080/v1")

    with pytest.raises(llm_client.LLMConfigError) as exc_info:
        llm_client.call_llm("hello")

    assert exc_info.value.error_type == "missing_local_model"


def test_unsupported_backend_raises_clear_error(monkeypatch):
    clear_backend_env(monkeypatch)
    monkeypatch.setenv("LLM_BACKEND", "bad_backend")

    with pytest.raises(llm_client.LLMConfigError) as exc_info:
        llm_client.call_llm("hello")

    assert exc_info.value.error_type == "unsupported_backend"
