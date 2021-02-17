from bs4 import BeautifulSoup 
import numpy as np
import requests 
import re
import os, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep 
import json
import datetime
import pickle
import signal

"""
@param cookies string copied from Chrome - check tutorial for how to get it 
@return cookies as dict require by lib-requests 
"""
def cookie_parser(cookie_str):
    cookies = {}
    for line in cookie_str.split(";"): 
        k,v = re.findall(r"^(.*?)=(.*)$", line)[0] 
        cookies[k] = v 
    return cookies

    
"""
@param skill_html the response html
from https://www.linkedin.com/in/xxx(target)/detail/skills/ 

@return list of non-empty-endorsement skill list 
"""    
def extract_skill_ids(skill_html): 
    skill_html = skill_html.replace("&quot;",'"') # replace &quot with " 
    soup = BeautifulSoup(skill_html, "lxml") 
    match = soup.find(string=re.compile('{"data":{"metadata":{"totalSkills"')).strip() 
    infos = json.loads(match)["included"]   
    skill_ids = []
    for elem in infos[1:]: # skills start from 1
        try:
            num_endorse = elem.get("endorsementCount")
            if num_endorse is None: continue
            if num_endorse == 0: continue
            skill_id = re.findall(r"^urn:li:fs_skill:(.*)$", elem.get("*skill"))[0] # e.g.(ACoAACQ30jUBAxoeotKYnsef9J7yxyQO2tfueB0,9) 
            skill_ids.append(skill_id)
        except:
            continue 
            
    return skill_ids
        

""" 
@param url "e.g. https://www.linkedin.com/in/xxx(url_id)/detail/skills/(ACoAAA0V_egB97IzPVHIuTlAaxahei3kpbWJuYM,1)"  
@param cookies dictionary of cookies constructed earlier 
@return a list of endorser url_ids that endorsed the skill represented by the param url
"""
def extract_skill_endorsers(url, cookies):
    r = requests.get(url, cookies=cookies).text.replace("&quot;", '"') 
    sleep(np.random.rand(1, 2) * 10)
    data_infos = re.findall(r'({"data":.*?)\n', r) 
    endorser_infos = []
    skill_name = "" 
    endorser_names = set()
    
    for data in data_infos: 
        try:
            js_dic = json.loads(data) 
            if not "included" in js_dic.keys(): continue 
            if js_dic["included"][0].get("endorser") is None and js_dic["included"][1].get("endorser") is None:
                continue
            endorser_infos.append(js_dic)
            
                
        except: 
            continue
        
    for endorser_info_dic in endorser_infos:
        for elem in endorser_info_dic["included"]:
            try: 
                if "standardizedSkillUrn" in elem.keys():
                    skill_name = elem.get("name") if skill_name == "" else skill_name
                    continue

                if elem.get("publicIdentifier") is not None:  
                    user_url_id = elem.get("publicIdentifier")  
                    endorser_names.add(user_url_id) 
            except: 
                continue  

    return skill_name, list(endorser_names)




"""
Extract the past working experience of the user (not containing education experience) 
@param  src_html  response from https://www.linkedin.com/in/xxx(target)/ 
@return experiences as array of tuple : [(companyName1, companyID1, startDate1, endDate1)...]
""" 
def extract_experience(src_html):  
    wrapper = re.findall(r'({"data":{"entityUrn":.*?)\n',src_html.replace("&quot;",'"'))[-1]   
    dic = json.loads(wrapper)
    experiences = [] # Array of tuple : [(companyName, companyID, startDate, endDate)]
    for elem in dic["included"]:
        try:
            if elem.get("dateRange") == None: continue
            if elem.get("*company") == None: continue
            company_id = elem.get("*company")
            company_name = elem.get("companyName") 
            start_year = elem.get("dateRange").get("start").get("year")
            start_month = elem.get("dateRange").get("start").get("month")

            end = elem.get("dateRange").get("end")
            end = end if end is not None else {"year":datetime.datetime.now().year, "month": datetime.datetime.now().month}
            end_year = end.get("year")
            end_month = end.get("month") 

            start_date = datetime.datetime(start_year, start_month, 1)
            end_date = datetime.datetime(end_year, end_month, 1)
            experiences.append(tuple([company_name, company_id, start_date, end_date]))

        except: 
            continue 
            
    return experiences



