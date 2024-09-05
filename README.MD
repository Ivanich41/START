# Деплой через Docker

0. Подложить `.env` в корень репозитория

1. Запустить виртуальные машины docker и registry
```
vagrant up
```

2. Подключиться к вм docker 
```
vagrant ssh docker
```

3. Вручную собрать образы и запушить в registry
* -поскольку для сборки контейнеров бд не был использован Dockerfile, директории оставлены пустыми 

```
cd /vagrant/bot_image/
docker build -t 192.168.50.11:5000/bot_image . 

docker pull postgres:16-alpine
docker tag postgres:16-alpine 192.168.50.11:5000/db_image
docker tag postgres:16-alpine 192.168.50.11:5000/db_repl_image

docker push 192.168.50.11:5000/bot_image
docker push 192.168.50.11:5000/db_image
docker push 192.168.50.11:5000/db_repl_image
```

4. Запустить сервисы 
```
docker compose up -d 
```

5. Отправиться к боту в Telegram  @pt_devops_poc_bot
