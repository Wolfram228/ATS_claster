# Backend проекта "Веб-сервис сбора и анализа статистической информации цен на электроэнергию"

## 1. Общая архитектура

Бэкенд проекта написан на языке **Python** с использованием фреймворка **Flask**, который обеспечивает лёгкость развертывания и гибкость при создании REST API.  
Основная роль бэкенда — это обработка, хранение и предоставление данных о ценах на электроэнергию, поступающих из внешних источников.

Он отвечает за:

- **Получение и обработку данных о ценах на электроэнергию** — модуль `fetch_data.py` регулярно загружает отчёты с официального ресурса АТС, преобразует их в структурированный формат и сохраняет в базу данных.
- **Взаимодействие с базой данных** — осуществляется через ORM SQLAlchemy, что позволяет работать с таблицами не напрямую через SQL-запросы, а через Python-классы (`models.py`). Это повышает читаемость, безопасность и удобство поддержки.
- **Предоставление API для фронтенда** — через Flask-приложение (`app.py`) реализованы REST API-эндпоинты, позволяющие запрашивать отчёты, фильтровать данные по дате, региону и другим параметрам, а также скачивать статистические отчёты в формате Excel.
- **Выполнение математических расчётов и генерацию статистики** — бэкенд агрегирует значения по типам генерации (ГЭС, ТЭС, АЭС и др.), рассчитывает средние цены, объёмы производства, экспорта и импорта электроэнергии.

Архитектура построена по **модульному принципу**, что обеспечивает прозрачное разделение логики:
- `config.py` хранит параметры подключения к базе данных;
- `models.py` описывает структуру таблиц и их поля;
- `fetch_data.py` отвечает за сбор и загрузку новых данных;
- `app.py` объединяет всё в единое веб-приложение и предоставляет интерфейсы для фронтенда.

Каждый компонент бэкенда выполняет строго определённую роль, а их взаимодействие происходит через единый слой данных (PostgreSQL).  
Такое решение делает систему **масштабируемой**, **устойчивой к ошибкам** и **удобной для расширения** — при необходимости можно добавить новые типы данных, отчётов или API без изменения основной логики.

## 2. Файлы проекта

### 2.1 `app.py` — назначение и содержание

app.py — главный файл бэкенда проекта. Его задачи:

- Инициализация приложения Flask — запуск веб-сервера, обработка HTTP-запросов.
- Подключение к базе данных — через SQLAlchemy и создание сессий для запросов.
- Организация API для фронтенда — маршруты /api/..., которые предоставляют данные о ценах, регионах, статистику и отчёты.
- Автоматическое обновление данных — запуск скрипта fetch_data.py через планировщик APScheduler каждый день в 18:00 и через ручной API /api/reload.
- Выполнение бизнес-логики — фильтрация данных по дате, региону, часу, агрегация, расчёт суммарного объёма и средних цен.
- Генерация Excel-отчётов — экспорт данных через /api/report/xls.
- Отображение веб-страницы — рендер главной страницы с графиками и статистикой (index.html).

### 2.1.1  Примеры кода и пояснения

#### 2.1.1 Инициализация приложения и базы данных
```python
app = Flask(__name__)
app.json.ensure_ascii=False
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
```
- Flask(__name__) — создаёт экземпляр веб-приложения.
- app.json.ensure_ascii=False — разрешает корректное отображение русских символов в JSON.
- create_engine(DB_URL) — подключение к базе данных PostgreSQL.
- Session = sessionmaker(bind=engine) — фабрика сессий для запросов к БД.
- Base.metadata.create_all(engine) — создаёт таблицы, если их ещё нет.

#### 2.1.2 Планировщик автоматического обновления данных
```python
def reload_data_bg():
    cwd = os.getcwd()
    python = os.path.join(cwd, 'venv/bin/python3')
    script = os.path.join(cwd, 'fetch_data.py')
    subprocess.run([python, script], cwd=cwd)

def start_scheduler():
    tz = pytz.timezone('Europe/Moscow')
    sched = BackgroundScheduler(timezone=tz)
    sched.add_job(reload_data_bg, 'cron', hour=18, minute=0, id='daily_fetch')
    sched.start()
```
- reload_data_bg() — запускает скрипт fetch_data.py в фоновом режиме.
- start_scheduler() — настраивает ежедневное автоматическое обновление данных в 18:00 по Москве.
  
