# import pandas as pd
# from pathlib import Path

# class CSVExporter:
#     def export(self, data, file_path):
#         Path(file_path).parent.mkdir(parents=True, exist_ok=True)
#         data.to_csv(file_path, index=False)

from pathlib import Path

class CSVExporter:
    def export(self, data, file_path):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(file_path, index=False)