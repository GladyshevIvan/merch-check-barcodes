# Merch check barcodes

## Краткое описание (Brief description)

FastAPI-приложение, представляющее собой anti-fraud систему, для проверки выполнения работы мерчендайзеров.
Основывается на снимке чека, содержащей штрихкод с информацией.

A FastAPI application, an anti-fraud system for verifying merchandiser’s work, based on a receipt image containing QR code information.

## Описание проекта (Description)

Мерчандайзер (торговый представитель компании) должен регулярно посещать несколько закрепленных за ним магазинов и фотографировать \ загружать готовые снимки полок с брендовыми товарами компании через ее специализированное мобильное приложение.
За каждый факт посещения магазина сотрудник получает вознаграждение (сдельная форма отплаты труда).
В момент создания фотографии, помимо информации о сотруднике и магазине, на сервер отправляется текущая дата, время и GPS-координаты, чтобы верифицировать ее подлинность (в СУБД компании есть данные о связи "GPS - магазин - сотрудник").
Однако, эти параметры можно изменить средствами операционной системы мобильного телефона, а саму фотографию снять повторно с экрана монитора/ноутбука/планшета.
Чтобы нивелировать эту проблему, сотрудника просят так же обязательно фотографировать любой чек из коробки у кассового аппарата, но текст в нем также можно подменить, а ручной просмотр контроллером занимает слишком много времени.
Необходимо было разработать Python-класс для более совершенной версии anti-fraud системы (защиты от подлога), которая основывалась на снимке чека, содержащего QR-код со следующей информацией:

```
t=20230323T1625&s=92.00&fn=9999078902005429&i=266&fp=25819331&n=1
```

- t - дата и время продажи («yyyymmddThhmm»).
- s - сумма чека.
- fn - ФН (номер фискального накопителя, запоминающего устройства, установленного в онлайн-кассе; 16 цифр).
- i – ФД (номер чека как фискального документа, отражает порядковый номер чека с момента регистрации онлайн-кассы в ФНС; до 10 цифр).
- fp - ФП|ФПД (фискальный признак документа; «контрольная сумма» чека, служащая защитой от ошибок при передаче данных в налоговую инспекцию, и внутри самой кассы; до 10 цифр).
- n - вид документа (1 - «приход»; есть еще возвраты, расходы и коррекции).

По условию основной метод получает на вход параметры: 
- Растровый файл
- Дата и время фото (формат "ISO 8601" (с часовым поясом) - "20250423T201202Z") 
- GPS (tuple - (64.527603, 40.574157)) 
- ID сотрудника (GUID) 
- ID магазина (GUID)

Условия проверки:
- Проверка подразумевает, что время в чеке отклоняется от времени отправки отчета не более, чем на величину ```HOURS_LIMIT```, установленную в ```.env```;
- Геолокация отправки отчета не отклоняется от геолокации магазина не более, чем на величину ```DISTANCE_LIMIT```, установленную в ```.env```;
- Так же должны выявляться попытки загрузить изображение чека повторно или подделку, используя для выявления проверки на связки ```fn```/```fp``` и ```fp```/```i```/```t```.

Если все проверки пройдены - чек добавляется в Базу Данных.


A merchandiser (a company sales representative) is required to regularly visit several assigned stores and photograph/upload images of shelves stocked with the company’s branded products using the company’s dedicated mobile application. For each store visit, the employee receives compensation (piece-rate payment).
At the time the photo is taken, in addition to information about the employee and store, the current date, time, and GPS coordinates are sent to the server to verify its authenticity (the company’s DBMS contains data linking “GPS location - store - employee”).
However, these parameters can be modified through the mobile phone’s operating system, and the photo itself can be retaken from a computer/laptop/tablet screen.
To mitigate this problem, employees are also asked to photograph any receipt from the cash register, but the text on it can also be faked, and manual review by a controller takes too much time.
The task was to develop a Python class for a more advanced version of an anti-fraud system (protection against forgery), which is based on an image of a receipt containing a QR code with the following information:

```
t=20230323T1625&s=92.00&fn=9999078902005429&i=266&fp=25819331&n=1
```

- t - sale date and time (“yyyymmddThhmm”).
- s - receipt amount.
- fn - FN (fiscal accumulator number, a memory device installed in the online cash register; 16 digits).
- i - FD (fiscal document number, reflects the serial number of the receipt since the online cash register was registered with the Federal Tax Service; up to 10 digits).
- fp - FP|FPD (fiscal document sign; the “checksum” of the receipt, serving as protection against errors when transmitting data to the tax inspectorate, and within the cash register itself; up to 10 digits).
- n - document type (1 - “incoming”; there are also returns, expenses, and corrections).

