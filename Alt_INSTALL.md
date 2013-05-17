Электронная регистратура
=================

Сервис электронной регистратуры обеспечивает Онлайн запись пациента на приём к врачу.
Для установки сервиса ознакомьтесь с системными требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* Серверная ОС семейства Linux
* Python 2.6 и выше
* MySQL 5, libmysqlclient-devel
* Web-Server Apache + mod_wsgi
* git
* zlib, zlib-devel

Установка
-----------

Описанная ниже установка и настройка ПО производится из консоли Linux. Используется root-доступ.

**Update системы**

```
apt-get update
apt-get upgrade
```

**Установка виртуального окружения и инструмента работы с пакетами Python**

```
apt-get -y install python python-dev python-module-setuptools
easy_install virtualenv pip
```

**Конфигурирование MySQL**

```
echo "CREATE DATABASE DATABASENAME DEFAULT CHARACTER SET utf8;" | mysql -u root -p
echo "CREATE USER 'DATABASEUSER'@'localhost' IDENTIFIED BY 'PASSWORD';" | mysql -u root -p
echo "GRANT ALL PRIVILEGES ON DATABASENAME.* TO 'DATABASEUSER'@'localhost';" | mysql -u root -p
echo "FLUSH PRIVILEGES;" | mysql -u root -p
```
Из под root-пользователя БД рекомендуется создать пользователя БД с ограниченными правами, который будет использован в проекте для работы с БД.
Подробнее про создание пользователей и раздачу прав можно почитать в оф. документации MySQL:

http://dev.mysql.com/doc/refman/5.1/en/create-user.html

http://dev.mysql.com/doc/refman/5.1/en/grant.html

Для работы с данными пользователю БД достаточно следующего набора привилегий:
SELECT, INSERT, UPDATE, DELETE, FILE, CREATE, ALTER, INDEX, DROP, CREATE TEMPORARY TABLES

**Подготовка директорий для размещения проекта**

Используем директорию /var/www/webapps/ для установки сайта.

В качестве имени проекта (my_project) можно использовать произвольное.
```
cd /var/www/webapps/
mkdir -p my_project/app my_project/app/conf/apache
mkdir -p my_project/logs my_project/run/eggs
```

**Создаём и активируем виртульное окружение для проекта**

```
virtualenv my_project/venv
source my_project/venv/bin/activate
```

**Создаём системного пользователя**

Пользователь, из-под которого будет работать mod_wsgi процесс.
В качестве USERNAME используется произвольное имя.
```
/usr/sbin/useradd --system --no-create-home --home-dir /var/www/webapps/my_project/ --user-group USERNAME
chsh -s /bin/bash USERNAME
```

**Клонирование github репозитория**

Перейти в корневую директорию проекта (в нашем примере: /var/www/webapps/my_project) и выполнить команду:
```
git clone https://github.com/KorusConsulting/elreg.git
```
Переключиться на ветку "AltLinux" и сделать pull изменений:
```
cd elreg
git checkout AltLinux
git pull
```
при этом необходимо наличие github аккаунта с правами доступа в корпоративный репозиторий


**Установка библиотек и приложений**

Устанавливаем ПО для разрешения зависимостей

* Для mysql-python:

```
apt-get install python-module-MySQLdb
```
* Для PIL (установка модулей и настройка путей к библиотекам):

```
apt-get install libjpeg libjpeg-devel libfreetype libfreetype-devel zlib zlib-devel
```

**Устанавливаем django и используемые модули**

```
apt-get install ftp://ftp.altlinux.org/pub/distributions/ALTLinux/Sisyphus/files/SRPMS/python-module-django-1.4-alt1.src.rpm
```
в случае возникновения проблем установки django из rpm, исполльзовать следующий способ:
```
pip install -r ElReg/requirements.txt
```
Дополнительные модули:
```
apt-get install ftp://ftp.altlinux.org/pub/distributions/ALTLinux/Sisyphus/files/x86_64/RPMS/redis-2.4.7-alt2.x86_64.rpm
apt-get install python-module-imaging
pip install redis --upgrade
service redis-server start
```

