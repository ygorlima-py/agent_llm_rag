import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from langchain_core.documents import Document

from chatapp.services.rag_pipeline import RAGPipeline


@patch("chatapp.services.rag_pipeline.AIModels")
@patch("chatapp.services.rag_pipeline.PGAsyncEngine")
@patch("chatapp.services.rag_pipeline.PGVectorLexicalRetriever")
@patch("chatapp.services.rag_pipeline.PGVectorMMRRetriever")
def test_rag_pipeline_init(mock_mmr, mock_lexical, mock_pg_engine, mock_models):
    mock_models_instance = MagicMock()
    mock_models.return_value = mock_models_instance
    mock_models_instance.embedding_model.return_value = MagicMock()
    mock_models_instance.llm_model.return_value = MagicMock()

    mock_pg_engine.return_value = MagicMock()

    pipeline = RAGPipeline()

    assert pipeline.embedding is not None
    assert pipeline.llm is not None
    assert pipeline.pg_async_engine is not None

    mock_pg_engine.assert_called_once()
    mock_lexical.assert_called_once()
    mock_mmr.assert_called_once()


@pytest.mark.asyncio
@patch("chatapp.services.rag_pipeline.AIModels")
@patch("chatapp.services.rag_pipeline.PGAsyncEngine")
@patch("chatapp.services.rag_pipeline.Reranker")
@patch("chatapp.services.rag_pipeline.PGVectorMMRRetriever")
@patch("chatapp.services.rag_pipeline.PGVectorLexicalRetriever")
async def test_get_documents(mock_lexical, mock_mmr, mock_reranker, mock_pg_engine, mock_models):
    mock_models_instance = MagicMock()
    mock_models.return_value = mock_models_instance
    mock_models_instance.embedding_model.return_value = MagicMock()
    mock_models_instance.llm_model.return_value = MagicMock()

    mock_pg_engine.return_value = MagicMock()

    mock_lexical_instance = MagicMock()
    mock_lexical.return_value = mock_lexical_instance
    mock_lexical_instance.lexical_docs = AsyncMock(return_value=[MagicMock(spec=Document)])

    mock_mmr_instance = MagicMock()
    mock_mmr.return_value = mock_mmr_instance
    mock_mmr_instance.mmr_docs = AsyncMock(return_value=[MagicMock(spec=Document)])

    mock_reranker_instance = MagicMock()
    mock_reranker.return_value = mock_reranker_instance
    mock_reranker_instance.rerank = MagicMock(return_value=[MagicMock(spec=Document)])

    pipeline = RAGPipeline()

    docs = await pipeline._get_documents("test question")

    assert len(docs) == 1
    mock_lexical_instance.lexical_docs.assert_called_once_with("test question")
    mock_mmr_instance.mmr_docs.assert_called_once_with("test question")
    mock_reranker_instance.rerank.assert_called_once()


@pytest.mark.asyncio
@patch("chatapp.services.rag_pipeline.AIModels")
@patch("chatapp.services.rag_pipeline.PGAsyncEngine")
@patch.object(RAGPipeline, "_get_documents", new_callable=AsyncMock)
async def test_build_context(mock_get_docs, mock_pg_engine, mock_models):
    mock_models_instance = MagicMock()
    mock_models.return_value = mock_models_instance
    mock_models_instance.embedding_model.return_value = MagicMock()
    mock_models_instance.llm_model.return_value = MagicMock()

    mock_pg_engine.return_value = MagicMock()

    mock_doc = MagicMock(spec=Document)
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"documents": {"bula": "http://example.com"}}

    mock_get_docs.return_value = [mock_doc]

    pipeline = RAGPipeline()
    context = await pipeline._build_context("Test question", max_chars=1000)

    assert "Url da Bula: http://example.com" in context
    assert "Conteudo: Test content" in context


@pytest.mark.asyncio
@patch("chatapp.services.rag_pipeline.AIModels")
@patch("chatapp.services.rag_pipeline.PGAsyncEngine")
@patch.object(RAGPipeline, "_build_context", new_callable=AsyncMock)
@patch("chatapp.services.rag_pipeline.PROMPT")
async def test_answer_question(mock_prompt, mock_build_context, mock_pg_engine, mock_models):
    mock_models_instance = MagicMock()
    mock_models.return_value = mock_models_instance

    mock_llm = MagicMock()
    mock_models_instance.embedding_model.return_value = MagicMock()
    mock_models_instance.llm_model.return_value = mock_llm

    mock_pg_engine.return_value = MagicMock()
    mock_build_context.return_value = "Mocked context"

    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=MagicMock(content="Mocked answer"))

    mock_prompt.__or__ = MagicMock(return_value=mock_chain)

    pipeline = RAGPipeline()
    response = await pipeline.answer_question("test question")

    assert response.content == "Mocked answer"
    mock_chain.ainvoke.assert_called_once_with(
        {"input": "test question", "context": "Mocked context"}
    )


    
    