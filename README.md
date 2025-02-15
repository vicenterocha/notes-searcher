# Notes Searcher

A tool that uses LanceDB for semantic search through your Obsidian notes and Ollama LLM to provide intelligent answers based on your notes' content.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Ollama installed with the `mistral` model
- An Obsidian vault with markdown notes

### Installing Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the Mistral model:
```bash
ollama pull mistral
```

## Installation

1. Clone this repository
2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

The tool has two main functions:
1. Indexing your notes (required before searching)
2. Searching through your notes

### Indexing Your Notes

Before you can search, you need to index your Obsidian vault:

```bash
poetry run python notes_searcher/main.py --notes-dir /path/to/your/obsidian/vault --index
```

This will:
- Scan all markdown files in your vault
- Create embeddings for each note
- Store them in a LanceDB database

### Searching Your Notes

To search through your notes:

```bash
poetry run python notes_searcher/main.py --notes-dir /path/to/your/obsidian/vault --query "your query here"
```

The tool will:
1. Use LanceDB to find the most relevant notes for your query
2. Feed these notes to the Mistral LLM through Ollama
3. Provide a comprehensive answer based on your notes
4. List the source notes used to generate the answer

## How it Works

1. **Embedding Generation**: Uses the `sentence-transformers` model `all-MiniLM-L6-v2` to create vector embeddings of your notes
2. **Vector Storage**: Stores these embeddings in LanceDB for efficient similarity search
3. **Semantic Search**: When you make a query, it finds the most relevant notes using vector similarity
4. **LLM Processing**: Uses Ollama's Mistral model to analyze the relevant notes and generate a comprehensive answer

## File Structure

- `notes_searcher/main.py`: Main script containing the NotesSearcher class
- `data/notes-db/`: Directory where the LanceDB database is stored
- `pyproject.toml`: Poetry project configuration and dependencies

## Dependencies

- `lancedb`: Vector database for efficient similarity search
- `sentence-transformers`: For generating text embeddings
- `ollama`: Python client for Ollama LLM
- `python-frontmatter`: For parsing markdown files with YAML frontmatter
- `pandas`: For data manipulation

## Note Format

The tool supports Obsidian markdown files with YAML frontmatter. Example:

```markdown
---
title: My Note Title
tags: [tag1, tag2]
---

Note content here...
```

## Limitations

- Currently processes the first 1500 characters of each note when sending to the LLM
- Requires the Mistral model to be installed in Ollama
- Indexes are stored locally and need to be rebuilt if notes change

## Example Output

When you run a search, you'll get output like this:

```
Answer:
=======
[The LLM's synthesized answer based on your notes will appear here]

Sources:
========
- Note Title 1
  Path: /path/to/note1.md
  Relevance Score: 0.8234

- Note Title 2
  Path: /path/to/note2.md
  Relevance Score: 0.7645
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've installed dependencies with `poetry install`
2. **Ollama Connection Error**: Ensure Ollama is running (`ollama serve`)
3. **No Results**: If you get no results after indexing, check:
   - The path to your notes directory is correct
   - Your markdown files have readable content
   - You've indexed the notes before searching

### Performance Tips

- First-time indexing might be slow for large vaults
- Consider reindexing periodically if you add many new notes
- The `--notes-dir` path should point to the root of your Obsidian vault

## Contributing

Feel free to open issues or submit pull requests!