"""
Flask Web Application for Synthetic Data Generator
Provides a modern web interface for generating synthetic data via prompt, file, schema, and time series.
"""
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import json

# ---------------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH (to import src)
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------
# IMPORT MODULES
# ---------------------------------------------------------
from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter
from src.exporters.excel_exporter import ExcelExporter

# ---------------------------------------------------------
# FLASK APP CONFIG
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_exporter(output_format):
    exporters = {
        'csv': CSVExporter(),
        'json': JSONExporter(),
        'excel': ExcelExporter()
    }
    return exporters.get(output_format, CSVExporter())


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Synthetic Data Generator API is running'})


# ---------------------------------------------------------
# 1. PROMPT-BASED GENERATION
# ---------------------------------------------------------
@app.route('/api/generate/prompt', methods=['POST'])
def generate_from_prompt():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        rows = int(data.get('rows', 1000))
        output_format = data.get('format', 'csv').lower()

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        if rows < 1 or rows > 100000:
            return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        df = engine.generate_from_prompt(prompt, rows, output_format)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
            tmp_path = tmp.name

        exporter = get_exporter(output_format)
        exporter.export(df, tmp_path)

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'synthetic_data.{output_format}',
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# 2. FILE-BASED GENERATION
# ---------------------------------------------------------
@app.route('/api/generate/file', methods=['POST'])
def generate_from_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: CSV, Excel, JSON'}), 400

        rows = int(request.form.get('rows', 1000))
        output_format = request.form.get('format', 'csv').lower()
        preserve_stats = request.form.get('preserve_stats', 'true').lower() == 'true'

        if rows < 1 or rows > 100000:
            return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)

        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        df = engine.generate_from_file(str(filepath), rows, preserve_stats, output_format)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
            tmp_path = tmp.name

        exporter = get_exporter(output_format)
        exporter.export(df, tmp_path)

        filepath.unlink()

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'synthetic_data.{output_format}',
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# 3. SCHEMA-BASED GENERATION
# ---------------------------------------------------------
@app.route('/api/generate/schema', methods=['POST'])
def generate_from_schema():
    try:
        data = request.get_json()
        schema = data.get('schema')
        rows = int(data.get('rows', 1000))
        output_format = data.get('format', 'csv').lower()

        if not schema:
            return jsonify({'error': 'Schema is required'}), 400

        if rows < 1 or rows > 100000:
            return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON schema'}), 400

        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        df = engine._generate_from_schema(schema, rows)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
            tmp_path = tmp.name

        exporter = get_exporter(output_format)
        exporter.export(df, tmp_path)

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'synthetic_data.{output_format}',
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# 4. TIME SERIES GENERATION (FAST, SAME ENGINE AS FILE-BASED)
# ---------------------------------------------------------
@app.route('/api/generate/timeseries', methods=['POST'])
def generate_timeseries():
    """
    Time series endpoint using the same SyntheticDataEngine.generate_from_file
    logic as the normal file-based generator, but restricted to CSV input and
    always returning CSV output.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Only allow CSV for this endpoint
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported for time series generation'}), 400

        rows = int(request.form.get('rows', 1000))
        output_format = 'csv'  # always CSV (matches frontend expectation)

        if rows < 1 or rows > 100000:
            return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)

        # Use the same engine & method as other file-based generation
        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        # preserve_stats True for time-series-like behaviour
        df = engine.generate_from_file(str(filepath), rows, True, output_format)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name

        exporter = CSVExporter()
        exporter.export(df, tmp_path)

        filepath.unlink()

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name='synthetic_timeseries_data.csv',
            mimetype='text/csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Synthetic Data Generator Web App...")
    print("📍 Access the app at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
