import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Initialize the tokenizer from Hugging Face Transformers library
tokenizer = T5Tokenizer.from_pretrained('t5-small')

# Load the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = T5ForConditionalGeneration.from_pretrained('cssupport/t5-small-awesome-text-to-sql')
model = model.to(device)
model.eval()

def generate_sql(input_prompt):
    # Tokenize the input prompt
    inputs = tokenizer(input_prompt, padding=True, truncation=True, return_tensors="pt").to(device)
    
    # Forward pass
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512)
    
    # Decode the output IDs to a string (SQL query in this case)
    generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return generated_sql


schema = """
    CREATE TABLE `pilot` (
  `Pilot_Id` int(11) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Age` int(11) NOT NULL,
  PRIMARY KEY (`Pilot_Id`)
);

CREATE TABLE `aircraft` (
  "Aircraft_ID" int(11) NOT NULL,
  "Aircraft" varchar(50) NOT NULL,
  "Description" varchar(50) NOT NULL,
  "Max_Gross_Weight" varchar(50) NOT NULL,
  "Total_disk_area" varchar(50) NOT NULL,
  "Max_disk_Loading" varchar(50) NOT NULL,
  PRIMARY KEY (`Aircraft_ID`)
);


CREATE TABLE `match` (
"Round" real,
"Location" text,
"Country" text,
"Date" text,
"Fastest_Qualifying" text,
"Winning_Pilot" text,
"Winning_Aircraft" text,
PRIMARY KEY ("Round"),
FOREIGN KEY (`Winning_Aircraft`) REFERENCES `aircraft`(`Aircraft_ID`),
FOREIGN KEY (`Winning_Pilot`) REFERENCES `pilot`(`Pilot_Id`)
);

CREATE TABLE `airport` (
"Airport_ID" int,
"Airport_Name" text,
"Total_Passengers" real,
"%_Change_2007" text,
"International_Passengers" real,
"Domestic_Passengers" real,
"Transit_Passengers" real,
"Aircraft_Movements" real,
"Freight_Metric_Tonnes" real,
PRIMARY KEY ("Airport_ID")
);

CREATE TABLE `airport_aircraft` (
"ID" int,
"Airport_ID" int,
"Aircraft_ID" int,
PRIMARY KEY ("Airport_ID","Aircraft_ID"),
FOREIGN KEY ("Airport_ID") REFERENCES `airport`(`Airport_ID`),
FOREIGN KEY ("Aircraft_ID") REFERENCES `aircraft`(`Aircraft_ID`)
);

"""
# Test the function
#input_prompt = "tables:\n" + "CREATE TABLE Catalogs (date_of_latest_revision VARCHAR)" + "\n" +"query for: Find the dates on which more than one revisions were made."
#input_prompt = "tables:\n" + "CREATE TABLE table_22767 ( \"Year\" real, \"World\" real, \"Asia\" text, \"Africa\" text, \"Europe\" text, \"Latin America/Caribbean\" text, \"Northern America\" text, \"Oceania\" text )" + "\n" +"query for:what will the population of Asia be when Latin America/Caribbean is 783 (7.5%)?."
#input_prompt = "tables:\n" + "CREATE TABLE procedures ( subject_id text, hadm_id text, icd9_code text, short_title text, long_title text ) CREATE TABLE diagnoses ( subject_id text, hadm_id text, icd9_code text, short_title text, long_title text ) CREATE TABLE lab ( subject_id text, hadm_id text, itemid text, charttime text, flag text, value_unit text, label text, fluid text ) CREATE TABLE demographic ( subject_id text, hadm_id text, name text, marital_status text, age text, dob text, gender text, language text, religion text, admission_type text, days_stay text, insurance text, ethnicity text, expire_flag text, admission_location text, discharge_location text, diagnosis text, dod text, dob_year text, dod_year text, admittime text, dischtime text, admityear text ) CREATE TABLE prescriptions ( subject_id text, hadm_id text, icustay_id text, drug_type text, drug text, formulary_drug_cd text, route text, drug_dose text )" + "\n" +"query for:" + "what is the total number of patients who were diagnosed with icd9 code 2254?"
input_prompt = "tables:\n" + schema + "\n" + "query for:" + "who all are the pilots?"

generated_sql = generate_sql(input_prompt)

print(f"The generated SQL query is: {generated_sql}")
#OUTPUT: The generated SQL query is: SELECT student_id FROM students WHERE NOT student_id IN (SELECT student_id FROM student_course_attendance)
