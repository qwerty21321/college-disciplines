import contextlib
import io
import unittest
from unittest.mock import patch
import task_manager as tm


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        tm.tasks.clear()
        tm.next_id = 1
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()

    def tearDown(self):
        self.redirect.__exit__(None, None, None)

    def add_three(self):
        for title in ("Купить хлеб", "Сделать ДЗ", "Погулять"):
            tm.add_task(title)

    def test_list_shows_all_three(self):
        self.add_three()
        tm.list_tasks()
        for task_id in (1, 2, 3):
            self.assertIn(f"ID: {task_id} |", self.output.getvalue())

    def test_done_uses_id_after_deletion(self):
        self.add_three()
        tm.delete_task(1)
        tm.mark_task_done(3)
        self.assertEqual([(t['id'], t['done']) for t in tm.tasks],
                         [(2, False), (3, True)])

    def test_unknown_and_negative_ids_do_not_change_tasks(self):
        self.add_three()
        for task_id in (-1, 0, 99):
            tm.mark_task_done(task_id)
        self.assertFalse(any(t['done'] for t in tm.tasks))

    def test_adjacent_completed_tasks_removed(self):
        for title in ("A", "B", "C", "D"):
            tm.add_task(title)
        tm.mark_task_done(1)
        tm.mark_task_done(2)
        tm.delete_completed_tasks()
        self.assertEqual([t['id'] for t in tm.tasks], [3, 4])
        self.assertIn("Удалено задач: 2", self.output.getvalue())

    def test_invalid_input_in_both_menu_branches(self):
        with patch('builtins.input', side_effect=['3', 'abc', '4', 'abc', '6']):
            tm.main()
        self.assertEqual(self.output.getvalue().count(
            "Ошибка: ID задачи должен быть целым числом."), 2)
        self.assertIn("Выход.", self.output.getvalue())

    def test_delete_logs_success_and_missing(self):
        tm.add_task("A")
        with self.assertLogs(level='INFO') as logs:
            tm.delete_task(1)
            tm.delete_task(1)
        self.assertIn('INFO:', logs.output[0])
        self.assertIn('ERROR:', logs.output[1])

    def test_id_not_reused_after_deletion(self):
        self.add_three()
        tm.delete_task(2)
        tm.add_task("Новая")
        self.assertEqual([t['id'] for t in tm.tasks], [1, 3, 4])

    def test_blank_title_rejected(self):
        tm.add_task("   ")
        self.assertEqual(tm.tasks, [])
        self.assertEqual(tm.next_id, 1)

    def test_empty_and_all_completed(self):
        tm.list_tasks()
        self.assertIn("Список пуст.", self.output.getvalue())
        tm.delete_completed_tasks()
        self.add_three()
        for task_id in (1, 2, 3):
            tm.mark_task_done(task_id)
        tm.delete_completed_tasks()
        self.assertEqual(tm.tasks, [])
        tm.delete_completed_tasks()
        self.assertIn("Удалено задач: 0", self.output.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
