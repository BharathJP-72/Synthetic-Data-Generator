import pandas as pd

class ExcelExporter:
    def export(self, data, file_path):
        data.to_excel(file_path, index=False)