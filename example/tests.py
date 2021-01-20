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
