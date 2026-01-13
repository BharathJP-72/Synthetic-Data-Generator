import json
import pandas as pd

class JSONExporter:
    def export(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data.to_dict(orient='records'), f, indent=2)