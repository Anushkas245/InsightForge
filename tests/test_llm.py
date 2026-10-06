from unittest.mock import patch, MagicMock

from analytics.llm import ask_llm


def test_ask_llm():
    mock_response = MagicMock()
    mock_response.message.content = "North America generates the most revenue."

    with patch("analytics.llm.chat", return_value=mock_response) as mock_chat:

        answer = ask_llm(
            "Which region generates the most revenue?",
            "North America: Revenue $14,317,164.50",
        )

        # Verify the returned AI answer.
        assert answer == "North America generates the most revenue."

        # Verify Ollama was called.
        mock_chat.assert_called_once()

        # Get the prompt sent to the model.
        call_args = mock_chat.call_args
        prompt = call_args.kwargs["messages"][0]["content"]

        # Verify the question and verified business data
        # were included in the prompt.
        assert "Which region generates the most revenue?" in prompt
        assert "North America: Revenue $14,317,164.50" in prompt

        # Verify the model configuration.
        assert call_args.kwargs["model"] == "qwen3.5:4b"
        assert call_args.kwargs["think"] is False