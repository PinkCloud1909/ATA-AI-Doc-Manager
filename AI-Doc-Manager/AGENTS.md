01/07/2026
You are working on the repository ATA-AI-Doc-Manager.

This project is a document management and RAG Q&A system intended for production deployment on Google Cloud services, not only local Docker Compose.

Target Google Cloud architecture:
- Backend: Cloud Run FastAPI service
- Frontend: Cloud Run or Firebase Hosting
- Database: Cloud SQL PostgreSQL
- Object storage: Cloud Storage
- Async processing: Cloud Tasks + Cloud Run worker or Cloud Run Jobs
- Embeddings and generation: Vertex AI Gemini
- Vector database: Vertex AI Vector Search
- Secrets: Secret Manager
- Build/deploy: Cloud Build + Artifact Registry

Important constraints:
- Inspect the existing repo before changing code.
- Preserve the existing architecture where reasonable.
- Keep local development support with Docker Compose.
- Do not hard-code project IDs, secrets, passwords, bucket names, or service URLs.
- Do not commit real credentials.
- Make changes narrowly scoped to the requested goal.
- Add or update tests where practical.
- Update documentation when config, deployment, or architecture changes.
- Before coding, summarize the files you expect to modify and why.
- After coding, summarize what changed, how to test it, and any remaining risks.