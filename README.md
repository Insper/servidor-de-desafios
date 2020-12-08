# Servidor de Desafios

1. [Configuração do servidor](#configuração-do-servidor)
2. [Como Usar](#como-usar)
3. [Agradecimentos](#agradecimentos)

## Configuração do servidor

### Setup

#### Poetry

##### Installing Poetry

In this project we use [Poetry](https://python-poetry.org/) for dependency management. You can install it by following the instructions here: https://python-poetry.org/docs/#installation

With Poetry installed you can install the dependencies with:

    $ poetry install

##### Activating the virtual env with Poetry

Always activate the virtual env before starting to work:

    $ poetry shell

#### React Frontend

We use [React](https://reactjs.org/) to develop our frontend. To install it you must first [install Node.js](https://nodejs.org/en/download/package-manager/). Then, go to `frontend` directory and install all the dependencies:

    $ cd frontend
    $ npm install

### Design

The font used for the logo is [Gayathri](https://fonts.google.com/specimen/Gayathri?preview.text=python%20gym&preview.text_type=custom).

### Running server in dev mode

Run the server with:

    $ ./manage.py runserver

To update the react frontend, run:

    $ cd frontend
    $ npm run dev

If you are developing the frontend, the following will probably be useful:

    $ cd frontend
    $ npm run watch



# ANTIGO

#### Configurando um ambiente virtual

Para não ter conflitos entre versões ou bibliotecas, podemos criar um ambiente virtual. Para isso, entre na pasta em que clonou o servidor e execute o seguinte comando no terminal:

    $ python -m venv env

#### Ativando o ambiente virtual

Depois de criado, é preciso ativar o ambiente virtual.

No Windows:

    $ env\Scripts\activate

No Linux/MacOS:

    $ . env/bin/activate

#### Instalando bibliotecas

Primeiramente, é necessário instalar a biblioteca customizada de execução de testes.
Para isso, vá até a pasta `ChallengeTestRunner` e instale a biblioteca:

    $ cd ChallengeTestRunner
    $ python setup.py install

Volte para a raíz da aplicação e instale todas as dependências que estão no arquivo `requirements.txt`:

    $ cd ..
    $ pip install -r requirements.txt

### Servidor de Produção

Para utilizar as configurações de produção modifique o arquivo `servidor_dessoft/settings/production.py`.

Para atualizar o servidor de produção basta executar um `git pull` e reiniciar o
Apache.

### Configuração do lambda

Execute o script `prepare_lambda_code.sh`. Faça o upload do arquivo
`lambda_code.zip` na função `testRunner` na Amazon.

## Como usar

### Adicionando usuários a partir do arquivo do Blackboard

Para adicionar todos os alunos de uma única vez, faça o download da lista de
alunos em formato CSV disponível no Blackboard. Então basta executar o seguinte
comando no servidor, via SSH:

    $ cd softdes
    $ source venv/bin/activate
    $ python manage.py batch_add_users ARQUIVO_BLACKBOARD.csv

### Criando um cadastro
Para criar um cadastro para administrar os exercícios, execute o comando:

    $ python manage.py createsuperuser

 Em seguida, basta definir um nome usuário e senha.

### Criando novos exercícios

Se você tiver configurado um ambiente virtual, é necessário [ativá-lo](#ativando-o-ambiente-virtual) sempre que for realizar alguma alteração nos exercícios:

Depois, execute o seguinte comando:

        $ python manage.py runserver

Isso permite você a entrar no Django admin (pode digitar no seu navegador: 'localhost:8000/admin/')
Para criar o exercício, clique em 'Adicionar', ao lado de 'Exercícios de programação'. Será necessário definir algumas características:


    * Título: Nome que aparecerá para o exercício no servidor
    * Descrição: Enunciado
    * Imagem: (opcional)
    * Testes: (Veja mais na seção de testes)
    * Nome função define qual deve ser o nome da função enviada pelo aluno.
    * Tag: Marca o conteúdo relacionado àquele exercício.
            * Você pode criar novas tags clicando em `Adicionar outro tag`

Na parte `Exercícios de programação`, você pode gerenciar os exercícios criados

### Testes

O arquivo de testes define a bateria de testes pelos quais a função enviada pelo
aluno passará. Ele deve seguir o seguinte exemplo:

    from challenge_test_lib import challenge_test as ch

    # O nome da classe deve necessariamente ser TestCase
    class TestCase(ch.TestCaseWrapper):
        TIMEOUT = 2  # Limite de tempo em segundos por teste (default: 3s)

        # A mensagem de erro é definida por meio de um decorator.
        # Ela não é obrigatória. Caso não seja definida, uma mensagem
        # padrão será apresentada em caso de erro.
        # Todos os testes devem começar com 'test_'
        @ch.error_message('Verificar quando os argumentos forem zero')
        def test_argumentos_zero(self):
            # A challenge_test_lib foi construída com base no unittest.
            # Assim, quaisquer asserts do unittest podem ser utilizados.
            # Para mais opções:
            # https://docs.python.org/3/library/unittest.html#assert-methods
            # A função submetida pelo aluno estará disponível como
            # self.challenge_fun. Neste exemplo ela recebe 3 argumentos,
            # mas a quantidade e tipo dos argumentos pode ser diferente
            self.assertAlmostEquals(self.challenge_fun(0, 0, 0), 0.0)

        # Outro exemplo de teste
        @ch.error_message('Verificar quando o número de meses é zero')
        def test_zero_meses(self):
            self.assertAlmostEquals(self.challenge_fun(100, 0, 0.1), 100.0)

#### Rodando a bateria de testes no terminal

Para executar sua bateria de testes no terminal (durante o desenvolvimento),
basta executar o script `insper_test.py`. Esse script é instalado no path do
Python junto com a biblioteca `challenge_test_lib`.

Você pode, por exemplo, criar um arquivo com respostas que deveriam passar no teste do exercício e um outro com algumas que deveriam falhar. Para executar, use o seguinte comando:

    $ insper_test.py -f nome_da_funcao arquivo_com_resposta.py arquivo_com_funções_teste.py

### Criando novos tutoriais

Entre no Django admin (`/admin/tutorials/tutorial`) e clique
em `ADICIONAR TUTORIAL`. A descrição aceita código HTML.

O campo `Replit url` pode ser usado para adicionar um iframe com
o [repl.it](https://repl.it) ao final do tutorial. O valor deste campo
deve ser uma url, fornecida em `Share Link` ao clicar em `share` no repl.it.

## Agradecimentos

Ao fazer um pull request inclua também uma descrição curta da sua contribuição nos agradecimentos. A partir de agora só aceitaremos os PRs que já tiverem os agradecimentos preenchidos.

Para isso, adicione seus dados em [`core/templates/core/thanks.html`](core/templates/core/thanks.html) utilizando a template tag `student_author`:

    {% student_author "SEU NOME" "SUA TURMA" "DESCRIÇÃO CURTA DA SUA CONTRIBUIÇÃO" "sua_foto" %}

Lembre-se de adicionar sua foto em [`static/assets/img/authors/`](static/assets/img/authors/). **Importante**: envie uma imagem quadrada.
