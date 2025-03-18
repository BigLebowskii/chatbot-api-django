from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .document_processor import DocumentProcessor
from .models import Documents, Conversation, Message
from .services.rag_service import RAGService
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer
)
from .services.vector_store import VectorStoreService

# Create your views here.

def index(request):
    return render(request, 'chatbot/index.html')

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        document = serializer.save()
        vector_store = VectorStoreService()
        vector_store.add_documents(document)
    
    def perform_destroy(self, instance):
        vector_store = VectorStoreService()
        vector_store.delete_document(instance.id)
        instance.delete()
    
    @action(detail=False, methods=['post'], url_path='upload_file')
    def upload_file(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        title = request.data.get('title', file.name)
        chunk_size = int(request.data.get('chunk_size', 1000))
        chunk_overlap = int(request.data.get('chunk_overlap', 200))
        
        # Process file
        processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        content = processor.process_file(file)
        
        # Create document
        document = Documents.objects.create(
            title=title,
            content=content,
            file_type=file.content_type
        )
        
        # Split text and add to vector store
        vector_store = VectorStoreService()
        text_chunks = processor.split_text(content)
        
        # If we have chunks, add them to the vector store
        if text_chunks:
            vector_store.add_document_chunks(document.id, text_chunks)
        else:
            # Fallback to old method if no chunks (empty document)
            vector_store.add_documents(document)
        
        return Response({
            'id': document.id,
            'title': document.title,
            'chunks': len(text_chunks),
            'message': "File uploaded and processed successfully"
        }, status=status.HTTP_201_CREATED)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @action(detail = False, methods=['post'])
    def chat(self, request):

        conversation_id = request.data.get('conversation_id')
        user_message = request.data.get('message')

        if not conversation_id or not user_message:
            return Response(
                {"error": "Both conversation_id and messages are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status = status.HTTP_404_NOT_FOUND
            )

        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        conversation_history = Message.objects.filter(conversation = conversation).order_by('created_at')

        rag_service=RAGService()
        response_data = rag_service.generate_response(conversation_history=conversation_history, query=user_message)

        assistant_message = Message.objects.create(
            conversation = conversation,
            role = 'assistant',
            content = response_data["answer"]
        )



        return Response({
            "id": assistant_message.id,"content": assistant_message.content,"created_at": assistant_message.created_at})