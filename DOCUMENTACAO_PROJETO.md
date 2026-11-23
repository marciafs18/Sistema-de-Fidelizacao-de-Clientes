# Documentação do Projeto — Sistema Web de Fidelização de Clientes

## 1. Apresentação
O projeto consiste em uma aplicação web para apoiar o gerenciamento de clientes, vendas parceladas e programa de fidelidade baseado em pontos. O sistema separa as permissões de acesso de acordo com o perfil do usuário.

## 2. Objetivo
Centralizar informações de clientes, acompanhar vendas e parcelas, registrar entradas e saídas de pontos e oferecer consultas para a operação da loja e para o cliente.

## 3. Perfis de usuário
- **Administrador (ADM):** gerencia usuários, cadastra clientes, realiza ajustes administrativos e possui acesso às operações administrativas.
- **Funcionário (FUNC):** acessa as funcionalidades operacionais da loja, conforme as permissões definidas no sistema.
- **Cliente (CLI):** acessa sua área, consulta informações de fidelidade e utiliza os recursos disponibilizados ao cliente.

## 4. Módulos e funcionalidades
### 4.1 Autenticação e usuários
O módulo de autenticação realiza a validação de e-mail e senha, cria e encerra sessões e registra eventos de login. Há fluxo para alteração de senha no primeiro acesso. O administrador pode cadastrar usuários dos perfis ADM e FUNC.

### 4.2 Cadastro e consulta de clientes
O módulo CRM permite cadastrar e editar clientes, consultar fichas e listar clientes. A listagem possui busca por nome, e-mail e telefone, filtro de situação e filtros de saldo mínimo e máximo de pontos.

### 4.3 Vendas e parcelas
O módulo financeiro registra vendas parceladas, calcula as parcelas e seus vencimentos e permite consultar parcelas. A listagem permite filtrar por situação, intervalo de vencimento, forma de pagamento e nome do cliente. O pagamento de uma parcela registra a forma realizada e a movimentação de pontos correspondente.

### 4.4 Programa de fidelidade
O módulo de fidelidade registra resgates, ajustes administrativos e movimentações de pontos. O saldo do cliente é calculado a partir do histórico de movimentações. Há relatório de pontos por origem.

### 4.5 QR Code
O módulo da loja possui leitor para validar tokens de QR Code. A área do cliente contém recurso relacionado ao QR Code. A validação registra eventos como QR inválido, expirado ou lido com sucesso.

### 4.6 Relatórios e auditoria
O sistema apresenta relatório de vendas bloqueadas por saldo insuficiente e relatório de movimentações de pontos por origem. O log de auditoria registra ações relevantes realizadas no sistema.

## 5. Tecnologias e arquitetura
A aplicação utiliza Python e Flask. O Flask organiza as rotas em módulos (blueprints), enquanto Flask-Login gerencia a autenticação. Flask-SQLAlchemy faz o mapeamento dos modelos para o banco de dados. As páginas são templates HTML com Jinja2.

Principais arquivos:
- `app.py`: criação e configuração da aplicação e registro dos módulos.
- `config.py`: configurações da aplicação e conexão com o banco.
- `models.py`: modelos de usuário, cliente, venda, parcela, resgate, movimentação de pontos e auditoria.
- `decorators.py`: controle de acesso por perfil.
- `auth/`, `crm/`, `financeiro/`, `fidelidade/`, `loja/` e `cliente_app/`: rotas dos módulos.
- `templates/`: páginas HTML organizadas por módulo.

## 6. Regras de negócio
As regras de negócio estão descritas no arquivo `REGRAS_DE_NEGOCIO.md`. A implementação verifica o saldo antes de registrar uma venda, registra débitos e créditos de pontos e valida a disponibilidade de pontos antes de um resgate.

## 7. Execução local
1. Instalar Python.
2. Criar e ativar ambiente virtual.
3. Executar `pip install -r requirements.txt`.
4. Executar `python app.py`.
5. Abrir `http://127.0.0.1:5000` no navegador.

## 8. Limitações identificadas na versão documentada
A versão recebida utiliza SQLite. A configuração do Vercel direciona o arquivo SQLite para `/tmp`, que é temporário. Não foi localizada integração com Firebase, Firestore ou outro serviço BaaS persistente. Assim, não se deve afirmar que a aplicação atende ao requisito de banco BaaS/JSON do enunciado sem que essa integração seja efetivamente realizada.

A estrutura recebida possui templates organizados por módulo, mas não foi localizada uma pasta independente de arquivos estáticos CSS, JavaScript e imagens no conteúdo do ZIP analisado. A documentação não declara essa separação como implementada.

## 9. Hospedagem\nURL pública informada pela equipe: http://sistema-pontos-vercel.vercel.app\n\n## 10. Identificação da equipe
Integrantes: Márcia Ferreira da Silva; Luiz Felipe Rodrigues da Silva; Paulo Ricardo da Mota Rodrigues

Disciplina: DWE-1 — 2026.2  
Projeto: Sistema Web de Fidelização de Clientes, Vendas e Controle de Pontos
