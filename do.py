import time
import pandas as pd
import google.generativeai as genai
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import sklearn as sk
import os
import subprocess
import sys
import re

data_set = 'imdb_movie_dataset.csv'
# data_set = 'gym_members_exercise_tracking.csv'
# data_set = 'score_updated.csv'
# data_set = 'score.csv'
# data_set = 'user_behavior_dataset.csv'


#=======================================    GEMINI SETUP ===========================================================================
genai.configure(api_key="AIzaSyCxGmyEE5jokRG6LKRKxwE0blo_N5XaORA")

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    # "top_k": 64,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[
    ]
)
#======================================================================================================================

def gen_code(data_snip):
    response1 = chat_session.send_message("Analyse the given data set "+data_set+" : "+data_snip)
    # response2 = chat_session.send_message("Generate a brief python code to dignose,preprocess , suitable analysis and visualisations for the data set "+data_set)
    # response3 = chat_session.send_message("add more analysis and visualizations and create a dashboard on Streamlit ")
    # response4 = chat_session.send_message("every time *generate the brief python code for the above descriptions").text
    response4 = chat_session.send_message("generate a python code to create a dashboard with all the possible visualization for the data set "+data_set+" on streamlit").text
    return response4

def trim(response):
    code = response[response.find("```python") + 9:]
    code = code[:code.find("```")]
    return code

def str_to_py(code_string, filename):
    with open(filename, 'w') as file:
        file.write(code_string)

def py_to_str(filename):
    with open(filename, 'r') as file:
        file_contents = file.read()
    return file_contents

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    print("\n MODULE : * "+package+" * IS BEING DOWNLOADED................ ")
    time.sleep(60)
def extract_error_info(traceback):
    # Extract the error type and missing key from the traceback
    error_type_match = re.search(r'(\w+Error):', traceback)
    missing_key_match = re.search(r"KeyError: '(.*?)'", traceback)
    line_number_match = re.search(r'File ".+?", line (\d+)', traceback)

    error_type = error_type_match.group(1) if error_type_match else "UnknownError"
    missing_key = missing_key_match.group(1) if missing_key_match else "UnknownKey"
    line_number = line_number_match.group(1) if line_number_match else "UnknownLine"

    return {
        'error_type': error_type,
        'missing_key': missing_key,
        'line_number': line_number
    }

def debug(filename,code, error, key_error , complex):
    if ("No module named" in error):
        locX, locY = error.find("'") + 1, error[error.find("'") + 1:].find("'")
        module = error[locX:locX + locY]
        install_package(module)
    else:
        if (complex == 0):
            query = "change the code for the error "+ error + " and generate the full code , refer the data set snippet for effective debuging"
            # query = "debug,correct the python code " + code + " . for the error " + error + " . and provide the whole corrected code . for reference snippet of the dataset  " + data_snip
            query = "please generate provide the full code always"
            response = chat_session.send_message(query).text
            # print(response)
            code = trim(response)
            str_to_py(code, filename)
        if (complex == 1):
            # query = code + " try another method to fix the error the error is being repeated more than 3 time . if the coder need to fix the error, add this comment in last line of the code 'coder need to fix it' along with the details to fix the error"
            query = key_error + " this error is not being fixed , change the whole code to rectify this error and generate the full brief code"
            query = "please generate provide the full code always"
            response = chat_session.send_message(query).text
            print(response)
            code = trim(response)
            print("=============== I am running =============================")
            str_to_py(code, filename)

def run(file):
    error_list = []
    round = 1
    while (1):
        try:
            result = subprocess.run(['python', file], check=True, capture_output=True, text=True)
            print("Output:  ")
            print(" ")
            print(result.stdout)  # Print the standard output of the script
            break
        except subprocess.CalledProcessError as e:
        # except Exception as e:
            error = str(e.stderr)
            key_error = extract_error_info(error)
            error_list.append(key_error)
            print("==================================== ROUND : " + str(round) + " ======================================")
            round += 1
            code = py_to_str(file)
            print(code)
            print("--------------------------------------------------------------------------")
            print(key_error)
            # error_list.append(key_error)
            # if(len(error_list)>=3 and error_list[len(error_list)-3] == error_list[len(error_list)-2] == error_list[len(error_list)-1]):
            #     debug(file,code, error,key_error , 1)
            # else:
            #     debug(file,code,error,key_error,0)
            if(len(error_list)>=2):
                print("\n.........\n"+error_list+"\n..........\n")
                if(error_list[len(error_list)-1] == error_list[len(error_list)-2]):
                    debug(file,code, error,key_error , 1)
            else:
                debug(file, code, error, key_error, 0)
            # debug(file,code,error,key_error,0)

def master(data_set):
    df = pd.read_csv(data_set)
    column = list(df.columns)
    print("COLUMN : \n", column,"\n\n")
    global data
    data = {}
    for col in column:
        column_name = col
        first_5_values = list(df[column_name].head(10))
        data[col] = first_5_values
    print("DATA SET SNIPPET : \n",data,"\n\n")
    global data_snip
    data_snip = str(data)
    # query = "Analyse the given snippet of datas set " + data_set + " : " + data_snip+ " \n  And generate a pyhthon code to diagnose,preprocess, and to excecute all the suitable analysis for the data set "+data_set
    # print(query)
    response = gen_code(data_snip)
    print("RESPONSE FROM GEMINI \n\n",response,"\n\n")
    code = trim(response)
    file = 'generated.py'
    str_to_py(code,file)
    run(file)

#=========================================================  START =================================================
master(data_set)
#==================================================================================================================
