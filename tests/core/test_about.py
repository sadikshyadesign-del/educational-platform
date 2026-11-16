import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_about_page_returns_200_with_single_h1(client):
    response = client.get(reverse("about"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert content.count("<h1") == 1
    assert content.count("</h1>") == 1
    assert "Suren Chhetri" in content


@pytest.mark.django_db
def test_homepage_still_returns_200(client):
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
