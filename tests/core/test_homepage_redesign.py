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
    assert "static/js/home.js" in content
    assert "<script>" not in content


@pytest.mark.django_db
def test_coming_soon_route_renders_shared_page(client):
    response = client.get(reverse("core:coming_soon"))

    assert response.status_code == 200
    assert "Coming soon." in response.content.decode()


@pytest.mark.django_db
def test_shared_navigation_renders_single_drawer_and_signup_actions(client):
    response = client.get(reverse("courses:list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert content.count('id="mobile-nav-drawer"') == 1
    assert reverse("account_login") in content
    assert reverse("account_signup") in content


@pytest.mark.django_db
def test_shared_navigation_keeps_student_dashboard_and_notifications(client, user_factory):
    user = user_factory(email="nav-student@example.com")
    client.force_login(user)

    response = client.get(reverse("courses:list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert reverse("dashboard:student") in content
    assert reverse("notifications:list") in content
    assert "My Dashboard" in content
    assert "Create account" not in content
