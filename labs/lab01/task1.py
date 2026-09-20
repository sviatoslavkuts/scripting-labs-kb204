import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# 1 Імпорт персональних даних
import random

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

# 2 Завантаження вихідного списку паролів та критеріїв (Варіант 14)
passwords = [
    "C2@Command",
    "plain123",
    "Backdoor@D3tect",
    "public123",
    "Rootk1t@Hunt",
    "access123",
    "Exploit@An4lysis",
    "basic",
    "Payload@D3code",
    "default123",
]
criteria = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}
forbidden_passwords = {
    "plain123",
    "public123",
    "access123",
    "basic",
    "default123",
    "user",
}

# 3 Генерація 3 випадкових індексів і додавання дублікатів у кінець
random_index = random.sample(range(len(passwords)), 3)
for i in random_index:
    passwords.append(passwords[i])

# 4 Оцінка надійності кожного пароля
results = []  # Створюємо порожній список для результатів

for pwd in passwords:
    if pwd in forbidden_passwords or len(pwd) < criteria["min_length"]:
        status = "Заборонений"
    else:
        has_dig = any(c.isdigit() for c in pwd)
        has_up = any(c.isupper() for c in pwd)
        has_low = any(c.islower() for c in pwd)
        has_spec = any(not c.isalnum() for c in pwd)

        groups_count = has_dig + has_up + has_low + has_spec

        if (
            groups_count == 4
            and len(pwd) >= criteria["min_length"] + 4
            and passwords.count(pwd) == 1
        ):
            status = "Дуже сильний"
        elif groups_count == 4:
            status = "Сильний"
        elif groups_count >= 2:
            status = "Середній"
        else:
            status = "Слабкий"

    # Зберігаємо результат для виведення
    results.append((pwd, status))

# 5 Виведення результату на екран
print("=" * 60)
print(
    f"Аналіз паролів | Студент: {STUDENT_NAME}, {GROUP_NAME}, Варіант {VARIANT_NUMBER}"
)
print("=" * 60)
print(f"{'Пароль':<25} | {'Статус'}")
print("-" * 60)

for pwd, status in results:
    print(f"{pwd:<25} | {status}")

print("=" * 60)