#### 2.1.3 Проверка параметров запросов
```python
def enforce_limit(f_iso, t_iso):
    if not f_iso or not t_iso:
        abort(400, 'Оба параметра from и to обязательны')
    f = datetime.fromisoformat(f_iso)
    t = datetime.fromisoformat(t_iso)
    if t < f:
        abort(400, 'to должно быть >= from')
    if (t - f) > timedelta(days=365):
        abort(400, 'нельзя запрашивать больше чем 3 месяца')
    return f, t
```
- Проверяет корректность дат начала (from) и конца (to) в API-запросах.
- Ограничивает максимальный период запроса до 1 года.
- При некорректных данных возвращает ошибку HTTP 400.

#### 2.1.4 API для ручного обновления данных
```python
@app.route('/api/reload', methods=['POST'])
def api_reload():
    threading.Thread(target=reload_data_bg, daemon=True).start()
    return jsonify({'status':'started','message':'Обновление запущено'})
```
- Запускает обновление данных в отдельном потоке, чтобы сервер не блокировался.
- Возвращает JSON с подтверждением начала процесса.

#### 2.1.5 API для получения таблицы данных
```python
@app.route('/api/table')
def api_table():
    f_iso = request.args.get('from')
    t_iso = request.args.get('to')
    f, t = enforce_limit(f_iso, t_iso)
    region = request.args.get("region")
    hour = request.args.get("hour")

    with engine.connect() as conn:
        filters = ["timestamp >= :from", "timestamp <= :to"]
        params = {"from": f, "to": t}
        if region:
            filters.append("region = :region")
            params["region"] = region
        if hour:
            filters.append("EXTRACT(HOUR FROM timestamp) = :hour")
            params["hour"] = int(hour)
        where_clause = " AND ".join(filters)
        sql = f"SELECT * FROM elec_reports WHERE {where_clause} ORDER BY timestamp, region"
        rows = conn.execute(text(sql), params).mappings()
        data = [dict(r) for r in rows]
    return jsonify(data)
```
- Позволяет фронтенду получать данные с фильтрами: даты, регион, час.
- Выполняет SQL-запрос и возвращает результат в формате JSON.

#### 2.1.6 Главная страница сайта
```python
@app.route("/")
def index():
    ses = Session()
    # Подготовка данных для графиков: прошлый и вчерашний день
    # ...
    ses.close()
    return render_template('index.html',
        gens_labels=[label for _,label in gens],
        prev_date=prev.strftime('%Y-%m-%d'),
        yest_date=yest.strftime('%Y-%m-%d'),
        vol_prev=[vol_prev[key] for key,_ in gens],
        vol_yest=[vol_yest[key] for key,_ in gens],
        shares=shares,
        prices=prices,
        region=region
    )
```
- Рендерит главную страницу с графиками и статистикой по генерации электроэнергии и ценам.
- Считает суммарный объём по типам генерации для предыдущих дней.

#### 2.1.7 Генерация Excel-отчёта
```python
@app.route('/api/report/xls')
def api_report_xls():
    df = pd.DataFrame(records)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     download_name="report.xlsx", as_attachment=True)
```
- Преобразует данные в Excel-файл с помощью pandas.
- Возвращает пользователю как скачиваемый файл.

### 2.2 Назначение файла `config.py`

Файл `config.py` — это **конфигурационный модуль** бэкенда, который хранит все основные настройки проекта.  
Он используется для удобного управления параметрами подключения и изоляции чувствительных данных (например, логина, пароля и адреса базы данных) от основного кода приложения.

Благодаря этому подходу:

- конфигурация отделена от логики программы,  
- можно легко менять параметры без изменения исходного кода,  
- обеспечивается безопасность и гибкость при развёртывании проекта на разных серверах.

---

### Пример содержимого файла `config.py`

```python
DB_URL = 'postgresql+psycopg2://energy_user:energy~ATS%istu@localhost/energy_db'
```

### 2.3 Назначение файла `fetch_data.py`

