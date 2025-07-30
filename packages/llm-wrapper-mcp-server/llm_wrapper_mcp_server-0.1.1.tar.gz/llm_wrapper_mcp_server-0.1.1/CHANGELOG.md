# CHANGELOG

### feat: Replace StdioServer with LLMMCPWrapper for generic LLM API server

## feat: Implement LLM audit logging and enhance usage tracking

This commit introduces comprehensive audit logging for LLM interactions and
enhances the existing usage tracking mechanism.

Key changes include:
- Integrated `AuditLogger` to log outbound prompts and inbound responses.
- Updated LLM usage tracking to include `cached_tokens`, `reasoning_tokens`,
  `project`, and `username` for more granular reporting.
- Ensured the `data` directory is created for SQLite databases.
- Added a `close` method to `LLMClient` for proper resource management.
- Updated project description and author email in `pyproject.toml`.
- Adjusted `.gitignore` to include the `data/` directory and remove `logs/`.
- Removed `data/accounting.sqlite` as it's no longer needed.
