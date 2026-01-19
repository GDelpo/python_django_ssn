from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("operaciones", "0015_alter_compraoperacion_precio_compra"),
    ]

    operations = [
        migrations.AlterField(
            model_name="baserequestmodel",
            name="estado",
            field=models.CharField(
                choices=[
                    ("BORRADOR", "Borrador"),
                    ("CARGADO", "Cargado (sin confirmar)"),
                    ("PRESENTADO", "Presentado"),
                    ("RECTIFICACION_PENDIENTE", "Rectificación Pendiente"),
                    ("A_RECTIFICAR", "Aprobado para Rectificar"),
                    ("ENVIADA", "Enviada (deprecated)"),
                    ("RECTIFICANDO", "Rectificando (deprecated)"),
                ],
                default="BORRADOR",
                help_text="Estado de la solicitud (Borrador, Enviada, Rectificando)",
                max_length=32,
            ),
        ),
    ]
