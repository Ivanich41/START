from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import paramiko
import logging
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os



#load_dotenv(find_dotenv())       
TOKEN = os.getenv('TOKEN')
SSH_HOST = os.getenv('RM_HOST')
SSH_USER = os.getenv('RM_USER')
SSH_PASSWORD = os.getenv('RM_PASSWORD')

DB_NAME = os.getenv('DB_DATABASE')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
# Класс соединения с базой данных, чтобы каждый раз вызывать его при взаимодействиях
class DatabaseConnection:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# Регулярные выражения для поиска email адресов и номеров телефонов
email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
phone_regex = re.compile(r'((8|\+7)[\-\s]?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2})')
password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')


logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



def create_ssh_client() -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=SSH_HOST, username=SSH_USER, password=SSH_PASSWORD)
    print(f'Соединение с сервером {SSH_HOST} установлено')
    return client


def start(update: Update, context: CallbackContext) -> None:
    logger.info('/start command called')
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def find_email(update: Update, context: CallbackContext) -> None:
    logger.info('/find_email command called')
    update.message.reply_text('Пожалуйста, введите текст для поиска email адресов.')

    context.user_data['waiting_for'] = 'email'


def find_phone_number(update: Update, context: CallbackContext) -> None:
    logger.info('/find_email command called')
    update.message.reply_text('Пожалуйста, введите текст для поиска номеров телефонов.')

    context.user_data['waiting_for'] = 'phone_number'


def verify_password(update: Update, context: CallbackContext) -> None:
    logger.info('/verify_password command called')
    update.message.reply_text('Пожалуйста, введите пароль для проверки его сложности.')

    context.user_data['waiting_for'] = 'password'


def process_email(update: Update, context: CallbackContext, user_text: str) -> None:
    emails = email_regex.findall(user_text)
    if emails:
        email_list = '\n'.join(f'{i+1}. {email}' for i, email in enumerate(emails))
        update.message.reply_text(f'Найденные email адреса:\n{email_list}')
        
        # Сохраняем найденные email в user_data
        context.user_data['emails'] = emails

        # Запрашиваем подтверждение на добавление в базу данных
        update.message.reply_text('Хотите добавить эти email адреса в базу данных? (да/нет)')
        context.user_data['waiting_for'] = 'confirmation_email'
    else:
        update.message.reply_text('Email адреса не найдены.')
        context.user_data['waiting_for'] = None


def process_phone_number(update: Update, context: CallbackContext, user_text: str) -> None:
    phones = phone_regex.findall(user_text)
    if phones:
        phone_list = '\n'.join(f'{i+1}. {phone[0]}' for i, phone in enumerate(phones))
        update.message.reply_text(f'Найденные номера телефонов:\n{phone_list}')
        
        # Сохраняем найденные телефоны в user_data
        context.user_data['phones'] = [phone[0] for phone in phones]

        # Запрашиваем подтверждение на добавление в базу данных
        update.message.reply_text('Хотите добавить эти номера телефонов в базу данных? (да/нет)')
        context.user_data['waiting_for'] = 'confirmation_phone'
    else:
        update.message.reply_text('Номера телефонов не найдены.')
        context.user_data['waiting_for'] = None


def process_password(update: Update, user_text: str) -> None:
    if password_regex.match(user_text):
        update.message.reply_text('Пароль сложный.')
    else:
        update.message.reply_text('Пароль простой.')


