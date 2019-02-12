# Servidor de Desafios

## Como usar

### Adicionando usuários a partir do arquivo do Blackboard

Para adicionar todos os alunos de uma única vez, faça o download da lista de
alunos em formato CSV disponível no Blackboard. Então basta executar o seguinte
comando no servidor, via SSH:

    $ cd softdes
    $ source venv/bin/activate
    $ python manage.py batch_add_users ARQUIVO_BLACKBOARD.csv

### Criando novos exercícios

Entre no Django admin (`/admin/challenges/challenge`) e clique
em `ADICIONAR CHALLENGE`. A data limite não é obrigatória. A opção
`Function name` define qual deve ser o nome da função enviada pelo aluno.

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

### Criando novos tutoriais

Entre no Django admin (`/admin/tutorials/tutorial`) e clique
em `ADICIONAR TUTORIAL`. A descrição aceita código HTML.

O campo `Replit url` pode ser usado para adicionar um iframe com
o [repl.it](https://repl.it) ao final do tutorial. O valor deste campo
deve ser uma url, fornecida em `Share Link` ao clicar em `share` no repl.it.

## Configuração do servidor

### Setup

Todas as dependências estão no arquivo `requirements.txt`:

    $ pip install -r requirements.txt

Além disso, é necessário instalar a biblioteca customizada de execução de testes.
Para isso, vá até a pasta `ChallengeTestRunner` e instale a biblioteca:

    $ cd ChallengeTestRunner
    $ python setup.py install

### Servidor de Produção

Para utilizar as configurações de produção é necessário que o arquivo
`InsperProgChallenges/production_settings.py` exista (ele pode estar vazio).

Para atualizar o servidor de produção basta executar um `git pull` e reiniciar o
Apache.

### Configuração do lambda

Execute o script `prepare_lambda_code.sh`. Faça o upload do arquivo
`lambda_code.zip` na função `testRunner` na Amazon.