According to the requirements, the main method receives the following parameters as input:
- Raster file (image)
- Photo date and time (ISO 8601 format (with time zone) - “20250423T201202Z”)
- GPS (tuple - (64.527603, 40.574157))
- Employee ID (GUID)
- Store ID (GUID)

Validation Rules:

- The check assumes that the time on the receipt deviates from the report submission time by no more than the ```HOURS_LIMIT``` set in ```.env```.
- The geolocation of the report submission does not deviate from the store’s geolocation by more than the ```DISTANCE_LIMIT``` set in ```.env```.
- The system must also detect attempts to upload the receipt image repeatedly or forgeries, using checks on the ```fn```/```fp``` and ```fp```/```i```/```t``` combinations.

If all checks pass, the receipt is added to the database.


## Реализованные требования (Implemented Requirements)

- Использован FastAPI для создания эндпоинта, на который приходит POST-запрос с информацией;
- Добавлен обработчик штрихкодов, извлекающий из них информацию;
- Использованы Pydantic модели для валидации данных;
- Реализована проверка на отклонение по времени;
- Реализована проверка на отклонение по GPS-координатам;
- Реализована проверка на дублирование чеков в Базе Данных;
- Для работы с Базой Данных использован паттерн 'Repository';
- В качестве СУБД выбран PostgreSQL;
- В качестве ORM использован SQLAlchemy;
- Использован Alembic для миграций схемы базы данных;
- Реализовано кеширование в Redis запросов к базе данных на получение GPS-координат магазинов;
- Добавлены модульные тесты (Pytest);
- Для модульного тестирования функций, где происходит обращение к Базе Данных, используются моки;
- Добавлено нагрузочное тестирование с помощью Locust;


<!--Space-->

- Implemented a FastAPI endpoint to receive POST requests with data.
- Added a barcode processor to extract information from barcodes.
- Utilized Pydantic models for data validation.
- Implemented time deviation check.
- Implemented GPS coordinate deviation check.
- Implemented duplicate receipt check in the database.
- Applied the Repository pattern for database interaction.
- PostgreSQL was selected as the database management system (DBMS).
- SQLAlchemy was used as the Object-Relational Mapper (ORM).
- Alembic was used for database schema migrations.
- Implemented Redis caching for store GPS coordinate queries to the database.
- Added unit tests (Pytest).
- Used mocks for unit testing of functions that interact with the database.
- Performed load testing with Locust.

## Подготовка проекта (Project preparation)

1. **Предварительная установка**
   * Установите PostgreSQL
   * Установите Redis

2. **Создайте Базу Данных в PostgreSQL**

3. **Создайте в корне проекта файл ```.env```**
   ```
   #Лимиты для проверки
   HOURS_LIMIT=2
   DISTANCE_LIMIT=2

   #Добавить пояс и использовать его при конвертации, например 'Europe/Moscow'
   TIME_ZONE=UTC
   
   #Настройки Базы Данных PostgreSQL
   DB_HOST="your_host"
   DB_PORT=5432
   DB_USER="postgres"
   DB_PASSWORD="password"
   DB_NAME="db_name"
   
   #Настройки Базы Данных Redis
   REDIS_HOST="your_host"
   REDIS_PORT=6379
   REDIS_DB="db_number"
   ```
   
   - Установите лимиты для времени и дистанции;
   - Добавьте временной пояс;
   - Добавьте настройки для PostgreSQL;
   - Добавьте настройки для Redis.

4. **Предварительная сборка**
   * Установите необходимые Python-пакеты, выполнив следующую команду в консоли

   ```
   pip install -r requirements.txt
   ```
   

<!--Space-->


1. **Prerequisites**
   * Install PostgreSQL
   * Install Redis

2. **Create a Database in PostgreSQL**

3. **Create a ```.env``` file in your project directory**
   ```
   #Limits for validation
   HOURS_LIMIT=2
   DISTANCE_LIMIT=2
   
   #Add time zone and use it during conversion, for example 'Europe/Moscow'
   TIME_ZONE=UTC
   
   #PostgreSQL Database Settings
   DB_HOST="your_host"
   DB_PORT=5432
   DB_USER="postgres"
   DB_PASSWORD="password"
   DB_NAME="db_name"
   
   #Redis Database Settings
   REDIS_HOST="your_host"
   REDIS_PORT=6379
   REDIS_DB="db_number"
   ```
   
   - Set the limits for time and distance.
   - Add the timezone.
   - Add the settings for PostgreSQL.
   - Add the settings for Redis.

4. **Initial Setup**
   * Install the necessary Python packages by running the following command in the console:
   ```
   pip install -r requirements.txt
   ```
   

## Использованные технологии (Technology Stack)

- **Python 3.13**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Redis**
- **Pytest**
- **Locust**