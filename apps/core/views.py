import base64
import functools
import hashlib
import logging
import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.core.constants import FAQ_CACHE_KEY
from apps.core.models import FAQItem
from apps.courses.models import Course

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def home_view(request):
    """
    Public home landing page.
    Renders the public homepage with featured courses, sample resources, and FAQs.
    """
    featured_courses = (
        Course.objects.filter(is_published=True, is_archived=False)
        .annotate(
            lesson_count=Count("lessons", filter=Q(lessons__is_published=True), distinct=True)
        )
        .order_by("-is_featured", "-created_at")[:6]
    )
    faqs = cache.get(FAQ_CACHE_KEY)
    if faqs is None:
        faqs = list(FAQItem.objects.filter(is_published=True).order_by("order", "id"))
        cache.set(FAQ_CACHE_KEY, faqs, timeout=3600)

    # TODO: Replace these editorial sample cards with categorized resource records.
    resources = [
        {
            "title": "SEE Model Questions — Worked Solutions",
            "description": "Step-by-step solutions to a full model question set for final preparation.",
            "category": "Worked Solutions",
            "icon": "pencil",
            "access": "request",
            "grade": "Grade 10",
            "topic": "Revision",
            "date": "22 Oct 2026",
        },
        {
            "title": "Integration — Assignment 2",
            "description": "Substitution and integration by parts with graded conceptual challenges.",
            "category": "Assignments",
            "icon": "clipboard-text",
            "access": "request",
            "grade": "Grade 12",
            "topic": "Calculus",
            "date": "21 Oct 2026",
        },
        {
            "title": "Compound Interest — Assignment 1",
            "description": "Four problems on yearly and half-yearly compounding. Show every step.",
            "category": "Assignments",
            "icon": "clipboard-text",
            "access": "free",
            "grade": "Grade 10",
            "topic": "Compound Interest",
            "date": "20 Oct 2026",
        },
        {
            "title": "Mock Test 1 — Mathematics Section",
            "description": "A timed practice paper complete with full answer key and rubric explanations.",
            "category": "Practice Questions",
            "icon": "list-check",
            "access": "request",
            "grade": "Grade 10",
            "topic": "Mock Exam",
            "date": "19 Oct 2026",
        },
        {
            "title": "Algebraic Expressions — Assignment 1",
            "description": "Factorisation, polynomial division, and algebraic identity mastery questions.",
            "category": "Assignments",
            "icon": "clipboard-text",
            "access": "free",
            "grade": "Grade 9",
            "topic": "Algebra",
            "date": "18 Oct 2026",
        },
        {
            "title": "Limits and Continuity — Practice",
            "description": "Standard limit evaluations, L'Hôpital's introductory techniques and continuity proofs.",
            "category": "Practice Questions",
            "icon": "list-check",
            "access": "free",
            "grade": "Grade 11",
            "topic": "Limits",
            "date": "16 Oct 2026",
        },
    ]

    context = {
        "featured_courses": featured_courses,
        "faqs": faqs,
        "resources": resources,
        "hero_webp_available": bool(finders.find("home/images/hero.webp")),
        "hero_jpg_available": bool(finders.find("home/images/hero.jpg")),
        "footer_image_available": bool(finders.find("home/images/footer.webp")),
        "footer_jpg_available": bool(finders.find("home/images/footer.jpg")),
    }
    return render(request, "core/home.html", context)


@require_http_methods(["GET"])
def about_view(request):
    """Public About page for Suren Chhetri."""
    return render(
        request,
        "core/about.html",
        {"portrait_available": bool(finders.find("site/img/suren-portrait.jpg"))},
    )


@require_http_methods(["GET"])
def robots_txt_view(request):
    """
    Serves plain-text robots.txt disallowing sensitive private paths and pointing to sitemap.
    """
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_http_methods(["GET"])
def privacy_view(request):
    """Static Privacy Policy page."""
    return render(request, "core/privacy.html")


@require_http_methods(["GET"])
def terms_view(request):
    """Static Terms of Service page."""
    return render(request, "core/terms.html")


@require_http_methods(["GET"])
def coming_soon_view(request):
    """Simple destination for homepage links whose full pages are not implemented yet."""
    return render(request, "core/coming_soon.html")


@require_http_methods(["GET"])
def health_check_view(request):
    """
    Health check endpoint returning HTTP 200 when the application
    and connected database are operational.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_healthy = True
    except Exception as exc:
        logger.error(f"Health check database failure: {exc}")
        return JsonResponse(
            {
                "status": "error",
                "database": "unhealthy",
                "error": str(exc),
                "timestamp": timezone.now().isoformat(),
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ok",
            "database": "healthy" if db_healthy else "unhealthy",
            "timestamp": timezone.now().isoformat(),
        },
        status=200,
    )


def handler403(request, exception=None):
    """Custom 403 Forbidden error view."""
    return render(request, "403.html", status=403)


def handler404(request, exception=None):
    """Custom 404 Not Found error view."""
    return render(request, "404.html", status=404)


@functools.lru_cache(maxsize=1)
def get_500_style_hash() -> str:
    """
    Computes base64-encoded SHA-256 hash of the <style> block in 500.html.
    Used strictly to permit the standalone 500.html inline stylesheet via CSP style-src.
    """
    template_path = Path(settings.BASE_DIR) / "templates" / "500.html"
    try:
        content = template_path.read_text(encoding="utf-8")
        match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
        if match:
            style_content = match.group(1)
            digest = hashlib.sha256(style_content.encode("utf-8")).digest()
            return base64.b64encode(digest).decode("ascii")
    except Exception as exc:
        logger.warning("Could not calculate 500.html style hash: %s", exc)
    return ""


def handler500(request):
    """
    Custom 500 Internal Server Error view.
    Attaches the 500.html inline style SHA-256 hash to style-src specifically on this response.
    """
    response = render(request, "500.html", status=500)
    style_hash = get_500_style_hash()
    if style_hash:
        hash_src = f"'sha256-{style_hash}'"
        # django-csp 4.0 update hooks
        response._csp_update = {"style-src": [hash_src]}
        response._csp_update_ro = {"style-src": [hash_src]}
        # Also append directly if header was already constructed or middleware was bypassed
        for header_name in ("Content-Security-Policy", "Content-Security-Policy-Report-Only"):
            if header_name in response:
                curr_header = response[header_name]
                if "style-src" in curr_header and hash_src not in curr_header:
                    response[header_name] = curr_header.replace(
                        "style-src ", f"style-src {hash_src} "
                    )
    return response


def csrf_failure(request, reason=""):
    """
    Custom styled CSRF failure view matching platform theme and providing clear recovery steps.
    """
    return render(request, "403_csrf.html", {"reason": reason}, status=403)
