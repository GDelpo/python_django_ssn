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

    def generar_preview(self):
        if not self.operations:
            return False  # Nada que mostrar

        # Serializa la solicitud y sus operaciones (de modelos reales)
        self.payload = serialize_operations(self.base_request, self.operations)

        # Si necesitás transformar algún campo, hacelo sobre el payload
        for operacion in self.payload.get("operaciones", []):
            if "cantEspecies" in operacion and operacion["cantEspecies"] is not None:
                if operacion.get("tipoEspecie") != "FC":  # Ajustar según tu lógica real
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
        operaciones_json = base_json.pop("operaciones", None)

        # Info general
        base_df = pd.DataFrame(list(base_json.items()), columns=["Campo", "Valor"])
        base_df["Campo"] = base_df["Campo"].apply(camel_to_title)

        # Operaciones
        operaciones_df = pd.json_normalize(operaciones_json or [])
        operaciones_df.columns = [camel_to_title(col) for col in operaciones_df.columns]

        base_df = base_df.replace([np.nan, np.inf, -np.inf], "")
        operaciones_df = operaciones_df.replace([np.nan, np.inf, -np.inf], "")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            sheet_name = "Solicitud"
            base_df.to_excel(
                writer,
                index=False,
                header=False,
                startrow=0,
                startcol=0,
                sheet_name=sheet_name,
            )
            startrow = len(base_df) + 2
            operaciones_df.to_excel(
                writer,
                index=False,
                startrow=startrow,
                startcol=0,
                sheet_name=sheet_name,
            )

            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            border_format = workbook.add_format({"border": 1})
            bold_border_format = workbook.add_format({"bold": True, "border": 1})

            # Estilado igual que antes...
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
