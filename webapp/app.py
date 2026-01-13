# """
# Flask Web Application for Synthetic Data Generator
# Provides a modern web interface for generating synthetic data via prompt, file, schema, and time series.
# """
# import os
# import sys
# from pathlib import Path
# from flask import Flask, render_template, request, jsonify, send_file
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import tempfile
# import json

# # ---------------------------------------------------------
# # ADD PROJECT ROOT TO PYTHON PATH (to import src)
# # ---------------------------------------------------------
# PROJECT_ROOT = Path(__file__).parent.parent
# sys.path.insert(0, str(PROJECT_ROOT))

# # ---------------------------------------------------------
# # IMPORT MODULES
# # ---------------------------------------------------------
# from src.core.engine import SyntheticDataEngine
# from src.generators.mimesis_generator import MimesisGenerator
# from src.exporters.csv_exporter import CSVExporter
# from src.exporters.json_exporter import JSONExporter
# from src.exporters.excel_exporter import ExcelExporter

# # ---------------------------------------------------------
# # FLASK APP CONFIG
# # ---------------------------------------------------------
# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
# UPLOAD_FOLDER.mkdir(exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def get_exporter(output_format):
#     exporters = {
#         'csv': CSVExporter(),
#         'json': JSONExporter(),
#         'excel': ExcelExporter()
#     }
#     return exporters.get(output_format, CSVExporter())


# # ---------------------------------------------------------
# # ROUTES
# # ---------------------------------------------------------

# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/api/health')
# def health():
#     return jsonify({'status': 'healthy', 'message': 'Synthetic Data Generator API is running'})


# # ---------------------------------------------------------
# # 1. PROMPT-BASED GENERATION
# # ---------------------------------------------------------
# @app.route('/api/generate/prompt', methods=['POST'])
# def generate_from_prompt():
#     try:
#         data = request.get_json()
#         prompt = data.get('prompt', '').strip()
#         rows = int(data.get('rows', 1000))
#         output_format = data.get('format', 'csv').lower()

#         if not prompt:
#             return jsonify({'error': 'Prompt is required'}), 400

#         if rows < 1 or rows > 100000:
#             return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

#         engine = SyntheticDataEngine()
#         engine.register_generator("mimesis", MimesisGenerator())

#         df = engine.generate_from_prompt(prompt, rows, output_format)

#         with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
#             tmp_path = tmp.name

#         exporter = get_exporter(output_format)
#         exporter.export(df, tmp_path)

#         return send_file(tmp_path, as_attachment=True,
#                          download_name=f'synthetic_data.{output_format}',
#                          mimetype='application/octet-stream')

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ---------------------------------------------------------
# # 2. FILE-BASED GENERATION
# # ---------------------------------------------------------
# @app.route('/api/generate/file', methods=['POST'])
# def generate_from_file():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400

#         file = request.files['file']

#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400

#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type. Allowed: CSV, Excel, JSON'}), 400

#         rows = int(request.form.get('rows', 1000))
#         output_format = request.form.get('format', 'csv').lower()
#         preserve_stats = request.form.get('preserve_stats', 'true').lower() == 'true'

#         filename = secure_filename(file.filename)
#         filepath = app.config['UPLOAD_FOLDER'] / filename
#         file.save(filepath)

#         engine = SyntheticDataEngine()
#         engine.register_generator("mimesis", MimesisGenerator())

#         df = engine.generate_from_file(str(filepath), rows, preserve_stats, output_format)

#         with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
#             tmp_path = tmp.name

#         exporter = get_exporter(output_format)
#         exporter.export(df, tmp_path)

#         filepath.unlink()

#         return send_file(tmp_path, as_attachment=True,
#                          download_name=f'synthetic_data.{output_format}',
#                          mimetype='application/octet-stream')

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ---------------------------------------------------------
# # 3. SCHEMA-BASED GENERATION
# # ---------------------------------------------------------
# @app.route('/api/generate/schema', methods=['POST'])
# def generate_from_schema():
#     try:
#         data = request.get_json()
#         schema = data.get('schema')
#         rows = int(data.get('rows', 1000))
#         output_format = data.get('format', 'csv').lower()

#         if not schema:
#             return jsonify({'error': 'Schema is required'}), 400

#         if rows < 1 or rows > 100000:
#             return jsonify({'error': 'Rows must be between 1 and 100,000'}), 400

#         if isinstance(schema, str):
#             schema = json.loads(schema)

#         engine = SyntheticDataEngine()
#         engine.register_generator("mimesis", MimesisGenerator())

#         df = engine._generate_from_schema(schema, rows)

#         with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
#             tmp_path = tmp.name

#         exporter = get_exporter(output_format)
#         exporter.export(df, tmp_path)

#         return send_file(tmp_path, as_attachment=True,
#                          download_name=f'synthetic_data.{output_format}',
#                          mimetype='application/octet-stream')

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ---------------------------------------------------------
# # 4. TIME SERIES GENERATION (FAST VERSION)
# # ---------------------------------------------------------
# @app.route('/api/generate/timeseries', methods=['POST'])
# def generate_timeseries():
#     """Fast time series generation: same method as file-based, but CSV only."""
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400

