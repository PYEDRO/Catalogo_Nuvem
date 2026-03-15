# setup_gcp.py
import subprocess
import random
import string
import sys
import json
import os

# ─── CAMINHO DO GCLOUD NO WINDOWS ────────────────────────────────────────────
GCLOUD_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Google", "Cloud SDK", "google-cloud-sdk", "bin", "gcloud.cmd"
)

if not os.path.exists(GCLOUD_PATH):
    GCLOUD_PATH = "gcloud"

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
PROJECT_BASE  = "catalogo-unifor"
PROJECT_NAME  = "Catalogo Inteligente"
REGION        = "us-central1"
SA_NAME       = "catalogo-sa"
SA_KEY_FILE   = "sa-key.json"
REGISTRY_NAME = "catalogo"
SERVICE_NAME  = "catalogo-backend"
# ──────────────────────────────────────────────────────────────────────────────

def run(cmd, capture=False, ignore_error=False):
    cmd = cmd.replace("gcloud", f'"{GCLOUD_PATH}"', 1)
    print(f"\n>>> {cmd}")
    result = subprocess.run(
        cmd, shell=True,
        capture_output=capture,
        text=True
    )
    if result.returncode != 0 and not ignore_error:
        print(f"\n[ERRO] {result.stderr}")
        sys.exit(1)
    return result

def run_output(cmd):
    cmd = cmd.replace("gcloud", f'"{GCLOUD_PATH}"', 1)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def generate_project_id():
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{PROJECT_BASE}-{suffix}"

