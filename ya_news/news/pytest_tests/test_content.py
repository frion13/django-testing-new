from news.forms import CommentForm


def test_home_page_news_limit(client, home_url, news_list):
    assert len(news_list) == 11

    response = client.get(home_url)

    assert len(response.context['object_list']) == 10


def test_home_page_news_order(client, home_url, news_list):
    expected_dates = sorted(
        (item.date for item in news_list), reverse=True,
    )[:10]

    response = client.get(home_url)

    dates = [item.date for item in response.context['object_list']]
    assert dates == expected_dates


def test_news_comments_order(client, detail_url, comments):
    expected_dates = sorted(item.created for item in comments)

    response = client.get(detail_url)

    news = response.context['object']
    dates = [item.created for item in news.comment_set.all()]
    assert dates == expected_dates


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authenticated_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)

    assert isinstance(response.context['form'], CommentForm)