#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400

#         if not file.filename.lower().endswith('.csv'):
#             return jsonify({'error': 'Only CSV files are supported for time series'}), 400

#         rows = int(request.form.get('rows', 1000))
#         output_format = 'csv'

#         filename = secure_filename(file.filename)
#         filepath = app.config['UPLOAD_FOLDER'] / filename
#         file.save(filepath)

#         engine = SyntheticDataEngine()
#         engine.register_generator("mimesis", MimesisGenerator())

#         df = engine.generate_from_file(str(filepath), rows, True, output_format)

#         with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
#             tmp_path = tmp.name

#         CSVExporter().export(df, tmp_path)

#         filepath.unlink()

#         return send_file(tmp_path, as_attachment=True,
#                          download_name='synthetic_timeseries_data.csv',
#                          mimetype='text/csv')

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ---------------------------------------------------------
# # RUN SERVER
# # ---------------------------------------------------------
# if __name__ == '__main__':
#     print("🚀 Starting Synthetic Data Generator Web App...")
#     print("📍 Access: http://localhost:5000")
#     app.run(debug=True, host='0.0.0.0', port=5000)


"""
Flask Web Application for Synthetic Data Generator
Provides a modern web interface for generating synthetic data via prompt, file, schema, time series, and EDA reports.
"""
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import json

import pandas as pd
from ydata_profiling import ProfileReport

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

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
REPORTS_FOLDER = BASE_DIR / 'reports'

UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORTS_FOLDER.mkdir(exist_ok=True)

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


def read_input_for_eda(path: Path) -> pd.DataFrame:
    """
    Read CSV or Excel (first sheet) into a DataFrame for EDA.
    Same logic as generate_report.py.
    """
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".xls", ".xlsx"):
        return pd.read_excel(path, sheet_name=0)
    raise ValueError(f"Unsupported input file extension: {ext}")


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

        return send_file(tmp_path, as_attachment=True,
                         download_name=f'synthetic_data.{output_format}',
                         mimetype='application/octet-stream')

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

        return send_file(tmp_path, as_attachment=True,
                         download_name=f'synthetic_data.{output_format}',
                         mimetype='application/octet-stream')

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
            schema = json.loads(schema)

        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        df = engine._generate_from_schema(schema, rows)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{output_format}') as tmp:
            tmp_path = tmp.name

        exporter = get_exporter(output_format)
        exporter.export(df, tmp_path)

        return send_file(tmp_path, as_attachment=True,
                         download_name=f'synthetic_data.{output_format}',
                         mimetype='application/octet-stream')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# 4. TIME SERIES GENERATION (FAST VERSION)
# ---------------------------------------------------------
@app.route('/api/generate/timeseries', methods=['POST'])
def generate_timeseries():
    """Fast time series generation: same method as file-based, but CSV only."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported for time series'}), 400

        rows = int(request.form.get('rows', 1000))
        output_format = 'csv'

        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)

        engine = SyntheticDataEngine()
        engine.register_generator("mimesis", MimesisGenerator())

        df = engine.generate_from_file(str(filepath), rows, True, output_format)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name

        CSVExporter().export(df, tmp_path)

        filepath.unlink()

        return send_file(tmp_path, as_attachment=True,
                         download_name='synthetic_timeseries_data.csv',
                         mimetype='text/csv')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# 5. EDA REPORT GENERATION (ydata-profiling)
# ---------------------------------------------------------
@app.route('/api/eda/report', methods=['POST'])
def generate_eda_report():
    """
    Generate an EDA HTML report using ydata-profiling.
    Accepts CSV/XLS/XLSX, returns the HTML report as a download.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Only allow CSV / Excel for EDA
        ext = Path(file.filename).suffix.lower()
        if ext not in ('.csv', '.xls', '.xlsx'):
            return jsonify({'error': 'Only CSV and Excel files are supported for EDA reports'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        input_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(input_path)

        # Read data
        df = read_input_for_eda(input_path)

        # Prepare report paths
        dataset_name = input_path.stem
        report_html = REPORTS_FOLDER / f"eda_{dataset_name}.html"

        # Title
        title = f"EDA: {dataset_name}"

        # Generate HTML report
        profile = ProfileReport(df, title=title)
        profile.to_file(report_html.as_posix())

        # (Optional) JSON profile like CLI version – generated but not returned
        try:
            expl_profile = ProfileReport(df, title=title, explorative=True)
            json_str = expl_profile.to_json()
            json_path = REPORTS_FOLDER / f".profile_{dataset_name}.json"
            with json_path.open("w", encoding="utf-8") as jf:
                jf.write(json_str)
        except Exception:
            # If JSON fails, ignore; HTML report is still useful
            pass

        # Clean up uploaded input file
        input_path.unlink(missing_ok=True)

        # Send HTML report as a downloadable file
        return send_file(
            report_html,
            as_attachment=True,
            download_name=f"eda_{dataset_name}.html",
            mimetype="text/html"
        )

    except Exception as e:
        return jsonify({'error': f'EDA report generation failed: {e}'}), 500


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Synthetic Data Generator Web App...")
    print("📍 Access: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
