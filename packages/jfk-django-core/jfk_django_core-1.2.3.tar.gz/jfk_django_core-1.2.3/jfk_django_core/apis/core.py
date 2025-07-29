import logging
import time
from datetime import timedelta

from celery.exceptions import TimeoutError
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from jfk_django_core.models import CoreHealthcheck
from jfk_django_core.tasks import celery_healthcheck_task

log = logging.getLogger(__name__)


class HealthCheck(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="healthcheck",
        request=OpenApiTypes.OBJECT,
    )
    def head(self, request, format=None) -> Response:
        try:
            return Response(status=status.HTTP_200_OK)
        except Exception:
            log.exception("HealthCheck Exception")
            return Response(
                "Unknown Error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CeleryHealthCheck(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="celery_healthcheck",
    )
    def head(self, request, format=None) -> Response:
        try:
            task_result = celery_healthcheck_task.apply_async()
            time.sleep(5)
            task_result.get(timeout=1)
            healt_check = CoreHealthcheck.objects.first()
            if (
                healt_check is not None
                and healt_check.healthcheck_run_datetime is not None
                and healt_check.healthcheck_run_datetime
                > timezone.now() - timedelta(seconds=10)
                and task_result.status == "SUCCESS"
            ):
                log.info("Celery Healthcheck Task Executed")
                return Response(status=status.HTTP_200_OK)
            return Response(
                "Celery is not executing tasks",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except TimeoutError:
            log.exception("Timeout Excheption on Healthcheck.")
            return Response(
                "Timeout on Celery Healthcheck Task",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception:
            log.exception("HealthCheck Exception")
            return Response(
                "Unknown Error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
