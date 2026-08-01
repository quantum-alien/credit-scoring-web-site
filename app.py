import datetime
import sqlite3
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Система Кредитного Скоринга",
    description="Веб-сервис автоматического анализа кредитоспособности заемщиков"
)

DB_NAME = "scoring.db"

def init_db():
    """
    Инициализация базы данных SQLite при старте приложения.
    Создает таблицу applications, если она не существует.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            birth_year INTEGER NOT NULL,
            monthly_income REAL NOT NULL,
            loan_amount REAL NOT NULL,
            loan_term INTEGER NOT NULL,
            credit_history TEXT NOT NULL,
            employment TEXT NOT NULL,
            score INTEGER NOT NULL,
            status TEXT NOT NULL,
            verdict TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Запускаем создание БД при импорте/старте модуля
init_db()

def run_scoring(birth_year: int, monthly_income: float, loan_amount: float, loan_term: int, credit_history: str, employment: str):
    """
    Математическая модель скоринга (согласно главе 2 курсовой работы).
    Возвращает кортеж: (итоговый_балл, статус, текстовый_вердикт)
    """
    score = 300  # Базовый скоринговый балл (как в НБКИ/FICO)
    current_year = datetime.datetime.now().year
    age = current_year - birth_year
    
    # --- БЛОК 1: ВОЗРАСТ (СТОП-ФАКТОРЫ И НАЧИСЛЕНИЕ) ---
    if age < 18:
        return 0, "REJECTED", f"Отказ: Возраст заемщика ({age} лет) меньше 18 лет."
    if age > 70:
        return 0, "REJECTED", f"Отказ: Возраст заемщика ({age} лет) превышает лимит в 70 лет."
        
    if 18 <= age <= 23:
        score += 50
    elif 24 <= age <= 50:
        score += 150
    elif 51 <= age <= 70:
        score += 100

    # --- БЛОК 2: ДОЛГОВАЯ НАГРУЗКА (PTI) ---
    if monthly_income <= 0:
        return 0, "REJECTED", "Отказ: Указан нулевой или отрицательный ежемесячный доход."
        
    requested_payment = loan_amount / loan_term
    pti = requested_payment / monthly_income
    
    if pti > 0.6:
        return int(score), "REJECTED", f"Отказ: Критический уровень долговой нагрузки (PTI = {pti:.1%}). Лимит превышен (>60%)."
        
    if pti <= 0.2:
        score += 200
    elif pti <= 0.4:
        score += 120
    elif pti <= 0.6:
        score += 50

    # --- БЛОК 3: КРЕДИТНАЯ ИСТОРИЯ ---
    if credit_history == 'bad':
        score -= 150
    elif credit_history == 'none':
        score += 50
    elif credit_history == 'good':
        score += 150
    elif credit_history == 'excellent':
        score += 250

    # --- БЛОК 4: ЗАНЯТОСТЬ (СТОП-ФАКТОРЫ И НАЧИСЛЕНИЕ) ---
    if employment == 'unemployed':
        return int(score), "REJECTED", "Отказ: Отсутствие официального источника дохода (статус безработного)."
    elif employment == 'employed':
        score += 100
    elif employment == 'business':
        score += 70
    elif employment == 'retired':
        score += 40

    # --- ВЫНЕСЕНИЕ ФИНАЛЬНОГО ВЕРДИКТА ---
    if score < 500:
        return int(score), "REJECTED", f"Отказ по баллам: Набрано {score} баллов (минимум для одобрения — 500)."
    elif 500 <= score < 650:
        approved_sum = int(loan_amount * 0.8)
        return int(score), "APPROVED", f"Условное одобрение со средним уровнем риска. Снижен лимит до {approved_sum:,} руб. Ставка 19.5% годовых."
    else:
        return int(score), "APPROVED", f"Одобрено! Высокий уровень надежности заемщика. Ставка 12.9% годовых."

def save_to_db(birth_year, monthly_income, loan_amount, loan_term, credit_history, employment, score, status, verdict):
    """Запись результатов обработки анкеты в БД SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (birth_year, monthly_income, loan_amount, loan_term, credit_history, employment, score, status, verdict)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (birth_year, monthly_income, loan_amount, loan_term, credit_history, employment, score, status, verdict))
    conn.commit()
    conn.close()

