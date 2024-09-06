# Деплой через ansible

0. Подложить .env в корень репозитория 

1. Поднять виртуальные машины:

- bot 
- pg_primary
- pg_replica
- ansible 

```
vagrant up 
```

2. Подключиться на мишину ansible 
```
vagrant ssh anisble
```

3. Переместить данные в /home/vagrant
```
cp -R /vagrant /home/vagrant
```

4. Запустить плейбук из директории /home/vagrant
```
ansible-playbook playbook_tg_bot.yml
```

5. Отправиться к боту в Telegram @pt_devops_poc_bot