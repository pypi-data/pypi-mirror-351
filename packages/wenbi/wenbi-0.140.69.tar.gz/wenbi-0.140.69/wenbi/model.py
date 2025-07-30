import dspy
import os
from wenbi.utils import segment


def get_lm_config(model_string, base_url=None):
    """
    Determine provider and return config dict for dspy.LM.
    Supports: ollama, openai, gemini (google-genai)
    """
    if not model_string:
        # Default to Ollama
        return {
            "base_url": "http://localhost:11434",
            "model": "ollama/qwen3",
        }
    parts = model_string.strip().split("/")
    provider = parts[0].lower() if parts else ""
    if provider == "ollama":
        return {
            "base_url": base_url or "http://localhost:11434",
            "model": model_string,
        }
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        return {
            "base_url": base_url or "https://api.openai.com/v1",
            "model": model_string.replace("openai/", ""),
            "api_key": api_key,
        }
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY_JSON")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GOOGLE_API_KEY_JSON environment variable not set."
            )
        return {
            "base_url": base_url or "https://generativelanguage.googleapis.com/v1beta",
            "model": model_string.replace("gemini/", ""),
            "api_key": api_key,
        }
    else:
        # Unknown provider, fallback to user input
        return {"base_url": base_url, "model": model_string}


def is_ollama(model_string):
    """
    Check the model_string (if provided) for the provider.
    If the model string starts with "ollama/", return "http://localhost:11434".
    If model_string is empty, default to "ollama/qwen3" with base_url "http://localhost:11434".
    Otherwise, return None.
    """
    if not model_string:
        return "http://localhost:11434"  # default for empty input
    parts = model_string.strip().split("/")
    if parts and parts[0].lower() == "ollama":
        return "http://localhost:11434"
    return None


def translate(
    vtt_path,
    output_dir=None,
    translate_language="Chinese",
    llm="",
    chunk_length=8,
    max_tokens=50000,
    timeout=3600,
    temperature=0.1,
    base_url="http://localhost:11434",
):
    """
    Translate English VTT content to a bilingual markdown file using the target language provided.

    Args:
        vtt_path (str): Path to the English VTT file
        output_dir (str): Directory for output files
        translate_language (str): Target language for translation
        llm (str): LLM model identifier
        chunk_length (int): Number of sentences per chunk for segmentation
        max_tokens (int): Maximum number of tokens for the LLM
        timeout (int): Timeout for the LLM in seconds
        temperature (float): Temperature for the LLM
        base_url (str): Base URL for the LLM

    Returns:
        str: Path to the generated markdown file
    """
    segmented_text = segment(vtt_path, sentence_count=chunk_length)
    paragraphs = segmented_text.split("\n\n")

    model_id = llm if llm else "ollama/qwen3"
    lm_config = get_lm_config(model_id, base_url=base_url)
    lm_config["max_tokens"] = max_tokens
    lm_config["timeout_s"] = timeout
    lm_config["temperature"] = temperature
    lm = dspy.LM(**lm_config)
    dspy.configure(lm=lm)

    class Translate(dspy.Signature):
        english_text = dspy.InputField(desc="English text to translate")
        translated_text = dspy.OutputField(
            desc=f"Translation into {translate_language}"
        )

    translator = dspy.ChainOfThought(Translate)
    translated_pairs = []

    for para in paragraphs:
        if para.strip():
            response = translator(english_text=para)
            translated_pairs.append(
                f"# English\n{para}\n\n# {translate_language}\n{response.translated_text}\n\n---\n"
            )

    markdown_content = "\n".join(translated_pairs)
    output_file = os.path.splitext(vtt_path)[0] + "_bilingual.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return output_file


def rewrite(
    file_path,
    output_dir=None,
    llm="",
    rewrite_lang="Chinese",
    chunk_length=8,
    max_tokens=50000,
    timeout=3600,
    temperature=0.1,
    base_url="http://localhost:11434",
):
    """
    Rewrites text by first segmenting the file into paragraphs.

    Args:
        file_path (str): Path to the input file
        output_dir (str, optional): Output directory
        llm (str): LLM model identifier
        rewrite_lang (str): Target language for rewriting (default: Chinese)
        chunk_length (int): Number of sentences per chunk for segmentation
        max_tokens (int): Maximum number of tokens for the LLM
        timeout (int): Timeout for the LLM in seconds
        temperature (float): Temperature for the LLM
        base_url (str): Base URL for the LLM
    """
    segmented_text = segment(file_path, sentence_count=chunk_length)
    paragraphs = segmented_text.split("\n\n")

    model_id = llm if llm else "ollama/qwen3"
    lm_config = get_lm_config(model_id, base_url=base_url)
    lm_config["max_tokens"] = max_tokens
    lm_config["timeout_s"] = timeout
    lm_config["temperature"] = temperature
    lm = dspy.LM(**lm_config)
    dspy.configure(lm=lm)

    rewritten_paragraphs = []
    for para in paragraphs:
        class ParaRewrite(dspy.Signature):
            """
            Rewrite this text in {rewrite_lang}, add punctuation, grammar corrected, proofread, converting from spoken to written form
            while preserving the meaning. Ensure the rewritten text is at least 95% of the original length.
            """
            text: str = dspy.InputField(
                desc=f"Spoken text to rewrite in {rewrite_lang}"
            )
            rewritten: str = dspy.OutputField(
                desc=f"Rewritten paragraph in {rewrite_lang}"
            )
        rewrite = dspy.ChainOfThought(ParaRewrite)
        response = rewrite(text=para)
        rewritten_paragraphs.append(response.rewritten)

    rewritten_text = "\n\n".join(rewritten_paragraphs)
    if output_dir:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_file = os.path.join(output_dir, f"{base_name}_rewritten.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(rewritten_text)
    else:
        out_file = None

    return rewritten_text
