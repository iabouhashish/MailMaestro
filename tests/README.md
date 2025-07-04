# MailMaestro Test Suite

This folder contains tests for all agents, plugins, integrations, and the main CLI of MailMaestro.

## Structure

- `agents/` - Tests for each agent factory (async, covers prompt loading/config)
- `plugins/` - Tests for each plugin (unit tests, side effects, pure logic)
- `integrations/` - Integration test for full pipeline run
- `test_main.py` - CLI/entrypoint coverage
- `conftest.py` - Global test fixtures and Gmail mocking
- `requirements-test.txt` - All requirements to run these tests

## Running the tests

1. **Install dependencies:**
   ```bash
   pip install -r requirements-test.txt
