# Guia de Deploy no OpenShift/OKD4

Este documento descreve o processo de deploy e atualização da aplicação Maintenance App no OpenShift.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Deploy Inicial](#deploy-inicial)
4. [Atualizando a Aplicação](#atualizando-a-aplicação)
5. [Comandos Úteis](#comandos-úteis)
6. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

- CLI `oc` instalado
- Acesso ao cluster OpenShift/OKD4
- Login no cluster: `oc login <URL_DO_CLUSTER>`

```bash
# Verificar se está logado
oc whoami

# Verificar o projeto atual
oc project
```

---

## Estrutura do Projeto

```
maintenance_app/
├── .env                    # Variáveis de ambiente (NÃO versionado)
├── .env.example            # Template de variáveis
├── Dockerfile              # Imagem da aplicação
├── openshift/              # Manifests do OpenShift
│   ├── 00-namespace.yaml
│   ├── 01-secret.yaml      # Credenciais (NÃO commitar)
│   ├── 02-configmap.yaml
│   ├── 03-pvc-postgres.yaml
│   ├── 04-postgres-deployment.yaml
│   ├── 05-postgres-service.yaml
│   ├── 06-redis-deployment.yaml
│   ├── 07-redis-service.yaml
│   ├── 08-imagestream.yaml
│   ├── 09-buildconfig.yaml
│   ├── 10-django-deployment.yaml
│   ├── 11-django-service.yaml
│   ├── 12-celery-worker-deployment.yaml
│   ├── 13-celery-beat-deployment.yaml
│   ├── 14-route.yaml
│   └── deploy.sh
└── docs/
    └── OPENSHIFT_DEPLOY.md
```

---

## Deploy Inicial

### 1. Criar o Projeto (Namespace)

```bash
oc new-project maintenance
# ou
oc project maintenance
```

### 2. Aplicar Secrets e ConfigMaps

```bash
cd openshift/

# Aplicar secrets (credenciais)
oc apply -f 01-secret.yaml

# Aplicar configurações
oc apply -f 02-configmap.yaml
```

### 3. Deploy do Banco de Dados e Redis

```bash
# PVC para dados do PostgreSQL
oc apply -f 03-pvc-postgres.yaml

# PostgreSQL
oc apply -f 04-postgres-deployment.yaml
oc apply -f 05-postgres-service.yaml

# Redis
oc apply -f 06-redis-deployment.yaml
oc apply -f 07-redis-service.yaml

# Aguardar ficarem prontos
oc rollout status deployment/postgres
oc rollout status deployment/redis
```

### 4. Configurar Build da Imagem

```bash
# ImageStream
oc apply -f 08-imagestream.yaml

# BuildConfig
oc apply -f 09-buildconfig.yaml

# Iniciar primeiro build
oc start-build maintenance --follow
```

### 5. Deploy da Aplicação

```bash
# Django
oc apply -f 10-django-deployment.yaml
oc apply -f 11-django-service.yaml

# Celery Worker
oc apply -f 12-celery-worker-deployment.yaml

# Celery Beat
oc apply -f 13-celery-beat-deployment.yaml

# Route (acesso externo)
oc apply -f 14-route.yaml
```

### 6. Verificar Deploy

```bash
# Ver todos os pods
oc get pods

# Ver URL da aplicação
oc get route maintenance -o jsonpath='{.spec.host}'
```

---

## Atualizando a Aplicação

### Processo Padrão de Atualização

Quando você fizer alterações no código, siga estes passos:

#### Passo 1: Commit e Push das Alterações

```bash
# Adicionar alterações
git add .

# Commit
git commit -m "feat: descrição da alteração"

# Push para o repositório
git push origin main
```

#### Passo 2: Iniciar Novo Build no OpenShift

```bash
# Iniciar build e acompanhar logs
oc start-build maintenance -n maintenance --follow
```

O build irá:
1. Clonar o repositório do GitHub
2. Construir a imagem Docker
3. Push da imagem para o registry interno

#### Passo 3: Reiniciar os Deployments

```bash
# Reiniciar todos os componentes da aplicação
oc rollout restart deployment/django-web deployment/celery-worker deployment/celery-beat -n maintenance
```

#### Passo 4: Verificar o Deploy

```bash
# Acompanhar status do rollout
oc rollout status deployment/django-web -n maintenance

# Ver pods
oc get pods -n maintenance

# Ver logs (se necessário)
oc logs -f deployment/django-web -n maintenance
```

### Atualização Rápida (One-liner)

```bash
# Commit, push, build e restart em uma linha
git add . && git commit -m "fix: correção" && git push origin main && \
oc start-build maintenance -n maintenance --follow && \
oc rollout restart deployment/django-web deployment/celery-worker deployment/celery-beat -n maintenance
```

### Atualizar Apenas Variáveis de Ambiente

Se você alterou apenas variáveis de ambiente (secrets ou configmap):

```bash
# Atualizar secret
oc apply -f openshift/01-secret.yaml

# Atualizar configmap
oc apply -f openshift/02-configmap.yaml

# Reiniciar deployments para carregar novas variáveis
oc rollout restart deployment/django-web deployment/celery-worker deployment/celery-beat -n maintenance
```

---

## Comandos Úteis

### Monitoramento

```bash
# Ver todos os pods
oc get pods -n maintenance

# Ver logs em tempo real
oc logs -f deployment/django-web -n maintenance
oc logs -f deployment/celery-worker -n maintenance
oc logs -f deployment/celery-beat -n maintenance

# Ver eventos do namespace
oc get events -n maintenance --sort-by='.lastTimestamp'

# Descrever um pod (para debug)
oc describe pod <nome-do-pod> -n maintenance
```

### Builds

```bash
# Listar builds
oc get builds -n maintenance

# Ver logs de um build específico
oc logs build/maintenance-5 -n maintenance

# Cancelar build em andamento
oc cancel-build maintenance-5 -n maintenance
```

### Scaling

```bash
# Escalar Django para 3 réplicas
oc scale deployment/django-web --replicas=3 -n maintenance

# Escalar Celery workers
oc scale deployment/celery-worker --replicas=2 -n maintenance
```

### Acesso ao Container

```bash
# Abrir shell no container Django
oc rsh deployment/django-web -n maintenance

# Executar comando específico
oc exec deployment/django-web -n maintenance -- python3 manage.py shell

# Executar migrations manualmente
oc exec deployment/django-web -n maintenance -- python3 manage.py migrate
```

### Rollback

```bash
# Ver histórico de rollouts
oc rollout history deployment/django-web -n maintenance

# Voltar para versão anterior
oc rollout undo deployment/django-web -n maintenance

# Voltar para revisão específica
oc rollout undo deployment/django-web --to-revision=2 -n maintenance
```

---

## Troubleshooting

### Pod não inicia (ImagePullBackOff)

A imagem não existe ou não foi buildada:

```bash
# Verificar se o build foi feito
oc get builds -n maintenance

# Fazer novo build
oc start-build maintenance -n maintenance --follow
```

### Pod com CrashLoopBackOff

Erro na aplicação:

```bash
# Ver logs do pod
oc logs <nome-do-pod> -n maintenance

# Ver logs do pod anterior (se reiniciou)
oc logs <nome-do-pod> -n maintenance --previous
```

### Erro de Permissão (PermissionError)

OpenShift roda containers como non-root. Use `/tmp` para arquivos temporários:

```python
# Errado
logging.basicConfig(filename='error_log.txt')

# Correto
logging.basicConfig(filename='/tmp/error_log.txt')
```

### Erro de CSRF

Adicione a URL do OpenShift em `settings.py`:

```python
CSRF_TRUSTED_ORIGINS = [
    'https://maintenance-maintenance.apps.okd.ignetworks.com',
]
```

### PVC Pendente

```bash
# Verificar PVCs
oc get pvc -n maintenance

# Ver storage classes disponíveis
oc get storageclass

# Editar PVC para usar storage class correta
oc edit pvc postgres-pvc -n maintenance
```

### Verificar Recursos

```bash
# Ver uso de recursos dos pods
oc adm top pods -n maintenance

# Ver limites configurados
oc get deployment django-web -n maintenance -o yaml | grep -A 10 resources
```

---

## URLs Importantes

- **Aplicação:** https://maintenance-maintenance.apps.okd.ignetworks.com
- **Admin Django:** https://maintenance-maintenance.apps.okd.ignetworks.com/admin/
- **Credenciais Admin:** `admin` / `admin`

---

## Contato

Em caso de dúvidas ou problemas, entre em contato com a equipe de NOC.
