# Polvo CLI

🐙 **Polvo CLI** - Find the best embedding model for your data

A command-line interface for testing and evaluating embedding models on your datasets using the Polvo API.

## Installation

### From PyPI (when published)
```bash
pip install polvo-cli
```

### Development Installation
```bash
git clone <repository-url>
cd polvo-cli
pip install -e .
```

## Quick Start

1. **Check API health**:
   ```bash
   polvo health
   ```

2. **List available models**:
   ```bash
   polvo models
   ```

3. **Test models on your dataset**:
   ```bash
   polvo test data.csv --model minilm --model mpnet
   ```

## Commands

### `polvo test`
Test embedding models on your dataset.

```bash
polvo test <file> [OPTIONS]

# Examples:
polvo test data.csv --model minilm --model mpnet --model openai-small
polvo test data.json --output csv > results.csv
polvo test data.txt --model minilm --api-url https://api.usepolvo.com
```

**Arguments:**
- `file`: Dataset file (CSV, JSON, or TXT)

**Options:**
- `--model, -m`: Models to test (can specify multiple, default: minilm, mpnet)
- `--column, -c`: Column name for CSV files
- `--output, -o`: Output format: table, json, csv (default: table)
- `--api-url`: API URL (default: http://localhost:8000)

### `polvo models`
List available embedding models.

```bash
polvo models [OPTIONS]

# Example:
polvo models --api-url https://api.usepolvo.com
```

**Options:**
- `--api-url`: API URL (default: http://localhost:8000)

### `polvo health`
Check API health status.

```bash
polvo health [OPTIONS]

# Example:
polvo health --api-url https://api.usepolvo.com
```

**Options:**
- `--api-url`: API URL (default: http://localhost:8000)

### `polvo version`
Show CLI version.

```bash
polvo version
```

## Configuration

### Environment Variables

You can set the default API URL using environment variables:

```bash
export POLVO_API_URL="https://api.usepolvo.com"
```

Or create a `.env` file in your working directory:

```env
POLVO_API_URL=https://api.usepolvo.com
```

## Output Formats

### Table Format (Default)
Beautiful table output with recommendations:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                Embedding Model Evaluation Results                ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Model   │ Retrieval │ Clustering │ Speed (ms) │ Cost/1K │ Dims │
├─────────┼───────────┼────────────┼────────────┼─────────┼──────┤
│ minilm  │      0.85 │       0.72 │        120 │    Free │  384 │
│ mpnet   │      0.88 │       0.78 │        180 │    Free │  768 │
└─────────┴───────────┴────────────┴────────────┴─────────┴──────┘

Recommendations:
  mpnet offers the best balance of quality and speed
  minilm is fastest for large-scale applications

Best model: mpnet
```

### JSON Format
Structured JSON output for programmatic use:

```bash
polvo test data.csv --output json
```

### CSV Format
CSV output for further analysis:

```bash
polvo test data.csv --output csv > results.csv
```

## Supported File Formats

- **CSV**: Comma-separated values (specify column with `--column`)
- **JSON**: JSON arrays or objects
- **TXT**: Plain text files (one text per line)

## Error Handling

The CLI provides clear error messages and appropriate exit codes:

- `0`: Success
- `1`: General error (file not found, API error, etc.)

## Examples

### Test Multiple Models on a Dataset
```bash
polvo test customer_reviews.csv \
  --model minilm \
  --model mpnet \
  --model openai-small \
  --output table
```

### Export Results for Analysis
```bash
polvo test data.csv --model minilm --model mpnet --output csv > evaluation_results.csv
```

### Check Remote API
```bash
polvo health --api-url https://api.usepolvo.com
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/usepolvo/polvo-cli). 