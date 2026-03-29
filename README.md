# Catálogo Inteligente

Aplicação web escalável de catálogo de produtos com filtros avançados, desenvolvida como Atividade Final da disciplina de Desenvolvimento de Software em Nuvem — ADS/IA EAD Unifor.

## Arquitetura

- **Frontend**: React + TypeScript + Tailwind CSS — deploy no Firebase Hosting
- **Backend**: FastAPI (Python) containerizado com Docker — deploy no Cloud Run (GCP)
- **Banco de dados**: Cloud Firestore (GCP)
- **Autenticação**: Firebase Authentication
- **CI/CD**: GitHub Actions com deploy automático

## Pré-requisitos

- Node.js 20+
- Python 3.11+
- Docker
- Conta GCP com os serviços habilitados: Cloud Run, Artifact Registry, Firestore, Firebase

## Configuração Local

### Backend

```bash
cd backend
cp .env.example .env
# Preencha o .env com suas credenciais
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
cp .env.example .env
# Preencha o .env com suas credenciais Firebase
npm install
npm run dev
```

### Testes

```bash
cd backend
pytest tests/ -v
```

### Docker

```bash
cd backend
docker build -t catalogo-backend .
docker run -p 8080:8080 --env-file .env catalogo-backend
```

## Secrets GitHub Actions necessários

Configure em Settings > Secrets and variables > Actions:

- `GCP_PROJECT_ID` — ID do projeto GCP
- `GCP_SA_KEY` — JSON da Service Account com permissões para Cloud Run, Artifact Registry e Firebase
- `ALLOWED_ORIGINS` — URL do frontend em produção
- `VITE_API_URL` — URL do Cloud Run em produção
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`

## Serviços GCP para habilitar

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Criar Artifact Registry

```bash
gcloud artifacts repositories create catalogo \
  --repository-format=docker \
  --location=us-central1
```

## Papéis da Equipe

| Papel | Responsabilidade |
|---|---|
| Arquiteto de Software em Nuvem | Arquitetura GCP, Docker, CI/CD |
| Desenvolvedor Back-end | FastAPI, Firestore, autenticação |
| Desenvolvedor Front-end | React, filtros, UI/UX |
| Engenheiro DevOps | GitHub Actions, Cloud Run, Artifact Registry |
| QA e Testes | Pytest, cobertura de testes |

## Documentação da API

Acesse `/docs` com o backend rodando para visualizar o Swagger/OpenAPI.

## Observações

Esse template cobre os principais requisitos da atividade: autenticação, CRUD, filtros avançados, Docker, Cloud Run, Firestore, Firebase Auth, Firebase Hosting, CI/CD com GitHub Actions, testes automatizados com Pytest, Swagger automático pelo FastAPI, variáveis de ambiente, separação dev/prod, logs de acesso e proteção de rotas por perfil.
