import os
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from django.conf import settings
from .vector_store import VectorStoreService

class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()

        self.llm = ChatOpenAI(
            model_name = "gpt-3.5-turbo",
            temperature = 0.7,
            api_key = settings.OPENAI_API_KEY
        )
    def generate_response(self, conversation_history, query):
        """
        Generate a response using the RAG pattern:
        1. Retrieve relevant documents
        2. Generate a response using the documents and conversation history
        """
        formatted_history = []
        for message in conversation_history:
            formatted_history.append({
                "role":message.role,
                "content": message.content
            })

        memory = ConversationBufferMemory(
            memory_key = "chat_history",
            output_key = "answer",
            return_messages=True
        )

        for message in formatted_history:
            if message["role"] == "user":
                memory.chat_memory.add_user_message(message["content"])
            else:
                memory.chat_memory.add_ai_message(message["content"])

        retriever = self.vector_store.vector_store.as_retriever(
            search_kwargs={"k": 3}
        )

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True
        )

        response = chain({"question": query})

        return {
            "answer" : response["answer"],
            "source_documents": response["source_documents"]
        }