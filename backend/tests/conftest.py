"""
conftest.py - carregado pelo pytest ANTES de qualquer test file.

Estrategia de mock:
1. asyncio.to_thread e substituido por execucao sincrona ANTES da importacao
   do firestore_service.py.
2. Firebase Admin SDK, Firestore e Storage sao completamente mockados via
   sys.modules. CRITICO: firebase_admin_mock.firestore deve apontar para
   firestore_mock explicitamente -- caso contrario `from firebase_admin import
   firestore` resolve o atributo auto-gerado do MagicMock pai, nao o nosso mock.
"""
import sys
import asyncio
from unittest.mock import MagicMock

# -- 1. Patch asyncio.to_thread -> execucao sincrona em testes ----------------
# DEVE rodar antes de qualquer import do app, pois firestore_service.py faz
# `from asyncio import to_thread` -- captura a referencia no momento do import.


async def _sync_to_thread(func, *args, **kwargs):
    """Substitui to_thread por execucao sincrona para testes unitarios."""
    return func(*args, **kwargs)

asyncio.to_thread = _sync_to_thread

# -- 2. Mock do resultado de COUNT aggregation ---------------------------------
aggregation_result = MagicMock()
aggregation_result.value = 0
count_response = [[aggregation_result]]

# -- 3. Mock de documento individual (exists=False -> get_by_id retorna None) --
doc_not_found = MagicMock()
doc_not_found.exists = False

# -- 4. Mock de colecao Firestore -- totalmente chainavel ----------------------
col_mock = MagicMock()
col_mock.count.return_value.get.return_value = count_response
col_mock.where.return_value = col_mock
col_mock.offset.return_value = col_mock
col_mock.limit.return_value = col_mock
col_mock.stream.return_value = []
col_mock.document.return_value.id = "mock-doc-id"
col_mock.document.return_value.get.return_value = doc_not_found

# -- 5. Firebase Admin mocks ---------------------------------------------------
firestore_client_mock = MagicMock()
firestore_client_mock.collection.return_value = col_mock

# firestore_mock.client() retorna firestore_client_mock
firestore_mock = MagicMock()
firestore_mock.client.return_value = firestore_client_mock

firebase_admin_mock = MagicMock()
firebase_admin_mock._apps = {"[DEFAULT]": MagicMock()}
firebase_admin_mock.initialize_app = MagicMock(return_value=MagicMock())

# CRITICO: `from firebase_admin import firestore` resolve firebase_admin_mock.firestore.
# Sem isto, o atributo auto-gerado do MagicMock e usado, quebrando toda a chain.
firebase_admin_mock.firestore = firestore_mock

auth_mock = MagicMock()
auth_mock.verify_id_token = MagicMock(return_value={
    "uid": "test-uid",
    "email": "admin@test.com",
    "role": "admin",
})

storage_mock = MagicMock()
credentials_mock = MagicMock()

# -- 6. Injeta mocks no sys.modules ANTES do app ser importado ----------------
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
