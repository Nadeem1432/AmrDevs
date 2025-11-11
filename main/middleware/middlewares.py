from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.conf import settings
from django.db import DatabaseError, ProgrammingError, OperationalError
from django.template import TemplateDoesNotExist
from django.core.exceptions import SuspiciousFileOperation
import traceback


class CustomErrorMiddleware:
    """
    Handles 404, 500, static directory errors (like 'Directory indexes are not allowed here'),
    and other unexpected exceptions gracefully.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            # Handle the static serve "Directory indexes are not allowed here" case
            if (
                response.status_code == 404
                and request.path.startswith('static')
            ):
                content = (
                    getattr(response, "content", b"").decode(errors="ignore")
                    if hasattr(response, "content")
                    else ""
                )
                if "Directory indexes are not allowed here" in content:
                    return render(
                        request,
                        "main/404.html",
                        {
                            "error_title": "Static Directory Access Blocked",
                            "error_message": (
                                "You tried to access a directory inside the static files "
                                "path (e.g. /static/js/). Only specific files can be served."
                            ),
                            "path": request.path,
                        },
                        status=404,
                    )

            # ✅ Normal 404 for unresolved URLs
            if response.status_code == 404:
                return render(request, "main/404.html", status=404)

            return response

        # URL resolution errors (no matching route)
        except Resolver404:
            return render(request, "main/404.html", status=404)

        # Database-related errors
        except (ProgrammingError, DatabaseError, OperationalError) as e:
            return render(
                request,
                "main/500.html",
                {"error_title": "Database Error", "error_message": str(e)},
                status=500,
            )

        # Template / file / path issues
        except (TemplateDoesNotExist, SuspiciousFileOperation, FileNotFoundError) as e:
            return render(
                request,
                "main/404.html",
                {"error_message": str(e)},
                status=404,
            )

        # All other errors (generic 500)
        except Exception as e:
            tb = traceback.format_exc()
            context = {
                "error_title": "Unexpected Error",
                "error_message": str(e),
                "traceback": tb if settings.DEBUG else "",
            }
            return render(request, "main/500.html", context, status=500)


class MaintenanceModeMiddleware:
    """
    If MAINTENANCE_MODE = True, show a simple maintenance message
    (except to superusers or staff).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        if getattr(settings, "MAINTENANCE_MODE", False):
            if not request.user.is_authenticated or not request.user.is_staff:
                # You can use a template or static HTML here
                return render(request, "common/maintenance.html", status=503)
        return self.get_response(request)