def get_uptime(update: Update, context: CallbackContext) -> None:
    logger.info('/get_uptime command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('uptime')
        uptime_output = stdout.read().decode().strip()
        update.message.reply_text(f'Uptime:  {uptime_output}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить uptime: {e}')


def get_release(update: Update, context: CallbackContext) -> None:
    logger.info('/get_release command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('lsb_release -a')
        release_output = stdout.read().decode().strip()
        update.message.reply_text(f'Информация о релизе системы:\n {release_output}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить release: {e}')


def get_uname(update: Update, context: CallbackContext) -> None:
    logger.info('/get_uname command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('uname -p')
        arch = stdout.read().decode().strip()
        stdin, stdout, stderr = ssh_client.exec_command('uname -n')
        hostname = stdout.read().decode().strip()
        stdin, stdout, stderr = ssh_client.exec_command('uname -r')
        kernel = stdout.read().decode().strip()
        update.message.reply_text(f'Архитектура CPU: {arch}, Имя хоста: {hostname}, Версия ядра: {kernel}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить uname: {e}')


def get_df(update: Update, context: CallbackContext) -> None:
    logger.info('/get_df command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('df -h')
        df_output = stdout.read().decode().strip()
        update.message.reply_text(f'{df_output}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о файловой системе: {e}')


def get_free(update: Update, context: CallbackContext) -> None:
    logger.info('/get_free command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('free -h')
        free_output = stdout.read().decode().strip()
        update.message.reply_text(f'{free_output}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о памяти: {e}')


def get_mpstat(update: Update, context: CallbackContext) -> None:
    logger.info('/get_mpstat command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('mpstat')
        get_mpstat = stdout.read().decode().strip()
        update.message.reply_text(f'{get_mpstat}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о производительности: {e}')


def get_w(update: Update, context: CallbackContext) -> None:
    logger.info('/get_w command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('w')
        get_w = stdout.read().decode().strip()
        update.message.reply_text(f'{get_w}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о пользователях: {e}')


def get_auths(update: Update, context: CallbackContext) -> None:
    logger.info('/get_auths command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''cat /var/log/auth.log | grep 'Accepted' | tail -n 10''')
        get_auths = stdout.read().decode().strip()
        update.message.reply_text(f'{get_auths}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о входах: {e}')


def get_critical(update: Update, context: CallbackContext) -> None:
    logger.info('/get_critical command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''journalctl --priority=crit | tail -n 5''')
        get_critical = stdout.read().decode().strip()
        update.message.reply_text(f'{get_critical}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о критических ошибках: {e}')


def get_ps(update: Update, context: CallbackContext) -> None:
    logger.info('/get_ps command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''ps au''')
        get_ps = stdout.read().decode().strip()
        update.message.reply_text(f'Процессы для текущего пользователя:\n{get_ps}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о процессах: {e}')


def get_ss(update: Update, context: CallbackContext) -> None:
    logger.info('/get_ss command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''ss -tulnp | awk '{print $1,"  "$2,"  "$5,"  "$7}' ''')
        get_ss = stdout.read().decode().strip()
        update.message.reply_text(f'Открытые порты в формате:\nПротокол ; Статус ; Адрес ; Команда запуска\n{get_ss}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о портах: {e}')

def get_services(update: Update, context: CallbackContext) -> None:
    logger.info('/get_services command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''systemctl | grep ".service" | grep "running" | awk {'print $1'}''')
        get_services = stdout.read().decode().strip()
        update.message.reply_text(f'{get_services}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о сервисах: {e}')        


def get_repl_logs(update: Update, context: CallbackContext) -> None:
    logger.info('/get_repl_logs command called')
    try:
        ssh_client = context.bot_data['ssh_client']
        stdin, stdout, stderr = ssh_client.exec_command('''sudo cat /var/log/postgresql/postgresql-15-main.log | grep checkpoint | tail -n 20''')
        get_repl_logs = stdout.read().decode().strip()
        update.message.reply_text(f'{get_repl_logs}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить информаицию о логах репликации: {e}') 


def get_emails(update: Update, context: CallbackContext) -> None:
    logger.info('/get_emails command called')
    try:
        # ssh_client = context.bot_data['ssh_client']
        # stdin, stdout, stderr = ssh_client.exec_command(''' sudo -u postgres psql -c "SELECT * FROM emails;" -d homework 2>/dev/null | grep -v 'could not change directory' ''')
        # get_emails = stdout.read().decode().strip()
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM emails;")
            result = cur.fetchall()
            cur.close()
        
        formatted_result = "\n".join([f"{item[0]}. {item[1]}" for item in result])
        update.message.reply_text(f'{formatted_result}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить имейлы из таблицы: {e}') 


def get_phones(update: Update, context: CallbackContext) -> None:
    logger.info('/get_phones command called')
    try:
        # ssh_client = context.bot_data['ssh_client']
        # stdin, stdout, stderr = ssh_client.exec_command(''' sudo -u postgres psql -c "SELECT * FROM phones;" -d homework 2>/dev/null | grep -v 'could not change directory' ''')
        # get_phones = stdout.read().decode().strip()
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM phones;")
            result = cur.fetchall()
            cur.close()
        
        formatted_result = "\n".join([f"{item[0]}. {item[1]}" for item in result])
        update.message.reply_text(f'{formatted_result}')
    except Exception as e:
        update.message.reply_text(f'Не удалось получить телефоны из таблицы: {e}')         


def get_apt_list(update: Update, context: CallbackContext) -> None:
    logger.info('/get_apt_list command called')
    update.message.reply_text('Введите имя пакета для получения информации или введите 0, чтобы получить список всех пактов.')
    context.user_data['waiting_for'] = 'apt_list'


def process_apt_list(update: Update, user_text: str, ssh_client: paramiko.SSHClient) -> None:
    try:
        if user_text != '0':
            command = f'apt show {user_text}'
        else:
            command = 'apt list --installed | cut -d/ -f1'

        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode().strip()

        if output:
            update.message.reply_text(output[:4000])  # Ограничение на длину сообщения Telegram
        else:
            update.message.reply_text('Информация не найдена.')

    except Exception as e:
        logger.error('Ошибка при выполнении команды apt: %s', e)
        update.message.reply_text(f'Ошибка при выполнении команды: {e}')


def handle_confirmation_email(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.lower()
    
    if user_text == 'да':
        emails = context.user_data.get('emails', [])
        if emails:
            with DatabaseConnection() as conn:
                with conn.cursor() as cur:
                    for email in emails:
                        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
                conn.commit()
            update.message.reply_text('Email адреса добавлены в базу данных.')
        else:
            update.message.reply_text('Нет email адресов для добавления.')
    elif user_text == 'нет':
        update.message.reply_text('Добавление email адресов отменено.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')

    context.user_data['waiting_for'] = None


def handle_confirmation_phone(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.lower()
    
    if user_text == 'да':
        phones = context.user_data.get('phones', [])
        if phones:
            with DatabaseConnection() as conn:
                with conn.cursor() as cur:
                    for phone in phones:
                        cur.execute("INSERT INTO phones (phone) VALUES (%s)", (phone,))
                conn.commit()
            update.message.reply_text('Номера телефонов добавлены в базу данных.')
        else:
            update.message.reply_text('Нет номеров телефонов для добавления.')
    elif user_text == 'нет':
        update.message.reply_text('Добавление номеров телефонов отменено.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')

    context.user_data['waiting_for'] = None


def handle_message(update: Update, context: CallbackContext) -> None:
    if 'waiting_for' not in context.user_data:
        update.message.reply_text('Жду команду')
        return

    user_text = update.message.text

    # тут содержатся обработчики ввода для разных случаев
    if context.user_data['waiting_for'] == 'email':
        process_email(update, context, user_text)
    elif context.user_data['waiting_for'] == 'confirmation_email':
        handle_confirmation_email(update, context)
    elif context.user_data['waiting_for'] == 'phone_number':
        process_phone_number(update, context, user_text)
    elif context.user_data['waiting_for'] == 'confirmation_phone':
        handle_confirmation_phone(update, context)
    elif context.user_data['waiting_for'] == 'password':
        process_password(update, user_text)
    elif context.user_data['waiting_for'] == 'apt_list':
        process_apt_list(update, user_text, context.bot_data['ssh_client'])
    else:
        context.user_data['waiting_for'] = None


def confirmation_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('waiting_for') == 'confirmation_email':
        handle_confirmation_email(update, context)
    elif context.user_data.get('waiting_for') == 'confirmation_phone':
        handle_confirmation_phone(update, context)
    else:
        handle_message(update, context)


def main() -> None:
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    ssh_client = create_ssh_client()
    dispatcher.bot_data['ssh_client'] = ssh_client

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("find_email", find_email))
    dispatcher.add_handler(CommandHandler("find_phone_number", find_phone_number))
    dispatcher.add_handler(CommandHandler("verify_password", verify_password))
    dispatcher.add_handler(CommandHandler("get_uptime", get_uptime))
    dispatcher.add_handler(CommandHandler("get_release", get_release))
    dispatcher.add_handler(CommandHandler("get_uname", get_uname))
    dispatcher.add_handler(CommandHandler("get_df", get_df))
    dispatcher.add_handler(CommandHandler("get_free", get_free))
    dispatcher.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dispatcher.add_handler(CommandHandler("get_w", get_w))
    dispatcher.add_handler(CommandHandler("get_auths", get_auths))
    dispatcher.add_handler(CommandHandler("get_critical", get_critical))
    dispatcher.add_handler(CommandHandler("get_ps", get_ps))
    dispatcher.add_handler(CommandHandler("get_ss", get_ss))
    dispatcher.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dispatcher.add_handler(CommandHandler("get_services", get_services))
    dispatcher.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dispatcher.add_handler(CommandHandler("get_emails", get_emails))
    dispatcher.add_handler(CommandHandler("get_phones", get_phones))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()