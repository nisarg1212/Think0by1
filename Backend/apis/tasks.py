import logging
from asgiref.sync import async_to_sync
from apis.engine.graph import OrchestrationGraph

logger = logging.getLogger(__name__)

def run_orchestration_task(question_id: int):
    """
    Background worker task to run the AI orchestration graph.
    This prevents the main HTTP thread from blocking.
    """
    logger.info(f"Starting background orchestration task for question_id: {question_id}")
    try:
        graph = OrchestrationGraph()
        # Since this runs in a synchronous worker thread, we use async_to_sync to run the graph
        async_to_sync(graph.run)(question_id)
        logger.info(f"Completed background orchestration task for question_id: {question_id}")
    except Exception as e:
        logger.error(f"Background orchestration task failed for question_id: {question_id} - Error: {e}")
        raise e
