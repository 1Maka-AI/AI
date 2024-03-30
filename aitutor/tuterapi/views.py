from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Assuming 'openai_api_key' is set in your environment or Django settings
openai_api_key = 'your_openai_api_key_here'

model = ChatOpenAI(openai_api_key=openai_api_key)
chat_history = []

template = """You are a virtual tutor, your audience is a teenager new to coding, whose name is Alex. Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Please talk to Alex like you are his/her best friend in an encouraging tone.
{context}
"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)
rag_chain = (
    qa_prompt
    | model
    | StrOutputParser()
)

@csrf_exempt
@require_http_methods(["POST"])
def answer_question(request):
    question = request.POST.get('question')
    doc_path = request.POST.get('doc_path')

    if not question or not doc_path:
        return JsonResponse({'error': 'Missing question or doc_path'}, status=400)

    loader = UnstructuredMarkdownLoader(doc_path)
    data = loader.load()
    context = data[0].page_content if data else ""

    answer = rag_chain.invoke({"question": question, "chat_history": chat_history, "context": context})

    if len(chat_history) >= 5:
        chat_history.pop(0)
    chat_history.append(HumanMessage(content=question, response=answer))

    return JsonResponse({'answer': answer})
