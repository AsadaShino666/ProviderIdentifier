from tqdm import tqdm
import time
Ban = ["proxy", "priva", "n/a", 'redacted', "domain admin", "domain manag", "disclosed",
               "reactivation period", "whois agent", "for sale", "domain registrar", "administrator domain",
               "admin contact", "domain contact", "protect", "statutory masking enabled", "guard", "non-public",
               "registrant", "null", "masked", "none", "na", "hidden", "registrator domennih imen", "registrar", "隐私"]

def load_other_data(WHOIS_file, Certificates_file, IP_file):
    #WHOIS_file = "All_effective_WHOIS.txt"
    #Certificates_file = "All_effective_certificates.txt"
    #IP_file = "All_effective_IP.txt"

    WHOIS = dict()
    for line in open(WHOIS_file, "r"):
        line = line[0:-1]
        line = line.split("\t\t\t")
        Name = line[0]
        WHOIS_data_list = line[1]
        WHOIS[Name] = list()
        WHOIS_data_list = WHOIS_data_list.split("\t")
        for item in WHOIS_data_list:
            if item == "None":
                continue
            if item == "":
                continue
            if item in Ban:
                continue
            WHOIS[Name].append(item)

        if len(WHOIS[Name]) == 0:
            WHOIS.pop(Name)

    Certificates = dict()
    for line in open(Certificates_file, "r"):
        line = line[0:-1]
        line = line.split("\t")
        if line[1].lower() in Ban or line[1] in Ban or line[1] == "":
            continue
        Certificates[line[0]] = line[1]

    NS_IP = dict()
    for line in open(IP_file, "r"):
        line = line[0:-1]
        line = line.split("\t")
        Name = line[0]
        NS_IP[Name] = list()
        line = line[1].split(" ")
        for item in line:
            if item == "":
                continue
            NS_IP[Name].append(item)

    IP_dict = dict()
    for NS in NS_IP:
        L = tuple(NS_IP[NS])
        if L not in IP_dict:
            IP_dict[L] = set()
        IP_dict[L].add(NS)

    return WHOIS, Certificates, NS_IP, IP_dict

def Load_zonefile(filename):
    #filename = "Hosting_relationship.txt"
    NS_set = set()
    print("Readfile")
    line_num = 0
    for line in open(filename, "r"):
        line_num += 1

    Num_of_User_Name = 0
    user_Name_num_dict = dict()
    Host_dict = dict()
    Num_main = 0
    Name_Num_dict_main = dict()
    Num_Name_dict_main = dict()
    Fa = dict()
    Hosted_by = dict()
    pbar = tqdm(total=line_num)
    for line in open(filename, "r"):
        pbar.update(1)
        line = line[0:-1]
        line = line.split("\t\t")
        Name = line[0]
        NS_name = line[-1]
        if NS_name[-1] == ".":
            NS_name = NS_name[0:-1]
        NS_set.add(NS_name)
        if NS_name not in Name_Num_dict_main:
            Num_main += 1
            Name_Num_dict_main[NS_name] = Num_main
            Num_Name_dict_main[Num_main] = NS_name
            Fa[Num_main] = Num_main
        if Name not in user_Name_num_dict:
            Num_of_User_Name += 1
            user_Name_num_dict[Name] = Num_of_User_Name
        if Name_Num_dict_main[NS_name] not in Host_dict:
            Host_dict[Name_Num_dict_main[NS_name]] = set()
        Host_dict[Name_Num_dict_main[NS_name]].add(user_Name_num_dict[Name])
        if user_Name_num_dict[Name] not in Hosted_by:
            Hosted_by[user_Name_num_dict[Name]] = set()
        Hosted_by[user_Name_num_dict[Name]].add(Name_Num_dict_main[NS_name])
    pbar.close()
    print("Readfile done")

    return NS_set, Num_of_User_Name, user_Name_num_dict, Host_dict, Num_main, Name_Num_dict_main, Num_Name_dict_main, Fa, Hosted_by
