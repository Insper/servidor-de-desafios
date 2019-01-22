# Servidor de Desafios

## Setup

Todas as dependências estão no arquivo `requirements.txt`:

    $ pip install -r requirements.txt

Além disso, é necessário instalar a biblioteca customizada de execução de testes. Para isso, 
vá até a pasta `ChallengeTestRunner` e instale a biblioteca:

    $ cd ChallengeTestRunner
    $ python setup.py install
   
## Servidor de Produção

Para utilizar as configurações de produção é necessário que o arquivo 
`InsperProgChallenges/production_settings.py` exista (ele pode estar vazio).

Para atualizar o servidor de produção basta executar um `git pull` e reiniciar o Apache.

## Configuração do lambda

Execute o script `prepare_lambda_code.sh`. Faça o upload do arquivo 
`lambda_code.zip` na função `testRunner` na Amazon.