from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from openai import OpenAI

class AiTutor:
    def __init__(self, model_name = 'gpt-3.5-turbo', role = 'Tutor', objective = None):
        '''
        Args:
            model_name: default to be 'gpt-3.5-turbo', can be finetuned model as well
            role：default to be 'Tutor', can be other roles like 'learning company'
            objective: defualt to be None which means the model will decide the objective, 
                can be 'summarization', 'debug' and 'question answering'.
        '''
        self.model_name = model_name
        self.role = role
        self.objective = objective
        self.client = OpenAI(api_key = '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')
        
        
    def ask(self, question, content = ''):
        message = self._message_generator(content, question) 
        completion = self.client.chat.completions.create(
        model=self.model_name,
        messages=message,
        )
        return completion.choices[0].message
    
    def _message_generator(self, content, question):
        msg = []
        if self.objective and content:
            msg = [{
                        "role": "system",
                        "content": f"You are a {self.role}. Your objective is {self.objective}. You are currently teaching {content}"
                    }]
        elif content:
            msg = [{
                        "role": "system",
                        "content": f"You are a {self.role}. You are currently teaching {content}"
                    }]
        msg.append({
                        "role": "user",
                        "content": f"{question}"
                    })
        return msg


aitutor = AiTutor()

@csrf_exempt
def ask_api(request):
    if request.method == 'POST':
        try:
            request_data = request.POST
            content = request_data.get('topic')
            question = request_data.get('question')
            if question is None:
                return JsonResponse({"error": "Missing arguments"}, status=400)
            result = aitutor.ask(content, question) 
            return JsonResponse(result, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)