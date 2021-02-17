import pickle as pk 

with open("user2info.pkl", "rb") as fp:
    user2info = pk.load(fp)


for k in user2info.keys(): 
    print(k) 
    print(user2info[k]["work_experience"])  
    print("\n")
    for k2 in user2info[k]["skill2endorsers"].keys():
        print(k2)
        print(user2info[k]["skill2endorsers"][k2])  
        print("\n")
    print("==========================================\n\n\n\n\n\n")