import argparse
import sys
from labs.lab02.task1 import User, Admin, UserAccount, AuditLog


def run_demo():
    print("=== Демонстрація Завдання 1: Система керування користувачами та безпекою ===")
    
    # 1. Створення журналу аудиту та базового користувача
    audit = AuditLog()
    user = User(username="student1", email="student1@example.com")
    
    # Встановлення захищеного пароля (PBKDF2 + сіль)
    user.set_password("SecurePass123!")
    print(f"[OK] Створено користувача: {user}")

    # Створення облікового запису (композиція)
    account = UserAccount(user=user, audit_log=audit)

    # 2. Перевірка валідації email через @property та сеттер
    print("\n--- Тестування валідації Email ---")
    try:
        user.email = "invalid-email"  # Неправильний формат
    except ValueError as e:
        print(f"[CATCH] Зловлено очікувану помилку валідації email: {e}")
    
    user.email = "new_student@university.ua"  # Правильний формат
    print(f"[OK] Email успішно змінено на: {user.email}")

    # 3. Автентифікація: успішний та невдалий вхід
    print("\n--- Тестування автентифікації (Login) та сесій ---")
    # Невдалий вхід (неправильний пароль)
    account.login("student1", "WrongPassword123", "192.168.1.10")
    
    # Успішний вхід
    success = account.login("student1", "SecurePass123!", "192.168.1.10")
    print(f"Статус входу: {'Успішно' if success else 'Помилка'}")
    print(f"Чи активна сесія (is_authenticated): {account.is_authenticated()}")

    # 4. Демонстрація прав адміністратора (наслідування від User)
    print("\n--- Тестування прав адміністратора (Admin) ---")
    admin = Admin(username="root_admin", email="admin@security.ua")
    admin.set_password("AdminRoot999!")
    
    # Додавання та перевірка прав
    admin.grant_permission("DELETE_USERS")
    admin.grant_permission("VIEW_LOGS")
    print(admin)
    print(f"Чи має право 'DELETE_USERS': {admin.has_permission('DELETE_USERS')}")
    
    # Відкликання прав
    admin.revoke_permission("DELETE_USERS")
    print(f"Після відкликання, чи має право 'DELETE_USERS': {admin.has_permission('DELETE_USERS')}")

    # 5. Вихід із системи (Logout)
    print("\n--- Тестування виходу (Logout) ---")
    account.logout()
    print(f"Після logout, чи автентифікований: {account.is_authenticated()}")

    # 6. Виведення повного журналу подій AuditLog
    print("\n=== Журнал аудиту подій (AuditLog) ===")
    audit.show_all()


def main():
    parser = argparse.ArgumentParser(description="Консольна утиліта лабораторної роботи №2 (Завдання 1)")
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")

    # Режим демо для першого завдання
    subparsers.add_parser("demo", help="Запустити демонстрацію ООП-моделей Завдання 1")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()