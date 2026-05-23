"""
conftest.py — carregado pelo pytest ANTES de qualquer test file.
Mocka o firebase_admin e google.cloud antes do app ser importado.
"""
import sys
from unittest.mock import MagicMock

# ── Mock completo do Firebase Admin ──────────────────────────────────────────
firebase_admin_mock = MagicMock()
firebase_admin_mock._apps = {"[DEFAULT]": MagicMock()}
firebase_admin_mock.initialize_app = MagicMock(return_value=MagicMock())

# ── Mock do resultado de COUNT aggregation ────────────────────────────────────
# firestore_service.py faz: count_result[0][0].value — precisa retornar int
aggregation_result = MagicMock()
aggregation_result.value = 0
count_response = [[aggregation_result]]

# ── Mock de coleção Firestore (chainável) ─────────────────────────────────────
col_mock = MagicMock()
col_mock.count.return_value.get.return_value = count_response
col_mock.where.return_value = col_mock          # .where().where()... chainável
col_mock.offset.return_value = col_mock         # .offset().limit().stream()
col_mock.limit.return_value = col_mock
col_mock.stream.return_value = iter([])         # nenhum documento

firestore_client_mock = MagicMock()
firestore_client_mock.collection.return_value = col_mock

firestore_mock = MagicMock()
firestore_mock.client = MagicMock(return_value=firestore_client_mock)

auth_mock = MagicMock()
auth_mock.verify_id_token = MagicMock(return_value={
    "uid": "test-uid",
    "email": "admin@test.com",
    "role": "admin",
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
