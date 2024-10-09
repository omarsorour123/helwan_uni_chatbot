from models import ChunkStore


def store():
    directory_path = "data"

    chunk_store = ChunkStore(directory_path=directory_path)
    chunk_store.load_data(extension=".json")
    chunk_store.prepare_documents()

    retriever = chunk_store.vector_store()
    return retriever


if __name__ == "__main__":
    store()
