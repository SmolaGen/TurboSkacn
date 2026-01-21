---
name: VibeProxy Integration
description: Instructions for checking and configuring Auto-Claude to work with VibeProxy and Google Gemini models.
---

# VibeProxy Integration Guide

This skill documents the configuration required to integrate Auto-Claude with VibeProxy (locally running proxy for Google Gemini models).

## 1. System Overview

Auto-Claude normally connects to Anthropic's API. To use Google Gemini models, we route traffic through **VibeProxy**.

**Flow:**
`Auto-Claude SDK` -> `http://127.0.0.1:8317/v1` (VibeProxy) -> `OpenAI/Anthropic Adapter` -> `Google Gemini API`

## 2. Prerequisites

*   **VibeProxy** must be running locally.
*   **Port**: Confirmed as **8317**.
*   **Management Key**: Required for authentication (acts as the Bearer token).

## 3. Environment Configuration (`apps/backend/.env`)

The `.env` file is critical. It must contain the following overrides:

```ini
# =============================================================================
# VIBEPROXY CONFIGURATION
# =============================================================================

# 1. Base URL must point to VibeProxy with /v1 suffix
ANTHROPIC_BASE_URL=http://127.0.0.1:8317/v1

# 2. Authentication Token (Management Key)
# This overrides the keychain token. "dummy" or "sk-ant-..." format works if VibeProxy accepts it,
# but using the actual Management Key is recommended if 407 errors occur.
CLAUDE_CODE_OAUTH_TOKEN=9CDCC8DB-769D-48BD-AF4D-08F97A47BE98

# 3. Model Mapping (CRITICAL)
# Maps generic Claude names to VibeProxy's specific Gemini aliases.
AUTO_BUILD_MODEL=gemini-claude-sonnet-4-5
ANTHROPIC_DEFAULT_HAIKU_MODEL=gemini-2.5-flash
ANTHROPIC_DEFAULT_SONNET_MODEL=gemini-claude-sonnet-4-5
ANTHROPIC_DEFAULT_OPUS_MODEL=gemini-claude-opus-4-5-thinking
ANTHROPIC_MODEL=gemini-claude-sonnet-4-5

# 4. Graphiti / Memory Config
# Ensure OpenRouter/Graphiti also points to the correct proxy port
OPENROUTER_BASE_URL=http://127.0.0.1:8317/v1
OPENROUTER_API_KEY=dummy-not-used
GRAPHITI_LLM_PROVIDER=openrouter
GRAPHITI_EMBEDDER_PROVIDER=openrouter
```

## 4. Required Code Changes

Standard Auto-Claude code requires patching to handle the custom model aliases correctly.

### Backend (`apps/backend/`)

1.  **`phase_config.py`**:
    *   **Goal**: Ensure `resolve_model_id` checks environment variables for overrides.
    *   **Logic**: Map `haiku`, `sonnet`, `opus` shorthands to `ANTHROPIC_DEFAULT_*_MODEL` env vars.

2.  **`core/client.py`**:
    *   **Goal**: Ensure the main `create_client` function resolves the model ID before creating the SDK client.
    *   **Change**: Import `resolve_model_id` and apply it to the `model` argument.

### Frontend Generators (`apps/frontend/`)

The frontend spawns isolated Python scripts for "Title Generation" and "Terminal Naming". These scripts bypass the main backend application and typically have hardcoded model IDs.

1.  **Files**:
    *   `src/main/title-generator.ts`
    *   `src/main/terminal-name-generator.ts`

2.  **Fix**:
    *   Inject `resolve_model_id` python logic directly into the generated Python script string.
    *   This ensures the script sees `gemini-2.5-flash` instead of `claude-haiku...` even when running in isolation.

## 5. UI Configuration

In the Auto-Claude Electron App Settings:

*   **Endpoint URL**: `http://127.0.0.1:8317/v1`
*   **Management Key**: `9CDCC8DB-769D-48BD-AF4D-08F97A47BE98`
*   **Verify SSL**: **Unchecked** (Disabled)

## 6. Troubleshooting

### `407 Proxy Authentication Required`
*   **Cause**: VibeProxy rejected the request because the `Authorization` header was missing or incorrect.
*   **Fix**: Ensure `CLAUDE_CODE_OAUTH_TOKEN` in `.env` matches the VibeProxy Management Key.

### `404 Not Found` (Model Error)
*   **Cause**: The URL might be incorrect (e.g., missing `/v1` or double `/v1/v1`), or the Model ID is not mapped.
*   **Fix 1**: Check `ANTHROPIC_BASE_URL` ends in `/v1`.
*   **Fix 2**: Check `ANTHROPIC_DEFAULT_*_MODEL` variables are set.

### `unknown provider for model claude-haiku-4-5`
*   **Cause**: The application is sending the raw Claude ID to VibeProxy, which doesn't recognize it.
*   **Fix**: The `resolve_model_id` logic is not working or not being called. Check `phase_config.py` and ensure the frontend generators are updated and rebuilt (`npm run build`).

### `401 Invalid bearer token`
*   **Cause**: The app is ignoring the custom Base URL and trying to hit Anthropic's real API with a dummy token.
*   **Fix**: The `.env` file is likely not loaded or cached. **Full restart** of backend and frontend is required.
