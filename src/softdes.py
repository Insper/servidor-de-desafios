'''
    Module responible for managing the whole application
'''
import sqlite3
import hashlib
import numbers
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from flask import Flask, request, render_template

DBNAME = './quiz.db'

def lambda_handler(event):
    '''
    Args:
        event (object): Object with infos to run the test of the code uploaded

    Returns:
        response: A string with a feedback from the test that was ran or not
    '''
    try:
        def not_equals(first, second):
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        exec(code, locals())

        test = []
        for index, arg in enumerate(args):
            if not 'desafio{0}'.format(ndes) in locals():
                return "Nome da função inválido. Usar 'def desafio{0}(...)'".format(ndes)

            if not_equals(eval('desafio{0}(*arg)'.format(ndes)), resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except:
        return "Função inválida."

def convert_data(orig):
    '''
    Args:
        orig (str): A string in the original date format

    Returns:
        response: A string with a brasilian date format
    '''
    return orig[8:10]+'/'+orig[5:7]+'/'+orig[0:4]+' '+orig[11:13]+':'+orig[14:16]+':'+orig[17:]

def get_quizes(user):
    '''
    Args:
        user (str): A string with the username

    Returns:
        response: A list of the quizes associated with that user
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user in ('admin', 'fabioja'):
        cursor.execute("SELECT id, numb from QUIZ")
    else:
        cursor.execute("SELECT id, numb from QUIZ where release < '{0}'"
                       .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    info = list(cursor.fetchall())
    conn.close()
    return info

def get_user_quiz(userid, quizid):
    '''
    Args:
        userid (int): The user id
        quizid (int): The quiz id

    Returns:
        response: A list with one value that is the quiz
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sent,answer,result from USERQUIZ where userid = '{0}' \
                   and quizid = {1} order by sent desc".format(userid, quizid))
    info = list(cursor.fetchall())
    conn.close()
    return info

def set_user_quiz(userid, quizid, sent, answer, result):
    '''
    Args:
        userid (int): The user id
        quizid (int): The quiz id
        sent (str): The expected values for that quiz
        answer (str): The answer of tha running that quiz
        result (bool): The result of comparing the expected and the answer
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) values (?,?,?,?,?);",
                   (userid, quizid, sent, answer, result))
    #
    conn.commit()
    conn.close()

def get_quiz(quiz_id, user):
    '''
    Args:
        id (int): The quiz id
        user (str): The username

    Returns:
        response: A list with one value that is the quiz
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    print("QUIZ_ID: ", quiz_id)
    if user in ('admin', 'fabioja'):
        cursor.execute("SELECT id, release, expire, problem, tests, \
                       results,  diagnosis, numb from QUIZ where id = {0}".format(quiz_id))
    else:
        cursor.execute("SELECT id, release, expire, problem, tests, results, diagnosis,\
                       numb from QUIZ where id = {0} and  release < '{1}'"
                       .format(quiz_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    info = list(cursor.fetchall())
    conn.close()
    return info

def set_info(pwd, user):
    '''
    Args:
        pwd (str): The user password
        user (str): The username
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()

def get_info(user):
    '''
    Args:
        user (str): The username
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT pass, type from USER where user = '{0}'".format(user))
    print("SELECT pass, type from USER where user = '{0}'".format(user))
    info = [reg[0] for reg in cursor.fetchall()]
    print("INFO: ", info)
    conn.close()
    if len(info) == 0:
        return None
    return info[0]

AUTH = HTTPBasicAuth()

APP = Flask(__name__, static_url_path='')
APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'

@APP.route('/', methods=['GET', 'POST'])
@AUTH.login_required
def main():
    '''
        Entry function of the program
    '''
    msg = ''
    page = 1
    challenges = get_quizes(AUTH.username())
    sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST' and 'ID' in request.args:
        quiz_id = request.args.get('ID')
        quiz = get_quiz(quiz_id, AUTH.username())
        if len(quiz) == 0:
            msg = "Boa tentativa, mas não vai dar certo!"
            page = 2
            return render_template('index.html', username=AUTH.username(),
                                   challenges=challenges, p=page, msg=msg)
        quiz = quiz[0]
        if sent > quiz[2]:
            msg = "Sorry... Prazo expirado!"

        file = request.files['code']
        filename = './upload/{0}_{1}.py'.format(AUTH.username(), sent.replace(":", '_'))
        file.save(filename)
        with open(filename, 'r') as f_p:
            answer = f_p.read()

        args = {"ndes": quiz_id, "code": answer, "args": eval(quiz[4]),
                "resp": eval(quiz[5]), "diag": eval(quiz[6])}

        feedback = lambda_handler(args)

        result = 'Erro'
        if len(feedback) == 0:
            feedback = 'Sem erros.'
            result = 'OK!'

        set_user_quiz(AUTH.username(), quiz_id, sent, feedback, result)

    if request.method == 'GET':
        if 'ID' in request.args:
            quiz_id = request.args.get('ID')
        else:
            quiz_id = 1

    if len(challenges) == 0:
        msg = "Ainda não há desafios! Volte mais tarde."
        page = 2
        return render_template('index.html', username=AUTH.username(),
                               challenges=challenges, p=page, msg=msg)

    quiz = get_quiz(quiz_id, AUTH.username())

    if len(quiz) == 0:
        msg = "Oops... Desafio invalido!"
        page = 2
        return render_template('index.html', username=AUTH.username(),
                               challenges=challenges, p=page, msg=msg)

    answers = get_user_quiz(AUTH.username(), quiz_id)

    return render_template('index.html', username=AUTH.username(),
                           challenges=challenges, quiz=quiz[0], e=(sent > quiz[0][2]),
                           answers=answers, p=page, msg=msg, expi=convert_data(quiz[0][2]))

@APP.route('/pass', methods=['GET', 'POST'])
@AUTH.login_required
def change():
    '''
        Function responsible for changing the user password
    '''
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        page = 1
        msg = ''
        if nova != repet:
            msg = 'As novas senhas nao batem'
            page = 3
        elif get_info(AUTH.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = 'A senha antiga nao confere'
            page = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), AUTH.username())
            msg = 'Senha alterada com sucesso'
            page = 3
    else:
        msg = ''
        page = 3

    return render_template('index.html', username=AUTH.username(),
                           challenges=get_quizes(AUTH.username()), p=page, msg=msg)


@APP.route('/logout')
def logout():
    '''
        Responsible for quiting the user from the applicatiom
    '''
    return render_template('index.html', p=2, msg="Logout com sucesso"), 401

@AUTH.get_password
def get_password(username):
    '''
        Gets the password of a user
    '''
    return get_info(username)

@AUTH.hash_password
def hash_pw(password):
    '''
        Hash a password with MD5 algorithm
    '''
    return hashlib.md5(password.encode()).hexdigest()

if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=80)
    