import cv2
import pytesseract
import re
from kraken import binarization
from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from pdf2image import convert_from_path
import loggerutility as logger

import ast
import PyPDF2
import pdfkit
import pathlib
import pdftotext
import pdfplumber
from PIL import Image
from PyPDF2 import PdfReader
import json, traceback, openai
import commonutility as common
from openai import OpenAI

# pytesseract.pytesseract.tesseract_cmd = 'E:/tes/tesseract.exe'

class visitingCard:
    mainPg_Instruction  = ""
    result              = {}

# Name extraction code (Name must be in left side)
    def get_full_name(self,lst):
        name1 = r"([a-zA-Z'.,-]+( [a-zA-Z'.,-]+)*){8,30}"
        full_name1 = re.search(name1, lst)

        if full_name1 is not None:
            return full_name1.group()


    # Email Id extraction code
    def get_email(self,lst):
        mail_pattern = r'\b[A-Za-z0-9. _%+-]+@[A-Za-z0-9. -]+\.[A-Z|a-z ]{2,3}'

        mail = re.search(mail_pattern, lst.replace(" ", "").replace("-", "."))
        if mail is not None:
            return mail.group()


    # contact number extraction code
    def get_phone_number(self,lst):
        contact_no4 = r'[0-9.]{13}\b'
        contact_no1 = r'[0-9]{10}\b'
        contact_no3 = r'[0-9.]{12}\b'
        contact_no2 = r'[0-9.]{11}\b'
        Contact_NO1 = re.search(contact_no1,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO1 is not None:
            logger.log('10','0')
            return Contact_NO1.group()
        Contact_NO2 = re.search(contact_no2,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO2 is not None:
            logger.log('11','0')
            return Contact_NO2.group()
        Contact_NO3 = re.search(contact_no3,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO3 is not None:
            logger.log('12','0')
            return Contact_NO3.group()
        Contact_NO4 = re.search(contact_no4,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO4 is not None:
            logger.log('13','0')
            return Contact_NO4.group()


    # website extraction code
    def get_website(self,lst):
        website_pattern = r'\b(WWW|www)+.[A-Za-z0-9. _%+-]+\.[A-Z|a-z]{2,3}\b'
        web = re.search(website_pattern, lst.replace(" ", ""))
        if web is not None:
            return web.group()


    def pdf_data_extractor(self,PDF_file):
        image_file_list = []
        with TemporaryDirectory() as tempdir:
        
            pdf_pages = convert_from_path(PDF_file, 500)
                
            # Read in the PDF file at 500 DPI

            # Iterate through all the pages stored above
            for page_enumeration, page in enumerate(pdf_pages, start=1):
            
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for image_file in image_file_list:
                text = str(((pytesseract.image_to_string(Image.open(image_file)))))
                

            return text


    # Accept the file for for data extraction

    def extract(self, File_path):
        # This function uses Regex patterns to extract data from a visiting card.
        result  = {}
        name    = File_path.split(".")
        logger.log(f"{name[1]}","0")

        if name[1] == "PDF" or name[1] == "pdf":
            OCR_Text = self.pdf_data_extractor(File_path)
            logger.log(f"Visiting card OCR ::: {OCR_Text}","0")
        else:
            im      = Image.open(File_path)
            bw_im   = binarization.nlbin(im)
            d       = decode(bw_im, symbols=[ZBarSymbol.QRCODE])
            if d:
                for i in d:
                    logger.log("QR code Exicuted","0")
                    OCR_Text = i.data.decode('utf-8')

                    OCR_Text = OCR_Text.replace(";", " ")
                    # logger.log(f"{OCR_Text}","0")
            else:
                path    = File_path
                image   = cv2.imread(path, 0)
                OCR     = pytesseract.image_to_string(image)
                # logger.log("f{len(OCR)}","0")
                # logger.log(f"{OCR}","0")
                logger.log(f"{OCR}","0")
                OCR_Text = OCR
        # ===========
        Final_text = {  "Name"      : self.get_full_name(OCR_Text),
                        "Telephone" : self.get_phone_number(OCR_Text),
                        "Email"     : self.get_email(OCR_Text),
                        "Website"   : self.get_website(OCR_Text)        
                    }
        
        # logger.log(f"{Final_text}","0")
        result["name"]       =  Final_text["Name"]
        result["tele1"]      =  Final_text["Telephone"]
        result["email_addr"] =  Final_text["Email"]
        result["Website"]    =  Final_text["Website"]
        logger.log(f"Visiting card result ::: {result}\n\n")

        return result
    

    def extractDataUsing_GPT(self, file_path, jsonData):
        # This function uses gpt-4.1 to extract data from a visiting card.
        try:
            mandatory               = []
            postOrderExtraction     = ""
            proc_mtd_value          = ""
            proc_api_key            = ""
            ai_proc_templ           = ""
            ai_proc_variables       = ""
            OCR_Text                = ""
            finalResult             = ""
            GPTInstruction_list     = []
            enhancement_parameters  = ""
            # enhancement_parameters =    {   
            #     '1': {'Blur': 3},
            #     '2': {'Gray': 1},
            #     '3': {'Resizing': 84},
            #     '4': {'Thresholding': 0.9}
            #                             }

            logger.log(f"json data ::: 186 {jsonData}","0")
            
            if 'ai_proc_templ' in jsonData.keys():
                ai_proc_templ = jsonData['ai_proc_templ']
            
            if 'proc_api_key' in jsonData.keys():
                proc_api_key = jsonData['proc_api_key']

            if 'IS_OCR_EXIST' in jsonData.keys():
                IS_OCR_EXIST = jsonData['IS_OCR_EXIST']

            if 'ai_proc_variables' in jsonData.keys():
                ai_proc_variables = jsonData['ai_proc_variables']

            if 'enhancement_parameters' in jsonData.keys():
                enhancement_parameters = jsonData['enhancement_parameters']
                if enhancement_parameters:
                    enhancement_parameters = json.loads(enhancement_parameters)

            if isinstance(ai_proc_variables, str):
                ai_proc_variables = json.loads(ai_proc_variables)

            if ai_proc_variables:
                for val in ai_proc_variables["Details"]:
                    if val['mandatory'] == 'true':
                        mandatory.append(val['name'])
                
                    if val["name"] == "POST_ORDER_EXTRACTION":
                        postOrderExtraction = val['defaultValue'].strip()
                        logger.log(f"\n\n POST_ORDER_EXTRACTION ::: {postOrderExtraction} {type(postOrderExtraction)}\n\n","0") 
        
            logger.log(f"ai_proc_variables::::235 {ai_proc_variables}","0")
            
            if 'proc_mtd' in jsonData.keys():
                self.processing_method = jsonData['proc_mtd']
                logger.log(f"self.processing_method:::{self.processing_method}")
            
            fileExtension = (pathlib.Path(file_path).suffix)
            logger.log(f"\nfileExtention::::> {fileExtension}","0")
            self.fileExtension_lower = fileExtension.lower()
            logger.log(f"\nfileExtention_lower()::::> {self.fileExtension_lower}","0")

            if IS_OCR_EXIST == 'false':
                logger.log(f"OCR Start !!!!!!!!!!!!!!!!!102","0")  
                dict = {}          
                if '.PDF' in self.fileExtension_lower or '.pdf' in self.fileExtension_lower or '.png' in self.fileExtension_lower :

                    if 'PP' == self.processing_method :
                        logger.log("\tCASE PP \n")
                        OCR_Text = self.pdfplumber_ocr(file_path)
                        
                    elif 'PT' == self.processing_method :
                        logger.log("\tCASE PT \n")
                        OCR_Text = self.pdftotext_ocr(file_path)
                        
                    elif 'PO' == self.processing_method:
                        logger.log("\tCASE PO \n")
                        OCR_Text = self.pytesseract_ocr(file_path)
                        
                    elif 'PPO' ==self.processing_method or 'PPO4' == self.processing_method :
                        logger.log("\tCASE PPO OR PPO4\n")
                        OCR_Text = self.pdfplumber_overlap(file_path)

                    elif 'PPF' == self.processing_method:
                        logger.log("\tCASE PPF\n")
                        OCR_Text=self.PyPDF_ocr(file_path)
                        
                    elif 'PPH' == self.processing_method:
                        logger.log("\nCASE PPH\n")
                        finalResult=self.process_image(file_path,proc_api_key,ai_proc_templ, ai_proc_variables)
                        logger.log(f"finalResult : {finalResult}")

                    if 'PPH' != self.processing_method:
                        keys_with_blank_values = [key for key, value in OCR_Text.items() if not value]
                        if len(keys_with_blank_values) != 0:      
                            OCR_Text = self.pytesseract_ocr(file_path)
                            
                    logger.log(f"Visisting Card pdf ocr ::::: {OCR_Text}","0")
                
                else:
                    path = file_path
                    image = cv2.imread(path)
                    if enhancement_parameters:
                        if '1' in enhancement_parameters.keys():
                            image = self.gaussianBlur(image,enhancement_parameters['1']['Blur'])
                        
                        if '2' in enhancement_parameters.keys():
                            image = self.grayscale(image)

                        if '3' in enhancement_parameters.keys():
                            image = self.resizing(image,enhancement_parameters['3']['Resizing'])
                        
                        if '4' in enhancement_parameters.keys():
                            image = self.thresholding(image,enhancement_parameters['4']['Thresholding'])


                    dict[str(1)] = pytesseract.image_to_string(image)
                    logger.log(f"\nVisisting Card Image inside pdf OCR ::: {dict}\n","0")
                    OCR_Text = dict
            
            else:
                if 'OCR_DATA' in jsonData.keys():
                    OCR_Text = jsonData['OCR_DATA']
            
            if ai_proc_templ:
                if 'PPH' != proc_mtd_value: 
                    if isinstance(ai_proc_variables, str):
                        ai_proc_variables = json.loads(ai_proc_variables)

                    for key in ai_proc_variables["Details"]:
                        if key["name"] == "main_page":
                            self.mainPg_Instruction = key['defaultValue']
                    
                    ai_proc_templ = ai_proc_templ.replace("<EXTRACT_INSTRUCTIONS>", self.mainPg_Instruction)
                    logger.log(f"\n\nai_proc_temp after replacing main Page instruction :::  \n{'-'* 35}\n{ai_proc_templ}\t {type(ai_proc_templ)}\n\n")

                    OCR_Text_str = "".join(OCR_Text.values()).replace("\n", " ")    # conevrting OCR dict to values
                    ai_proc_templ = ai_proc_templ.replace("<DOCUMENT_DATA>", OCR_Text_str)
                    logger.log(f"\n\nai_proc_temp after replacing OCR_Text_str ::: \n{'-'* 35}\n{type(ai_proc_templ)}\t{ai_proc_templ}\n\n")
                    
                    ai_proc_templ = ast.literal_eval(ai_proc_templ) 
                    logger.log(f"\n\nai_proc_templ after conversion from string to dict::: \n{'-'* 35}\n{type(ai_proc_templ)} \n\n{ai_proc_templ}\n\n")

                    GPTInstruction_list = [eachInstruction_json for eachInstruction_json in ai_proc_templ]
                    logger.log(f"\n\nGPTInstruction_list::: {type(GPTInstruction_list)} \n\n{GPTInstruction_list}\n\n")

                    logger.log(f"proc_api_key line 310 ::: {proc_api_key}")
                    finalResult = self.call_GPT_Service(GPTInstruction_list, proc_api_key)
               
            return finalResult
            
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)

    def pytesseract_ocr(self,PDF_file):
        image_file_list     =  []
        dict                =  {}
        
        logger.log(f"pytesseract_ocr filename ::: {PDF_file}\n{type(PDF_file)} \n")
        with TemporaryDirectory() as tempdir:
            pdf_pages = convert_from_path(PDF_file, 500)
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg" 
                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for page_no,image_file in enumerate(image_file_list): 
                text = cv2.imread(image_file)
                image_file = self.resizing(text, 50)
                dict[str(page_no+1)] = str(((pytesseract.image_to_string(image_file)))).strip()

            logger.log(f"pytesseract for image ::::: {dict}","0") 

            return dict
        
    def pdfplumber_ocr(self,PDF_file):
        OCR_lst = []
        ocr_text_final = ""
        dict = {}
        
        file = pdfplumber.open(PDF_file)
        ocr_text = file.pages
        logger.log(f"file.pages::: {file.pages}", "0")
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            dict[str(page_no+1)] = ocr_text_final.strip()
            # OCR_lst.append(ocr_text_final)
        # print(len(dict.values()))
        # print(dict)
        return dict
    
    def pdftotext_ocr(self,PDF_file):
        with open(PDF_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        OCR_Text = "\n\n".join(pdf)
        return OCR_Text
    
    def gaussianBlur(self,img,blur_value):
        logger.log(f"gaussianBlur::::54> {blur_value}","0")
        img = cv2.GaussianBlur(img, (blur_value, blur_value),cv2.BORDER_DEFAULT)
        return img

    def grayscale(self,img):
        logger.log(f"grayscale::::59","0")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def resizing(self,img,scale_percent):
        logger.log(f"resizing::::64> {scale_percent}","0")
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)
        return img

    def thresholding(self,img,thresholding_value):
        logger.log(f"thresholding::::72> {thresholding_value}","0")
        mean_value = img.mean()
        threshold_value = mean_value * thresholding_value
        _, img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
        return img

    def pdfplumber_overlap(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}
        
        pdf = pdfplumber.open(fileName)
        ocr_text = pdf.pages
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text(layout=True, x_tolerance=1)
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()
        
        logger.log(f"OCR_dict after overlap:::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict

    def PyPDF_ocr(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}

        pdfFileObj = open(fileName, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        ocr_text = pdfReader.pages
        
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()

        logger.log(f"OCR_dict PyPDF :::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict

    def call_GPT_Service(self, GPTInstruction_list, proc_api_key, max_response_tokens = 500):
        
        result                = ""
        completion            = ""
        resultContent         = ""
        Final_extracted_data  = {}
        
        if len(proc_api_key) != 0 :
            client                = OpenAI(
                                            api_key = proc_api_key #"sk-svcacct-xoSzrEWzvU4t1fbEluOkT3BlbkFJkj7Pvc8kU98y1P3LdI1c",
                                        )
        else:
            raise Exception(f" OpenAI API Key cannot be blank ::: '{proc_api_key}' ")

        logger.log(f"proc_api_key ::: {proc_api_key} ")
        
        logger.log(f" \n\nBefore gpt-4.1 CALL FINAL MESSAGE  :::\n{'-'*30}\n{GPTInstruction_list}, \t{type(GPTInstruction_list)}\n","0")    

        completion = client.chat.completions.create(
                                                    model               = "gpt-4.1",
                                                    messages            = GPTInstruction_list,
                                                    temperature         = 0,
                                                    max_tokens          = max_response_tokens,
                                                    frequency_penalty   = 0,
                                                    presence_penalty    = 0,
                                                    )                    

        logger.log(f"\n\n Completion result gpt-4.1 raw response :::\n{completion} \t{type(completion)}\n","0")  
        try:                                      
            resultContent = (completion.choices[0].message.content).replace("`", "").replace("json", "")
            result = json.loads(resultContent)
            logger.log(f"Extraction filtered Result  line 451 ::: {result}")
        except Exception as e :
            logger.log("Trimming actual open AI response content inside of curly brackets")
            if "{" in resultContent and "}" in resultContent :
                result = json.loads(resultContent[ resultContent.index("{") : resultContent.index("}")+1 ])
                logger.log(f"Extraction filtered Result line 456::: {result}")
            else:
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                return str(returnErr)

        logger.log(f"\n\n Completion result gpt-4.1 :::\n{result} \t{type(result)}\n","0")

        
        Final_extracted_data["Name"]      = result["name"]    
        Final_extracted_data["Telephone"] = result["tele1"]   
        Final_extracted_data["Email"]     = result["email_addr"]
        Final_extracted_data["Website"]   = result["website"]    
        logger.log(f"\n\n Completion result gpt-4.1 :::\n{Final_extracted_data} \t{type(Final_extracted_data)}\n","0")

        return Final_extracted_data
           
