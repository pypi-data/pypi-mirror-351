from germanium.decorators import login

from germanium.test_cases.rest import RestTestCase
from germanium.tools.trivials import assert_in, assert_equal, assert_true, assert_is_not_none
from germanium.tools.http import (assert_http_bad_request, assert_http_not_found, assert_http_method_not_allowed,
                                  assert_http_accepted, build_url, assert_http_unauthorized, assert_http_ok,
                                  assert_http_redirect)
from germanium.tools.rest import assert_valid_JSON_created_response, assert_valid_JSON_response

from .test_case import HelperTestCase, AsSuperuserTestCase

from issue_tracker.dynamo.models import Comment


class RESTDynamodDBTestCase(AsSuperuserTestCase, HelperTestCase, RestTestCase):

    COMMENT_API_URL = '/api/dynamo-comment/{}/'
    COMMENT_UI_URL = '/dynamo-comment/{}/'

    @classmethod
    def setUpClass(cls):
        Comment.create_table()
        for i in range(10):
            comment = Comment(
                user_id=str(i),
                issue_id=str(i % 3),
                content=f'test message {i}',
                is_public=bool(i % 2),
                priority=i
            )
            comment.save()

    @classmethod
    def tearDownClass(cls):
        Comment.delete_table()

    @login(is_superuser=True)
    def test_get_api_dynamo_comments_should_return_right_data(self):
        resp = self.get(f'{self.COMMENT_API_URL.format(0)}?_fields=user_id,content,is_public,priority')
        assert_valid_JSON_response(resp)
        assert_equal(len(resp.json()), 4)
        for i, data in enumerate(resp.json()):
            assert_equal(data['priority'], i * 3)
            assert_equal(data['user_id'], str(i * 3))
            assert_equal(data['is_public'], bool(i % 2))
            assert_equal(data['content'], f'test message {i * 3}')

    @login(is_superuser=True)
    def test_get_api_dynamo_one_comment_should_return_right_data(self):
        resp = self.get(f'{self.COMMENT_API_URL.format(0)}3/?_fields=id,user_id,content,is_public,priority')
        assert_valid_JSON_response(resp)
        data = resp.json()
        assert_equal(data['priority'], 3)
        assert_equal(data['user_id'], '3')
        assert_equal(data['is_public'], True)
        assert_equal(data['content'], f'test message 3')

    def test_get_api_dynamo_comments_without_authorization_should_return_unauthorized(self):
        assert_http_unauthorized(self.get(self.COMMENT_API_URL.format(0)))

    @login(is_superuser=True)
    def test_get_dynamo_should_return_list_view(self):
        assert_http_ok(self.get(self.COMMENT_UI_URL.format(0)))

    @login(is_superuser=True)
    def test_get_dynamo_should_return_detail_view(self):
        assert_http_ok(self.get(f'{self.COMMENT_UI_URL.format(0)}3/'))

    @login(is_superuser=True)
    def test_get_dynamo_should_return_not_found_for_invalid_object_detail(self):
        assert_http_not_found(self.get(f'{self.COMMENT_UI_URL.format(1)}3/'))

    def test_get_dynamo_comments_without_authorization_should_return_redirect_to_login(self):
        assert_http_redirect(self.get(f'{self.COMMENT_UI_URL.format(0)}0/'))
        assert_http_redirect(self.get(self.COMMENT_UI_URL.format(0)))
