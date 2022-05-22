from pathlib import Path

from django.test import TestCase


class TestJustTest(TestCase):
    def test_success_get(self):
        resp = self.client.get("/test/just-test/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"1")

    def test_failed_get(self):
        resp = self.client.get("/test/just-test/abc")
        self.assertEqual(resp.status_code, 422)

    def test_success_post(self):
        resp = self.client.post("/test/just-test/1", data={"name_id": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"2")

    def test_failed_post(self):
        resp = self.client.post("/test/just-test/abc")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.post("/test/just-test/1", data={"name_id": "abc"})
        self.assertEqual(resp.status_code, 422)


class TestFunctionView(TestCase):
    def test_success_get(self):
        resp = self.client.get("/test/test-get-func/1", data={"name_id": "2"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")  # '1' + '2' = '12'

    def test_failed_get(self):
        resp = self.client.get("/test/test-get-func/1")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.get("/test/test-get-func/1", data={"name": "2"})
        self.assertEqual(resp.status_code, 422)

        resp = self.client.post("/test/test-get-func/1")
        self.assertEqual(resp.status_code, 405)

        resp = self.client.post("/test/test-get-func/1?name_id=2")
        self.assertEqual(resp.status_code, 405)

    def test_success_post(self):
        resp = self.client.post("/test/test-post-func/1", HTTP_Authorization="2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")

    def test_failed_post(self):
        resp = self.client.post("/test/test-post-func/1")
        self.assertEqual(resp.status_code, 422)

        resp = self.client.get("/test/test-post-func/1", HTTP_Authorization="2")
        self.assertEqual(resp.status_code, 405)

    def test_success_put(self):
        resp = self.client.put("/test/test-put-func/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")  # default = "2"

        resp = self.client.put(
            "/test/test-put-func/2", data={"name": "3"}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"23")

    def test_failed_put(self):
        resp = self.client.post("/test/test-put-func/1")
        self.assertEqual(resp.status_code, 405)

    def test_success_delete(self):
        cookies = self.client.cookies
        cookies["session_id"] = 2
        resp = self.client.delete("/test/test-delete-func/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"12")  # "1" + "2" = "12"

        resp = self.client.delete("/test/test-delete-func/2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"22")

    def test_failed_delete(self):
        resp = self.client.delete("/test/test-delete-func/1")
        self.assertEqual(resp.status_code, 422)


class TestExclusive(TestCase):
    def test_success_get(self):
        resp = self.client.get("/test/test-query-page", data={"page-size": 20})
        self.assertEqual(resp.content, b"0")

        resp = self.client.get(
            "/test/test-query-page-by-exclusive", data={"page-size": 20}
        )
        self.assertEqual(resp.content, b"0")

        resp = self.client.get(
            "/test/test-query-page", data={"page-size": 20, "page-num": 3}
        )
        self.assertEqual(resp.content, b"40")

        resp = self.client.get(
            "/test/test-query-page-by-exclusive", data={"page-size": 20, "page-num": 3}
        )
        self.assertEqual(resp.content, b"40")


class TestCommonView(TestCase):
    def test_func_view_success(self):
        resp = self.client.get("/test/test-common-func-view", data={"id": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"1")

        resp = self.client.post("/test/test-common-func-view", data={"name": "Rie"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"Rie")

    def test_path_func_view_success(self):
        resp = self.client.get("/test/test-common-func-view/1", data={"name": "Rie"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"1Rie")

        resp = self.client.post("/test/test-common-func-view/2", data={"name": "Rie"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"2")

    def test_class_view_success(self):
        resp = self.client.get("/test/test-common-class-view", data={"id": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"1")

        resp = self.client.post("/test/test-common-class-view", data={"name": "Rie"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"Rie")

    def test_class_view_failed(self):
        resp = self.client.put("/test/test-common-class-view")
        self.assertEqual(resp.status_code, 405)


class TestUpload(TestCase):
    def test_upload_file_failed(self):
        resp = self.client.post("/test/test-upload-file-view", data={"file": "file"})
        self.assertEqual(resp.status_code, 422)

    def test_upload_file_success(self):
        file_path = Path(__file__).resolve(strict=True).parent.parent / "洛神赋.md"
        with open(file_path, "rb") as file:
            resp = self.client.post("/test/test-upload-file-view", data={"file": file})
            self.assertEqual(resp.status_code, 200)

    def test_upload_image_failed(self):
        file_path = Path(__file__).resolve(strict=True).parent.parent / "洛神赋.md"
        with open(file_path, "rb") as file:
            resp = self.client.post(
                "/test/test-upload-image-view", data={"image": file}
            )
            self.assertEqual(resp.status_code, 422)

    def test_upload_image_success(self):
        image_path = Path(__file__).resolve(strict=True).parent.parent / "Python39.png"

        with open(image_path, "rb") as image:
            resp = self.client.post(
                "/test/test-upload-image-view", data={"image": image}
            )
            self.assertEqual(resp.status_code, 200)
