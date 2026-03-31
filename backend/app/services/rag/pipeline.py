class RAGPipeline:
    def __init__(self):
        pass
    def process_document(self, text: str, metadata: dict = None):
        words = text.split()
        chunk_size = 600
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks
    def retrieve_context(self, query: str, k: int = 5):
        return ""
