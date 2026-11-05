# Runbook — Endereço de acesso das empresas (D-088)

Desde a [D-088](../00-governance/decision-register.md#d-088--identificação-da-empresa-pelo-endereço-de-acesso) o login identifica a empresa pelo endereço ([ADR-012](../adr/ADR-012.md)). **Tenant sem domínio verificado não faz login.** **Nenhum destes passos foi executado em ambiente real.** Execução real exige autorização explícita, backup recente e restore testado (D-028/D-029).

## 1. Antes do deploy da versão com D-088

A migration `20261106120000_tenant_domains` é aditiva e cria a tabela vazia. Entre aplicá-la e subir a aplicação nova, cadastre um subdomínio da plataforma para **cada** tenant que deve continuar entrando. Sem isso, os usuários desses tenants recebem `404 TENANT_DOMAIN_NOT_FOUND` no login.

1. Liste os tenants e escolha, com o responsável, o subdomínio de cada um (letras minúsculas, dígitos e hífen):
   ```sql
   SELECT id, name, status FROM tenants WHERE deleted_at IS NULL ORDER BY name;
   ```
2. Cadastre, um tenant por vez (só insere; repetir não duplica, porque `hostname` é único):
   ```sql
   BEGIN;
   -- UUID v7 (D-001 / ADR-009): funcao TEMPORARIA, some ao fechar a sessao; o schema nao muda.
   CREATE FUNCTION pg_temp.uuid_v7() RETURNS text LANGUAGE sql VOLATILE AS $$
     SELECT encode(
       set_bit(set_bit(
         overlay(uuid_send(gen_random_uuid())
                 PLACING substring(int8send((extract(epoch FROM clock_timestamp()) * 1000)::bigint) FROM 3)
                 FROM 1 FOR 6),
         52, 1), 53, 1),
       'hex')::uuid::text
   $$;
   INSERT INTO tenant_domains (id, tenant_id, hostname, kind, status, verified_at, updated_at)
   VALUES (pg_temp.uuid_v7(), '<tenant_id>', '<subdominio>.<dominio-da-plataforma>',
           'platform_subdomain', 'verified', now(), now())
   ON CONFLICT (hostname) DO NOTHING;
   SELECT tenant_id, hostname, status FROM tenant_domains WHERE tenant_id = '<tenant_id>';
   COMMIT;
   ```
   Se o `SELECT` não mostrar o endereço, ele já pertence a outro tenant: escolha outro. Nunca transfira um domínio de um tenant para outro sem decisão explícita.
3. DNS e TLS: o subdomínio precisa resolver para o Nginx da plataforma (registro wildcard `*.<dominio-da-plataforma>`) e ter certificado válido.
4. Nginx: em cada `server` do CRM, `/v1` vai para o backend com `proxy_set_header Host $host;`. O backend não lê `X-Forwarded-Host`.
5. Depois do deploy, confira com `GET https://<endereco>/v1/auth/tenant`: deve devolver o nome da empresa.

## 2. Tenant novo

`npm run tenant:provision-trial` já cria o subdomínio verificado (`--subdomain`, com `PLATFORM_BASE_DOMAIN` no ambiente). Ele só cadastra subdomínio da plataforma.

## 3. Domínio próprio do cliente

**Não implementado.** O desenho (desafio TXT, CNAME, TLS depois da verificação, reverificação periódica) está no [ADR-012](../adr/ADR-012.md). Até existir, não cadastre domínio `custom` como `verified` à mão: isso pularia a prova de propriedade.

## 4. Desativar um endereço

```sql
UPDATE tenant_domains SET status = 'disabled', updated_at = now() WHERE hostname = '<hostname>';
```

Login e refresh nesse endereço param na hora; requisições já autenticadas, em até 30 s. Sem outro domínio verificado, a empresa fica sem acesso.

## 5. Desenvolvimento local

O seed cria `exemplo.localhost` (Empresa Exemplo) e `trial.localhost` (Empresa Trial). Abra `http://exemplo.localhost:5173`; detalhes em [local-development.md](local-development.md).
