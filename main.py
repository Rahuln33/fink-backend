####################
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# from mysql.connector import errorcode
# import openai
# import json
# from fuzzywuzzy import fuzz

# app = Flask(__name__)
# CORS(app)

# # MySQL connection configuration
# mysql_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'rahul@333',
#     'database': 'fink',
#     'raise_on_warnings': True
# }

# # Initialize OpenAI client
# client = openai.AzureOpenAI(
#     azure_endpoint="https://finkdataopenai.openai.azure.com/",
#     api_key='d57b4f240c6f4c12bb8d316469e45f69',
#     api_version="2024-02-15-preview"
# )

# # Load FinKraft data from JSON file
# with open('finkraft_data.json', 'r') as file:
#     finkraft_data = json.load(file)



# def extract_information(data, query, threshold=80):
#     """
#     Recursively extract relevant information from nested data based on the user's query
#     with fuzzy matching.
#     """
#     query = query.lower()
#     extracted_values = []

#     if isinstance(data, dict):
#         for key, value in data.items():
#             if fuzz.partial_ratio(query, key.lower()) >= threshold:
#                 if isinstance(value, (dict, list)):
#                     nested_values = extract_information(value, query, threshold)
#                     extracted_values.extend(nested_values)
#                 else:
#                     extracted_values.append(str(value))
#             elif isinstance(value, (dict, list)):
#                 nested_values = extract_information(value, query, threshold)
#                 extracted_values.extend(nested_values)
#     elif isinstance(data, list):
#         for item in data:
#             nested_values = extract_information(item, query, threshold)
#             extracted_values.extend(nested_values)
    
#     return extracted_values

# def create_table(cursor):
#     table_schema = (
#         "CREATE TABLE IF NOT EXISTS CHATGPT ("
#         "  id INT AUTO_INCREMENT PRIMARY KEY,"
#         "  session_id VARCHAR(255),"
#         "  email_id VARCHAR(255),"
#         "  user_input TEXT,"
#         "  bot_response TEXT"
#         ")"
#     )
#     try:
#         cursor.execute(table_schema)
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
#             print("CHATGPT table already exists.")
#         else:
#             print(err.msg)

# def get_conversation_history(cursor, session_id):
#     query = "SELECT user_input, bot_response FROM CHATGPT WHERE session_id = %s"
#     cursor.execute(query, (session_id,))
#     history = cursor.fetchall()
#     conversation = []
#     for user_input, bot_response in history:
#         conversation.append({"role": "user", "content": user_input})
#         conversation.append({"role": "assistant", "content": bot_response})
#     return conversation

# def get_or_create_session_id(cursor, email_id):
#     cursor.execute("SELECT session_id FROM CHATGPT WHERE email_id = %s LIMIT 1", (email_id,))
#     result = cursor.fetchone()
#     if result:
#         return result[0]
#     else:
#         cursor.execute("SELECT MAX(session_id) FROM CHATGPT")
#         max_session_id = cursor.fetchone()[0]
#         if max_session_id:
#             new_session_id = int(max_session_id) + 1
#         else:
#             new_session_id = 10001
#         return str(new_session_id)

# @app.route('/api/start_session', methods=['POST'])
# def start_session():
#     data = request.json
#     email = data.get('email')
#     print("Received email:", email)

#     if not email:
#         print("Email is missing")
#         return jsonify({'error': 'Email is required'}), 400

#     conn = None
#     cursor = None
#     try:
#         conn = mysql.connector.connect(**mysql_config)
#         cursor = conn.cursor()
#         create_table(cursor)  # Ensure the table is created before inserting data

#         # Generate or retrieve a session ID
#         session_id = get_or_create_session_id(cursor, email)
#         print("Generated session ID:", session_id)

#         # Insert the email into the database with default values for user_input and bot_response
#         insert_query = "INSERT INTO CHATGPT (session_id, email_id, user_input, bot_response) VALUES (%s, %s, %s, %s)"
#         cursor.execute(insert_query, (session_id, email, '', ''))
#         conn.commit()
#         print("Inserted email with session ID:", insert_query)

#         return jsonify({'session_id': session_id}), 200
#     except mysql.connector.Error as err:
#         print(f"MySQL error: {err}")
#         return jsonify({'error': 'Database error'}), 500
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_input = data.get('message')
#     email = data.get('email')
#     session_id = data.get('session_id')
#     print("Received email:", email)
#     print("Session ID:", session_id)
#     print("User input:", user_input)

#     if not user_input or not email or not session_id:
#         return jsonify({'response': 'Invalid input parameters.'}), 400

#     conn = None
#     cursor = None
#     try:
#         conn = mysql.connector.connect(**mysql_config)
#         cursor = conn.cursor()
#         create_table(cursor)

#         info = extract_information(finkraft_data, user_input)
        
#         if info:
#             bot_response = "\n".join(info)
#         else:
#             conversation_history = get_conversation_history(cursor, session_id)
#             conversation_history.append({"role": "user", "content": user_input})
            
