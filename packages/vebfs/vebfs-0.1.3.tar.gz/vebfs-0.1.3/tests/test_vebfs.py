import os
import unittest
from vebfs import (
    copy_file, move_file, delete_file, delete_directory,
    create_backup, get_file_size, list_all_files, ensure_directory_exists,
    find_files, find_directories
)

class TestVebfsOperations(unittest.TestCase):

    # Подготовка тестовых данных
    def setUp(self):
        # Создаём необходимые файлы и директории для тестов
        if not os.path.exists("example.txt"):
            with open("example.txt", "w") as f:
                f.write("Hello from vebfs!")
        if not os.path.exists("old_folder"):
            os.makedirs("old_folder")
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def test_copy_file(self):
        """Тестируем копирование файла."""
        copy_file("example.txt", "copy_example.txt")
        with open("copy_example.txt", "r") as f:
            content = f.read().strip()
        self.assertEqual(content, "Hello from vebfs!")

    def test_move_file(self):
        """Тестируем перемещение файла."""
        move_file("copy_example.txt", "moved_example.txt")
        self.assertTrue(os.path.exists("moved_example.txt"))
        self.assertFalse(os.path.exists("copy_example.txt"))

    def test_create_backup(self):
        """Тестируем создание резервной копии файла."""
        with open("moved_example.txt", "w") as f:
            f.write("Some content")
        create_backup("moved_example.txt", "backup_example.txt")
        self.assertTrue(os.path.exists("backup_example.txt"))

    def test_get_file_size(self):
        """Тестируем получение размера файла."""
        with open("moved_example.txt", "w") as f:
            f.write("Some content")
        create_backup("moved_example.txt", "backup_example.txt")
        self.assertTrue(os.path.exists("backup_example.txt"), "Резервная копия не была создана.")
        size = get_file_size("backup_example.txt")
        self.assertEqual(size, len("Some content"), f"Ожидаемый размер файла не совпадает с реальным: {size}")

    def test_delete_file(self):
        """Тестируем удаление файла."""
        with open("moved_example.txt", "w") as f:
            f.write("Some content")
        delete_file("moved_example.txt")
        self.assertFalse(os.path.exists("moved_example.txt"))

    def test_delete_directory(self):
        """Тестируем удаление директории."""
        delete_directory("old_folder", recursive=True)
        self.assertFalse(os.path.exists("old_folder"))

    def test_ensure_directory_exists(self):
        """Тестируем создание директории, если она не существует."""
        ensure_directory_exists("new_folder")
        self.assertTrue(os.path.exists("new_folder"))
        # Если директория уже существует, не должна быть создана заново
        ensure_directory_exists("new_folder")
        self.assertTrue(os.path.exists("new_folder"))

    def test_find_files(self):
        """Тестируем поиск файлов по шаблону."""
        files = find_files(".", "*.txt")
        self.assertGreater(len(files), 0)
        self.assertTrue(all(file.endswith(".txt") for file in files))

    def test_find_directories(self):
        """Тестируем поиск директорий по шаблону."""
        dirs = find_directories(".", "log*")
        self.assertGreater(len(dirs), 0)
        self.assertTrue(all("log" in dir_name for dir_name in dirs))

    # Завершение тестов
    def tearDown(self):
        """Очистка тестовых данных."""
        if os.path.exists("example.txt"):
            os.remove("example.txt")
        if os.path.exists("moved_example.txt"):
            os.remove("moved_example.txt")
        if os.path.exists("backup_example.txt"):
            os.remove("backup_example.txt")
        if os.path.exists("new_folder"):
            os.rmdir("new_folder")
        if os.path.exists("logs"):
            os.rmdir("logs")

if __name__ == "__main__":
    unittest.main()
