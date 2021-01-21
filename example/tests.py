from django.test import TestCase


class TestJustTest(TestCase):
    def test_success_get(self):
        resp = self.client.get("/just-test/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"1")

    def test_failed_get(self):
        resp = self.client.get("/just-test/abc")
        self.assertEqual(resp.status_code, 422)

    def test_success_post(self):
        resp = self.client.post("/just-test/1", data={"name_id": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"2")

    def test_failed_post(self):
        resp = self.client.post("/just-test/abc")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.post("/just-test/1", data={"name_id": "abc"})
        self.assertEqual(resp.status_code, 422)


class TestFunctionView(TestCase):
    def test_success_get(self):
        resp = self.client.get("/test-get-func/1", data={"name_id": '2'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")  # '1' + '2' = '12'

    def test_failed_get(self):
        resp = self.client.get("/test-get-func/1")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.get("/test-get-func/1", data={"name": '2'})
        self.assertEqual(resp.status_code, 422)

        resp = self.client.post("/test-get-func/1")
        self.assertEqual(resp.status_code, 405)

    def test_success_post(self):
        resp = self.client.post("/test-post-func/1", HTTP_Authorization='2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")

    def test_failed_post(self):
        resp = self.client.post("/test-post-func/1")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.get("/test-post-func/1", HTTP_Authorization='2')
        self.assertEqual(resp.status_code, 405)

    def test_success_put(self):
        resp = self.client.put("/test-put-func/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")  # default = "2"

        resp = self.client.put("/test-put-func/2", data={"name": "3"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"23")

    def test_failed_put(self):
        resp = self.client.post("/test-put-func/1")
        self.assertEqual(resp.status_code, 405)

