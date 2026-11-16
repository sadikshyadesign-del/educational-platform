import pytest
from django.urls import reverse

from apps.courses.models import Course


@pytest.mark.django_db
def test_homepage_keeps_real_courses_and_renders_resource_samples(client):
    Course.objects.create(
        title="Published Mathematics",
        slug="published-mathematics",
        short_description="A real course description.",
        is_published=True,
    )

    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "SEE Model Questions — Worked Solutions" in content
    assert "6 items" in content
    assert "Published Mathematics" in content
    assert reverse("courses:detail", kwargs={"slug": "published-mathematics"}) in content
    assert 'id="home-hero"' in content
    assert 'class="home-image-trail"' in content
    assert "home/home-figma.css" in content
    assert "static/js/home.js" in content
    assert "<script>" not in content


@pytest.mark.django_db
def test_coming_soon_route_renders_shared_page(client):
    response = client.get(reverse("core:coming_soon"))

    assert response.status_code == 200
    assert "Coming soon." in response.content.decode()
