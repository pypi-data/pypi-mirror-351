import time
import asyncio
from pathlib import Path

from graphrag.config.load_config import load_config
from graphrag.logger.rich_progress import RichProgressLogger
from graphrag.api.index import build_index

def index_graphrag(directory, GRAPHRAG_PATH=None):
    async def run_indexing(directory):
        start_time = time.time()

        conf = load_config(root_dir=Path(directory))
        index_result = await build_index(config=conf, progress_logger=RichProgressLogger("GraphRAG Indexer"))

        try:
            for workflow_result in index_result:
                status = f"error\n{workflow_result.errors}" if workflow_result.errors else "success"
                print(f"Workflow Name: {workflow_result.workflow}\tStatus: {status}")
        except Exception as e:
            print(f"Error processing results: {e}")
            print("Trying indexing using CLI")

            import subprocess
            status = subprocess([GRAPHRAG_PATH, "index", "--root", directory])
            #print(status.stdout)
            if status.stderr:
                print(f"Error: {status.stderr}")

        end_time = time.time()
        print(f"Indexing completed in {end_time - start_time} seconds")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_indexing(directory))
    loop.close()