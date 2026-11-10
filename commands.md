1. Проверка Docker

docker version
docker info

Проверка работы Docker и текущей конфигурации.


2. Проверка портов

Get-NetTCPConnection -State Listen -LocalPort 8080,5432 -ErrorAction SilentlyContinue

Порты 8080 и 5432 перед началом работы были свободны.


3. Сборка образа приложения

docker build -t lab5-app:lab5-timkov .

docker images lab5-app

Создан образ:

lab5-app:lab5-timkov


4. Создание Docker-сетей

docker network create --driver bridge --subnet "172.28.14.0/24" --gateway "172.28.14.1" "public-net-lab5-timkov"

docker network create --driver bridge --internal --subnet "172.29.14.0/24" --gateway "172.29.14.1" "private-net-lab5-timkov"

Проверка:

docker network inspect public-net-lab5-timkov private-net-lab5-timkov --format '{{.Name}} | Internal={{.Internal}} | {{json .IPAM.Config}}'

Результат:

public-net-lab5-timkov
Internal=false
Subnet=172.28.14.0/24
Gateway=172.28.14.1

private-net-lab5-timkov
Internal=true
Subnet=172.29.14.0/24
Gateway=172.29.14.1


5. Создание тома MySQL

docker volume create lab5-timkov-mysql-data


6. Запуск MySQL

docker run -d --name lab5-timkov-mysql --network private-net-lab5-timkov --network-alias mysql_db --env-file mysql.env -v "lab5-timkov-mysql-data:/var/lib/mysql" mysql:8.4

Проверка запуска:

docker logs --tail 60 lab5-timkov-mysql

MySQL подключён только к private-net. Порт 3306 на хосте не публикуется.


7. Загрузка данных в MySQL

docker cp .\sql\mysql.sql lab5-timkov-mysql:/tmp/mysql.sql

docker exec lab5-timkov-mysql sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -ulab5 --default-character-set=utf8mb4 lab5 < /tmp/mysql.sql'

Проверка данных:

"SELECT * FROM student_record;" | docker exec -i lab5-timkov-mysql sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -ulab5 --default-character-set=utf8mb4 lab5'

Получена запись:

Тимков Дмитро Віталійович
6.1214-пі-2


8. Запуск приложения с MySQL

docker create --name lab5-timkov-app-private --hostname lab5-timkov-app-private --network public-net-lab5-timkov --env-file app-private.env -p 127.0.0.1:8080:8080 lab5-app:lab5-timkov

docker network connect private-net-lab5-timkov lab5-timkov-app-private

docker start lab5-timkov-app-private

Приложение доступно:

http://localhost:8080


9. Проверка сетей приложения

docker inspect lab5-timkov-app-private --format '{{json .NetworkSettings.Networks}}'

Приложение подключено к:

public-net-lab5-timkov
private-net-lab5-timkov

Полученные IP:

172.28.14.2
172.29.14.3


10. Проверка MySQL

docker inspect lab5-timkov-mysql --format '{{json .NetworkSettings.Networks}}'

MySQL находится только в private-net.

Проверка публикации портов:

docker inspect lab5-timkov-mysql --format '{{json .HostConfig.PortBindings}}'

Результат:

{}

Проверка Docker DNS:

docker exec lab5-timkov-app-private getent hosts mysql_db

Результат:

172.29.14.2 mysql_db


11. Проверка отключения private-net

docker network disconnect private-net-lab5-timkov lab5-timkov-app-private

После отключения private-net веб-страница продолжила работать, но соединение с MySQL стало недоступно.

Возвращение сети:

docker network connect private-net-lab5-timkov lab5-timkov-app-private

После подключения доступ к данным MySQL восстановился.


12. Остановка первой архитектуры

docker stop lab5-timkov-app-private lab5-timkov-mysql


13. Создание тома PostgreSQL

docker volume create lab5-timkov-postgres-data


14. Запуск PostgreSQL

docker run -d --name lab5-timkov-postgres --network host --env-file postgres.env -v "lab5-timkov-postgres-data:/var/lib/postgresql/data" postgres:17-alpine

PostgreSQL запущен с --network host без использования -p.


15. Проверка PostgreSQL

docker logs --tail 60 lab5-timkov-postgres

docker exec lab5-timkov-postgres pg_isready -h 127.0.0.1 -p 5432 -U lab5 -d lab5

Результат:

127.0.0.1:5432 - accepting connections


16. Загрузка данных в PostgreSQL

docker cp .\sql\postgres.sql lab5-timkov-postgres:/tmp/postgres.sql

docker exec lab5-timkov-postgres psql -U lab5 -d lab5 -v ON_ERROR_STOP=1 -f /tmp/postgres.sql

Проверка:

"SELECT * FROM student_record;" | docker exec -i lab5-timkov-postgres psql -U lab5 -d lab5

Получена запись:

Тимков Дмитро Віталійович
6.1214-пі-2


17. Запуск приложения с PostgreSQL

docker create --name lab5-timkov-app-host --hostname lab5-timkov-app-host --network public-net-lab5-timkov --env-file app-host.env --add-host pg_db:host-gateway -p 127.0.0.1:8080:8080 lab5-app:lab5-timkov

docker start lab5-timkov-app-host


18. Проверка второй архитектуры

docker inspect lab5-timkov-app-host --format '{{json .NetworkSettings.Networks}}'

Приложение находится только в public-net.

Проверка PostgreSQL:

docker inspect lab5-timkov-postgres --format '{{.HostConfig.NetworkMode}}'

Результат:

host

Проверка публикации портов:

docker inspect lab5-timkov-postgres --format '{{json .HostConfig.PortBindings}}'

Результат:

{}

Проверка pg_db:

docker exec lab5-timkov-app-host cat /etc/hosts

Имя pg_db добавлено через host-gateway.


19. Проверка отключения PostgreSQL

docker stop lab5-timkov-postgres

После остановки PostgreSQL приложение осталось доступным, но появилась ошибка подключения к БД.

Запуск PostgreSQL:

docker start lab5-timkov-postgres

Проверка:

docker exec lab5-timkov-postgres pg_isready -h 127.0.0.1 -p 5432 -U lab5 -d lab5

После запуска доступ к данным восстановился.


20. Проверка порта 5432

Get-NetTCPConnection -State Listen -LocalPort 5432 -ErrorAction SilentlyContinue

Порт 5432 находится в состоянии Listen.