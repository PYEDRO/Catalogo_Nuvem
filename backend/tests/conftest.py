"""
conftest.py — carregado pelo pytest ANTES de qualquer test file.
Mocka o firebase_admin e google.cloud antes do app ser importado.
"""
import sys
from unittest.mock import MagicMock

# ── Mock completo do Firebase Admin ──────────────────────────────────────────
firebase_app_mock = MagicMock()
firebase_app_mock._apps = {"[DEFAULT]": MagicMock()}

firebase_admin_mock = MagicMock()
firebase_admin_mock._apps = {"[DEFAULT]": MagicMock()}
firebase_admin_mock.initialize_app = MagicMock(return_value=MagicMock())

firestore_mock = MagicMock()
firestore_client_mock = MagicMock()
firestore_mock.client = MagicMock(return_value=firestore_client_mock)

auth_mock = MagicMock()
auth_mock.verify_id_token = MagicMock(return_value={
    "uid": "test-uid",
    "email": "admin@test.com",
    "role": "admin"
})

storage_mock = MagicMock()
credentials_mock = MagicMock()

# ── Injeta os mocks no sys.modules ───────────────────────────────────────────
sys.modules["firebase_admin"] = firebase_admin_mock
sys.modules["firebase_admin.credentials"] = credentials_mock
sys.modules["firebase_admin.auth"] = auth_mock
sys.modules["firebase_admin.firestore"] = firestore_mock
sys.modules["firebase_admin.storage"] = storage_mock
sys.modules["firebase_admin._apps"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["google.auth.credentials"] = MagicMock()
