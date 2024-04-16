from openai import OpenAI
openai_client = OpenAI()

import datetime
import time
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

import pprint, json

query_A = """
Imagine you are participating in a game called 'Guess 2/3 of the Average.' The game involves guessing a number between 0 and 100. The winner is the one whose guess is closest to 2/3 of the average guess of all participants. How would you approach your guess strategically to maximize your chances of winning? Please provide your guess and explain your reasoning, in json format with "reasoning" and "guess" as the keys. Take a deep breath and think step-by-step.
"""

## against AI
query_B = """
Imagine you are participating in a game called 'Guess 2/3 of the Average.' The game involves guessing a number between 0 and 100. The winner is the one whose guess is closest to 2/3 of the average guess of all participants. Considering you're playing against advanced AI models, how would you approach your guess strategically to maximize your chances of winning? Please provide your guess and explain your reasoning, in json format with "reasoning" and "guess" as the keys. Take a deep breath and think step-by-step.
"""

import gspread

from oauth2client.service_account import ServiceAccountCredentials

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]
json_file_name = 'JSON_FILE_NAME.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1YaopOcD6i_fEiLmrAEsW9V0iWvH9ahPT_txrQTHjVOc'

doc = gc.open_by_url(spreadsheet_url)

worksheet_name_A = "GuessTheAverage_by_ai_A"
worksheet_name_B = "GuessTheAverage_by_ai_B"

worksheet_A = doc.worksheet(worksheet_name_A)
worksheet_B = doc.worksheet(worksheet_name_B)

### GPT-4 models
def chatgpt_guesses(model_name, query, worksheet):

    resp = openai_client.chat.completions.create(
      model=model_name,
      messages=[
        {"role": "user", "content": query},
      ]
    )
    print(resp)
    
    attempts = 0
    max_retry = 3
    while attempts < max_retry:
        try:
           
            r = resp.choices[0].message.content.replace('```json','').replace('```','').replace("\n"," ")
            int_bracket_close_position = r.rfind('}')
            r = json.loads(r[:int_bracket_close_position + 1])
            guess = r["guess"]
            reasoning = str(r["reasoning"])
            # reasoning = str(r["reasoning"].replace("\n\n",""))

            row = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resp.model, guess, reasoning, str(resp.choices[0].message)]
            len_cols = len(worksheet.col_values(1))
            print(len_cols)
            result_insert = worksheet.insert_row(row, len_cols+1, value_input_option='USER_ENTERED')
            print(result_insert)
            break
        except:
            print("seems like the connection is going through some issues... : trial no : ", attempts)
            attempts = attempts + 1

for i in range(500):
    print(f'---\nTrial no: {i+1}')
    chatgpt_guesses("gpt-4-turbo-2024-04-09", query_A, worksheet_A)
    chatgpt_guesses("gpt-4-turbo-2024-04-09", query_B, worksheet_B)
    time.sleep(1)
