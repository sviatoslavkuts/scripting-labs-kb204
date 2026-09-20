import os
import sys

# 1 Імпорт персональних даних та налаштування шляху пошуку
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

# Вхідні дані для Варіанта 14
users = {
    "blockchain_dev": {
        "role": "blockchain_developer",
        "clearance": 3,
        "department": "Blockchain",
        "active": True,
    },
    "smart_contract_auditor": {
        "role": "contract_auditor",
        "clearance": 3,
        "department": "Audit",
        "active": True,
    },
    "crypto_trader": {
        "role": "trader",
        "clearance": 2,
        "department": "Trading",
        "active": True,
    },
    "wallet_user": {
        "role": "wallet_user",
        "clearance": 1,
        "department": "Users",
        "active": True,
    },
    "mining_pool": {
        "role": "miner",
        "clearance": 1,
        "department": "Mining",
        "active": False,
    },
}
resources = [
    ("smart_contracts", 3),
    ("audit_reports", 3),
    ("trading_algorithms", 2),
    ("wallet_interface", 1),
    ("private_keys", 3),
    ("public_blockchain", 1),
    ("defi_protocols", 3),
    ("validator_nodes", 3),
    ("market_data", 2),
    ("community_forum", 1),
]
security_levels = (
    "Public Blockchain",
    "Permissioned",
    "Private Network",
    "Institutional",
)
blocked_users = {"mining_pool", "flash_loan_attack", "rug_pull_scam"}

# 2 Виведення списку ресурсів із текстовою назвою рівня безпеки
print("=" * 70)
print(
    f"Список ресурсів | Студент: {STUDENT_NAME}, {GROUP_NAME}, Варіант {VARIANT_NUMBER}"
)
print("=" * 70)

for res_name, res_level in resources:
    # Рівні йдуть від 1 до 4, а індекси в кортежі від 0 до 3, тому віднімаємо 1
    level_text = security_levels[res_level - 1]
    print(f"Ресурс: {res_name:<20} | Рівень безпеки: {level_text}")

print("\n" + "=" * 70)
print("Перевірка прав доступу користувачів")
print("=" * 70)

# Формуємо список користувачів для перевірки доступу
users_to_test = list(users.keys()) + ["flash_loan_attack", "unknown_user"]

# 3 та 4 Реалізація алгоритму перевірки та виведення результатів
for username in users_to_test:
    print(f"\n--- Доступ для: {username} ---")
    for res_name, res_level in resources:
        # 1. Якщо користувача немає в словнику users
        if username not in users:
            status = "DENY (User not found)"

        # 2. Якщо користувач є у списку заблокованих
        elif username in blocked_users:
            status = "DENY (User is blocked)"

        # 3. Якщо обліковий запис неактивний
        elif users[username]["active"] == False:
            status = "DENY (Account inactive)"

        # 4. Якщо рівень допуску користувача більший або дорівнює рівню ресурсу
        elif users[username]["clearance"] >= res_level:
            status = "ALLOW"

        # 5. Якщо рівень допуску менший за рівень ресурсу
        else:
            status = "DENY (Insufficient clearance)"

        # Виведення у заданому форматі
        print(f"user={username} resource={res_name} -> {status}")
