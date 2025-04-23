# import json
# from django.test import TestCase
# from django.conf import settings
# from apps.ssn_client.clients import SsnService

# class SsnServiceTests(TestCase):
#     def setUp(self):
#         self.service = SsnService(
#             username=settings.SSN_API_USERNAME,
#             password=settings.SSN_API_PASSWORD,
#             cia=settings.SSN_API_CIA,
#             base_url=settings.SSN_API_BASE_URL,
#             max_retries=settings.SSN_API_MAX_RETRIES,
#             retry_delay=settings.SSN_API_RETRY_DELAY,
#         )

#     def test_token_retrieval(self):
#         token = self.service.token
#         self.assertIsNotNone(token)
#         self.assertTrue(isinstance(token, str) and len(token) > 0)

#     def test_refresh_token(self):
#         old_token = self.service.token
#         refreshed = self.service._refresh_token()
#         self.assertTrue(refreshed)
#         new_token = self.service.token
#         self.assertNotEqual(new_token, old_token)

#     def test_check_token(self):
#         valid = self.service._check_token()
#         self.assertTrue(valid)

#     # NO FUNCIONAN ESTOS PUNTOS TODAVIA. DEBERÍAN DARLE EL ALTA DESDE LA SSN

#     # def test_get_especies(self):
#     #     # Usamos un valor literal, ya que no contamos con un modelo TipoEspecie
#     #     tipo_especie = "ACCIONES"
#     #     response = self.service.get_resource("especies", params={"tipoEspecie": tipo_especie})
#     #     self.assertIsNotNone(response, "La respuesta no debe ser None")
#     #     self.assertIsInstance(response, list, "La respuesta debe ser una lista")

#     # def test_get_bancos(self):
#     #     response = self.service.get_resource("bancos")
#     #     self.assertIsNotNone(response, "La respuesta no debe ser None")
#     #     self.assertIsInstance(response, list, "La respuesta debe ser una lista")

#     # def test_get_custodio_depositarias(self):
#     #     response = self.service.get_resource("custodioydepositarias")
#     #     self.assertIsNotNone(response, "La respuesta no debe ser None")
#     #     self.assertIsInstance(response, list, "La respuesta debe ser una lista")

#     # def test_get_sociedades_rg(self):
#     #     response = self.service.get_resource("sociedadesrg")
#     #     self.assertIsNotNone(response, "La respuesta no debe ser None")
#     #     self.assertIsInstance(response, list, "La respuesta debe ser una lista")

#     def test_entrega_semanal_post(self):
#         """
#         Test para el servicio POST de presentación de inversiones semanales.
#         Se envía un JSON de ejemplo y se verifica que la respuesta no sea nula,
#         y que contenga un mensaje de éxito esperado.
#         """
#         payload = json.loads("""{
#         "codigoCompania": "0744",
#         "tipoEntrega": "Semanal",
#         "cronograma": "2025-10",
#         "operaciones": [
#             {
#                 "tipoEspecie": "ON",
#                 "codigoEspecie": "YM35O",
#                 "cantEspecies": 100000.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "25022025",
#                 "fechaLiquidacion": "27022025",
#                 "precioCompra": 1.0
#             },
#             {
#                 "tipoEspecie": "FC",
#                 "codigoEspecie": "883",
#                 "cantEspecies": 137582.21,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "25022025",
#                 "fechaLiquidacion": "25022025",
#                 "precioCompra": 0.73
#             },
#             {
#                 "tipoEspecie": "FC",
#                 "codigoEspecie": "883",
#                 "cantEspecies": 137582.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "V",
#                 "fechaMovimiento": "26022025",
#                 "fechaLiquidacion": "26022025",
#                 "fechaPaseVt": "",
#                 "precioPaseVt": "",
#                 "precioVenta": 0.73
#             },
#             {
#                 "tipoEspecie": "TP",
#                 "codigoEspecie": "S30J8",
#                 "cantEspecies": 2808610.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "28022025",
#                 "fechaLiquidacion": "28022025",
#                 "precioCompra": 1.33
#             },
#             {
#                 "tipoEspecie": "TP",
#                 "codigoEspecie": "S30J5",
#                 "cantEspecies": 74900000.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "28022025",
#                 "fechaLiquidacion": "28022025",
#                 "precioCompra": 1.33
#             },
#             {
#                 "tipoEspecie": "TP",
#                 "codigoEspecie": "TZXD7",
#                 "cantEspecies": 64750000.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "28022025",
#                 "fechaLiquidacion": "28022025",
#                 "precioCompra": 1.54
#             },
#             {
#                 "tipoEspecie": "TP",
#                 "codigoEspecie": "TZXY5",
#                 "cantEspecies": 90560000.0,
#                 "codigoAfectacion": "999",
#                 "tipoValuacion": "V",
#                 "tipoOperacion": "C",
#                 "fechaMovimiento": "28022025",
#                 "fechaLiquidacion": "28022025",
#                 "precioCompra": 1.1
#             }
#         ]
#         }""")

#         response = self.service.post_resource("entregaSemanal", data=payload)
#         self.assertIsNotNone(response, "La respuesta no debe ser None")
#         self.assertIn("ENVIADO CORRECTAMENTE", str(response), "El mensaje de éxito no se encontró en la respuesta")
