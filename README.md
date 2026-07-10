# CEMO - Controle de Insumos

MVP em Python + Streamlit para controle de insumos, estoque, processos de compra, atas/contratos, alertas, relatórios e auditoria do CEMO/INCA.

## Recursos entregues

- Login com hash de senha e perfis de acesso.
- Usuário inicial administrador.
- Banco SQLite com SQLAlchemy, preparado para migração futura para PostgreSQL/Supabase.
- Cadastro e consulta de insumos.
- Controle de estoque com entradas, saídas, ajustes, perdas, devoluções e inventário.
- Cálculo de consumo médio diário, cobertura em dias e ponto de reposição.
- Processos de compra em tabela e visão Kanban.
- Cadastro de atas e contratos.
- Alertas automáticos de estoque, cobertura, validade, processos parados, entregas atrasadas e atas vencendo/vencidas.
- Auditoria de operações críticas.
- Importação de planilhas Excel com leitura de abas, tratamento de células mescladas, prévia, sugestão de mapeamento e relatório.
- Relatórios exportáveis em CSV e Excel.

## Observação sobre a planilha original

O briefing cita `INSUMOS CPC_CEMO (3).xlsx`, mas o arquivo não estava dentro do zip recebido nem no repositório vazio do GitHub no momento da criação. Por isso, a primeira versão entrega a rotina de importação pronta para carregar essa planilha pela tela **Importar planilha**. Ao importar, campos sem correspondência clara são preservados em `dados_origem`.

## Requisitos

- Python 3.11 ou superior
- Windows, Linux ou macOS

## Instalação

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Copie `.env.example` para `.env` se quiser personalizar banco, nome da aplicação ou credenciais iniciais.

## Inicialização do banco

```bash
python -m database.init_db
```

## Execução local

```bash
streamlit run app.py
```

## Login inicial

- E-mail: `admin@cemo.local`
- Senha: `Admin@123`
- Perfil: `administrador`

Troque essa senha no primeiro acesso.

## Importação da planilha

1. Acesse **Importar planilha**.
2. Envie `INSUMOS CPC_CEMO (3).xlsx`.
3. Revise a prévia por aba.
4. Ajuste o mapeamento das colunas quando necessário.
5. Confirme a importação.

Campos reconhecidos automaticamente incluem código, descrição, categoria, subcategoria, unidade, fabricante, marca, fornecedor, observações, estoque atual, estoque mínimo e consumo médio mensal.

## Estrutura do projeto

```text
app.py
config/
database/
services/
pages/
components/
utils/
data/
tests/
```

## Publicação no Streamlit Community Cloud

1. Suba o repositório para o GitHub.
2. No Streamlit Community Cloud, selecione o repositório.
3. Configure `app.py` como arquivo principal.
4. Defina os segredos equivalentes ao `.env`, se necessário.
5. Em produção, não versionar `database/cemo.db`; use volume persistente ou banco externo.

## Migração futura para Supabase/PostgreSQL

A aplicação usa SQLAlchemy e lê `DATABASE_URL` do ambiente. Para migrar:

1. Criar banco PostgreSQL/Supabase.
2. Ajustar `DATABASE_URL`.
3. Instalar driver `psycopg[binary]`.
4. Rodar uma rotina de migração/seed.
5. Revisar persistência de arquivos importados e backups.

## Testes

```bash
pytest
```

Os testes cobrem login, criação de usuário, permissões, cálculo de cobertura, criticidade, movimentação de estoque, alertas e auditoria.

## Erros comuns

- `ModuleNotFoundError`: rode `pip install -r requirements.txt`.
- Banco não encontrado: rode `python -m database.init_db`.
- Senha inicial não funciona: verifique `INITIAL_ADMIN_EMAIL` e `INITIAL_ADMIN_PASSWORD` no `.env` antes da primeira inicialização.
- Importação sem registros: revise o mapeamento da coluna de descrição.

## Limitações da versão 1

- Configurações são lidas do `.env`; a tela mostra os parâmetros, mas ainda não persiste mudanças em tabela.
- Documentos/anexos de atas aparecem como campo planejado para evolução.
- A importação real depende do envio da planilha original.
- Ainda não há integração com e-mail, Supabase, SSO ou armazenamento externo.

## Sugestões para versão 2

- Persistir parâmetros de criticidade em tabela editável.
- Criar anexos para processos e atas.
- Implementar workflow de solicitações do laboratório.
- Adicionar histórico visual por processo.
- Criar perfis de permissão granular por ação.
- Migrar banco para PostgreSQL/Supabase.
