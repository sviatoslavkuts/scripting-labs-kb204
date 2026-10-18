import json
from collections import defaultdict
from typing import List, Dict, Any


class EDRLogAggregator:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.alerts: List[Dict[str, Any]] = []
        self.load_logs()

    # Завантаження EDR логів з JSON-файлу
    def load_logs(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.alerts = data
                elif isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            self.alerts = value
                            break
            print(f"[OK] Успішно завантажено {len(self.alerts)} записів з файлу: {self.filepath}")
        except FileNotFoundError:
            print(f"[ERROR] Файл не знайдено за шляхом: {self.filepath}")
            self.alerts = []
        except json.JSONDecodeError:
            print(f"[ERROR] Помилка декодування JSON у файлі: {self.filepath}")
            self.alerts = []

    # Агрегація подій за рівнем критичності (Severity)
    def get_severity_stats(self) -> Dict[str, int]:
        stats = defaultdict(int)
        for alert in self.alerts:
            severity = str(alert.get("Severity", "UNKNOWN")).upper()
            stats[severity] += 1
        return dict(stats)

    # Агрегація подій за назвою загрози (ThreatName)
    def get_threat_type_stats(self) -> Dict[str, int]:
        stats = defaultdict(int)
        for alert in self.alerts:
            t_name = str(alert.get("ThreatName", "Unknown"))
            stats[t_name] += 1
        return dict(stats)

    # Фільтрація неліквідованих загроз на основі ActionTaken
    def filter_unresolved(self) -> List[Dict[str, Any]]:
        unresolved = []
        # Дії, які свідчать, що загроза НЕ була повністю заблокована чи видалена
        unresolved_actions = ["detected", "ignored", "noaction", "pending", "open", "unresolved"]
        for alert in self.alerts:
            action = str(alert.get("ActionTaken", "")).lower()
            if action in unresolved_actions:
                unresolved.append(alert)
        return unresolved

    # Формування зведеного звіту за результатами аналізу логів
    def generate_report(self) -> str:
        severity_stats = self.get_severity_stats()
        threat_stats = self.get_threat_type_stats()
        unresolved_alerts = self.filter_unresolved()

        report_lines = [
            "=== EDR & Antivirus Log Aggregation Report (Variant 14) ===",
            f"Загальна кількість подій: {len(self.alerts)}",
            f"Кількість неліквідованих загроз: {len(unresolved_alerts)}",
            "\n[+] Статистика за критичністю (Severity):"
        ]
        
        for sev, count in severity_stats.items():
            report_lines.append(f"    - {sev}: {count}")

        report_lines.append("\n[+] Статистика за типами загроз (ThreatName):")
        for t_type, count in threat_stats.items():
            report_lines.append(f"    - {t_type}: {count}")

        return "\n".join(report_lines)