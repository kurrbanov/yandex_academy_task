# REST API сервис для магазина Candy Store.

Подлкючаемся к виртуальной машине:
```
ssh login@IPv4
```

Устанавливаем нужные пакеты:
```
sudo apt-get update
sudo apt-get install -y vim mosh tmux htop git curl wget unzip zip gcc build-essential make
sudo apt-get install -y zsh tree redis-server nginx zlib1g-dev libbz2-dev libreadline-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev python3-dev python-imaging python3-lxml libxslt-dev python-libxml2 python-libxslt1 libffi-dev libssl-dev python-dev gnumeric libsqlite3-dev libpq-dev libxml2-dev libxslt1-dev libjpeg-dev libfreetype6-dev libcurl4-openssl-dev supervisor
```

Устанавливаем Python 3.8.5:
```
wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz ; \
tar xvf Python-3.8.* ; \
cd Python-3.8.5 ; \
mkdir ~/.python ; \
./configure --enable-optimizations --prefix=/home/entrant/.python ; \
make -j8 ; \
sudo make altinstall
```

Обновляем pip
```
sudo /home/entrant/.python/bin/python3.8 -m pip install -U pip
```

Клонируем к себе GitHub-репозиторий
```
git clone https://github.com/kurrbanov/yandex_academy_task.git
```


Переходим в директорию yandex_academy_task и активируем venv
```
cd yandex_academy_task
source venv/bin/activate
```

Переходим в restapi_project и накатываем миграции
```
python3 ./manage.py makemigrations candy_store
python3 ./manage.py migrate
```

Устанавливаем Gunicorn
```
pip install gunicorn
```

Создаём конфигурационный файл и прописываем его
```
vim gunicorn_config.py
```

```python
command = '/home/entrant/yandex_academy_task/venv/bin/gunicorn'
pythonpath = '/home/entrant/yandex_academy_task/restapi_project'
bind = '127.0.0.1:8001'
workers = 9 
user = 'entrant'
limit_request_fields = 32000
limit_request_field_size = 0
# environment variables
raw_env = 'DJANGO_SETTINGS_MODULE=restapi_project.settings'
```

Создадим папку bin и внутри неё start_gunicorn.sh
```
#!/bin/bash
#activate virtual environment
source /home/entrant/yandex_academy_task/venv/bin/activate
#execute command launching gunicorn
exec gunicorn -c "/home/entrant/yandex_academy_task/gunicorn_config.py" restapi_project.wsgi
```

Настроим nginx
```
sudo vim /etc/nginx/sites-enabled/default
```
```
server {
	listen 0.0.0.0:8080;

	root /var/entrant/html;

	server_name _;

	location / {
		proxy_pass http://127.0.0.1:8001;
		proxy_set_header X-Forwarded-Host $server_name;
		proxy_set_header X-Real-IP $remote_addr;
		add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
		add_header Access-Control-Allow-Origin *;
	}
}
```

Запускаем сервер командой
```
./start_gunicorn.sh
```


Пример отправки запроса на сервер
```python
import requests as req
response = req.get('http://0.0.0.0:8080/couriers/1')
print(response.text)
```
