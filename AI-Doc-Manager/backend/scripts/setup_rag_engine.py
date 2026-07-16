"""One-time setup script for Vertex AI RAG Engine in Serverless mode.

Creates the RAG corpus and optionally enables serverless mode at the project
level.  Idempotent — safe to run multiple times.

## Prerequisites

Before running this script:
1. Enable the required APIs:
   - ``aiplatform.googleapis.com``
   - ``vectorsearch.googleapis.com``
   - (optional, for layout parser) ``documentai.googleapis.com``
2. Authenticate: ``gcloud auth application-default login``
3. For serverless mode, set your project's default location to us-central1.

## Usage

    # Enable serverless mode AND create the corpus:
    python scripts/setup_rag_engine.py --project my-project --enable-serverless

    # Create corpus only (serverless already enabled):
    python scripts/setup_rag_engine.py --project my-project

    # Custom display name and location:
    python scripts/setup_rag_engine.py --project my-project \\
        --display-name "my-rag-corpus" --location us-central1

## Output

Prints the ``RAG_CORPUS_RESOURCE`` value to set in your ``.env`` file.
"""

from __future__ import annotations

import argparse
import logging
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up Vertex AI RAG Engine corpus (serverless mode)."
    )
    parser.add_argument(
        "--project", required=True, help="GCP project ID"
    )
    parser.add_argument(
        "--location",
        default="us-central1",
        help="RAG Engine location (serverless is us-central1 only)",
    )
    parser.add_argument(
        "--display-name",
        default="dms-backend",
        help="Corpus display name",
    )
    parser.add_argument(
        "--enable-serverless",
        action="store_true",
        help="Enable serverless mode at the project level (one-time)",
    )
    parser.add_argument(
        "--embedding-model",
        default="text-embedding-005",
        help="Embedding model for the corpus",
    )
    parser.add_argument(
        "--skip-corpus",
        action="store_true",
        help="Only enable serverless mode; skip corpus creation",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    import vertexai
    from vertexai.preview import rag

    vertexai.init(project=args.project, location=args.location)
    logger.info("Vertex AI SDK initialised (project=%s, location=%s)", args.project, args.location)

    # -- Enable serverless mode (project-level, one-time) --------------------
    if args.enable_serverless:
        config_name = f"projects/{args.project}/locations/{args.location}/ragEngineConfig"
        logger.info("Enabling serverless mode via %s ...", config_name)
        try:
            rag.update_rag_engine_config(
                rag.RagEngineConfig(
                    name=config_name,
                    rag_managed_db_config=rag.RagManagedDbConfig(
                        tier=rag.Serverless()
                    ),
                )
            )
            logger.info("Serverless mode enabled successfully.")
        except Exception as exc:
            logger.error("Failed to enable serverless mode: %s", exc)
            logger.error(
                "Ensure the project is allowlisted for serverless mode "
                "and the location is us-central1."
            )
            sys.exit(1)

    # -- Create corpus -------------------------------------------------------
    if args.skip_corpus:
        logger.info("Skipping corpus creation (--skip-corpus).")
        return

    display_name = args.display_name
    logger.info(
        "Creating RAG corpus '%s' with embedding model %s ...",
        display_name,
        args.embedding_model,
    )
    try:
        # NOTE: within backend_config, the preview SDK expects the legacy
        # EmbeddingModelConfig shape (publisher_model), not
        # RagEmbeddingModelConfig(vertex_prediction_endpoint=...).
        corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                vector_db=rag.RagManagedVertexVectorSearch(),
                rag_embedding_model_config=rag.EmbeddingModelConfig(
                    publisher_model=f"publishers/google/models/{args.embedding_model}"
                ),
            ),
        )
    except Exception as exc:
        logger.error("Failed to create corpus: %s", exc)
        sys.exit(1)

    corpus_name = corpus.name
    logger.info("Corpus created: %s", corpus_name)

    print()
    print("─── Add this to your .env file ───")
    print(f"RAG_CORPUS_RESOURCE={corpus_name}")
    print()
    print("─── Post-setup checklist ───")
    print("☐ Document AI API enabled?  (documentai.googleapis.com)")
    print("☐ Vector Search API enabled? (vectorsearch.googleapis.com)")
    print("☐ If using the layout parser:")
    print("   ☐ Create a LAYOUT_PARSER_PROCESSOR in the Cloud Console")
    print("   ☐ Set RAG_LAYOUT_PARSER_ENABLED=true")
    print("   ☐ Set RAG_LAYOUT_PARSER_PROCESSOR_NAME=projects/.../processors/...")


if __name__ == "__main__":
    main()
