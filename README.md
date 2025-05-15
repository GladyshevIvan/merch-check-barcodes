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
- Использован Docker для контейнеризации;
- Применен Docker-compose - инструмент для запуска многоконтейнерных приложений. 


<!--Space-->

- Implemented a FastAPI endpoint to receive POST requests with data;
- Added a barcode processor to extract information from barcodes;
- Utilized Pydantic models for data validation;
- Implemented time deviation check;
- Implemented GPS coordinate deviation check;
- Implemented duplicate receipt check in the database;
- Applied the Repository pattern for database interaction;
- PostgreSQL was selected as the database management system (DBMS);
- SQLAlchemy was used as the Object-Relational Mapper (ORM);
- Alembic was used for database schema migrations;
- Implemented Redis caching for store GPS coordinate queries to the database;
- Added unit tests (Pytest);
- Used mocks for unit testing of functions that interact with the database;
- Performed load testing with Locust;
- Used Docker for containerization;
- Implemented Docker Compose for multi-container application orchestration.

## Подготовка проекта (Project preparation)

1. **Установите [Docker](https://www.docker.com/)**


2. **Предварительная сборка**

   * Клонируйте репозиторий:

    ```bash
    git clone https://gitflic.ru/project/vanoglady/merch-check-barcodes.git
    cd <имя_папки_проекта>
    ```

   * Запустите сборку образа с помощью Docker Compose:

    ```bash
    docker-compose build
    ```

3. **Развертывание проекта**
   * Если развертывание происходит на другой машине, проверьте, установлен ли на ней [Docker](https://www.docker.com/) и имеется ли доступ к созданным контейнерам
   * В новой папке создайте новый `docker-compose.yml`, который будет использоваться для развертывания приложения
   * Пропишите в нем переменные окружения для конфигурации приложения, PostgreSQL и Redis:
     #### FastAPI приложение: 
     * `DB_HOST`: Хост базы данных PostgreSQL
     * `DB_PORT`: Порт базы данных PostgreSQL
     * `DB_USER`: Имя пользователя PostgreSQL
     * `DB_PASSWORD`: Пароль пользователя PostgreSQL
     * `DB_NAME`: Имя базы данных PostgreSQL
     * `REDIS_HOST`: Хост Redis
     * `REDIS_PORT`: Порт Redis
     * `REDIS_DB`: Номер базы данных Redis
     * `HOURS_LIMIT`: Максимальное количество часов
     * `DISTANCE_LIMIT`: Максимальное расстояние
     * `TIME_ZONE`:  Часовой пояс приложения
     #### PostgreSQL:
     * `POSTGRES_USER`: Имя пользователя PostgreSQL
     * `POSTGRES_PASSWORD`: Пароль пользователя PostgreSQL
     * `POSTGRES_DB`: Имя базы данных PostgreSQL

   * Полученные контейнеры разверните с помощью:
      
      ```bash
      docker-compose up -d
     ```

4. **Примените миграции Alembic**

   ```bash
   docker exec -it fastapi_app alembic upgrade head
   ```
   * Эта команда выполнит миграции Базы Данных, определенные в проекте, для создания необходимых таблиц и схем в PostgreSQL   


5. **При желании добавьте записи в Базу Данных**
   * Подключитесь к базе данных PostgreSQL внутри контейнера `fastapi_app`:

        ```bash
        docker exec -it fastapi_app psql -h postgres -U postgres -d appdb
        ```
     
   * Выполните SQL-запросы для добавления данных. Например, информации о магазине:

        ```sql
        INSERT INTO shops (id, shop_code, latitude, longitude) VALUES ('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3', '9999078900004658', 64.527603, 40.574157);
        ```

   * Для проверки содержимого таблицы `shops` используйте:

        ```sql
        SELECT * FROM shops;
        ```
     
6. **При желании проверьте кэшируются ли результаты запросов к Базе Данных в Redis**
   * После отправки успешного запроса (например, через Postman) выполните:

        ```bash
        docker exec -it redis redis-cli -h redis -p 6379
        ```

   * В `redis-cli` выполните:
        ```
        KEYS *
        ```

   * Если кэширование работает, должен высветиться ключ, связанный с запросом.
     

7. **Отправка запросов**
   * Для отправки запросов, можно воспользоваться [Postman](https://www.postman.com/downloads/)
   * Создайте новый запрос `POST`.
   * Введите URL: `http://localhost:8000/send_report` (или URL вашего POST эндпоинта)
   * В разделе `Body`, выберите `form-data`
   * Введите парметры:
     - barcode_img - Изображение штрихкода
     - date_and_time - Дата и время отчета в формате ISO 8601
     - latitude - Широта местоположения, откуда был отправлен отчет
     - longitude - Долгота местоположения, откуда был отправлен отчет
     - employee_id - UUID мерчендайзера, отправляющего отчет
     - shop_id - UUID магазина, в котором выполнил работу мерчендайзер
   * Нажмите `Send`
   * Если запрос выполнится успешно: высветится "Принято", иначе "Не принято"


8. **Остановка приложения**

   ```bash
   docker-compose down
   ```


<!--Space-->


1. **Install [Docker](https://www.docker.com/)**


2. **Pre-build Setup**

   * Clone the repository:

    ```bash
    git clone https://gitflic.ru/project/vanoglady/merch-check-barcodes.git
    cd <project_folder_name>
    ```

   * Build the image using Docker Compose:

    ```bash
    docker-compose build
    ```

3. **Project Deployment**
   * f deploying on a different machine, ensure [Docker](https://www.docker.com/) is installed and the created containers are accessible.
   * In a new folder, create a `docker-compose.yml` file for deploying the application.
   * Configure the environment variables for the application, PostgreSQL, and Redis:
     #### FastAPI application: 
     * `DB_HOST`: PostgreSQL database host
     * `DB_PORT`: PostgreSQL database port
     * `DB_USER`: PostgreSQL username
     * `DB_PASSWORD`: PostgreSQL password
     * `DB_NAME`: PostgreSQL database name
     * `REDIS_HOST`: Redis host
     * `REDIS_PORT`: Redis port
     * `REDIS_DB`: Redis database number
     * `HOURS_LIMIT`: Maximum allowed hours
     * `DISTANCE_LIMIT`: Maximum allowed distance
     * `TIME_ZONE`: Application timezone
     #### PostgreSQL:
     * `POSTGRES_USER`: PostgreSQL username
     * `POSTGRES_PASSWORD`: PostgreSQL password
     * `POSTGRES_DB`: PostgreSQL database name

   * Deploy the containers using:
      
      ```bash
      docker-compose up -d
     ```

4. **Apply Alembic Migrations**

   ```bash
   docker exec -it fastapi_app alembic upgrade head
   ```
   * This command will execute the database migrations defined in the project to create the necessary tables and schemas in PostgreSQL   


5. **Optionally Add Data to the Database**
   * Connect to the PostgreSQL database inside the `fastapi_app` container:

        ```bash
        docker exec -it fastapi_app psql -h postgres -U postgres -d appdb
        ```
     
   * Execute SQL queries to insert data. For example, to add store information:

        ```sql
        INSERT INTO shops VALUES ('F10F6CAF-5A98-426C-80D5-281A5D6FF0B3', '9999078900004658', 64.527603, 40.574157);
        ```

   * To check the contents of the `shops` table, use:

        ```sql
        SELECT * FROM shops;
        ```
     
6. **Optionally Check if Database Query Results Are Cached in Redis**
   * After making a successful request (e.g., via Postman), run:

        ```bash
        docker exec -it redis redis-cli -h redis -p 6379
        ```

   * В `redis-cli` выполните:
        ```
        KEYS *
        ```

   * If caching is working, a key related to the request should appear.
     

7. **Sending Requests**
   * To send requests, you can use [Postman](https://www.postman.com/downloads/).
   * Create a new `POST` request.
   * Enter the URL: http://localhost:8000/send_report (or your POST endpoint URL).
   * In the `Body` section, select `form-data`.
   * Enter the parameters:
     - barcode_img – Barcode image
     - date_and_time – Report date and time in ISO 8601 format
     - latitude – Latitude of the location from which the report was sent
     - longitude – Longitude of the location from which the report was sent
     - employee_id – UUID of the merchandiser submitting the report
     - shop_id – UUID of the store where the merchandiser performed the work
   * Click `Send`.
   * If the request is successful, the response will be "Accepted"; otherwise, it will be "Rejected".


8. **Stopping the Application**

   ```bash
   docker-compose down
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
- **Docker**
- **Docker-compose**