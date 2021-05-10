from django.urls import path

from . import views

urlpatterns = [
    path("just-test/<id>", views.JustTest.as_view()),
    # test function based views with method get, post, put, delete
    # test view injection parameters check Path, Query, Header, Cookie, Body
    path("test-get-func/<name>", views.get_func),
    path("test-post-func/<name>", views.post_func),
    path("test-put-func/<id>", views.put_func),
    path("test-delete-func/<id>", views.test_delete_func),
    # test view injection parameters check Exclusive
    path("test-query-page", views.query_page),
    path("test-query-page-by-exclusive", views.query_page_by_exclusive),
    # test common view without @allow_request_method and injection parameters
    path("test-common-func-view", views.test_common_func_view),
    path("test-common-func-view/<id>", views.test_common_path_func_view),
    path("test-common-class-view", views.CommonClassView.as_view()),
    path("test-upload-file-view", views.TestUploadFile.as_view()),
    path("test-upload-image-view", views.TestUploadImage.as_view()),
]
