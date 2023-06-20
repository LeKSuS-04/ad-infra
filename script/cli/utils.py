from tools import Task, TaskManager


def run_tasks_with_manager(*tasks: Task):
    manager = TaskManager()
    manager.add_tasks(list(tasks))
    manager.run_tasks()
