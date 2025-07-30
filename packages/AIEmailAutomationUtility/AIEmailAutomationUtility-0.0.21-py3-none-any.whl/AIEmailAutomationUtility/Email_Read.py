import imaplib
import email
import os
import json
import time
import loggerutility as logger
from flask import request
import traceback
from fpdf import FPDF
from openai import OpenAI
import requests
import openai
import google.generativeai as genai
from datetime import datetime

from .Save_Transaction import Save_Transaction
from .Email_Upload_Document import Email_Upload_Document
from .Email_Classification import Email_Classification
from .EmailReplyAssistant import EmailReplyAssistant
from .Email_Draft import Email_Draft
from .Email_DocumentUploader import Email_DocumentUploader
import sqlite3

class Email_Read:
    def read_email(self, email_config):
        try:
            logger.log("inside read_email")
            mail = imaplib.IMAP4_SSL(email_config['host'], email_config['port'])
            mail.login(email_config['email'], email_config['password'])
            logger.log("login successfully")
            mail.select('inbox')

            while True:
                status, email_ids = mail.search(None, 'UNSEEN')
                emails = []
                
                if status == 'OK':
                    email_ids = email_ids[0].split()

                    if not email_ids: 
                        logger.log("Email not found, going to check new mail")
                        logger.log("Email not found,\ngoing to check new mail \n")
                    else:
                    
                        for email_id in email_ids:
                            email_body = ""
                            attachments = []
                            status, data = mail.fetch(email_id, '(RFC822)')
                            
                            if status == 'OK':
                                raw_email = data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                sender_email = msg['From']
                                cc_email = msg['CC']
                                subject = msg['Subject']
                                to = msg['To']

                                if msg.is_multipart():
                                    for part in msg.walk():
                                        content_type = part.get_content_type()
                                        if content_type == "text/plain":
                                            email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                                else:
                                    email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              

                                email_data = {
                                    "email_id": email_id,
                                    "from": sender_email,
                                    "to": to,
                                    "cc": cc_email,
                                    "subject": subject,
                                    "body": email_body
                                }
                                emails.append(email_data)
                                logger.log(f"emails:: {emails}")
                                call_save_transaction = Save_Transaction()
                                save_transaction_response = call_save_transaction.email_save_transaction(email_data)
                                logger.log(f"save_transaction_response:: {save_transaction_response}")
                time.sleep(10)
        
        except Exception as e:
            return {"success": "Failed", "message": f"Error reading emails: {str(e)}"}
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception as close_error:
                logger.log(f"Error during mail close/logout: {str(close_error)}")

    def read_email_automation(self, email_config):
        # try:
        logger.log(f"inside read_email_automation")
        # logger.log(f"email_config ::: {email_config}")
        LABEL                       = "Unprocessed_Email"
        file_JsonArray              = []
        templateName                = "ai_email_automation.json"
        fileName                    = ""

        Model_Name =  email_config.get('model_type', 'OpenAI') 
        reciever_email_addr = email_config.get('email', '').replace("\xa0", "").strip()
        receiver_email_pwd = email_config.get('password', '').replace("\xa0", "").strip()
        host =  email_config.get('host', '') 
        port =  email_config.get('port', '') 

        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(reciever_email_addr, receiver_email_pwd)
        logger.log("login successfully")
        mail.select('inbox')
                    
        file_JsonArray, categories = self.read_JSON_File(templateName)

        while True:
            status, email_ids = mail.search(None, 'UNSEEN')
            emails = []
            
            if status == 'OK':
                email_ids = email_ids[0].split()

                if not email_ids: 
                    logger.log("Email not found, going to check new mail")
                    logger.log("Email not found,\ngoing to check new mail \n")
                else:
                
                    for email_id in email_ids:
                        email_body = ""
                        attachments = []
                        status, data = mail.fetch(email_id, '(RFC822)')
                        
                        if status == 'OK':
                            raw_email = data[0][1]
                            msg = email.message_from_bytes(raw_email)

                            subject = msg['Subject']
                            sender_email_addr   = msg['From']
                            cc_email_addr       = msg['CC']
                            subject             = msg['Subject']

                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/plain":
                                        email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                            else:
                                email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              
                            
                            openai_Process_Input  = email_body 
                            logger.log(f"\nEmail Subject::: {subject}")
                            logger.log(f"\nEmail body::: {openai_Process_Input}")

                            openai_api_key = email_config.get('openai_api_key', '') 
                            geminiAI_APIKey = email_config.get('gemini_api_key', '') 
                            signature = email_config.get('signature', '') 
                            localAIURL = email_config.get('local_ai_url', '') 
                            
                            if len(str(openai_Process_Input)) > 0 :
                                email_cat_data = {
                                    "model_type" : Model_Name,
                                    "openai_api_key" : openai_api_key,
                                    "categories" : categories,
                                    "email_body" : email_body,
                                    "gemini_api_key" : geminiAI_APIKey,
                                    "signature" : signature,
                                    "local_ai_url" : localAIURL,
                                }
                                # logger.log(f"\nemail_cat_data ::: {email_cat_data}")
                                email_classification = Email_Classification()
                                emailCategory = email_classification.detect_category(email_cat_data)
                                emailCategory = emailCategory['message']
                                logger.log(f"\nDetected Email category ::: {emailCategory}")
                                
                                if emailCategory == 'Others':
                                    logger.log(f"Marking email as UNREAD. ")
                                    mail.store(email_id, '-FLAGS', '\\Seen')

                                    mail.create(LABEL)
                                    mail.copy(email_id, LABEL)
                                    mail.store(email_id, '+FLAGS', '\\Deleted')  # Mark for deletion
                                    mail.expunge()                         
                                    logger.log(f"Mail removed from inbox and added to '{LABEL}' label.")
                                
                                elif emailCategory == "Product Enquiry":
                                    
                                    if Model_Name == "OpenAI":
                                        responseMethod, parameters = self.get_JsonArray_values(emailCategory, file_JsonArray)
                                        if responseMethod == "Reply_Email_Ai_Assistant" :

                                            emailreplyassistant = EmailReplyAssistant()
                                            openai_Response = emailreplyassistant.Reply_Email_Ai_Assistant(openai_api_key, parameters["Assistant_Id"], openai_Process_Input, subject)
                                            
                                            logger.log(f"Process openai_Response ::: {openai_Response['message']}\n")
                                            email_details = {"sender":sender_email_addr, "cc":cc_email_addr, "subject":subject, "body": email_body}

                                            email_draft = Email_Draft()
                                            status, response = email_draft.draft_email(email_config, email_details, openai_Response['message'])
                                            logger.log(f"status ::: {status}")
                                        else :
                                            message = f"Invalid response method received '{responseMethod}' for category : '{emailCategory}'"
                                            raise ValueError(message)
                                    elif Model_Name == "LocalAI":
                                        logger.log("localAI")
                                        Detect_Email_category = False
                                        LocalAI_Response = emailCategory
                                        logger.log(f"Process LocalAI_Response ::: {LocalAI_Response}\n")
                                        email_details = {"sender":sender_email_addr, "cc":cc_email_addr, "subject":subject, "body": email_body}

                                        email_draft = Email_Draft()
                                        status, response = email_draft.draft_email(email_config, email_details, LocalAI_Response)
                                        logger.log(f"status ::: {status}")
                                    elif Model_Name == "GeminiAI":
                                        logger.log("GeminiAI")
                                        Detect_Email_category = False
                                        GeminiAI_Response = emailCategory
                                        logger.log(f"Process GeminiAI_Response ::: {GeminiAI_Response}\n")
                                        email_details = {"sender":sender_email_addr, "cc":cc_email_addr, "subject":subject, "body": email_body}

                                        email_draft = Email_Draft()
                                        status, response = email_draft.draft_email(email_config, email_details, GeminiAI_Response)
                                        logger.log(f"status ::: {status}")
                                    else:
                                        raise ValueError(f"Invalid Model Name provided : '{Model_Name}'")

                                elif emailCategory == "Purchase Order":
                                    responseMethod, parameters = self.get_JsonArray_values(emailCategory, file_JsonArray)
                                    logger.log(f"responseMethod ::: {responseMethod}")
                                    logger.log(f"parameters ::: {parameters}")

                                    # Download the attachment
                                    fileName = self.download_attachment(msg)

                                    # Get today's date folder path
                                    today_date = datetime.today().strftime('%Y-%m-%d')
                                    order_folder = os.path.join("ORDERS", today_date)

                                    if responseMethod == "Upload_Document":
                                        if len(fileName) != 0:
                                            email_upload_document = Email_DocumentUploader()
                                            file_path = os.path.join(order_folder, fileName)  # Correct file path

                                            with open(file_path, "rb") as file:
                                                response_status, restAPI_Result = email_upload_document.email_document_upload(file, parameters)
                                                logger.log(f"email_upload_document_response ::: {restAPI_Result}")
                                        else:
                                            new_fileName = self.create_file_from_emailBody(email_body, sender_email_addr, parameters)
                                            new_file_path = os.path.join(order_folder, new_fileName)

                                            with open(new_file_path, "rb") as file:
                                                response_status, restAPI_Result = email_upload_document.email_document_upload(file, parameters)
                                                logger.log(f"email_upload_document_response ::: {restAPI_Result}")

                                        if response_status == "200":
                                            logger.log(f"Attachment uploaded successfully against Document ID: '{restAPI_Result}'.")
                                        else:
                                            logger.log(restAPI_Result)
                                    
                                    else :
                                        message = f"Invalid response method received '{responseMethod}' for category : '{emailCategory}'"
                                        raise ValueError(message)
                                else:
                                    message = f"Detected Email category not found : '{emailCategory}'"
                                    raise ValueError(message)
            time.sleep(10)
        
        # except Exception as e:
        #     return {"status": "Failed", "message": f"Error reading emails: {str(e)}"}
        # finally:
        #     try:
        #         mail.close()
        #         mail.logout()
        #     except Exception as close_error:
        #         logger.log(f"Error during mail close/logout: {str(close_error)}")
        #         return {"status": "Failed", "message": f"Error reading emails: {str(close_error)}"}

    def read_email_quotation(self, email_config):
        # try:
        logger.log(f"inside read_email_automation")
        LABEL                       = "Unprocessed_Email"
        file_JsonArray              = []
        templateName                = "ai_email_automation.json"
        fileName                    = ""

        Model_Name =  email_config.get('model_type', 'OpenAI') 
        reciever_email_addr = email_config.get('email', '').replace("\xa0", "").strip()
        receiver_email_pwd = email_config.get('password', '').replace("\xa0", "").strip()
        host =  email_config.get('host', '') 
        port =  email_config.get('port', '') 

        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(reciever_email_addr, receiver_email_pwd)
        logger.log("login successfully")
        mail.select('inbox')
                    
        file_JsonArray, categories = self.read_JSON_File(templateName)

        while True:
            status, email_ids = mail.search(None, 'UNSEEN')
            emails = []
            
            if status == 'OK':
                email_ids = email_ids[0].split()

                if not email_ids: 
                    logger.log("Email not found, going to check new mail")
                    logger.log("Email not found,\ngoing to check new mail \n")
                else:
                
                    for email_id in email_ids:
                        email_body = ""
                        attachments = []
                        status, data = mail.fetch(email_id, '(RFC822)')
                        
                        if status == 'OK':
                            raw_email = data[0][1]
                            msg = email.message_from_bytes(raw_email)

                            subject = msg['Subject']
                            sender_email_addr   = msg['From']
                            cc_email_addr       = msg['CC']
                            subject             = msg['Subject']

                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/plain":
                                        email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                            else:
                                email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              
                            
                            openai_Process_Input  = email_body 
                            logger.log(f"\nEmail Subject::: {subject}")
                            logger.log(f"\nEmail body::: {openai_Process_Input}")

                            openai_api_key = email_config.get('openai_api_key', '') 
                            geminiAI_APIKey = email_config.get('gemini_api_key', '') 
                            signature = email_config.get('signature', '') 
                            localAIURL = email_config.get('local_ai_url', '') 
                            logger.log(f"\ngeminiAI_APIKey::: {geminiAI_APIKey}")
                            logger.log(f"\nlocalAIURL::: {localAIURL}")
                            logger.log(f"\nsignature::: {signature}")
                            
                            if len(str(openai_Process_Input)) > 0 :
                                email_cat_data = {
                                    "model_type" : Model_Name,
                                    "openai_api_key" : openai_api_key,
                                    "categories" : categories,
                                    "email_body" : email_body,
                                    "gemini_api_key" : geminiAI_APIKey,
                                    "signature" : signature,
                                    "local_ai_url" : localAIURL,
                                }
                                # logger.log(f"\nemail_cat_data ::: {email_cat_data}")
                                email_classification = Email_Classification()
                                emailCategory = email_classification.detect_category(email_cat_data)
                                emailCategory = emailCategory['message']
                                logger.log(f"\nDetected Email category ::: {emailCategory}")
                                
                                if emailCategory == "Quotation":
                                    responseMethod, parameters = self.get_JsonArray_values(emailCategory, file_JsonArray)
                                    
                                    logger.log(f"Inside Quotation")
                                    # Step 4: Identify customer from email using AI
                                    customer_data = self.identify_customer(email_body, subject, Model_Name, openai_api_key, geminiAI_APIKey, localAIURL, parameters["Customer_Assistant_Id"])
                                    logger.log(f"Identified customer: {customer_data}")
                                    
                                    # Step 5: Identify product from email using AI
                                    products = self.identify_products(email_body, subject, Model_Name, openai_api_key, geminiAI_APIKey, localAIURL, parameters["Product_Assistant_Id"])
                                    
                                    for product in products:
                                        db_connection = sqlite3.connect('price_list.db')
                                        cursor = db_connection.cursor()

                                        # Get rate from SQLite database
                                        query = f'SELECT Price FROM price_list_table WHERE "Item No." = "{product.get("item_no", "")}";'
                                        cursor.execute(query)
                                        result = cursor.fetchone()
                                        
                                        if result:
                                            rate = result[0]  
                                            product["rate"] = rate
                                        else:
                                            product["rate"] = None
                                    
                                    logger.log(f"Identified products: {products}")
                                    logger.log(f"Identified products length: {len(products)}")
                                    quotation_draft = self.generate_quotation_draft(
                                        customer_data, 
                                        products,
                                        Model_Name, 
                                        openai_api_key, 
                                        geminiAI_APIKey, 
                                        localAIURL,
                                        parameters["Customer_Assistant_Id"],
                                        email_body, 
                                        subject,
                                        signature
                                    )
                                    logger.log(f"quotation_draft ::: {quotation_draft}")
                                    
                                    # Step 8: Send draft quotation email
                                    email_details = {"sender":sender_email_addr, "cc":cc_email_addr, "subject":subject, "body": email_body}
                                    email_draft = Email_Draft()
                                    status, response = email_draft.quotation_draft_email(email_config, email_details, quotation_draft)
                                    logger.log(f"status ::: {status}")
                                    
                                    logger.log(f"Quotation email sent to {sender_email_addr}")
                                    
                                else:
                                    logger.log(f"Marking email as UNREAD. ")
                                    mail.store(email_id, '-FLAGS', '\\Seen')

                                    mail.create(LABEL)
                                    mail.copy(email_id, LABEL)
                                    mail.store(email_id, '+FLAGS', '\\Deleted')  # Mark for deletion
                                    mail.expunge()                         
                                    logger.log(f"Mail removed from inbox and added to '{LABEL}' label.")

            time.sleep(10)

    def identify_customer(self, email_body, subject, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id):
        logger.log("Inside identify_customer")        
        
        if model_type == "OpenAI":
            prompt = f"""Identify the customer code, customer name in json format from the following email {email_body} and received from {subject}. Do not include any instruction as the output will be directly in a program."""
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.identify_customer_product_reply_assitant(openai_api_key, assistant_id, email_body, subject, prompt)

        elif model_type == "GeminiAI": 
            prompt = f"""Identify the customer code, customer name in json format from the following email {email_body} and received from {subject}. Do not include any instruction as the output will be directly in a program."""
            ai_result = self.identify_customer_product_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""Identify the customer code and customer name in JSON format from the following email: {email_body}, received from {subject}. 
            If no customer details are found, return:{{"customer_name": "","customer_code": ""}}Only return the JSON object. No explanations, no additional text."""
            ai_result = self.identify_customer_product_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "{}"
        
        customer_data = {}
        if ai_result["status"] == "Success":
            customer_data = json.loads(ai_result["message"])
        else:            
            customer_data = {
                "customer_name": "",
                "customer_code": ""
            }
        return customer_data
    
    def identify_products(self, email_body, subject, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id):
        logger.log("Inside identify_products")    
        
        if model_type == "OpenAI":
            prompt = f"""
                Can you give me price information of all products in following format requested_description, item_no, make, description, price, price unit, inventory unit for following items in strictly in JSON String format {email_body}. 
                If there is one product or multiple should return in list. 
                Do not include any instruction as the output will be directly in a program.
                """
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.identify_customer_product_reply_assitant(openai_api_key, assistant_id, email_body, subject, prompt)

        elif model_type == "GeminiAI":
            prompt = f"""
                Can you give me price information of all products in following format requested_description, item_no, make, description, price, price unit, inventory unit for following items in strictly in JSON String format {email_body}. 
                If there is one product or multiple should return in list. 
                Do not include any instruction as the output will be directly in a program.
                """
            ai_result = self.identify_customer_product_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""Can you give me price information in following format requested_description, item_no, make, description, price, price unit, inventory unit for following items it strictly in json format which loads directly in json {email_body}. If there is one product or multiple should return in list. 
            If no product details are found, return:[] Only return the JSON object. No explanations, no additional text."""
            ai_result = self.identify_customer_product_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "{}"
        
        product_data = {}
        if ai_result["status"] == "Success":
            logger.log(f"ai_result ::: {ai_result}")   
            product_data = json.loads(ai_result["message"])
        else:            
            product_data = []
        return product_data
    
    def generate_quotation_draft(self, customer_data, products, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id, email_body, subject, signature):
        logger.log("Inside generate_quotation_draft")   
        
        customer = customer_data
        
        product_table = "Products:\n"
        for product in products:
            product_table += f'- {product.get("requested_description")} (Code: {product.get("item_no")}) = ${product.get("rate")}\n'
        
        if model_type == "OpenAI":
            prompt = f"""
                Generate product information in HTML tabular format with line separators for rows and columns in a draft reply based on the following information:

                Customer: {customer.get('customer_name', '')}  
                Customer Code: {customer.get('customer_code', '')}  

                {product_table}  
                product_table must contain only price column even if it is none(set it as -).
                Original Email Subject: {subject}  

                Return only the following JSON String format:
                {{
                    "email_body": {{
                        "body": "Draft email body proper response, It should not be same like mail content and does not having any signature part like Best regards.",
                        "table_html": "Table Details with Sr. No. in HTML",
                        "signature": "{signature}"
                    }}
                }}

                Do not include signature in body and any instructions, explanations, or additional text—only the JSON object.
            """
            logger.log(f"Quotation draft ::: {prompt}")
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.create_quotation_draft(openai_api_key, assistant_id, email_body, subject, prompt)   

        elif model_type == "GeminiAI":
            prompt = f"""
                Create an HTML product information email draft with the following details:

                Customer Name: {customer.get('customer_name', '')}
                Customer Code: {customer.get('customer_code', '')}

                Product Information:
                {product_table}
                Note: Include price column with a value of "-" if price is not available.

                Email Subject Reference: {subject}

                Please format the response as a valid JSON string with these fields:
                {{
                    "email_body": {{
                        "body": "Professional email content that summarizes the product information without being identical to the input data. Do not include signature here.",
                        "table_": "HTML table with SR. No. column and product details",
                        "signature": "{signature}"
                    }}
                }}

                Ensure the JSON is properly formatted with escaped newlines (\\n) and no trailing commas. Return only the valid JSON string without additional explanations or instructions.
            """
            logger.log(f"Quotation draft ::: {prompt}")
            ai_result = self.create_quotation_draft_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""
                Generate product information in HTML tabular format with line separators for rows and columns in a draft reply based on the following information:

                Customer: {customer.get('customer_name', '')}  
                Customer Code: {customer.get('customer_code', '')}  

                {product_table}  
                - The table must contain the **Price** column, even if it is empty (set it as `-` if None).  
                - The table should include **Sr. No.** as the first column.  
                - Format the table with `<table>`, `<tr>`, `<th>`, and `<td>` tags with some border to table.

                Original Email Subject: {subject}  

                Return **strictly** in the following JSON String format:
                - All keys must be: `body`, `table_`, and `signature` inside the `email_body` JSON.  
                - **Do not include** `\n`, `\`, `\\`, or any unnecessary escape characters.  
                - Do not include instructions, explanations, or additional text—only the JSON object.  

                Format:
                {{
                    "email_body": {{
                        "body": "Draft email body proper response, It should not contain the table or signature.",
                        "table_": "Table Details with Sr. No. in HTML only",
                        "signature": "{signature}"
                    }}
                }}
            """
            logger.log(f"Quotation draft ::: {prompt}")
            ai_result = self.create_quotation_draft_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "Error: Unable to generate quotation draft. Please check the configuration."
        
        logger.log(f"Quotation draft ai_result::: {ai_result}")
        quotation_draft_data = None
        if ai_result != None:
            quotation_draft_data = json.loads(ai_result)["email_body"]
        return quotation_draft_data

    def identify_customer_product_LocalAI(self, openai_api_key, email_body, local_ai_url, prompt):
        logger.log("Inside identify_customer_product_LocalAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Local AI message for detecting category::: {message}")
            openai.api_key = openai_api_key
            client = OpenAI(base_url=local_ai_url, api_key="lm-studio")
            completion = client.chat.completions.create(
                model="mistral",
                messages=message,
                temperature=0,
                stream=False,
                max_tokens=4096
            )

            final_result = str(completion.choices[0].message.content)
            final_result = final_result.replace("\n```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","").replace("html","")
            logger.log(f"finalResult:520  {final_result}")
            return {"status": "Success", "message": final_result}

        except Exception as e:
            logger.log(f"Error with LocalAI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with LocalAI detection/generation: {str(e)}"}
        
    def create_quotation_draft_LocalAI(self, openai_api_key, email_body, local_ai_url, prompt):
        logger.log("Inside create_quotation_draft_LocalAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Local AI message for detecting category::: {message}")
            openai.api_key = openai_api_key
            client = OpenAI(base_url=local_ai_url, api_key="lm-studio")
            completion = client.chat.completions.create(
                model="mistral",
                messages=message,
                temperature=0,
                stream=False,
                max_tokens=4096
            )

            final_result = str(completion.choices[0].message.content)
            final_result = final_result.replace("\n```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","").replace("html","")
            logger.log(f"finalResult:520  {final_result}")
            return final_result

        except Exception as e:
            logger.log(f"Error with LocalAI detection/generation: {str(e)}")
            return str(e)
        
    def identify_customer_product_GeminiAI(self, gemini_api_key, email_body, prompt):
        logger.log("Inside identify_customer_product_GeminiAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Gemini AI message for detecting category::: {message}")
            message_list = str(message)

            genai.configure(api_key=gemini_api_key)
            # model = genai.GenerativeModel('gemini-1.0-pro')
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(message_list)
            
            final_result = ""
            for part in response:
                final_result = part.text
                logger.log(f"response:::  {final_result}")
                if final_result:
                    try:
                        final_result = final_result.replace("\\", "").replace('```', '').replace('json', '')
                        if final_result.startswith("{{") and final_result.endswith("}}"):
                            final_result = final_result[1:-1]
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {final_result} {type(final_result)}")

            logger.log(f"finalResult:::  {final_result}")
            return {"status": "Success", "message": final_result}

        except Exception as e:
            logger.log(f"Error with Gemini AI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with Gemini AI detection/generation: {str(e)}"}
        
    def create_quotation_draft_GeminiAI(self, gemini_api_key, email_body, prompt):
        logger.log("Inside identify_customer_product_GeminiAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Gemini AI message for detecting category::: {message}")
            message_list = str(message)

            genai.configure(api_key=gemini_api_key)
            # model = genai.GenerativeModel('gemini-1.0-pro')
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(message_list)
            
            final_result = ""
            for part in response:
                final_result = part.text
                logger.log(f"response:::  {final_result}")
                if final_result:
                    try:
                        final_result = final_result.replace('```', '').replace('json', '')
                        if final_result.startswith("{{") and final_result.endswith("}}"):
                            final_result = final_result[1:-1]
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {final_result} {type(final_result)}")

            logger.log(f"finalResult:::  {final_result}")
            return final_result

        except Exception as e:
            logger.log(f"Error with Gemini AI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with Gemini AI detection/generation: {str(e)}"}
        
    def save_attachment(self, part, download_dir):
        try:
            filename = part.get_filename()
            if filename:
                # Create the directory if it doesn't exist
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                file_path = os.path.join(download_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                logger.log(f"Attachment saved: {file_path}")
                return file_path
        except Exception as e:
            return {"success": "Failed", "message": f"Error saving attachment: {str(e)}"}

    def Read_Email(self, data):
        try:

            reciever_email_addr = data.get("reciever_email_addr")
            receiver_email_pwd = data.get("receiver_email_pwd")
            host = data.get("host")
            port = data.get("port")
            openai_api_key = data.get("openai_api_key") 
            geminiAI_APIKey = data.get("GeminiAI_APIKey")
            localAIURL = data.get("LOCAL_AI_URL")

            if not all([reciever_email_addr, receiver_email_pwd, host, port]):
                raise ValueError("Missing required email configuration fields.")

            logger.log(f"\nReceiver Email Address: {reciever_email_addr}\t{type(reciever_email_addr)}", "0")
            logger.log(f"\nReceiver Email Password: {receiver_email_pwd}\t{type(receiver_email_pwd)}", "0")
            logger.log(f"\nHost: {host}\t{type(host)}", "0")
            logger.log(f"\nPort: {port}\t{type(port)}", "0")

            email_config = {
                'email': reciever_email_addr,
                'password': receiver_email_pwd,
                'host': host,
                'port': int(port),
                'openai_api_key': openai_api_key,
                'gemini_api_key': geminiAI_APIKey,
                'local_ai_url': localAIURL
            }

            emails = self.read_email(email_config)            
            logger.log(f"Read_Email response: {emails}")

        except Exception as e:
            logger.log(f"Error in Read_Email: {str(e)}")

    def download_attachment(self, msg):
        base_folder = "ORDERS"  # Main folder for storing orders
        today_date = datetime.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
        date_folder = os.path.join(base_folder, today_date)  # Path: ORDERS/YYYY-MM-DD

        # Ensure folders exist
        os.makedirs(date_folder, exist_ok=True)

        filename = ""

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(date_folder, filename)  # Save inside date-wise folder

                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                logger.log(f"\nAttachment saved: '{filepath}'")
            else:
                logger.log("\nNo Attachment found.")
        return filename
    
    def read_JSON_File(self, json_fileName):
        category_list               = []
        categories                  = ""
        try:
            if os.path.exists(json_fileName):
                with open(json_fileName, "r") as fileObj:
                    file_JsonArray = json.load(fileObj) 
                    
                    for eachJson in file_JsonArray :
                        for key, value in eachJson.items():
                            if key == "Category" and value:
                                category_list.append(value)
                        # categories = ", ".join(category_list)
                        
                return file_JsonArray, category_list

            else:
                message = f"{json_fileName} file not found."
                raise Exception(message)
        except Exception as e:
            msg = f"'{json_fileName}' file is empty. Please provide JSON parameters in the filename."
            trace = traceback.format_exc()
            logger.log(f"Exception in writeJsonFile: {msg} \n {trace} \n DataType ::: {type(msg)}")
            raise Exception(msg)
        
    def get_JsonArray_values(self, category, jsonArray):
        responseMethod  = ""
        parameters      = ""
        
        for eachJson in jsonArray :
            for key, value in eachJson.items():
                if value == category:
                    responseMethod  = eachJson["Response_Method"]  
                    parameters      = eachJson["Parameters"]
        
        return responseMethod, parameters
    
    def create_file_from_emailBody(self, text, sender_email_addr, parameters):
        base_folder = "ORDERS"
        today_date = datetime.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
        order_folder = os.path.join(base_folder, today_date)

        # Ensure the date-wise folder exists
        os.makedirs(order_folder, exist_ok=True)

        # Generate filename from sender's email
        fileName = sender_email_addr[sender_email_addr.find("<")+1:sender_email_addr.find("@")].strip().replace(".","_")
        
        if parameters["FILE_TYPE"] == "pdf":
            fileName = fileName + ".pdf"
            filePath = os.path.join(order_folder, fileName)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
            pdf.output(filePath)
            logger.log(f"New PDF file created from email body and stored in '{filePath}'")

        elif parameters["FILE_TYPE"] == "txt":
            fileName = fileName + ".txt"
            filePath = os.path.join(order_folder, fileName)

            with open(filePath, "w") as file:
                file.write(text)
                logger.log(f"New TXT file created from email body and stored in '{filePath}'")
        else:
            message = f"Invalid File Type received."
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        return fileName

        