def get_recent_applications():
    """Получение 5 последних записей из базы данных для вывода истории"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, loan_amount, score, status, verdict, created_at FROM applications ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows

# HTML, CSS (Bootstrap 5) и JavaScript интерфейс страницы
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель Кредитного Скоринга</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            background-color: #0f172a;
            color: #ffffff;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        .card {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
        }}
        h1, h2, h3, h4, h5, h6, .form-label {{
            color: #ffffff !important;
        }}
        .form-control, .form-select {{
            background-color: #0f172a;
            border: 1px solid #334155;
            color: #ffffff !important;
        }}
        .form-control:focus, .form-select:focus {{
            background-color: #0f172a;
            border-color: #10b981;
            color: #ffffff !important;
            box-shadow: 0 0 0 0.25rem rgba(16, 185, 129, 0.25);
        }}
        /* Стилизация опций выпадающего списка для предотвращения черного текста на некоторых устройствах */
        select option {{
            background-color: #0f172a;
            color: #ffffff;
        }}
        /* Переопределение серого/темного цвета Bootstrap-подписей на контрастный светло-серый */
        .form-text, .text-muted {{
            color: #cbd5e1 !important;
        }}
        .text-accent {{
            color: #10b981 !important;
        }}
        .badge-approved {{
            background-color: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }}
        .badge-rejected {{
            background-color: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid #ef4444;
        }}
        .list-group-item {{
            color: #ffffff !important;
        }}
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="text-center mb-5">
            <h1 class="fw-bold"><i class="fa-solid fa-shield-halved text-accent me-2"></i>Кредитный Скоринг <span class="text-accent">Экспресс</span></h1>
            <p class="text-muted">Прототип автоматизированного экспресс-андеррайтинга физических лиц (FastAPI + SQLite)</p>
        </div>

        <div class="row g-4">
            <div class="col-lg-7">
                <div class="card p-4 shadow-sm">
                    <h3 class="h5 mb-4 text-accent"><i class="fa-solid fa-file-invoice-dollar me-2"></i>Анкета заемщика</h3>
                    
                    <form action="/evaluate" method="post">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">Год рождения</label>
                                <input type="number" name="birth_year" class="form-control" value="1995" min="1930" max="2010" required>
                                <div class="form-text text-muted">Допустимый возраст: от 18 до 70 лет</div>
                            </div>
                            
                            <div class="col-md-6">
                                <label class="form-label">Ежемесячный доход (руб.)</label>
                                <input type="number" name="monthly_income" class="form-control" value="85000" min="0" required>
                                <div class="form-text text-muted">Официально подтвержденный оклад</div>
                            </div>

                            <div class="col-md-6">
                                <label class="form-label">Сумма кредита (руб.)</label>
                                <input type="number" name="loan_amount" class="form-control" value="400000" min="1000" required>
                            </div>

                            <div class="col-md-6">
                                <label class="form-label">Срок кредитования (мес.)</label>
                                <input type="number" name="loan_term" class="form-control" value="24" min="1" max="120" required>
                            </div>

                            <div class="col-md-6">
                                <label class="form-label">Кредитная история</label>
                                <select name="credit_history" class="form-select">
                                    <option value="excellent">Отличная (нет долгов, много закрытых)</option>
                                    <option value="good" selected>Хорошая (были закрыты вовремя)</option>
                                    <option value="none">Отсутствует (новый заемщик)</option>
                                    <option value="bad">Плохая (имеются текущие просрочки)</option>
                                </select>
                            </div>

                            <div class="col-md-6">
                                <label class="form-label">Тип занятости</label>
                                <select name="employment" class="form-select">
                                    <option value="employed" selected>Наемный рабочий (официально)</option>
                                    <option value="business">Предприниматель / Собственный бизнес</option>
                                    <option value="retired">Пенсионер</option>
                                    <option value="unemployed">Временно безработный</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-success w-100 mt-4 py-2 fw-semibold">
                            <i class="fa-solid fa-calculator me-2"></i>Отправить заявку на скоринг
                        </button>
                    </form>
                </div>

                {result_block}
            </div>

            <div class="col-lg-5">
                <div class="card p-4 shadow-sm mb-4">
                    <h3 class="h5 mb-3 text-accent"><i class="fa-solid fa-database me-2"></i>База данных СУБД SQLite</h3>
                    <p class="small text-muted mb-4">История последних 5 обработанных заявок, сохраненных в реальном времени в таблицу.</p>
                    
                    <div class="list-group list-group-flush">
                        {history_rows}
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <h4 class="h6 mb-3"><i class="fa-solid fa-circle-info text-accent me-2"></i>Шкала принятия решений банка:</h4>
                    <ul class="small text-muted ps-3">
                        <li class="mb-2"><strong class="text-light">650 – 1000 баллов</strong> — Высокий рейтинг. Одобрение под льготный процент (12.9%).</li>
                        <li class="mb-2"><strong class="text-light">500 – 649 баллов</strong> — Средний рейтинг. Одобрение с урезанием лимита на 20% и повышенным процентом (19.5%).</li>
                        <li class="mb-2"><strong class="text-light">Менее 500 баллов / Стоп-факторы</strong> — Отказ системы. Высокий риск невозврата средств.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    # Собираем актуальную историю записей из базы данных
    history = get_recent_applications()
    history_html = ""
    for row in history:
        badge_class = "badge-approved" if row[3] == "APPROVED" else "badge-rejected"
        badge_text = "ОДОБРЕНО" if row[3] == "APPROVED" else "ОТКАЗ"
        
        history_html += f"""
        <div class="list-group-item bg-transparent border-secondary py-3 px-0">
            <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                <h6 class="mb-0 text-white">ID заявки: {row[0]} <span class="ms-2 fw-normal text-muted" style="font-size: 0.8rem;">({row[5]})</span></h6>
                <span class="badge {badge_class}">{row[2]} баллов ({badge_text})</span>
            </div>
            <p class="mb-1 small text-light">Сумма кредита: <span class="text-accent">{row[1]:,} руб.</span></p>
            <small class="text-muted d-block">{row[4]}</small>
        </div>
        """
    if not history_html:
        history_html = "<p class='text-muted text-center py-3'>История пуста. Отправьте первую заявку через форму!</p>"
        
    return HTML_TEMPLATE.format(result_block="", history_rows=history_html)

@app.post("/evaluate", response_class=HTMLResponse)
async def evaluate(
    birth_year: int = Form(...),
    monthly_income: float = Form(...),
    loan_amount: float = Form(...),
    loan_term: int = Form(...),
    credit_history: str = Form(...),
    employment: str = Form(...)
):
    # Запускаем логику скоринга
    score, status, verdict = run_scoring(birth_year, monthly_income, loan_amount, loan_term, credit_history, employment)
    
    # Сохраняем результат в СУБД SQLite
    save_to_db(birth_year, monthly_income, loan_amount, loan_term, credit_history, employment, score, status, verdict)
    
    # Формируем красивую плашку с результатом расчета
    alert_class = "border-success bg-opacity-10 bg-success" if status == "APPROVED" else "border-danger bg-opacity-10 bg-danger"
    text_color = "text-success" if status == "APPROVED" else "text-danger"
    icon = "fa-circle-check" if status == "APPROVED" else "fa-circle-xmark"
    
    result_block = f"""
    <div class="card p-4 mt-4 border-2 {alert_class}">
        <div class="d-flex align-items-center mb-3">
            <i class="fa-solid {icon} {text_color} fs-3 me-3"></i>
            <h4 class="mb-0 fw-bold {text_color}">Статус решения: {status}</h4>
        </div>
        <p class="fs-5 mb-2 text-white">Итоговый скоринговый балл: <strong class="text-accent">{score}</strong> из 1000</p>
        <hr class="border-secondary my-2">
        <p class="mb-0 text-white"><strong>Вердикт системы:</strong> {verdict}</p>
    </div>
    """
    
    # Снова запрашиваем историю из базы данных с учетом новой записи
    history = get_recent_applications()
    history_html = ""
    for row in history:
        badge_class = "badge-approved" if row[3] == "APPROVED" else "badge-rejected"
        badge_text = "ОДОБРЕНО" if row[3] == "APPROVED" else "ОТКАЗ"
        
        history_html += f"""
        <div class="list-group-item bg-transparent border-secondary py-3 px-0">
            <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                <h6 class="mb-0 text-white">ID заявки: {row[0]} <span class="ms-2 fw-normal text-muted" style="font-size: 0.8rem;">({row[5]})</span></h6>
                <span class="badge {badge_class}">{row[2]} баллов ({badge_text})</span>
            </div>
            <p class="mb-1 small text-light">Сумма кредита: <span class="text-accent">{row[1]:,} руб.</span></p>
            <small class="text-muted d-block">{row[4]}</small>
        </div>
        """

    return HTML_TEMPLATE.format(result_block=result_block, history_rows=history_html)

if __name__ == "__main__":
    # Запуск сервера локально на порту 8000
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)