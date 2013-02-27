Электронная регистратура
=================

Сервис электронной регистратуры обеспечивает Онлайн запись пациента на приём к врачу. 
Для установки сервиса ознакомьтесь с системными требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* Python 2.7 (http://www.python.org/download/)
* PIL (http://www.pythonware.com/products/pil/)
* MySQL 5 (http://dev.mysql.com/downloads/installer/)
* Python-connector to MySQL (http://dev.mysql.com/downloads/connector/python/#downloads)
* Web-Server Apache2.2 (http://www.sai.msu.su/apache/dist/httpd/binaries/win32/) + mod_wsgi (http://code.google.com/p/modwsgi/wiki/DownloadTheSoftware)
* git (http://git-scm.com/download/win)

Под windows используются только 32-bit версии

Установка
-----------
* Установить MySQL

При конфигурировании MySQL, рекомендуется установить в my.cnf:

```
lower_case_table_names=2
```
* Создать новую БД, например с именем: elreg.
* Создать пользователя БД, которому дать привелегии на работу с elreg.
* Установить Apache
* Скачать модуль mod_wsgi, скопиррвать в директорию модулей Apache2.2/modules, подключить модуль в конфиге Apache2.2/conf/httpd.conf:

```
LoadModule mod_wsgi modules/mod_wsgi.so
```

* Установить Python и прописать его в системный путь (например, через cmd):

```
set PATH=%PATH%;D:\Python27;D:\Python27\Scripts
```

* Установить setup_tools (https://pypi.python.org/pypi/setuptools/0.6c11#downloads)

* Установить pip

```
easy_install.exe pip
```

* Создать директорию проекта, например D:\projects\elreg и перейти в неё в консоли:

```
cd D:\projects\elreg
```

* Установить virtualenv, создать и активировать виртуальную среду

```
pip install virtualenv
virtualenv venv
venv\Scripts\activate
```

* Установить Python-connector к MySQL (http://dev.mysql.com/downloads/connector/python/#downloads), при установке указав путь виртуальному окружению, чтобы коннектор работал с питоном из окружения (D:\projects\elreg\venv)
* Установить PIL (http://www.pythonware.com/products/pil/)
* Клонировать репозиторий из git, для этого в директории проекта вызвать из контекстного меню Git Bash и выполнить команду:

```
git clone https://github.com/KorusConsulting/elreg.git code
git checkout new_intservice
```

* Установить зависимости через командную строку:

```
pip install -r code\requirements.txt
```

Настройка серверного окружения
-----------

* Конфигурирование виртуальных хостов Apache (Apache2.2/conf/extra/httpd-vhosts.conf), секция Virtual Hosts, добавить следующие конфигурации:
