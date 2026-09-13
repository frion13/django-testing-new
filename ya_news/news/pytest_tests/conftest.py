from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create_user(username='other_user')


@pytest.fixture
def author_client(db, author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def other_user_client(db, other_user):
    client = Client()
    client.force_login(other_user)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Новость', text='Текст новости')


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news, author=author, text='Комментарий автора',
    )


@pytest.fixture
def news_list(db):
    today = timezone.localdate()
    return News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text=f'Текст новости {index}',
            date=today - timedelta(days=index),
        )
        for index in range(11)
    ])


@pytest.fixture
def comments(db, news, author):
    now = timezone.now()
    result = []
    for index in range(3):
        item = Comment.objects.create(
            news=news, author=author, text=f'Комментарий {index}',
        )
        # auto_now_add заменяет дату при создании: обновляем её отдельно.
        # Порядок времени противоположен порядку первичных ключей.
        created = now - timedelta(hours=index)
        Comment.objects.filter(pk=item.pk).update(created=created)
        item.refresh_from_db()
        result.append(item)
    return result


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def comments_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}