def check_gcloud():
    print("\n[1/8] Verificando gcloud CLI...")
    result = subprocess.run(
        f'"{GCLOUD_PATH}" --version',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[ERRO] gcloud nao encontrado no caminho: {GCLOUD_PATH}")
        print("Instale em: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    print(f"[OK] gcloud encontrado em: {GCLOUD_PATH}")
    print(result.stdout.splitlines()[0])

def login():
    print("\n[2/8] Verificando autenticacao...")
    result = run_output(
        "gcloud auth list --filter=status:ACTIVE --format='value(account)'"
    )
    if not result:
        print("Nenhuma conta ativa. Iniciando login...")
        run("gcloud auth login")
    else:
        print(f"[OK] Conta ativa: {result}")

def create_project():
    print("\n[3/8] Criando projeto no GCP...")
    attempts = 0
    project_id = None

    while attempts < 10:
        candidate = generate_project_id()
        print(f"Tentando ID: {candidate}")
        cmd = f'"{GCLOUD_PATH}" projects create {candidate} --name="{PROJECT_NAME}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            project_id = candidate
            print(f"[OK] Projeto criado: {project_id}")
            break
        elif "already in use" in result.stderr or "already exists" in result.stderr:
            print(f"ID {candidate} ja em uso. Tentando outro...")
            attempts += 1
        else:
            print(f"[ERRO] {result.stderr}")
            sys.exit(1)

    if not project_id:
        print("[ERRO] Nao foi possivel criar o projeto apos 10 tentativas.")
        sys.exit(1)

    return project_id

def set_default_project(project_id):
    print(f"\n[4/8] Definindo projeto padrao: {project_id}")
    run(f"gcloud config set project {project_id}")
    print("\n[AVISO] Verifique se o Billing esta ativo para este projeto.")
    print(f"Acesse: https://console.cloud.google.com/billing/linkedaccount?project={project_id}")
    print("Apos vincular uma conta de faturamento, pressione ENTER para continuar.")
    input()

def enable_services(project_id):
    print("\n[5/8] Habilitando servicos GCP...")
    services = [
        "run.googleapis.com",
        "artifactregistry.googleapis.com",
        "firestore.googleapis.com",
        "secretmanager.googleapis.com",
        "firebase.googleapis.com",
        "iam.googleapis.com",
        "cloudresourcemanager.googleapis.com",
    ]
    for service in services:
        print(f"  Habilitando {service}...")
        run(f"gcloud services enable {service} --project={project_id}")
    print("[OK] Todos os servicos habilitados.")

def create_artifact_registry(project_id):
    print("\n[6/8] Criando Artifact Registry...")
    existing = run_output(
        f"gcloud artifacts repositories list "
        f"--location={REGION} --project={project_id} "
        f"--format=value(name)"
    )
    if REGISTRY_NAME in existing:
        print("[OK] Artifact Registry ja existe.")
    else:
        run(
            f"gcloud artifacts repositories create {REGISTRY_NAME} "
            f"--repository-format=docker "
            f"--location={REGION} "
            f"--description=Imagens-Catalogo "
            f"--project={project_id}"
        )
        print("[OK] Artifact Registry criado.")

def create_firestore(project_id):
    print("\n[7/8] Criando banco Firestore...")
    existing = run_output(
        f"gcloud firestore databases list "
        f"--project={project_id} --format=value(name)"
    )
    if "(default)" in existing or "default" in existing:
        print("[OK] Firestore ja existe.")
    else:
        run(
            f"gcloud firestore databases create "
            f"--region={REGION} "
            f"--project={project_id}",
            ignore_error=True
        )
        print("[OK] Firestore criado.")

def create_service_account(project_id):
    print("\n[8/8] Criando Service Account...")
    sa_email = f"{SA_NAME}@{project_id}.iam.gserviceaccount.com"

    existing = run_output(
        f"gcloud iam service-accounts list "
        f"--filter=email:{sa_email} "
        f"--format=value(email) "
        f"--project={project_id}"
    )

    if sa_email in existing:
        print("[OK] Service Account ja existe.")
    else:
        run(
            f"gcloud iam service-accounts create {SA_NAME} "
            f"--display-name=Catalogo-SA "
            f"--project={project_id}"
        )
        print("[OK] Service Account criada.")

    roles = [
        "roles/run.admin",
        "roles/artifactregistry.writer",
        "roles/secretmanager.secretAccessor",
        "roles/iam.serviceAccountUser",
        "roles/datastore.user",
        "roles/firebase.admin",
        "roles/logging.logWriter",
    ]

    print("  Aplicando permissoes...")
    for role in roles:
        run(
            f"gcloud projects add-iam-policy-binding {project_id} "
            f"--member=serviceAccount:{sa_email} "
            f"--role={role}",
            capture=True,
            ignore_error=True
        )
    print("[OK] Permissoes aplicadas.")

    if os.path.exists(SA_KEY_FILE):
        print(f"[OK] Chave {SA_KEY_FILE} ja existe.")
    else:
        run(
            f"gcloud iam service-accounts keys create {SA_KEY_FILE} "
            f"--iam-account={sa_email} "
            f"--project={project_id}"
        )
        print(f"[OK] Chave salva em: {SA_KEY_FILE}")

    return sa_email

def save_summary(project_id, sa_email):
    summary = {
        "project_id": project_id,
        "region": REGION,
        "service_account": sa_email,
        "sa_key_file": SA_KEY_FILE,
        "artifact_registry": f"{REGION}-docker.pkg.dev/{project_id}/{REGISTRY_NAME}",
        "cloud_run_service": SERVICE_NAME,
        "proximos_passos": [
            f"1. Acesse https://console.firebase.google.com e vincule o projeto {project_id}",
            "2. Ative Firebase Authentication com e-mail e senha",
            "3. Baixe o serviceAccountKey.json do Firebase Console",
            f"4. Rode: gcloud secrets create firebase-credentials --data-file=serviceAccountKey.json --project={project_id}",
            "5. Copie o conteudo de sa-key.json como secret GCP_SA_KEY no GitHub",
            f"6. Adicione GCP_PROJECT_ID={project_id} nos secrets do GitHub",
            "7. Faca push para a branch main e o CI/CD assume"
        ]
    }

    with open("gcp_setup_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("  SETUP CONCLUIDO COM SUCESSO")
    print("=" * 60)
    print(f"\n  Project ID       : {project_id}")
    print(f"  Regiao           : {REGION}")
    print(f"  Service Account  : {sa_email}")
    print(f"  Artifact Registry: {REGION}-docker.pkg.dev/{project_id}/{REGISTRY_NAME}")
    print(f"  Chave SA         : {SA_KEY_FILE}")
    print(f"\n  Resumo salvo em  : gcp_setup_summary.json")
    print("\nPROXIMOS PASSOS:")
    for step in summary["proximos_passos"]:
        print(f"  {step}")
    print("=" * 60)

def main():
    print("=" * 60)
    print("  SETUP GCP - CATALOGO INTELIGENTE")
    print("  Arquiteto de Software em Nuvem")
    print("=" * 60)
    print(f"\n  gcloud path: {GCLOUD_PATH}")

    check_gcloud()
    login()
    project_id = create_project()
    set_default_project(project_id)
    enable_services(project_id)
    create_artifact_registry(project_id)
    create_firestore(project_id)
    sa_email = create_service_account(project_id)
    save_summary(project_id, sa_email)

if __name__ == "__main__":
    main()