import time
import requests
from config import API_URL, CHECK_INTERVAL
from bot_sender import send_msg
from mail_sender import send_mail

def get_latest_record():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()["data"][0]

    latest_date = data["date"]
    load_time = data["loaded"]
    count = data["count"]

    return latest_date, load_time, count

def run_monitor():
    last_date = None
    last_count = None

    send_msg("Мониторинг СЭИ запущен, ожидаю новые данные")
    send_mail("Мониторинг СЭИ", "Мониторинг запущен, ожидаю новые данные")

    while True:
        try:
            current_date, load_time, current_count = get_latest_record()

            if last_date is None:
                last_date = current_date
                last_count = current_count

                msg = (
                    f"Последняя запись на сервере, дата, {current_date}, "
                    f"время обработки, {load_time}, количество, {current_count}"
                )

                send_msg(msg)
                send_mail("Последняя запись СЭИ", msg)

            elif current_date != last_date:
                msg = (
                    f"Найдено обновление данных, новая дата, {current_date}, "
                    f"время обработки, {load_time}, количество, {current_count}"
                )

                send_msg(msg)
                send_mail("Обновление данных СЭИ", msg)

                last_date = current_date
                last_count = current_count

        except Exception as e:
            err = f"Ошибка при запросе API, подробности, {e}"
            send_msg(err)
            send_mail("Ошибка мониторинга", err)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_monitor()
