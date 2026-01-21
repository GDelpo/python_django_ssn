"""
Comando para enviar alertas de vencimientos por email.

Uso:
    python manage.py send_deadline_alerts
    python manage.py send_deadline_alerts --dry-run
    python manage.py send_deadline_alerts --level danger

Este comando está diseñado para ejecutarse como tarea programada (cron).
Ejemplo de cron diario a las 8:00 AM:
    0 8 * * * cd /app && python manage.py send_deadline_alerts
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from operaciones.services.alert_service import AlertService, AlertLevel

logger = logging.getLogger("operaciones")


class Command(BaseCommand):
    help = "Envía alertas de vencimientos pendientes por email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra las alertas sin enviar emails",
        )
        parser.add_argument(
            "--level",
            choices=["all", "danger", "warning"],
            default="warning",
            help="Nivel mínimo de alerta a enviar (default: warning)",
        )
        parser.add_argument(
            "--to",
            type=str,
            help="Email de destino (usa ALERT_EMAIL_TO por defecto)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🔔 Verificando alertas de vencimientos..."))
        
        # Obtener alertas
        alertas = AlertService.get_alertas_pendientes()
        
        if not alertas:
            self.stdout.write(self.style.SUCCESS("✅ No hay alertas pendientes"))
            return
        
        # Filtrar por nivel
        level_filter = options["level"]
        if level_filter == "danger":
            alertas = [a for a in alertas if a.level == AlertLevel.DANGER]
        elif level_filter == "warning":
            alertas = [a for a in alertas if a.level in [AlertLevel.DANGER, AlertLevel.WARNING]]
        
        if not alertas:
            self.stdout.write(self.style.SUCCESS("✅ No hay alertas del nivel especificado"))
            return
        
        # Mostrar resumen
        self.stdout.write(f"\n📋 Alertas encontradas: {len(alertas)}")
        for alerta in alertas:
            level_icon = {
                AlertLevel.DANGER: "🔴",
                AlertLevel.WARNING: "🟡",
                AlertLevel.INFO: "🔵",
                AlertLevel.SUCCESS: "🟢",
            }.get(alerta.level, "⚪")
            
            self.stdout.write(
                f"  {level_icon} {alerta.title}: {alerta.message}"
            )
        
        # Modo dry-run
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\n⚠️  Modo dry-run: no se enviaron emails"))
            return
        
        # Determinar destinatario
        to_email = options.get("to") or getattr(settings, "ALERT_EMAIL_TO", None)
        
        if not to_email:
            self.stdout.write(self.style.ERROR(
                "❌ No se especificó email de destino. "
                "Use --to o configure ALERT_EMAIL_TO en settings."
            ))
            return
        
        # Enviar email
        try:
            self._send_alert_email(alertas, to_email)
            self.stdout.write(self.style.SUCCESS(f"\n✅ Email enviado a {to_email}"))
        except Exception as e:
            logger.exception("Error enviando email de alertas")
            self.stdout.write(self.style.ERROR(f"❌ Error enviando email: {e}"))

    def _send_alert_email(self, alertas, to_email):
        """Envía el email con las alertas."""
        
        # Contexto para el template
        context = {
            "alertas": alertas,
            "total_alertas": len(alertas),
            "alertas_criticas": len([a for a in alertas if a.level == AlertLevel.DANGER]),
            "company_name": getattr(settings, "COMPANY_NAME", "Sistema SSN"),
            "base_url": getattr(settings, "BASE_URL", ""),
        }
        
        # Renderizar email
        subject = self._build_subject(alertas)
        html_message = render_to_string("emails/deadline_alerts.html", context)
        plain_message = strip_tags(html_message)
        
        # Enviar
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )

    def _build_subject(self, alertas):
        """Construye el asunto del email según la urgencia."""
        criticas = len([a for a in alertas if a.level == AlertLevel.DANGER])
        
        if criticas > 0:
            return f"🚨 URGENTE: {criticas} presentación(es) SSN vencida(s)"
        else:
            return f"⚠️ Recordatorio: {len(alertas)} presentación(es) SSN pendiente(s)"
