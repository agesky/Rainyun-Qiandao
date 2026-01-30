import unittest

from rainyun.web.auth import hash_password, issue_token, verify_password, verify_token


class WebAuthTests(unittest.TestCase):
    def test_password_hash(self) -> None:
        password = "test123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("bad", hashed))

    def test_token_issue_and_verify(self) -> None:
        token = issue_token("admin", "secret", 1)
        payload = verify_token(token, "secret")
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), "admin")
        self.assertIsNone(verify_token(token, "wrong"))


if __name__ == "__main__":
    unittest.main()
