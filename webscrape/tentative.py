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
    cookie_str = 'li_sugr=2b62d20d-4905-444e-a538-f07a1feadb2f; bcookie="v=2&6f8410b8-b0d8-4b8f-8bf5-239142321e88"; lissc=1; bscookie="v=1&20201220200242e344c232-aa24-4519-8a27-d5da6b9506ceAQH71xyZxpNwSM1qSRHN1FShAdXZzBD-"; li_rm=AQGOQGh5fUe25wAAAXcdkjMFAjYe0or_97PLjw2NGfZh6pu0Tov0J624hwaTwTGnjhvFTXD9KU6MPwfRYE-kkKryJcGqwq1vjP1BH94G5dTNVUcibTpgw2Nb; _ga=GA1.2.388260073.1611108862; aam_uuid=17193061939447905092347891705167064179; g_state={"i_l":0}; JSESSIONID="ajax:6661573881781652824"; _gcl_au=1.1.1133925316.1612394929; timezone=America/Guatemala; _gid=GA1.2.361636778.1612997530; lang=v=2&lang=en-us; spectroscopyId=f25b1ae3-4235-432c-9b9a-d5ddd91c095b; AMCVS_14215E3D5995C57C0A495C55@AdobeOrg=1; li_oatml=AQHphKFmQsnfEAAAAXedJEu6wjMdOwdTn-Xo3WlQNwaLxaY0wLA5Bh-vWpXud-JMRpNS7BlbZIhhMVJMytgFQzwvIEz2Brjr; AMCV_14215E3D5995C57C0A495C55@AdobeOrg=-637568504|MCIDTS|18673|MCMID|16627044507729075582331259510278283192|MCAAMLH-1613877811|7|MCAAMB-1613877811|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1613280211s|NONE|vVersion|5.1.1|MCCIDH|-1705543759; UserMatchHistory=AQLicC0nuaE7rgAAAXefa7Fayxz6cH_kGA7mEHwKnRuSZL2JGKBXTIqNG7GK-iDszvQPUl04t0MqkV9fxs2QOznTs5K4NO0dPAYwMriMHVb3JUnvtv8TRxYPPjDUv_LKK3e6hMzMTy_qEWvJ2ZOrGCPnV2wEJn83mGlV1zOE3AWzJjXja-YKJDQLWXL6lsvIL4RPy-ypX9wjJXRu7Nmb9LoOFfaSOM3q3AQItOVUrNBOmfb-GID646eWolacbN9y9ikMMved3YOhEjDbNTXqZZDvk-NA-OhqurzR; lidc="b=VGST03:s=V:r=V:g=2239:u=1:i=1613290014:t=1613376414:v=1:sig=AQGHWXAzX4PXogDpnVtLT5FCEHQdY-FL"; fid=AQEkbzxtR1iepwAAAXefmB0ypLJAi1e1kLk56w0gbG1UHY5PYEj7xG87qnYO5QwxoZukKnr4hZag4g; ccookie=AQG/hou2WWLtzQAAAXefmIWIz6Jr0kzj0JkXz6wiMEPuC3oIU6PluhUpjd5460WFnjJbQA0pkW/Fd3Ob8ufBRwVyKHfmo+A/Etmek0er0tDWIs0uhi2t56AVIz/bIoPJTCiX9Q==; G_ENABLED_IDPS=google; fid=AQHuQUOQ04JdWgAAAXefnPqVfRN0QzZwaPi4NRVPh7Uib_sTJlKBSfdW5IiBDFIAy-bjnTKSMv_7BQ; _gat=1; fcookie=AQGGgMfVcEi5RwAAAXefnQaVyw9vSTFWS8Hh3TDLkIVInO-ey0q6Bv0_M7mk4ceN5Kr9aaylorBsyvgKBVfgnGhWoGVzOFHqu1aVSM0T6U7fZ5pGVdphZ8Cf8x_FOoBkeEaOobVnNIFGRb-9zl3CyH6WYGZ1cQP_ihXKJZ-CJf5iUda0QIH_lAsAjVW4pmTWiD1UJxQ1aZIxntG9PqCPu8pBzAJ0XJrb9kM_U2aLDNqhj2EtV_Mm65blOUWv2DZ8129C-vxl_XgC6JrNEIT2esdJG0kZ4k1Enrj4x/rj8kbyVRjhMOspl+PRbI+TGnVKK7x7kIfzVsWuWByFPUBZBCuHArYR7RaHkYGWdA=='
    cookies = cookie_parser(cookie_str) 
    
    # Extract user experience from user_base_url
    src_html = requests.get(user_base_url, cookies=cookies).text  
    experiences = extract_experience(src_html) 
    
    # Extract all skill_ids
    skill_src_html = requests.get(user_base_url + skill_suffix, cookies=cookies).text  
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

    while(len(queue) != 0):  
        top_id = queue.pop(0) 
        if top_id in visited_users: continue
        
        visited_users.add(top_id)

        try: 
            experiences, skill2endorsers = single_iteration(top_id) 
            user2info[top_id] = {"work_experience" : experiences, "skill2endorsers":skill2endorsers} 
            for l in skill2endorsers.values(): 
                for user in l:            
                    queue.append(user)
        except:
            print(f"Currently successfully recorded {count} users, failed on {len(visited_users) - count} users...") 
            continue 
            
        count += 1 
        print(f"Currently successfully recorded {count} users, failed on {len(visited_users) - count} users...") 
        if len(visited_users) % 20 == 0: sleep(60)  
        if (count >= 100): break  
        

    with open('user2info.pkl', 'wb') as fp:
        pickle.dump(user2info, fp, protocol=pickle.HIGHEST_PROTOCOL)
         