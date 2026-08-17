# Kajlia Recovery Assistant

A Streamlit app that reads a real estate developer's payment database and explains what the numbers show in plain language.

**Live app:** https://kajlia-recovery-assistant.streamlit.app

## What it does
- Reads a SQLite database directly (36 flats, 255 payments)
- Shows headline figures: total sale, recovered, unsecured outstanding
- Charts monthly recovery
- Uses the Anthropic API to describe what the data shows

## Keeping the model honest
All arithmetic happens in Python. The model receives figures already converted to crore and is instructed not to recalculate, not to give advice, and to say when something isn't in the data.

## Built with
Python · SQLite · pandas · Streamlit · Anthropic API

Runs on anonymised data.
