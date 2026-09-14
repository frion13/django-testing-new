from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf as lazy_fixture


HOME_URL = lazy_fixture('home_url')
DETAIL_URL = lazy_fixture('detail_url')
LOGIN_URL = lazy_fixture('login_url')
SIGNUP_URL = lazy_fixture('signup_url')
EDIT_URL = lazy_fixture('edit_url')
DELETE_URL = lazy_fixture('delete_url')
LOGOUT_URL = lazy_fixture('logout_url')

ANONYMOUS_CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
OTHER_USER_CLIENT = lazy_fixture('other_user_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, route_client, method, expected_status',
    (
        (HOME_URL, ANONYMOUS_CLIENT, 'get', HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS_CLIENT, 'get', HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, 'get', HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, 'get', HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, 'get', HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, 'get', HTTPStatus.OK),
        (EDIT_URL, OTHER_USER_CLIENT, 'get', HTTPStatus.NOT_FOUND),
        (DELETE_URL, OTHER_USER_CLIENT, 'get', HTTPStatus.NOT_FOUND),
        (LOGOUT_URL, AUTHOR_CLIENT, 'post', HTTPStatus.OK),
    ),
)
def test_route_returns_expected_status(
    url, route_client, method, expected_status,
):
    response = getattr(route_client, method)(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize('url', (EDIT_URL, DELETE_URL))
def test_anonymous_redirected_to_login(
    client, url, login_url,
):
    query_string = urlencode({'next': url})
    expected_url = f'{login_url}?{query_string}'

    response = client.get(url)

    assertRedirects(
        response,
        expected_url,
        status_code=HTTPStatus.FOUND,
        target_status_code=HTTPStatus.OK,
    )
