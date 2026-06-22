# b2bflow – Desafio Técnico

Script Python que busca contatos no **Supabase** e envia mensagens personalizadas via **Z-API (WhatsApp)**.

---

## 1. Configuração da tabela no Supabase

Acesse o **SQL Editor** do seu projeto e execute:

```sql
create table contacts (
  id    bigint generated always as identity primary key,
  name  text not null,
  phone text not null  -- formato E.164 sem '+', ex: 5511999999999
);

-- Dados de exemplo
insert into contacts (name, phone) values
  ('Ana Silva',   '5511991110001'),
  ('Bruno Costa', '5511991110002'),
  ('Carla Souza', '5511991110003');
```

---

## 2. Configuração do `.env`

```bash
cp .env.example .env
```

Preencha `.env` com suas credenciais reais:

| Variável           | Onde encontrar                                         |
|--------------------|--------------------------------------------------------|
| `SUPABASE_URL`     | Supabase → Project Settings → API → Project URL       |
| `SUPABASE_KEY`     | Supabase → Project Settings → API → anon/service key  |
| `SUPABASE_TABLE`   | Nome da tabela (padrão: `contacts`)                   |
| `ZAPI_INSTANCE_ID` | Painel Z-API → sua instância → ID                     |
| `ZAPI_TOKEN`       | Painel Z-API → sua instância → Token                  |
| `ZAPI_CLIENT_TOKEN`| Painel Z-API → sua conta → Client Token               |

---

## 3. Como rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

O script imprime logs estruturados no terminal e encerra indicando quantas mensagens foram enviadas com sucesso.
