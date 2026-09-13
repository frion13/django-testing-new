from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment


def test_anonymous_user_cannot_create_comment(
    client, detail_url, login_url, form_data, comment,
):
    initial_count = Comment.objects.count()
    original_comments = list(Comment.objects.order_by('pk').values())
    query_string = urlencode({'next': detail_url})
    expected_url = f'{login_url}?{query_string}'

    response = client.post(detail_url, data=form_data)

    assert Comment.objects.count() == initial_count
    assert list(Comment.objects.order_by('pk').values()) == original_comments
    assertRedirects(response, expected_url, status_code=HTTPStatus.FOUND)


def test_authenticated_user_creates_comment(
    author_client, author, news, detail_url, comments_url, form_data,
):
    initial_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(detail_url, data=form_data)

    assert Comment.objects.count() == len(initial_ids) + 1
    comment = Comment.objects.exclude(pk__in=initial_ids).get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news
    assertRedirects(response, comments_url, status_code=HTTPStatus.FOUND)


@pytest.mark.parametrize('text', ('Ты редиска!', 'Ты РЕДИСКА!'))
def test_comment_with_bad_word_is_not_saved(
    author_client, detail_url, text, comment,
):
    initial_count = Comment.objects.count()
    original_comments = list(Comment.objects.order_by('pk').values())

    response = author_client.post(detail_url, data={'text': text})

    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == initial_count
    assert list(Comment.objects.order_by('pk').values()) == original_comments
    assertFormError(response.context['form'], 'text', 'Не ругайтесь!')


def test_author_can_edit_comment(
    author_client, comment, edit_url, comments_url, form_data,
):
    initial_count = Comment.objects.count()
    original_author_id = comment.author_id
    original_news_id = comment.news_id

    response = author_client.post(edit_url, data=form_data)

    comment.refresh_from_db()
    assert Comment.objects.count() == initial_count
    assert comment.text == form_data['text']
    assert comment.author_id == original_author_id
    assert comment.news_id == original_news_id
    assertRedirects(response, comments_url, status_code=HTTPStatus.FOUND)


def test_author_can_delete_comment(
    author_client, comment, delete_url, comments_url,
):
    initial_count = Comment.objects.count()

    response = author_client.post(delete_url)

    assert Comment.objects.count() == initial_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assertRedirects(response, comments_url, status_code=HTTPStatus.FOUND)


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_other_user_cannot_change_comment(
    other_user_client, comment, request, url_fixture, form_data,
):
    url = request.getfixturevalue(url_fixture)
    original_comments = list(Comment.objects.order_by('pk').values())

    response = other_user_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert list(Comment.objects.order_by('pk').values()) == original_comments
