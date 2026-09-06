import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authed_client():
    from rest_framework.test import APIClient
    user = User.objects.create_user(email="uploader@example.com", password="pw12345")
    c = APIClient()
    c.force_authenticate(user)
    return c


@pytest.mark.django_db
def test_upload_requires_auth(api_client):
    f = SimpleUploadedFile("test.txt", b"hi", content_type="text/plain")
    r = api_client.post("/api/files/upload/", {"file": f}, format="multipart")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_upload_text_file(authed_client):
    f = SimpleUploadedFile("hello.txt", b"hello world", content_type="text/plain")
    r = authed_client.post("/api/files/upload/", {"file": f}, format="multipart")
    assert r.status_code == 201
    assert r.data["size"] == len(b"hello world")
    assert "url" in r.data


@pytest.mark.django_db
def test_upload_rejects_disallowed_extension(authed_client):
    f = SimpleUploadedFile("evil.exe", b"boom", content_type="application/octet-stream")
    r = authed_client.post("/api/files/upload/", {"file": f}, format="multipart")
    assert r.status_code in (400, 415)


@pytest.mark.django_db
def test_list_own_uploads(authed_client):
    f = SimpleUploadedFile("first.txt", b"first", content_type="text/plain")
    authed_client.post("/api/files/upload/", {"file": f}, format="multipart")
    r = authed_client.get("/api/files/")
    assert r.status_code == 200
    assert r.data["count"] == 1
