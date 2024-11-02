Projeto desenvolvido para a nuvem AWS utilizando CloudFormation como IaC e python para os microsserviços que são implementados e executados no AWS Lambda.
O desenvolvimento dos microsserviços em python utiliza POO, Arquitetura em camadas, Clean Architecture, SQLAlchemy ORM e Pytest para executar os testes unitários.

# Comandos úteis para utilização e ativação do ambiente

## Para Criar o Ambiente Virtual Python:
```virtualenv -p python3 venv```
## Para Ativar o Ambiente:
```. venv/bin/activate```
## Para instalar pacotes:
```pip3 install -r requirements.txt```
## Para Atualizar requirements:
```venv/bin/pip3 freeze > requirements.txt```
## Para gerar arquivo supressor do pylint:
```pylint --generate-rcfile > .pylintrc```
## Para rodar testes unitários:
```pytest -v```
## Para rodar pre-commit em qualquer momento:
```pre-commit run --all-files```
