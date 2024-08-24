from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
__import__('pysqlite3')
import sys
import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
    setattr(collections, "MutableSequence", collections.abc.MutableSequence)


sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceHub,Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pdfplumber

def load_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def split_text(text):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

def setup_chain(documents):
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    vector_store = Chroma.from_documents(documents, embeddings)
    llm = Ollama(model="llama2-uncensored", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
    return qa

path = "../assets/drylab.pdf"
text = load_pdf(path)
documents = [Document(page_content=doc) for doc in split_text(text)]
qa = setup_chain(documents)
while True:
    question = input("Ask a question: ")
    if question.lower() == "exit":
        break
    answer = qa.invoke(question)
    print(answer)