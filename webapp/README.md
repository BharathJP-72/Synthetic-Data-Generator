# Synthetic Data Generator - Web Application

A beautiful, modern web interface for generating high-quality synthetic data using AI-powered intelligence.

## Features

✨ **Three Generation Modes:**
- **Prompt-Based**: Describe your data needs in natural language
- **File-Based**: Upload existing files to generate similar synthetic data
- **Schema-Based**: Define precise data structures with JSON schemas

🎨 **Modern UI:**
- Vibrant gradient design
- Smooth animations
- Glassmorphism effects
- Fully responsive
- Drag-and-drop file upload

📊 **Output Formats:**
- CSV
- JSON
- Excel

## Installation

1. **Install Dependencies**

```bash
# Install main project dependencies (if not already installed)
cd ..
pip install -r requirements.txt

# Install web app dependencies
cd webapp
pip install -r requirements-webapp.txt
```

2. **Run the Application**

```bash
python app.py
```

3. **Access the Web Interface**

Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Prompt-Based Generation

1. Click on the "Prompt-Based" tab
2. Describe your data in natural language (e.g., "Customer data with names, emails, ages 18-80")
3. Set the number of rows
4. Choose output format
5. Click "Generate Data"

### File-Based Generation

1. Click on the "File-Based" tab
2. Upload a CSV or Excel file (drag & drop or click to browse)
3. Set the number of rows to generate
4. Choose output format
5. Optionally preserve statistical properties
6. Click "Generate Data"

### Schema-Based Generation

1. Click on the "Schema-Based" tab
2. Define your JSON schema with field types and constraints
3. Set the number of rows
4. Choose output format
5. Click "Generate Data"

**Example Schema:**
```json
{
  "name": {"type": "string", "mimesis": "person.full_name"},
  "email": {"type": "string", "mimesis": "person.email"},
  "age": {"type": "integer", "mimesis": "person.age", "constraints": {"min": 18, "max": 65}},
  "city": {"type": "string", "mimesis": "address.city"}
}
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Generate from Prompt
```
POST /api/generate/prompt
Content-Type: application/json

{
  "prompt": "Customer data with names and emails",
  "rows": 1000,
  "format": "csv"
}
```

### Generate from File
```
POST /api/generate/file
Content-Type: multipart/form-data

file: <uploaded file>
rows: 1000
format: csv
preserve_stats: true
```

### Generate from Schema
```
POST /api/generate/schema
Content-Type: application/json

{
  "schema": {...},
  "rows": 1000,
  "format": "csv"
}
```

## Configuration

- **Port**: Default is 5000 (change in `app.py`)
- **Max File Size**: 16MB (change `MAX_CONTENT_LENGTH` in `app.py`)
- **Upload Folder**: `webapp/uploads/` (automatically created)

## Troubleshooting

**Issue**: Module not found errors
- **Solution**: Make sure you've installed all dependencies from both `requirements.txt` files

**Issue**: Port already in use
- **Solution**: Change the port in `app.py` or stop the process using port 5000

**Issue**: File upload fails
- **Solution**: Check file size (max 16MB) and format (CSV, Excel only)

## Development

To run in development mode with auto-reload:

```bash
python app.py
```

The Flask app runs with `debug=True` by default for development.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Data Generation**: Mimesis library
- **Styling**: Custom CSS with modern design patterns

## License

Same as the main Synthetic Data Generator project.
