import json
import os
import re
import requests
import sys
import random
import csv
import time
import zipfile
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
import traceback
import concurrent.futures

class Helper():

    def __init__(self):

        self.MAX_TRIALS = 3

    def get_url_response(self, url):

        print("Processing URL: ", url,)

        count = 0

        while count < self.MAX_TRIALS:
            try:
                headers = {
                    'Cookie': 'ak_bmsc=549F26DC47CA396FA9219F88EA3C3E85~000000000000000000000000000000~YAAQj+PfrYIa1Fh/AQAAJpdRdg/s+v0we8Bg1Dlf5l1f39/zp1AAXcBnxCKDqRmVYDkOcn8aItiF5Ef3ESu7T784YGF0bY6mhTrlEwVSHUHCYV+X94yaaY0b/zg8OgJFraYeiOJkdDPUKw8bN+ZdhzIv5vk2dv+sBRyYkRjL2rXUNRubITaABbilHSIal2sFI184v+1V16c5jvejT7aMA1tk4Z2SpSvc39RXUkG4MqRIKybPz+09hJvrmOKl/XvIThqNrwzZkV0sIz+shzqHOfJuzWl9p6WYkR8rQRxqQ9bW5EhHmFe7+BveHmcy8+cN75VtgUg6C3XvTr8pBuepYmfkGvPBE1j/2SyOSQ22WjveyBRReqs1zIdUvfZGyjGhRA==; ASP.NET_SessionId=vwbel4xgrga0kyswsl5n3yl0; IpLocation={"IPLocationID":0,"StartingIP":0,"EndingIP":0,"CountryCode":"KR","CountryName":null,"StateProvName":null,"CityName":"Jeonnong-Dong","PostalCode":"02543","County":null,"StateProvCode":"11","Latitude":37.58,"Longitude":127.05,"Shard":0,"ActualIP":3552587152,"CountryID":52,"RegionID":null}; IpLocationChecked=True; __AntiXsrfToken=159a67ecd1c144728ab77c2ae4f62f5f; _bbs.uid=a3d63c2f-3d38-469c-a1c7-361eca082f43; _track_tkn=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJhM2Q2M2MyZi0zZDM4LTQ2OWMtYTFjNy0zNjFlY2EwODJmNDMiLCJqdGkiOiI4MjM3N2JjOS1kZTgxLTQ2Y2ItOWUzNi04YWZjNTllY2JjNGMiLCJlbnMiOiIyMCIsInN1aWQiOiIiLCJiZnNyIjoiMCIsImRpZCI6IjEwIiwidWFpZCI6IjIyMjczNSIsInVpcCI6IjIxMS4xOTIuNDUuMTQ0IiwiZXhwIjoxNjQ2OTcxOTMwLCJpc3MiOiJodHRwczovL2FwaS5iaXpidXlzZWxsLmNvbSIsImF1ZCI6ImJpemJ1eXNlbGwifQ.p9nveXV2AxXCj-YcFAQC6HpuRQFw8IgApAGovzIfdLY; ss_o=true'
                }
                return requests.get(url, headers=headers, timeout=30).text

            except Exception as error:
                print('Error in getting URL response: ', error)

            count += 1

        return False

    def make_soup_url(self, url):
        return BeautifulSoup(self.get_url_response(url), 'lxml')

    def read_txt_file(self, filename):
        with open(filename) as infile:
            ids = [row.replace('\n', '').replace('\r', '') for row in infile]
        return ids

    def reading_csv(self, csv_filename):
        f = open(csv_filename, 'r', encoding='utf-8', errors='replace')
        csv_data = []
        reader = csv.reader(f)
        for row in reader:
            csv_data.append(row)

        f.close()
        return csv_data

    def writing_csv(self, data, csv_filename):

        myFile = open(csv_filename, 'w', newline='',
                      encoding='utf-8', errors='replace')
        with myFile:
            writer = csv.writer(myFile, quoting=csv.QUOTE_ALL)
            writer.writerows(data)

        return csv_filename

    def checking_folder_existence(self, dest_dir):
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
            print("Directory ", dest_dir,  " Created ")
        else:
            pass
            # print("Directory " , dest_dir ,  " Exists ")

        return dest_dir

    def write_json_file(self, data, filename):

        while 1:
            try:
                with open(filename, 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, indent=4)
                break
            except Exception as error:
                print("Error in writing Json file: ", error)
                time.sleep(1)

    def read_json_file(self, filename):
        data = {}
        with open(filename, encoding='utf-8') as json_data:
            data = json.load(json_data)
        return data

    def is_file_exist(self, filename):
        if os.path.exists(filename):
            return True
        else:
            return False

    def list_all_files(self, directory, extension):
        all_files = []
        for file in os.listdir(directory):
            if file.endswith(extension):
                all_files.append(os.path.join(directory, file))
        return all_files

    def write_random_file(self, text, file_name):
        file = open(file_name, "w", encoding='utf-8')
        file.write(str(text))
        file.close()

    def read_random_file(self, file_name):
        f = open(file_name, "r", encoding='utf-8')
        return f.read()

    def get_time_stamp(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def json_exist_data(self, fileName):
        json_data = []
        if self.is_file_exist(fileName):
            json_data = self.read_json_file(fileName)
        return json_data

    def log_error(self, text, fileName,):
        self.checking_folder_existence('logs')
        if self.is_file_exist('logs\\'+fileName):
            file = open("logs\\" +fileName, "a", encoding='utf-8')
            file.write(str(text) + "\n" + "*"*100)
            file.write(str(text))
            file.close()
        else:
            file = open("logs\\"+ str(fileName), "w", encoding='utf-8')
            file.write(str(text) + "\n" + "*"*100)
            file.write(str(text))
            file.close()
    
    def run_multiThread(self,function,max_workers,*args):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(function, args)  

    def dollar_to_int(self,text):
        try:
            return int(text.replace("$", "").replace(",", ""))
        except:
            return 0
    
    def get_text_from_tag(self,tag):
        if tag is not None:
            return tag.text.strip()
        return ""


    def get_url_from_tag(self,tag):
        if tag is not None:
            try:
                return tag['href']
            except:
                pass
        return ""