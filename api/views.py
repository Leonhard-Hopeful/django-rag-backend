from django.shortcuts import render
# Create your views here.
import os
import logging
import json
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from langchain_core.messages import AIMessage, HumanMessage

from .langchain_logic import get_vectorstore_from_file, get_conversational_rag_chain

load_dotenv()

class ChatView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            return Response({"error": "Google API Key not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 1. Get data from the request
        pdf_file = request.FILES.get('pdf_file')
        chat_history_json = request.data.get('chat_history', '[]')
        user_query = request.data.get('user_query', '')

        if not pdf_file or not user_query:
            return Response({"error": "Missing pdf_file or user_query"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Reconstruct chat history from JSON
        chat_history_data = json.loads(chat_history_json)
        chat_history = []
        for msg in chat_history_data:
            if msg['type'] == 'ai':
                chat_history.append(AIMessage(content=msg['content']))
            else:
                chat_history.append(HumanMessage(content=msg['content']))

        # 3. Run the RAG pipeline
        try:
            vector_store = get_vectorstore_from_file(pdf_file, google_api_key)
            if vector_store is None:
                return Response({"error": "Failed to process PDF file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            rag_chain = get_conversational_rag_chain(vector_store, google_api_key)
            
            # Add user's new message to history for the chain
            chat_history.append(HumanMessage(content=user_query))

            response = rag_chain.invoke({
                "chat_history": chat_history,
                "input": user_query
            })

            return Response({"answer": response['answer']}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Failed to process PDF and create vector store: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
