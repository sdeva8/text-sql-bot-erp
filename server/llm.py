from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import re
from llm_schema import llm_schema_context
class Seq2SeqGenerator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Seq2SeqGenerator, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path='gaussalgo/T5-LM-Large-text2sql-spider'):
        if not self._initialized:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._initialized = True
    
    def extract_sql_query(self,input_string):
    # Regular expression pattern to match SQL queries
        sql_pattern = re.compile(r'\b(SELECT|INSERT|UPDATE)\b.*$', re.IGNORECASE)

        # Find the first match
        match = sql_pattern.search(input_string)

        # Extract the matched SQL query
        if match:
            return match.group()
        else:
            return None

    def generateSQL(self, question, schema):

        input_text = " ".join(["Question: ", question, "Schema:", schema])

        model_inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(**model_inputs, max_length=512)
        flat_outputs = outputs.view(-1).tolist()
        val = {}
        output_text = self.tokenizer.decode(flat_outputs, skip_special_tokens=True)
        val['llm_Sql'] = output_text
        ex = self.extract_sql_query(output_text)
        val['extract_Sql'] = ex
        return val


# Example usage:
if __name__ == "__main__":
    generator_instance1 = Seq2SeqGenerator()
    generator_instance2 = Seq2SeqGenerator()

    print(generator_instance1 is generator_instance2)  # Should print True

    question = "who all are the pilots?"
    schema = llm_schema_context
    eq = generator_instance1.extract_sql_query("  ,  * SELECT * FROM data where ID IN (SELECT NAME FROM people)")
    print(eq)
    sql_output = generator_instance1.generateSQL(question, schema)
    
