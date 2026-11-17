import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

tasks = []
next_id = 1


def add_task(title):
    global next_id
    title = title.strip()
    if not title:
        print("Ошибка: название задачи не может быть пустым.")
        return
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    print(f"Задача '{title}' добавлена.")


def list_tasks():
    print("\n--- Список задач ---")
    if not tasks:
        print("Список пуст.")
        return
    for task in tasks:
        status = "V" if task["done"] else "X"
        print(f"[{status}] ID: {task['id']} | {task['title']}")
    print("--------------------")


def mark_task_done(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            print(f"Задача с ID {task_id} выполнена.")
            return
    print("Задача не найдена.")


def delete_task(task_id):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[index]
            logging.info("Задача с ID %s удалена.", task_id)
            return
    logging.error("Задача с ID %s не найдена.", task_id)


def delete_completed_tasks():
    print("\nУдаление выполненных задач...")
    count = len(tasks)
    tasks[:] = [task for task in tasks if not task["done"]]
    count -= len(tasks)
    print(f"Удалено задач: {count}")


def main():
    while True:
        print("\nМеню:")
        print("1. Добавить задачу")
        print("2. Показать задачи")
        print("3. Отметить задачу как выполненную")
        print("4. Удалить задачу по ID")
        print("5. Удалить все выполненные задачи")
        print("6. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_task(input("Введите название задачи: "))
        elif choice == "2":
            list_tasks()
        elif choice == "3":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("Ошибка: ID задачи должен быть целым числом.")
                continue
            mark_task_done(task_id)
        elif choice == "4":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("Ошибка: ID задачи должен быть целым числом.")
                continue
            delete_task(task_id)
        elif choice == "5":
            delete_completed_tasks()
        elif choice == "6":
            print("Выход.")
            break
        else:
            print("Неверный ввод.")


if __name__ == "__main__":
    main()
