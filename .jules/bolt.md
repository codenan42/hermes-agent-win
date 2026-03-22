## 2025-05-14 - Selective shallow copying in message processing pipelines
**Learning:** Replacing `copy.deepcopy` with selective shallow copying in message-processing pipelines (e.g., Anthropic prompt caching) can result in a massive performance speedup (e.g. ~30x for 500 messages). This is critical for maintaining performance as conversation history grows.
**Action:** When transforming lists of dictionaries (like conversation history), prefer `list(original_list)` and `msg.copy()` for only the messages that need changes, rather than a full `copy.deepcopy(original_list)`.

## 2025-05-14 - Anthropic content normalization consistency
**Learning:** In `run_agent.py`, `_prepare_anthropic_messages_for_api` uses `self._content_has_image_parts` to detect images. When transformation is required, `_preprocess_anthropic_content` must be applied to *every* message in the history (not just the ones with images) to ensure consistent content normalization and compatibility with the Anthropic API.
**Action:** When optimizing message transformations, ensure the logic preserves the original behavior of applying normalization across the entire history once the transformation is triggered.
