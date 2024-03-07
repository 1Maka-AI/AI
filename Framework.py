# -*- coding: utf-8 -*-
import queue
import threading
import time
import uuid
from json import dumps, loads
from openai import OpenAI


app = Flask(__name__)


# Object represents each questionnaire input by a user
class Questionnaire:
    def __init__(self, user_id:int, answer:list, interest_mark:int, ability_mark:int):
        self.user = user_id
        self.answer = answer
        self.interest_mark = interest_mark
        self.ability_mark = ability_mark

# Object represents each curriculum
class Curriculum:
    def __init__(self, curr_id:int, content = 'url', content_type = 'text'):
        self.learning_group = []
        self.content = content
        self.content_typr = content_type
        self.pre = []
        
        
# Processing questionnaire and save information into database
class QuestionProcess:
    def __init__(self, model, learning_group_db, interest_db):
        self.model = model
        self.lg_db = learning_group_db
        self.in_db = interest_db
        self.meta_queue = queue.Queue()
        self.ability_queue = queue.Queue()
        self.producer_thread = threading.Thread(target=self.producer)
        self.consumer_thread = threading.Thread(target=self.consumer)
        self.producer_thread.start()
        self.consumer_thread.start()

    def stop_processing(self):
        self.producer_thread.join()
        self.consumer_thread.join()
        
    def process_wrapper(self, questionnaire):
        self.producer(questionnaire)
        self.consumer()
        
    def producer(self,questionnaire):
        while True:
            try:
                user = questionnaire.user
                answer = questionnaire.answer
                interests = answer[:questionnaire.interest_mark]
                ability_data = answer[questionnaire.ability_mark:]
                self.meta_queue.put((user, interests))
                self.ability_queue.put((user, ability_data))
                break
            except:
                time.sleep(1)

    def consumer(self):
        while True:
            try:
                uid1, meta_data = self.meta_queue.get()
                uid2, ability_data = self.ability_queue.get()
            except:
                time.sleep(1)
            assert uid1 == uid2
            self.user_id = uid1
            self.X = meta_data + ability_data
            self.learning_group = self.model.predict(self.X)
            self.writeToDb(self, self.lg_db, self.in_db)
            self.queue.task_done()

            
    def writeToDb(self,lg_db, in_db):
        lg_db.put({self.user_id:self.learning_group})
        in_db.put({self.user_id:self.interests})

# Processing each curriculum and save information into database
class CurriculumProcess:
    def __init__(self, interest_pool  = [], txt_model_name = 'gpt-3.5-turbo', pic_model_name = 'tall-e'):
        self.txt_model_name = txt_model_name
        self.pic_model_name = pic_model_name
        self.interest_pool = interest_pool
    
    def assign(self, curriculum, rules):
        self.curr_id = uuid.uuid4()
        self.content = curriculum.content
        self.curriculum_id = curriculum.curr_id
        self.content_type = curriculum.content_type
        if curriculum.learning_group:
            self.lg = curriculum.learning_group
        else:
            self.lg = rules[curriculum]
        
    def contentPersonalization(self, interest, content):
        client = OpenAI()

        message = [{
                        "role": "user",
                        "content": f"rewrite the following content with example or scenario under {interest}: {content}"
                    }]
        completion = client.chat.completions.create(
        model=self.txt_model_name,
        messages=message,
        )
        pcontent = completion.choices[0].message
        return pcontent
    
    def interfacePersonalization(self, interest):
        pass
    
    def process(self, content, per_db, meta_db):
        for id, interest in enumerate(self.interest_pool):
            pcontent = self.contentPersonalization(interest, content)
            pcontent_id = uuid.uuid4()
            meta_db.put({(id, self.lg):pcontent_id})
            per_db.put({pcontent_id:pcontent})
            
