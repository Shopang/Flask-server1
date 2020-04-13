from flask import Flask, request
import os, random, sqlite3


app = Flask(__name__)

def read_file(path):
    f = open(path, 'r', encoding='UTF8')
    s = f.read()
    f.close()
    return s


def manage_file(path, mode, text):
    f = open(path, mode, encoding='UTF8')
    f.write(text)
    f.close()


# value는 문자열, added는 논리값 또는 숫자
def add_value(value, added):
    value = int(value) if value else 0
    return str(value + added)


def update_game_result(game_table_name, group_index, game_index, score1, score2):
    try:
        f = None
        f = open(g_save_path + game_table_name, 'a', encoding='utf-8')

        game_result = '{},{},{},{}\n'.format(group_index, game_index, score1, score2)
        f.write(game_result)
    except OSError:
        pass
    finally:
        if f:
            f.close()

    return (f != None)


# ----------------------------------------------- #


@app.route('/')
def basic():
    return '성공'


@app.route('/create_1_0', methods=['GET', 'POST'])
def create_game_table():
    global g_title_index
    text = request.form['text']

    file_list = os.listdir(g_save_path)

    while True:
        g_title_index = (g_title_index + 1) % len(g_titles)
        title = g_titles[g_title_index]

        filename = title + str(random.randrange(1000, 9999))

        if not filename in file_list:
            manage_file(g_save_path + filename, 'w', text)
            return filename

    return 'no_remain_names'


# 대진표 초기화(경기 결과 삭제 + 대진표 수정)
@app.route('/reset_1_0', methods=['GET', 'POST'])
def reset_game_table():
    text = request.form['text']
    game_table = request.form['game_table']

    manage_file(g_save_path + game_table, 'w', text)
    return 'true'


# 대진표 초기화(경기 결과 삭제)
@app.route('/disabled_1_0', methods=['GET', 'POST'])
def locked_game_table():
    game_table = request.form['game_table']

    if not game_table in g_locked_game_tables:
        g_locked_game_tables.append(game_table)
    return 'true'


@app.route('/enter_1_0', methods=['GET', 'POST'])
def enter_to_game_table():
    filename = request.form['game_table']

    if not filename in os.listdir(g_save_path):
        return 'false'

    return read_file(g_save_path + filename)


@app.route('/add_game_result_1_0', methods=['GET', 'POST'])
def add_game_result():
    game_table_name = request.form['game_table']
    groupIndex = request.form['group_index']
    gameIndex = request.form['game_index']
    score1 = request.form['score1']
    score2 = request.form['score2']
    is_game_maker = request.form['is_game_maker']

    # 비활성 모드에서 모임장이 아니면, 종료
    if game_table_name in g_locked_game_tables and is_game_maker == 'no':
        return 'true'

    if update_game_result(game_table_name, groupIndex, gameIndex, score1, score2):
        return 'true'

    return 'false'


@app.route('/register_1_0', methods=['GET', 'POST'])
def register():
    id = request.form['id']
    pw = request.form['pw']
    addr = request.form['addr']

    f = open(g_info_path, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()

    for line in lines:
        tid, tpw = line.split('_')[0], line.split('_')[1].split('\n')[0]
        if tid == id:
            if tpw == pw:
                return 'register_fail'

    f = open(g_info_path, 'a', encoding='UTF8')
    f.write('{}_{}_{}\n'.format(id, pw, addr))
    f.close()

    return 'register_success'


@app.route('/login_event_1_0', methods=['GET', 'POST'])
def login():
    id = request.form['id']
    pw = request.form['pw']

    f = open(g_info_path, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()

    for line in lines:
        tid, tpw = line.split('_')[0], line.split('_')[1].split('\n')[0]
        if tid == id:
            if tpw == pw:
                return line.split('_')[-1].split('\n')[0]

    return 'login_fail'


@app.route('/latest_version_1_0', methods=['GET', 'POST'])
def latest_version():
    return '1.0'


@app.route('/store_link_1_0', methods=['GET', 'POST'])
def store_link():
    device = request.form['device']     # iphone/android
    return 'com.flutter.gender.separation' if device == 'android' else 'com.flutter.gender.separation'


# @app.route('/notice_event_1_0', methods=['GET', 'POST'])
# def notice():
#     date = request.form['date']
#     notice = request.form['notice']

#     conn = sqlite3.connect(g_db_path)
#     cur = conn.cursor()

#     cur.execute('select count(*) from sqlite_master where name="notice"')
#     if not cur.fetchall()[0][0]:
#         cur.execute('create table notice (date text, content text)')

#     cur.execute('insert into notice values (?, ?)', (date, notice))

#     conn.commit()
#     conn.close()

#     return 'noticed'


# @app.route('/get_notice', methods=['GET', 'POST'])
# def get_notice():
#     conn = sqlite3.connect(g_db_path)
#     cur = conn.cursor()

#     cur.execute('select * from notice')
#     latest = ''
#     for row in cur:
#         latest = row

#     return '{}_{}'.format(latest[0], latest[1])


@app.route('/get_titles', methods=['GET', 'POST'])
def get_titles():
    f = open(g_keyword_path, 'r', encoding='UTF8')
    titles = [row.strip() for row in f]
    random.shuffle(titles)
    f.close()

    s = ''
    for title in sorted(titles):
        s += title + ' '

    return s[:-1]


@app.route('/add_title', methods=['GET', 'POST'])
def add_title():
    title = request.form['title']

    manage_file(g_keyword_path, 'a', '\n'+title) # 마지막줄 공백이 없으므로 직접추가.
    return 'added'


def initialize():
    f = open(g_keyword_path, 'r', encoding='UTF8')
    titles = [row.strip() for row in f]
    random.shuffle(titles)
    f.close()

    return titles


# ----------------------------------------------- #
default_path = '/var/www/Flask-server1/'
g_save_path = default_path + 'rooms/'
g_keyword_path = default_path + 'party_names/title.txt'
g_info_path = default_path + 'accounts/info.txt'
g_db_path = default_path + 'database/notices.db'

# ----------------------------------------------- #

g_title_index = 0
g_titles = initialize()

# 비활성 대진표 목록
g_locked_game_tables = []


app.run()
