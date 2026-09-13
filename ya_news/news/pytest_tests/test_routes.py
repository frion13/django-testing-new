from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from django.contrib.auth import SESSION_KEY
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_fixture',
    ('home_url', 'detail_url', 'login_url', 'signup_url'),
)
def test_public_pages_available_to_anonymous(client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_author_can_access_comment_pages(
    author_client, request, url_fixture,
):
    url = request.getfixturevalue(url_fixture)

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_other_user_cannot_access_comment_pages(
    other_user_client, request, url_fixture,
):
    url = request.getfixturevalue(url_fixture)

    response = other_user_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_anonymous_redirected_to_login(
    client, request, url_fixture, login_url,
):
    url = request.getfixturevalue(url_fixture)
    query_string = urlencode({'next': url})
    expected_url = f'{login_url}?{query_string}'

    response = client.get(url)

    assertRedirects(
        response,
        expected_url,
        status_code=HTTPStatus.FOUND,
        target_status_code=HTTPStatus.OK,
    )


def test_authenticated_user_can_log_out(author_client, author, logout_url):
    assert author_client.session[SESSION_KEY] == str(author.pk)

    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
    assert SESSION_KEY not in author_client.session
