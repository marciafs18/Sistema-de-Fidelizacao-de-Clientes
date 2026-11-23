# Sistema Web de Fidelização de Clientes, Vendas e Controle de Pontos

## 1. Sobre o projeto

O Sistema Web de Fidelização de Clientes foi desenvolvido para apoiar o acompanhamento de clientes, vendas, parcelas e movimentações de pontos. A aplicação possui áreas destinadas à administração/funcionários e aos clientes, com acesso controlado por perfil.

O projeto foi desenvolvido em **Python**, utilizando o framework **Flask**. As páginas são renderizadas com templates HTML e os dados são manipulados por meio do Flask-SQLAlchemy.

> **Hospedagem:** http://sistema-pontos-vercel.vercel.app

## 2. Funcionalidades implementadas

- **Autenticação:** tela de login, validação de credenciais e encerramento de sessão.
- **Perfis de acesso:** administrador (ADM), funcionário (FUNC) e cliente (CLI), com restrição de funcionalidades conforme o perfil.
- **Gestão de usuários:** cadastro de usuários administrativos e funcionários pelo administrador.
- **Gestão de clientes:** cadastro, edição, consulta e visualização da ficha do cliente.
- **Busca e filtros:** pesquisa de clientes por nome, e-mail ou telefone, filtro por situação (ativo/inativo) e faixa de saldo de pontos. A listagem de parcelas também possui filtros por situação, período de vencimento, forma de pagamento e nome do cliente.
- **Vendas e parcelas:** registro de vendas parceladas e acompanhamento das parcelas.
- **Fidelidade:** consulta de saldo, movimentação de pontos, resgate e ajustes administrativos.
- **QR Code:** geração/visualização de QR Code na área do cliente e validação do token pelo leitor da loja.
- **Relatórios:** consulta de movimentações de pontos por origem e relatório de vendas bloqueadas por saldo insuficiente.
- **Auditoria:** registro de ações importantes, como login, criação de cliente, venda, pagamento de parcela e leitura de QR Code.

## 3. Regras de negócio

O sistema contém regras para controlar o uso dos pontos. Entre elas:

- O saldo de pontos é calculado a partir das movimentações registradas.
- O cadastro de venda verifica se o cliente possui saldo suficiente, conforme a regra documentada no arquivo `REGRAS_DE_NEGOCIO.md`.
- O pagamento de parcela registra a movimentação de crédito de pontos.
- O resgate verifica se o cliente possui pontos suficientes.
- Ações administrativas relevantes são registradas no log de auditoria.

Consulte `REGRAS_DE_NEGOCIO.md` para a descrição detalhada da regra de venda condicionada ao saldo de pontos.

## 4. Tecnologias utilizadas

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Login
- Flask-WTF
- HTML e Jinja2
- SQLite (configuração atual do projeto)
- Vercel (configuração de deploy presente no repositório)

## 5. Organização dos arquivos

```text
.
├── app.py
├── config.py
├── extensions.py
├── models.py
├── decorators.py
├── requirements.txt
├── vercel.json
├── REGRAS_DE_NEGOCIO.md
├── auth/
│   └── routes.py
├── crm/
│   └── routes.py
├── financeiro/
│   └── routes.py
├── fidelidade/
│   └── routes.py
├── loja/
│   └── routes.py
├── cliente_app/
│   └── routes.py
└── templates/
    ├── base.html
    ├── auth/
    ├── crm/
    ├── financeiro/
    ├── fidelidade/
    ├── loja/
    ├── cliente_app/
    └── errors/
```

As pastas de rotas separam os módulos funcionais da aplicação. Os arquivos HTML estão organizados em `templates/` por área do sistema.

## 6. Como executar localmente

É necessário ter Python instalado.

1. Baixe ou clone este repositório.
2. Abra o terminal na pasta do projeto.
3. Crie e ative um ambiente virtual:

   **Windows**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/macOS**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Execute a aplicação:
   ```bash
   python app.py
   ```

6. Acesse no navegador o endereço local informado pelo Flask (normalmente `http://127.0.0.1:5000`).

## 7. Banco de dados e hospedagem — observação sobre a versão entregue

A configuração presente no código utiliza **SQLite**. Quando a variável de ambiente do Vercel está ativa, o banco é configurado em `/tmp/poc.db`, que é um diretório temporário. Portanto, essa configuração não equivale a um banco BaaS persistente como Firebase/Firestore e os dados podem não ser preservados entre execuções/instâncias.

O enunciado da disciplina menciona o uso de um serviço BaaS e armazenamento em banco web. Essa integração não está identificada na versão de código recebida para documentação. Esta documentação descreve o que está efetivamente implementado, sem afirmar uma integração que não consta no projeto.

## 8. Equipe

**Integrantes:** Márcia Ferreira da Silva; Luiz Felipe Rodrigues da Silva; Paulo Ricardo da Mota Rodrigues

## 9. Disciplina

**Disciplina:** DWE-1 — 2026.2  
**Projeto:** Sistema Web de Fidelização de Clientes, Vendas e Controle de Pontos

---