При получении сообщений об ошибках необходимо разрешить необходимые зависимости и повторно выполнить установку из requirements.txt. В конечном результате все пакеты должны установиться без уведомления об ошибках.


**Настройка Apache**

Создать конфиг сайта и отредактировать его любым текстовым редактором, в качестве DOMAIN использовать выбранное доменное имя сайта:
```
nano /etc/httpd2/conf/sites-available/DOMAIN
```

вставить следующее содержимое, подставив вместо USER и DOMAIN имя ранее созданного пользователя и выбранный домен:

```
<VirtualHost *>
ServerAdmin root@DOMAIN
ServerName DOMAIN

Alias /site_media/ /var/www/webapps/my_project/elreg/ElReg/elreg_app/media/
Alias /static_admin/ /var/www/webapps/my_project/venv/lib/python2.6/site-packages/django/contrib/admin/static/
Alias /static/ /var/www/webapps/my_project/elreg/ElReg/elreg_app/static/
Alias /robots.txt /var/www/webapps/my_project/app/webapp/site_media/robots.txt
Alias /favicon.ico /var/www/webapps/my_project/elreg/ElReg/elreg_app/static/images/favicon.ico

CustomLog "|/usr/sbin/rotatelogs2 /var/www/webapps/my_project/logs/access.log.%Y%m%d 5M" combined
ErrorLog "|/usr/sbin/rotatelogs2 /var/www/webapps/my_project/logs/error.log.%Y%m%d 5M"
LogLevel warn

WSGIDaemonProcess DOMAIN user=USER group=USER processes=1 threads=15 maximum-requests=10000 python-path=/var/www/webapps/my_project/venv/lib/python2.6/site-packages python-eggs=/var/www/webapps/my_project/run/eggs
WSGIProcessGroup DOMAIN
WSGIScriptAlias / /var/www/webapps/my_project/elreg/ElReg/wsgi.py

<Directory /var/www/webapps/my_project/elreg/ElReg/elreg_app/media>
Order deny,allow
Allow from all
Options -Indexes FollowSymLinks
</Directory>

<Directory /var/www/webapps/my_project/app/conf/apache>
Order deny,allow
Allow from all
</Directory>

</VirtualHost>
```

** Активировать конфигурацию:

DOMAIN - ранее выбранный домен
```
a2ensite DOMAIN
```

**Установить привилегии для директории проекта**

```
chown -R USERNAME:USERNAME /var/www/webapps/my_project/
```

**Перезапустить апач**

```
service httpd2 restart
```

**Настройка django**

Для первоначальной настройки django необходимо прописать параметры подключение к БД в файле /var/www/webapps/my_project/elreg/ElReg/settings_local.py
Затем выполнить команду для создания таблиц в БД:
```
python elreg/ElReg/manage.py syncdb
python elreg/ElReg/manage.py migrate
```
```
python elreg/ElReg/manage.py collectstatic
```

В процессе будет предложено ввести логин/пароль администратора.

**Настройка сайта**
* Зайти в административный интерфейс:
http://DOMEN/admin/
* Ввести логин/пароль администратора
* Перейти в интерфес настроек сайта:
http://DOMEN/admin/settings/
* Заполнить необходимую информацию о текущем сайте, почтовом сервере, часовом поясе

-----------
**Замечания**

Может понадобиться прописать пути к виртуальному окружению в wsgi скрипте (в случае, если при открытии сайта в логах обнаружатся ошибки о недостающих библиотеках)
Для этого необходимо внести следующие строки в файл wsgi.py (до импорта from django.core.wsgi import get_wsgi_application):

```
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'venv/lib/python2.6/site-packages/')))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'app', 'webapp')))
```

* Применение изменений, внесенных в файлы .py

Для того, чтобы избавиться от постоянно перезагрузки Apache после внесения изменений в файлы проекта, достаточно выполнить следующую команду:

```
touch /var/www/webapps/my_project/elreg/ElReg/wsgi.py
```

Дополнительную информацию по настройке сервера можно получить по адресу:

http://www.lennu.net/2012/05/14/django-deployement-installation-to-ubuntu-12-dot-04-server/
