from llm_scripts.dialogue import DialogueModel
import pandas as pd


class SalesBotHandler:
    def __init__(self,
                #  bert_model_name='cointegrated/rubert-tiny', 
                #  llm_model_name='TheBloke/CodeLlama-7B-Instruct-GGUF',
                #  llm_model_path='codellama-7b-instruct.Q4_0.gguf',
                #  reviews_path = "/home/zhigul/llm/cleaned_coffee.csv"):
            ):
        self.llm_model = DialogueModel()
        self.llm_model.init_model()
    
    def load_reviews(self, reviews_path):
        return pd.read_csv(reviews_path)
    
    def query(self, sql, engine):
        print(f'"SQL QUERY:\n {sql}"')
        return pd.read_sql(sql, con=engine)
    
    def create_and_run_sql_query(self, customer_input):
        sql_res = self.llm_model.generate_text2sql_response(customer_input)
        return self.query(sql_res, self.llm_model.engine)
    
    def process_customer_input(self, customer_input):
        """
        Метод для ведения диалога с клиентом с использованием LLM Model.
        """
        # relevant_reviews = self.bert_embedder.retrieve_reviews(customer_input, self.reviews)
        is_text2sql = self.llm_model.classify_rag_or_text2sql(customer_input)
        if 'да' in is_text2sql.lower():
            print('ЭТО TEXT2SQL')
            res = self.create_and_run_sql_query(customer_input)
        else:
            print('ЭТО ПРОСТО RAG')
            res = self.llm_model.generate_rag_response(customer_input, relevant_reviews)
        
        return res

    def generate_answer(self, msg):
        return self.llm_model.generate_answer(msg)

    def generate_first_message(self):
        """
        Метод для генерации первого письма с использованием LLM Model.
        """
        return self.llm_model.generate_first_message()