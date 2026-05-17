# Admission Data Ingestion

File `admission_sources.example.json` la danh sach nguon mau de tool tai du lieu tuyen sinh chinh thuc va luu raw document vao database.

Chay migration truoc:

```bash
docker exec -it ms_admission_service alembic upgrade head
```

Chay ingest trong container:

```bash
docker exec -it ms_admission_service python -m app.tools.ingest_admission_sources \
  --source-file data/admission_sources.example.json
```

Neu file JSON la danh sach source chuan hien tai, danh dau cac source cu khong con nam trong file la `obsolete`:

```bash
docker exec -it ms_admission_service python -m app.tools.ingest_admission_sources \
  --source-file data/admission_sources.example.json \
  --mark-missing-obsolete
```

Test nhanh 1 truong:

```bash
docker exec -it ms_admission_service python -m app.tools.ingest_admission_sources \
  --source-file data/admission_sources.example.json \
  --limit 1
```

Sau khi chay, kiem tra PostgreSQL:

```sql
SELECT code, name, province FROM admission.universities;
SELECT document_type, year, status, url FROM admission.admission_sources;
SELECT content_type, content_size, fetched_at FROM admission.admission_raw_documents;
```

Luu y: danh sach source mau chi la diem bat dau. Khi lam data that, moi dong nen dung URL chinh thuc cua truong va co `source_year`.

Validate sau moi lan ingest:

```bash
docker exec -it ms_admission_service python -m app.tools.validate_admission_sources \
  --source-file data/admission_sources.example.json
```

Tool validate se kiem tra:

- source co ton tai trong DB khong
- status co phai `fetched` khong
- raw document co du lon khong
- HTML/text da extract co chua cac `expected_keywords` trong file JSON khong

## Vector index / RAG retrieval

Sau khi ingest, tool mac dinh se tao vector chunks tu `content_text` va luu vao bang `admission.admission_document_chunks`.

Database dung extension `pgvector`, cot search chinh la `embedding_vector vector(768)`. Cot `embedding` dang JSONB van duoc giu lai de debug/compat.

Provider mac dinh la local hashing de dev khong can API key:

```env
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=local-hashing-v1
EMBEDDING_DIMENSION=768
```

Dung Gemini:

```env
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=768
GEMINI_API_KEY=...
```

`text-embedding-001` va `text-embedding-004` la ten model Gemini cu. Code se tu dong map cac model nay sang `gemini-embedding-001`, nhung nen cap nhat `.env` de tranh nham lan.

Dung OpenAI:

```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=768
OPENAI_API_KEY=...
```

Luu y: neu doi provider/model/dimension, can build lai vector index:

```bash
docker exec -it ms_admission_service python -m app.tools.build_admission_vector_index --rebuild
```

Neu chi muon tai raw document va bo qua vector index:

```bash
docker exec -it ms_admission_service python -m app.tools.ingest_admission_sources \
  --source-file data/admission_sources.example.json \
  --skip-vector-index
```

Build lai vector index tu cac raw document moi nhat:

```bash
docker exec -it ms_admission_service python -m app.tools.build_admission_vector_index --rebuild
```

Kiem tra tren Swagger/API:

- `GET /api/admission/rag/stats`: xem so chunks/documents da index
- `POST /api/admission/rag/index`: build/rebuild vector index
- `POST /api/admission/rag/search`: semantic search theo noi dung tuyen sinh
- `POST /api/admission/rag/chat`: chatbot hoi dap thong tin truong/nganh dua tren RAG context

Vi du body search:

```json
{
  "query": "nganh cong nghe thong tin o TP HCM",
  "top_k": 5,
  "province": "TP.HCM",
  "year": 2025
}
```

Vi du body chat:

```json
{
  "question": "O TP HCM co truong nao tuyen nganh cong nghe thong tin?",
  "top_k": 6,
  "province": "TP.HCM",
  "year": 2025,
  "use_llm": true
}
```

Response chat tra ve `answer` va `sources`; FE nen hien thi `sources[].source_url` de nguoi dung kiem tra thong tin goc.
