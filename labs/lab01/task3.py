import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from functools import wraps

# Імпорт персональних даних
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

# Налаштування для 14 варіанта і персональна сіль
SALT = f"{VARIANT_NUMBER:05d}"  # Генерує "00014"
MIN_PASSWORD_LENGTH = 16


# Шляхи до папки data та файлів (створюватимуться автоматично)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
LOG_JSON = os.path.join(DATA_DIR, 'log.json')

# Власний виняток для короткого пароля
class ValidationError(Exception):
    pass

# Функція хешування sha512 для 14 варіанта  
def generate_hash(password: str, salt: str = SALT) -> str:
    if not password or not salt:
        raise ValueError("Пароль або сіль не можуть бути порожніми.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Пароль занадто короткий. Мінімальна довжина: {MIN_PASSWORD_LENGTH}")
    
    # Хешування конкатенації пароля та солі
    hasher = hashlib.sha512()
    hasher.update((password + salt).encode('utf-8'))
    return hasher.hexdigest()

# Функції реєстрації користувачів
def create_user(username, password):
    return username, generate_hash(password)

def create_users(users_list):
    # Автоматичне створення папки data
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(USERS_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['login', 'hash'])
        for u, p in users_list:
            try:
                writer.writerow(create_user(u, p))
            except (ValueError, ValidationError) as e:
                print(f"[-] Помилка реєстрації {u}: {e}")

# Декоратор логування
def log_event(func):
    @wraps(func)
    def wrapper(username, password, *args, **kwargs):
        status = "failure"
        try:
            result = func(username, password, *args, **kwargs)
            status = "success" if result else "failure"
            return result
        except Exception:
            status = "failure"
            raise
        finally:
            os.makedirs(DATA_DIR, exist_ok=True)
            log_entry = {
                "event": "login",
                "user": username,
                "result": status,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "args": args,
                "kwargs": kwargs
            }
            try:
                logs = []
                if os.path.exists(LOG_JSON):
                    with open(LOG_JSON, 'r', encoding='utf-8') as f:
                        try:
                            logs = json.load(f)
                        except json.JSONDecodeError:
                            pass
                logs.append(log_entry)
                with open(LOG_JSON, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=4)
            except OSError as e:
                print(f"Помилка запису логу: {e}")
    return wrapper

# Функція автентифікації
@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")
    
    try:
        with open(USERS_CSV, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            users_db = list(reader)
            
        hashed_pw = generate_hash(password)
        for row in users_db:
            if row['login'] == username and row['hash'] == hashed_pw:
                return True
        return False
    except (ValueError, ValidationError):
        return False

# Головна функція main()
def main():
    print("=" * 60)
    print(f"Завдання 3 | Студент: {STUDENT_NAME}, {GROUP_NAME}, Варіант {VARIANT_NUMBER}")
    print("=" * 60)

    # 10 користувачів
    users_to_register = (
        ("admin", "SuperSecretAdminPassword123"),
        ("user1", "VeryLongPasswordForUserOne"),
        ("user2", "Short123"),
        ("user3", "AnotherLongPasswordHere321"),
        ("user4", "JustAnotherPassword123456"),
        ("user5", "SecurePasswordForUserFive"),
        ("user6", "MyPass1234567890123"),
        ("user7", "PasswordNumberSeven12345"),
        ("user8", "ThisIsUserEightPassword2026"),
        ("user9", "FinalUserPassword123456789")
    )
    
    print("\n--- 1. Реєстрація користувачів (Створення бази) ---")
    try:
        create_users(users_to_register)
        print("[+] Користувачів оброблено та записано в users.csv")
    except (OSError, PermissionError) as e:
        print(f"[-] Помилка роботи з файлом: {e}")
        
    print("\n--- 2. Читання бази даних ---")
    try:
        with open(USERS_CSV, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            users_db = list(reader)
            print(f"{'Логін':<15} | {'Хеш (перші 40 символів)'}")
            print("-" * 60)
            for row in users_db:
                print(f"{row['login']:<15} | {row['hash'][:40]}...")
    except FileNotFoundError:
        print("[-] Файл бази даних не знайдено.")
    except (OSError, PermissionError) as e:
        print(f"[-] Помилка читання: {e}")

    print("\n--- 3. Тестування автентифікації та логування ---")
    try:
        # Успішний вхід
        print(f"Вхід 'admin' (правильний пароль): {login('admin', 'SuperSecretAdminPassword123')}")
        # Неправильний пароль
        print(f"Вхід 'user1' (неправильний пароль): {login('user1', 'WrongPassword1234567890')}")
        # Порожній пароль (викличе ValueError)
        print("Вхід 'user4' (порожній пароль): ", end="")
        print(login("user4", ""))
    except (ValueError, ValidationError) as e:
        print(f"Спіймано виняток: {e}")
        
    print("\n[+] Усі тести завершено. ")

if __name__ == "__main__":
    main()