import tempfile
import unittest
from pathlib import Path

from rainyun.data.models import Account
from rainyun.data.store import DataStore
from rainyun.scheduler.runner import MultiAccountRunner


class SchedulerRunnerTests(unittest.TestCase):
    def test_mark_result_updates_store(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "config.json"
            store = DataStore(data_path)
            store.load()
            account = Account(id="acc_1", name="测试账号")
            store.add_account(account)

            runner = MultiAccountRunner(store)
            result = runner._mark_result(account, success=True, message="success")
            updated = store.get_account("acc_1")

            self.assertTrue(result.success)
            self.assertIsNotNone(updated)
            self.assertEqual(updated.last_status, "success")


if __name__ == "__main__":
    unittest.main()
