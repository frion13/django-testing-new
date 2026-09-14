from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from django.contrib.auth import SESSION_KEY
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS
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


@pytest.mark.parametrize(
    'text',
    [f'Ты {variant}!' for word in BAD_WORDS
     for variant in (word, word.upper())],
)
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

    response = author_client.post(edit_url, data=form_data)

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert Comment.objects.count() == initial_count
    assert updated_comment.text == form_data['text']
    assert updated_comment.author_id == comment.author_id
    assert updated_comment.news_id == comment.news_id
    assertRedirects(response, comments_url, status_code=HTTPStatus.FOUND)


def test_author_can_delete_comment(
    author_client, comment, delete_url, comments_url,
):
    initial_count = Comment.objects.count()

    response = author_client.post(delete_url)

    assert Comment.objects.count() == initial_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assertRedirects(response, comments_url, status_code=HTTPStatus.FOUND)


def test_other_user_cannot_edit_comment(
    other_user_client, comment, edit_url, form_data,
):
    initial_count = Comment.objects.count()

    response = other_user_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert Comment.objects.count() == initial_count
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author_id == comment.author_id
    assert unchanged_comment.news_id == comment.news_id
    assert unchanged_comment.created == comment.created


def test_other_user_cannot_delete_comment(
    other_user_client, comment, delete_url,
):
    original_comments = list(Comment.objects.order_by('pk').values())

    response = other_user_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
    assert list(Comment.objects.order_by('pk').values()) == original_comments


def test_authenticated_user_can_log_out(author_client, author, logout_url):
    assert author_client.session[SESSION_KEY] == str(author.pk)

    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
    assert SESSION_KEY not in author_client.session
