Электронная регистратура
=================

Сервис электронной регистратуры обеспечивает Онлайн запись пациента на приём к врачу. 
Для установки сервиса ознакомьтесь с системными требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* Python 2.7 (http://www.python.org/download/)
* PIL (http://www.pythonware.com/products/pil/)
* MySQL 5 (http://dev.mysql.com/downloads/installer/)
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
set PYTHONPATH=%PYTHONPATH%;D:\Python27;D:\Python27\Scripts
set PATH=%PATH%;%PYTHONPATH%
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

* Установить MySQL-python 

```
 easy_install MySQL-python
```

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

* Конфигурирование виртуальных хостов Apache (Apache2.2/conf/extra/httpd-vhosts.conf), секция Virtual Hosts, добавить следующую конфигурацию:

```
<VirtualHost %SERVER_HOST%:%SERVER_PORT%>
  ServerName %SERVER_HOST%:%SERVER_PORT%
  DocumentRoot "%PROJECT_CODE_ROOT%"
  
  Alias /site_media/ %PROJECT_CODE_ROOT%/ElReg/elreg_app/media/
  Alias /static_admin/ %PROJECT_ROOT%/venv/lib/python2.7/site-packages/django/contrib/admin/static/
  Alias /static/ %PROJECT_CODE_ROOT%/ElReg/elreg_app/static/
#  Alias /robots.txt %PROJECT_ROOT%/app/webapp/site_media/robots.txt
  Alias /favicon.ico %PROJECT_CODE_ROOT%/ElReg/elreg_app/static/images/favicon.ico
  
  CustomLog logs/%PROJECT_NAME%-access.log combined
  ErrorLog logs/%PROJECT_NAME%-error.log
  LogLevel warn
  
  WSGIScriptAlias / %PROJECT_CODE_ROOT%/ElReg/wsgi.py
  
  <Directory %PROJECT_CODE_ROOT%/ElReg/elreg_app/media>
    Order deny,allow
    Allow from all
    Options -Indexes FollowSymLinks
  </Directory>

</VirtualHost>
```

где

```
%SERVER_HOST% - хост, по которому будет вестись обращение к ИС (как вариант - IP сервера)
%SERVER_PORT% - порт, по которому будет вестись обращение к ИС (например, 80)
%PROJECT_ROOT% - директория, где располагаются файлы проекта (в нашем примере, D:/projects/elreg)
%PROJECT_NAME% - название проекта (например, elreg)
%PROJECT_CODE_ROOT% - директория, где располагается код проекта (в нашем примере, D:/projects/elreg/code)
```

* Перезапустить Apache

* Настройка сайта

Для первоначальной настройки сайта необходимо прописать параметры подключение к БД в файле %PROJECT_CODE_ROOT%/ElReg/settings_local.py 
Затем выполнить команду для создания таблиц в БД:

```
python code\ElReg\manage.py syncdb
python code\ElReg\manage.py migrate
```

```
python code\ElReg\manage.py collectstatic
```

Добавить активацию виртуального окружения в начало файла code\ElReg\wsgi.py:

```
activate_this = '%PROJECT_ROOT%/venv/Scripts/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
```

* Зайти в административный интерфейс: http://%SERVER_HOST%:%SERVER_PORT%/admin/
* Ввести логин/пароль администратора
* Перейти в интерфес настроек сайта: http://%SERVER_HOST%:%SERVER_PORT%/admin/settings/
* Заполнить необходимую информацию о текущем сайте, почтовом сервере, часовом поясе