"""
Run a single iteration of BFS 
Given the top user of queue, extract user experiences (as list), 
and skill2endorse (as dict) and return 
@param top user_id of BFS queue
@return experiences (list), skill2endorse (dict)
"""
def single_iteration(user_id): 
    user_base_url = f"https://www.linkedin.com/in/{user_id}/" 
    skill_suffix = "detail/skills/" 

    # Get cookie for session infomation to be used for requests
    cookie_str = 'bcookie="v=2&1f78842f-a151-4360-8ac2-31f1bbc2d39b"; bscookie="v=1&2021021704315186a72ec2-bc60-4326-814a-003b829d856eAQHz4JoFtIkUkWyrE6aXQTbBuijcFLKy"; lidc="b=TGST07:s=T:r=T:g=2004:u=1:i=1613540528:t=1613626784:v=1:sig=AQEha5_Zjt6j6vmTHmE_oCjUdoVmCfl5"; _ga=GA1.2.1559737382.1613536312; _gid=GA1.2.1694167689.1613536312; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C18676%7CMCMID%7C78801844199195096893114186480001794538%7CMCAAMLH-1614145186%7C7%7CMCAAMB-1614145186%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1613547586s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2008823391; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; aam_uuid=78956972041796514423168562877135467041; li_rm=AQHOGTJv25i5EAAAAXeuQkE6sw6sztgq5NHS8USlTobC1lm3PCTpguxLH91PeK2JwD-7GIPYGRNeW5k-l44E-J7n9i5zTPyYciJ_joSk6rFAuDf6ZMf8H49f; timezone=America/Chicago; UserMatchHistory=AQIKb89i5IMeQgAAAXeugouBtLRnOU9o85f5i9tKAIA3HoxcgnIDolbRB9VJpaC4N_y8xFRgHLWnuzoXvbU-lHV7ON-q4Z3CXpizHpLjvdrk2xUK2-SCqn21Q8oEJdBqpPfwvnyF87Tn_yl4JBMYt0PliZOr2d9DWyMtZwd3exwI-aQt4xEFH8vr2paBrA7lygjzVdD0MIy6SbUxW7nC2QKApJoKe7_kbeQ10DqreZgsaFS9sUL6r_ptufGV8R4oFigAasRqmZs9p6-SByuG8KPxiRebIFv7fCaThVg; li_sugr=e35415c5-b8a3-4b3b-a9fb-da8f4638e74e; AnalyticsSyncHistory=AQKpJM41wtiWCQAAAXeuRPalcGiTNduse-pD3v8RurQ7jQFvCwZylLBnttYbVPGeJDqWNZ22VExTFPDVaw27gQ; lms_ads=AQEx79nPATwCzAAAAXeuRPf_uj0qBtR0Taknh4EBQxIOgQNkRTQ4X4trhLwkcmCN3hXVyBozzGTaEzxeaac1mzvDPt5yGLmB; lms_analytics=AQEx79nPATwCzAAAAXeuRPf_uj0qBtR0Taknh4EBQxIOgQNkRTQ4X4trhLwkcmCN3hXVyBozzGTaEzxeaac1mzvDPt5yGLmB; visit=v=1&M; lang=v=2&lang=en-us; JSESSIONID=ajax:7755993694139518288; li_at=AQEDATR6hEwFUpVsAAABd66AXnUAAAF30ozidU4AVqQxUbooUQudhzPMpHtSo4CPS3uxvFjEVWgoY87AtoZVJCzgFb0nc11wC-nmz5yHyFiv0k-FhXOTe3055NI_rORgHl4-0OeXNfsdF5sRJjUJsBz5; liap=true; sdsc=22%3A1%2C1613540434448%7EJBSK%2C01We5iEWmvgqYjBgb0R1NgEsVPGQ%3D; _gcl_au=1.1.1504729621.1613540440'
    cookies = cookie_parser(cookie_str) 
    
    # Extract user experience from user_base_url
    src_html = requests.get(user_base_url, cookies=cookies).text  
    sleep(np.rand(1, 2) * 5)
    experiences = extract_experience(src_html) 
    
    # Extract all skill_ids
    skill_src_html = requests.get(user_base_url + skill_suffix, cookies=cookies).text  
    sleep(np.rand(1, 2) * 5)
    skill_ids = extract_skill_ids(skill_src_html)    
    
    # Based on skill_ids, construct all requests(skill pages) to be queried
    # e.g. https://www.linkedin.com/in/bharath-pattabiraman-66063761/detail/skills/(ACoAAA0V_egB97IzPVHIuTlAaxahei3kpbWJuYM,1)
    queries = [user_base_url + skill_suffix + skill_id for skill_id in skill_ids]  
    skill2endorsers = {}
    for q in queries:
        skill_name, endorsers = extract_skill_endorsers(q, cookies) 
        if skill_name == "" or len(endorsers) == 0: continue
        else: skill2endorsers[skill_name] = endorsers 
    return experiences, skill2endorsers


def handler_interupt(): 
    with open('user2info.pkl', 'wb') as fp:
        pickle.dump(user2info, fp, protocol=pickle.HIGHEST_PROTOCOL)
    exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler_interupt)
    queue = ["bharath-pattabiraman-66063761"] # Queue of identifier for BFS 
    visited_users = set() 
    user2info = {} 
    count = 0
    failure_count = 0

    while(len(queue) != 0):  
        top_id = queue.pop(0) 
        if top_id in visited_users: continue
        if failure_count > 10:
            break
        
        visited_users.add(top_id)

        try: 
            experiences, skill2endorsers = single_iteration(top_id) 
            user2info[top_id] = {"work_experience" : experiences, "skill2endorsers":skill2endorsers} 
            for l in skill2endorsers.values(): 
                for user in l:            
                    queue.append(user)

            with open('queue.pkl', 'r') as fp:
                data = fp.read()
            with open('queue.pkl', 'wb') as fp:
                pickle.dump(queue, fp, protocol=pickle.HIGHEST_PROTOCOL)

            with open('visited_users.pkl', 'r') as fp:
                data = fp.read()
            with open('visited_users.pkl', 'wb') as fp:
                pickle.dump(visited_users, fp, protocol=pickle.HIGHEST_PROTOCOL)

            failure_count = 0
            sleep(np.random.gamma(shape = 10.0, scale = 1.0))

        except:
            print(f"Currently successfully recorded {count} users, failed on {len(visited_users) - count} users...") 
            failure_count += 1
            sleep(np.random.gamma(shape = 10.0, scale = 1.0))
            continue 
            
        count += 1 
        print(f"Currently successfully recorded {count} users, failed on {len(visited_users) - count} users...") 
        if len(visited_users) % 20 == 0: sleep(60)  
        if (count >= 1000): break  
        

    with open('user2info.pkl', 'wb') as fp:
        pickle.dump(user2info, fp, protocol=pickle.HIGHEST_PROTOCOL)
         