#             completion = client.chat.completions.create(
#                 model="gpt-35-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are Fink, a representative for FinKraft AI. Provide detailed and user-friendly information to the users."},
#                 ] + conversation_history,
#                 temperature=0.7,
#                 max_tokens=150,
#                 top_p=1.0,
#                 frequency_penalty=0,
#                 presence_penalty=0,
#                 stop=None
#             )
#             bot_response = completion.choices[0].message.content
        
#         insert_query = "INSERT INTO CHATGPT (session_id, email_id, user_input, bot_response) VALUES (%s, %s, %s, %s)"
#         print("Insert query:", insert_query)
#         insert_data = (session_id, email, user_input, bot_response)
#         print("Insert data:", insert_data)
#         cursor.execute(insert_query, insert_data)
#         conn.commit()
        
#         return jsonify({'response': bot_response})
#     except mysql.connector.Error as err:
#         print(f"MySQL error: {err}")
#         return jsonify({'response': 'Database error.'}), 500
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# if __name__ == '__main__':
#     app.run(debug=True)




from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
import openai
import json
from fuzzywuzzy import fuzz

app = Flask(__name__)
CORS(app)

# MySQL connection configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rahul@333',
    'database': 'fink',
    'raise_on_warnings': True
}

# Initialize OpenAI client
client = openai.AzureOpenAI(
    azure_endpoint="https://finkdataopenai.openai.azure.com/",
    api_key='d57b4f240c6f4c12bb8d316469e45f69',
    api_version="2024-02-15-preview"
)

# Load FinKraft data from JSON files
with open('finkraft_data.json', 'r') as file:
    finkraft_data = json.load(file)

with open('bio_data.json', 'r') as file:
    bio_data = json.load(file)

def extract_information(data_sources, query, threshold=80):
    """
    Extract relevant information from multiple nested data sources based on the user's query
    with fuzzy matching.
    """
    query = query.lower()
    extracted_values = []

    for data in data_sources:
        if isinstance(data, dict):
            for key, value in data.items():
                if fuzz.partial_ratio(query, key.lower()) >= threshold:
                    if isinstance(value, (dict, list)):
                        nested_values = extract_information([value], query, threshold)
                        extracted_values.extend(nested_values)
                    else:
                        extracted_values.append(str(value))
                elif isinstance(value, (dict, list)):
                    nested_values = extract_information([value], query, threshold)
                    extracted_values.extend(nested_values)
        elif isinstance(data, list):
            for item in data:
                nested_values = extract_information([item], query, threshold)
                extracted_values.extend(nested_values)
    
    return extracted_values

def create_table(cursor):
    table_schema = (
        "CREATE TABLE IF NOT EXISTS CHATGPT ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  session_id VARCHAR(255),"
        "  email_id VARCHAR(255),"
        "  user_input TEXT,"
        "  bot_response TEXT"
        ")"
    )
    try:
        cursor.execute(table_schema)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("CHATGPT table already exists.")
        else:
            print(err.msg)

def get_conversation_history(cursor, session_id):
    query = "SELECT user_input, bot_response FROM CHATGPT WHERE session_id = %s"
    cursor.execute(query, (session_id,))
    history = cursor.fetchall()
    conversation = []
    for user_input, bot_response in history:
        conversation.append({"role": "user", "content": user_input})
        conversation.append({"role": "assistant", "content": bot_response})
    return conversation

def get_or_create_session_id(cursor, email_id):
    cursor.execute("SELECT session_id FROM CHATGPT WHERE email_id = %s LIMIT 1", (email_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("SELECT MAX(session_id) FROM CHATGPT")
        max_session_id = cursor.fetchone()[0]
        if max_session_id:
            new_session_id = int(max_session_id) + 1
        else:
            new_session_id = 10001
        return str(new_session_id)

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        create_table(cursor)  # Ensure the table is created before inserting data

        # Generate or retrieve a session ID
        session_id = get_or_create_session_id(cursor, email)

        # Insert the email into the database with default values for user_input and bot_response
        insert_query = "INSERT INTO CHATGPT (session_id, email_id, user_input, bot_response) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (session_id, email, '', ''))
        conn.commit()

        return jsonify({'session_id': session_id}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    email = data.get('email')
    session_id = data.get('session_id')

    if not user_input or not email or not session_id:
        return jsonify({'response': 'Invalid input parameters.'}), 400

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        create_table(cursor)

        # Extract information from both finkraft_data and bio_data
        data_sources = [finkraft_data, bio_data]
        info = extract_information(data_sources, user_input)
        
        if info:
            bot_response = "\n".join(info)
        else:
            conversation_history = get_conversation_history(cursor, session_id)
            conversation_history.append({"role": "user", "content": user_input})
            
            completion = client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[
                    {"role": "system", "content": "You are Fink, a representative for FinKraft AI. Provide detailed and user-friendly information to the users."},
                ] + conversation_history,
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            bot_response = completion.choices[0].message.content
        
        insert_query = "INSERT INTO CHATGPT (session_id, email_id, user_input, bot_response) VALUES (%s, %s, %s, %s)"
        insert_data = (session_id, email, user_input, bot_response)
        cursor.execute(insert_query, insert_data)
        conn.commit()
        
        return jsonify({'response': bot_response})
    except mysql.connector.Error as err:
        return jsonify({'response': 'Database error.'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