Файл `fetch_data.py` — это ключевой компонент бэкенда, который отвечает за **автоматическую загрузку, обработку и сохранение данных о ценах на электроэнергию** из официального источника [АТС Энерго](https://www.atsenergo.ru/).

Он выполняет следующие задачи:
- обращается к сайту и скачивает отчёты в формате `.xls`;
- парсит полученные данные в структуру `pandas.DataFrame`;
- сохраняет данные в базу PostgreSQL через SQLAlchemy;
- ведёт журнал загрузок, чтобы не дублировать уже сохранённые даты.

---

### Основные функции и логика работы

#### 2.3.1. Импорты и настройка окружения

```python
import warnings
from urllib3.exceptions import InsecureRequestWarning
import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models import Base, ElecReport, LoadHistory
from config import DB_URL

warnings.simplefilter('ignore', InsecureRequestWarning)
```
### Здесь подключаются библиотеки:
- requests, BeautifulSoup — для загрузки и парсинга страниц сайта;
- pandas — для чтения Excel-файлов и работы с таблицами;
- sqlalchemy — для соединения с базой данных;
- datetime — для работы с датами;
- warnings — для отключения ненужных SSL-предупреждений.

#### 2.3.2. Подключение к базе данных
```python
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
```
- создаётся соединение с базой данных по строке из config.py;
- при необходимости создаются таблицы из моделей;
- создаётся объект Session для выполнения операций с базой.

#### 2.3.3. Загрузка Excel-файлов
```python
def download_xls(date):
    """Скачать XLS за конкретную дату."""
    ds = date.strftime('%Y%m%d')
    url_page = f'https://www.atsenergo.ru/nreport?rname=trade_region_spub&rdate={ds}'
    page = requests.get(url_page, headers=HEADERS, verify=False)
    page.raise_for_status()

    soup = BeautifulSoup(page.content, 'html.parser')
    link = soup.find('a', href=lambda h: h and 'fid=' in h)
    if not link:
        raise ValueError("нет .xls ссылки на странице")
    file_url = urljoin(page.url, link['href'])

    resp = requests.get(file_url, headers=HEADERS, verify=False)
    resp.raise_for_status()
    return BytesIO(resp.content)
```
#### Эта функция:
- формирует ссылку на отчёт по дате;
- находит на странице ссылку на .xls файл;
- скачивает отчёт и возвращает его в виде байтового потока BytesIO для последующего чтения pandas.

#### 2.3.4. Разбор и сохранение данных в базу
```python
def parse_and_save(df, date, db):
    """Разбор DataFrame и запись в базу + журнал."""
    inserted = 0
    for _, row in df.iterrows():
        rec = ElecReport(
            region=row['region'],
            timestamp=datetime.combine(date.date(), time(int(row['hour']), 0)),
            **{c: (float(row[c]) if pd.notnull(row[c]) else None) for c in COLS[2:]}
        )
        db.add(rec)
        inserted += 1
    db.commit()

    hist = LoadHistory(
        data_date=date.date(),
        load_time=datetime.now(),
        count=inserted
    )
    db.merge(hist)
    db.commit()
```
#### Эта функция:
- преобразует данные Excel в записи модели ElecReport;
- записывает их в таблицу отчётов;
- добавляет запись в таблицу LoadHistory, фиксируя, что данные за эту дату успешно загружены.

#### 2.3.5. Главный блок выполнения
```python
if __name__ == '__main__':
    db = Session()
    first = db.query(LoadHistory).order_by(LoadHistory.data_date).first()
    start = first.data_date if first else datetime.today().date() - timedelta(days=3*365)
    today = datetime.today().date()

    cur = datetime.combine(start, time(0))
    while cur.date() <= today:
        try:
            exists = db.query(LoadHistory).filter_by(data_date=cur.date()).first()
            if not exists or exists.count == 0:
                bio = download_xls(cur)
                df = pd.read_excel(bio, skiprows=5, header=0, names=COLS, engine='xlrd')
                parse_and_save(df, cur, db)
                print(f"{cur.date()}: LOADED")
            else:
                print(f"{cur.date()}: OK")
        except Exception as e:
            print(f"{cur.date()}: ERROR — {e}")
        cur += timedelta(days=1)

    db.close()
```
#### Этот блок:
- определяет диапазон дат для загрузки (по истории или за последние 3 года);
- для каждой даты проверяет, были ли данные уже загружены;
- если нет — скачивает отчёт, парсит и сохраняет;
- выводит результат загрузки в консоль.

### Итог
**Файл fetch_data.py автоматизирует процесс получения и обновления данных в базе.
Он обеспечивает:**
- полную автономность — данные подтягиваются без ручного участия;
- актуальность — система сама следит, какие отчёты уже загружены;
- гибкость — легко изменить период загрузки или источник.
#### Таким образом, fetch_data.py — это ядро системы сбора данных, без которого веб-сервис не смог бы получать и анализировать информацию об изменении цен на электроэнергию.

### 2.4 Назначение файла `models.py`

Файл `models.py` отвечает за **описание структуры базы данных** и взаимодействие с ней через ORM (Object-Relational Mapping) — библиотеку SQLAlchemy.  
Он позволяет работать с таблицами не напрямую через SQL-запросы, а через классы и объекты Python, что делает код более понятным, безопасным и удобным для поддержки.

---

#### 2.4.1. Подключение необходимых модулей

```python
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
```
- declarative_base() — функция, создающая базовый класс Base, от которого наследуются все модели (таблицы).

#### 2.4.2 Создание базового класса
```python
Base = declarative_base()
```

Этот объект является "основой" для всех моделей.
Он хранит метаданные о таблицах и используется при создании структуры базы (Base.metadata.create_all(engine) в fetch_data.py).

---

#### 2.4.3. Модель ElecReport — таблица отчётов об электроэнергии
```python
class ElecReport(Base):
    __tablename__ = 'elec_reports'
    id         = Column(Integer, primary_key=True)
    region     = Column(String, nullable=False)
    timestamp  = Column(DateTime, nullable=False)
    plan_GES       = Column(Float)
    plan_AES       = Column(Float)
    plan_TES       = Column(Float)
    plan_SES       = Column(Float)
    plan_VES       = Column(Float)
    plan_other     = Column(Float)
    techmin_GES    = Column(Float)
    techmin_AES    = Column(Float)
    techmin_TES    = Column(Float)
    techmin_SES    = Column(Float)
    techmin_VES    = Column(Float)
    techmin_other  = Column(Float)
    technomin_GES     = Column(Float)
    technomin_AES     = Column(Float)
    technomin_TES     = Column(Float)
    technomin_SES     = Column(Float)
    technomin_VES     = Column(Float)
    technomin_other   = Column(Float)
    techmax_GES    = Column(Float)
    techmax_AES    = Column(Float)
    techmax_TES    = Column(Float)
    techmax_SES    = Column(Float)
    techmax_VES    = Column(Float)
    techmax_other  = Column(Float)
    plan_consumption = Column(Float)
    plan_export      = Column(Float)
    plan_import      = Column(Float)
    price_buy        = Column(Float)
    price_sell       = Column(Float)
    full_plan        = Column(Float)
```
#### Описание таблицы:
- __tablename__ = 'elec_reports' — имя таблицы в базе данных.
- id — первичный ключ (уникальный идентификатор записи).
- region — регион, к которому относятся данные.
- timestamp — дата и час наблюдения.
- Остальные поля (plan_GES, plan_AES, techmin_*, price_buy, price_sell, и т.д.) содержат различные параметры и расчётные показатели:
- - plan_ — плановые значения генерации по видам станций (ГЭС, АЭС, ТЭС, СЭС, ВЭС и др.);
- - techmin/technomin/techmax_ — технические минимумы и максимумы;
- - price_buy / price_sell — закупочная и продажная цена электроэнергии;
- - plan_consumption, plan_export, plan_import — прогнозируемое потребление, экспорт и импорт энергии.

**Эта таблица — основное хранилище данных, загружаемых из отчётов.** 

---

#### 2.4.4. Модель LoadHistory — таблица истории загрузок
```python
class LoadHistory(Base):
    __tablename__ = 'load_history'
    data_date  = Column(Date, primary_key=True)       # дата отчёта
    load_time  = Column(DateTime, nullable=False)     # время загрузки
    count      = Column(Integer, nullable=False)      # число записей
```

#### Описание таблицы:
- data_date — дата отчёта, за которую были загружены данные;
- load_time — точное время, когда отчёт был добавлен в базу;
- count — количество записей, загруженных за этот день.
#### Эта таблица используется для ведения журнала загрузок в модуле fetch_data.py, чтобы избежать повторной загрузки одних и тех же файлов.


### Итог
**Файл models.py реализует модель данных приложения.
Он выполняет ключевую роль в архитектуре бэкенда:**
- описывает структуру всех таблиц базы данных;
- связывает Python-код с SQL через ORM SQLAlchemy;
- обеспечивает единый интерфейс для чтения и записи данных;
- позволяет удобно управлять и изменять структуру без ручного написания SQL-запросов.
  
#### Таким образом, models.py — это структурный каркас всей базы данных проекта.

