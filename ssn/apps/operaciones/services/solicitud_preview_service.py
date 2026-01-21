from io import BytesIO
from urllib.parse import quote

import numpy as np
import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from ..helpers.text_utils import pretty_json
from ..serializers import serialize_operations


class SolicitudPreviewService:
    def __init__(self, base_request, operations):
        self.base_request = base_request
        self.operations = operations  # Lista de instancias de modelo
        self.payload = None
        self.formatted_json = ""
        self.mailto_link = ""
        self.excel_link = ""
        self.is_monthly = base_request.tipo_entrega == "Mensual"

    def generar_preview(self):
        if not self.operations:
            return False  # Nada que mostrar

        # Serializa la solicitud y sus operaciones/stocks (de modelos reales)
        self.payload = serialize_operations(self.base_request, self.operations)

        # Transformaciones para operaciones semanales
        if not self.is_monthly:
            for operacion in self.payload.get("operaciones", []):
                if "cantEspecies" in operacion and operacion["cantEspecies"] is not None:
                    if operacion.get("tipoEspecie") != "FC":
                        operacion["cantEspecies"] = int(float(operacion["cantEspecies"]))

        # Formateo JSON y mailto link
        self.formatted_json = pretty_json(self.payload)
        tipo_entrega = self.payload.get("tipoEntrega", "Desconocido")
        mail_subject = f"modelo de operacion - {tipo_entrega}"
        mail_body = f"ID: {self.base_request.uuid}\nSolicitud:\n{self.formatted_json}"
        self.mailto_link = (
            f"mailto:?subject={quote(mail_subject)}&body={quote(mail_body)}"
        )
        return True

    def generar_excel(self):
        if not self.payload:
            return None

        from ..helpers import camel_to_title

        base_json = self.payload.copy()

        # Extraer datos según el tipo de entrega
        if self.is_monthly:
            # Para mensual, extraemos el array único de stocks
            stocks_json = base_json.pop("stocks", [])
            # Separar por tipo para generar hojas separadas en Excel
            stock_inversion = [s for s in stocks_json if s.get("tipo") == "I"]
            stock_plazo_fijo = [s for s in stocks_json if s.get("tipo") == "P"]
            stock_cheque_pd = [s for s in stocks_json if s.get("tipo") == "C"]
        else:
            operaciones_json = base_json.pop("operaciones", None)

        # Info general
        base_df = pd.DataFrame(list(base_json.items()), columns=["Campo", "Valor"])
        base_df["Campo"] = base_df["Campo"].apply(camel_to_title)
        base_df = base_df.replace([np.nan, np.inf, -np.inf], "")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book
            border_format = workbook.add_format({"border": 1})
            bold_border_format = workbook.add_format({"bold": True, "border": 1})
            header_format = workbook.add_format({"bold": True, "border": 1, "bg_color": "#D9E1F2"})

            if self.is_monthly:
                # Para mensual: múltiples hojas
                self._write_base_sheet(writer, base_df, "Solicitud", border_format, bold_border_format)
                
                if stock_inversion:
                    self._write_stock_sheet(writer, stock_inversion, "Stock Inversión", 
                                          camel_to_title, border_format, bold_border_format, header_format)
                if stock_plazo_fijo:
                    self._write_stock_sheet(writer, stock_plazo_fijo, "Stock Plazo Fijo",
                                          camel_to_title, border_format, bold_border_format, header_format)
                if stock_cheque_pd:
                    self._write_stock_sheet(writer, stock_cheque_pd, "Stock Cheque PD",
                                          camel_to_title, border_format, bold_border_format, header_format)
            else:
                # Para semanal: hoja única con operaciones
                sheet_name = "Solicitud"
                base_df.to_excel(
                    writer,
                    index=False,
                    header=False,
                    startrow=0,
                    startcol=0,
                    sheet_name=sheet_name,
                )
                
                operaciones_df = pd.json_normalize(operaciones_json or [])
                operaciones_df.columns = [camel_to_title(col) for col in operaciones_df.columns]
                operaciones_df = operaciones_df.replace([np.nan, np.inf, -np.inf], "")
                
                startrow = len(base_df) + 2
                operaciones_df.to_excel(
                    writer,
                    index=False,
                    startrow=startrow,
                    startcol=0,
                    sheet_name=sheet_name,
                )

                worksheet = writer.sheets[sheet_name]
                
                # Estilado
                for row in range(len(base_df)):
                    worksheet.write(row, 0, base_df.iloc[row, 0], bold_border_format)
                    worksheet.write(row, 1, base_df.iloc[row, 1], border_format)

                for col_num, value in enumerate(operaciones_df.columns):
                    worksheet.write(startrow, col_num, value, bold_border_format)
                for row_idx, row in operaciones_df.iterrows():
                    for col_idx, value in enumerate(row):
                        worksheet.write(
                            startrow + 1 + row_idx, col_idx, value, border_format
                        )
                for i, col in enumerate(base_df.columns):
                    max_len = max(base_df[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, max_len + 2)
                for i, col in enumerate(operaciones_df.columns):
                    max_len = max(operaciones_df[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, max_len + 2)

        output.seek(0)
        filename = f"previews/solicitud_{self.base_request.uuid}.xlsx"
        file_path = default_storage.save(filename, ContentFile(output.read()))
        return default_storage.url(file_path)

    def _write_base_sheet(self, writer, base_df, sheet_name, border_format, bold_border_format):
        """Escribe la hoja de información base de la solicitud."""
        base_df.to_excel(
            writer,
            index=False,
            header=False,
            startrow=0,
            startcol=0,
            sheet_name=sheet_name,
        )
        worksheet = writer.sheets[sheet_name]
        
        for row in range(len(base_df)):
            worksheet.write(row, 0, base_df.iloc[row, 0], bold_border_format)
            worksheet.write(row, 1, base_df.iloc[row, 1], border_format)
        
        for i, col in enumerate(base_df.columns):
            max_len = max(base_df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, max_len + 2)

    def _write_stock_sheet(self, writer, stock_data, sheet_name, camel_to_title, 
                          border_format, bold_border_format, header_format):
        """Escribe una hoja para un tipo específico de stock."""
        stock_df = pd.json_normalize(stock_data)
        stock_df.columns = [camel_to_title(col) for col in stock_df.columns]
        stock_df = stock_df.replace([np.nan, np.inf, -np.inf], "")
        
        stock_df.to_excel(
            writer,
            index=False,
            startrow=0,
            startcol=0,
            sheet_name=sheet_name,
        )
        
        worksheet = writer.sheets[sheet_name]
        
        # Estilo del header
        for col_num, value in enumerate(stock_df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        # Estilo de datos
        for row_idx, row in stock_df.iterrows():
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx + 1, col_idx, value, border_format)
        
        # Ajustar ancho de columnas
        for i, col in enumerate(stock_df.columns):
            max_len = max(stock_df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, max_len + 2)
