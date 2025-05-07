from tqdm import tqdm
import time
import json
import tldextract
import re
import sys
import Load_data
sys.setrecursionlimit(1 << 25)

class Edge:
    __slots__ = ['From', 'To', 'Next', 'Type'] 
    def __init__(self, From, To, Next, Type):
        self.From, self.To, self.Next, self.Type = From, To, Next, Type

NS_number = 1
head = list()
cnt_edge = 0
Edge_list = list()
Fa = dict()
Num_Name_dict_main = dict()
Num_of_subdomain = dict()
TLD_of_ns_num = dict()
Hosted_by = dict()
Ban_TLD = {"cm", "commmm", "com2", "comv", "ro", "comm", "or", "lol", "xyz", "comf"}

Have_Edge = set()
def Find(item):
    if Fa[item] == item:
        return item
    Fa[item] = Find(Fa[item])
    return Fa[item]

def AddEdge(From, To, Type):
    global cnt_edge
    if From == To:
        return
    cnt_edge += 1
    Next = head[From]
    Edge_list.append(Edge(From, To, Next, Type))
    head[From] = cnt_edge

def deal_file(Num_to_SLD, Cycle_Type):
    global Num_of_subdomain
    global Hosted_by
    chengfen = dict()
    pbar = tqdm(total=len(Hosted_by))
    NS_hosting_num = dict()
    for item in Hosted_by:
        pbar.update(1)
        NS_Num_list = set()
        for NS_num in Hosted_by[item]:
            NS_num = Find(NS_num)
            NS_Num_list.add(NS_num)
            if NS_num not in NS_hosting_num:
                NS_hosting_num[NS_num] = set()
            NS_hosting_num[NS_num].add(item)

        Len = len(NS_Num_list)
        if Len <= 1:
            continue
        NS_Num_list = list(NS_Num_list)
        for i in range(Len):
            if NS_Num_list[i] not in chengfen:
                chengfen[NS_Num_list[i]] = dict()
            for j in range(Len):
                if j == i:
                    continue
                if NS_Num_list[j] not in chengfen[NS_Num_list[i]]:
                    chengfen[NS_Num_list[i]][NS_Num_list[j]] = 0
                chengfen[NS_Num_list[i]][NS_Num_list[j]] += 1

    pbar.close()
    for item in NS_hosting_num:
        NS_hosting_num[item] = len(NS_hosting_num[item])
    global Edge_list, cnt_edge
    Edge_list.clear()
    Edge_list.append(Edge(0, 0, 0, False))
    cnt_edge = 0

    chengfen_copy = dict()
    for item in chengfen:
        chengfen_copy[item] = chengfen[item].copy()
    pbar = tqdm(total=len(chengfen))
    for From in chengfen:
        pbar.update(1)
        if len(chengfen[From]) == 0:
            continue
        for To in chengfen[From]:
            if From == To:
                continue
            if Cycle_Type == 0:
                if Num_to_SLD[From] == Num_to_SLD[To] and Num_of_subdomain[From] == Num_of_subdomain[To] and (TLD_of_ns_num[From] == TLD_of_ns_num[To] or (TLD_of_ns_num[From] not in Ban_TLD and TLD_of_ns_num[To] not in Ban_TLD)):
                    AddEdge(From, To, True)
                    Have_Edge.add((From, To))
                    continue
            if Cycle_Type == 1:
                if chengfen[From][To]/NS_hosting_num[From] >= 0.901:
                    AddEdge(From, To, True)
    pbar.close()
    return NS_hosting_num, chengfen_copy

def Search_SCC(dfn, low, s, in_stack, scc, sz):
    global dfncnt, tp, sc
    dfncnt = 0
    tp = 0
    sc = 0

    def tarjan(u):
        global dfncnt, tp, sc
        dfncnt += 1
        low[u] = dfn[u] = dfncnt
        tp = tp + 1
        s[tp] = u
        in_stack[u] = True
        i = head[u]
        while i:
            if Edge_list[i].Type == False:
                i = Edge_list[i].Next
                continue
            v = Edge_list[i].To
            if dfn[v] == 0:
                tarjan(v)
                low[u] = min(low[u], low[v])
            elif in_stack[v]:
                low[u] = min(low[u], dfn[v])
            i = Edge_list[i].Next
            if i == 0:
                break
        if dfn[u] == low[u]:
            sc = sc + 1
            while s[tp] != u:
                scc[s[tp]] = sc
                sz[sc] = sz[sc] + 1
                in_stack[s[tp]] = False
                tp = tp - 1
            scc[s[tp]] = sc
            sz[sc] = sz[sc] + 1
            in_stack[s[tp]] = 0
            tp = tp - 1
    pbar = tqdm(total=NS_number)
    for i in range(1, NS_number):
        pbar.update(1)
        if i not in Fa:
            continue
        if i != Find(i):
            continue
        if scc[i] == 0:
            tarjan(i)
    pbar.close()

    SCC = dict()
    for i in range(1, NS_number):
        if i not in Fa:
            continue
        if i != Find(i):
            continue
        if scc[i] == 0:
            continue
        if sz[scc[i]] == 1:
            continue
        if scc[i] not in SCC:
            SCC[scc[i]] = list()
        SCC[scc[i]].append(i)
    return SCC

company_suffixes =     ["ltd", "Co.", "Inc", "LLC", "GmbH", "AG", "S.A.", "S/A", "pte ltd", 'SAS',
                        "Sp. z o.o.", "Oy", "B.V", "OOO", "Pte. Ltd.", "Sdn. Bhd.", '.com',
                        "Co., Ltd.", "CORP.", "LIMITED",  "s.r.o.", "Corporation", 'Ltda',
                        "LTD", "a.s.", "j.d.o.o", "INC", "S.r.l.", "CO.", "ApS", "SRL", 'Ditta',
                        "s. r. o.", "Co.,Ltd", "d.o.o.", "SP Z O O", "LLP", "ZO.O.", 'Spa', 'S.p.A', 'Societa',
                        "a.s.", "s.r.l.", "TOV", "s.p.", "Group", "operating",  "company", "limit", "Digital",
                        "technologies", "technology", "science", "netcom", "online", 'Computer', 'Systems', "Media",  "Services", "Service",
                        "networks", "network", "communication", "Software", "zaixian", "wangluo", 'system',
                        "jishu", "youxian", "gongsi",  "cn", "Tic.Ltd.Sti", 'Internet', "Redemption",
                        "International", "Hong Kong", "Beijing", "Taiwan", "China", 'Shenzhen', 'Brasil', 'US', "Temple",
                        "Bilisim", "Solutions", "Xiamen",  ",", ".", "\"", " ", "(", ")"]

def remove_company_suffixes(input_str):
    for suffix in company_suffixes:
        input_str = input_str.replace(suffix.lower(), "")
    return input_str.strip()

def Comp_str(Str_list, Flag=False):
    def filter_string(string:str):
        string = str(string)
        Str = ""
        for s in string:
            Str += s
        Str = Str.lower()
        Str = remove_company_suffixes(Str)
        pattern = r"[^a-zA-Z0-9]+"
        filtered_string = re.sub(pattern, '', Str).lower()
        if filtered_string != "":
            return filtered_string
        else:
            return string

    def normalized_edit_distance(str1, str2):
        m, n = len(str1), len(str2)
        if m < n:
            str1, str2 = str2, str1
            m, n = n, m
        if max(m,n) == 0:
            return False
        dp = [[0] * (n + 1) for _ in range(2)]
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            dp[i % 2][0] = i
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i % 2][j] = dp[(i - 1) % 2][j - 1]
                else:
                    dp[i % 2][j] = min(dp[(i - 1) % 2][j], dp[i % 2][j - 1], dp[(i - 1) % 2][j - 1]) + 1
        return dp[m % 2][n] / max(m, n)

    def baseline(a1, b1):
        if a1 == b1:
            return 2
        if normalized_edit_distance(a1, b1) < 0.15:
            if len(a1) > len(b1):
                return 1
            else:
                return -1
        else:
            return 0
    def Pre_del(a):
        pattern = r"[^\u4e00-\u9fa5\u3040-\u30FF\uAC00-\uD7AF\u0400-\u04FF\u0600-\u06FFa-zA-Z0-9]+"
        a1 = re.sub(pattern, '', filter_string(a)).lower()
        if a1 == "":
            a1 = filter_string(a)
        return a1

    fa_Final = dict()
    for item in Str_list:
        fa_Final[item] = item
    Deal = dict()
    Len = len(Str_list)
    Dict_after_deal = dict()
    Fa_deal = dict()
    Deal_list = set()
    for i in range(Len):
        Deal[Str_list[i]] = Pre_del(Str_list[i])
        Deal_list.add(Deal[Str_list[i]])
        if Deal[Str_list[i]] not in Dict_after_deal:
            Dict_after_deal[Deal[Str_list[i]]] = list()
            Fa_deal[Deal[Str_list[i]]] = Deal[Str_list[i]]
        Dict_after_deal[Deal[Str_list[i]]].append(Str_list[i])
    for item in Dict_after_deal:
        Min = 6553665536
        Min_str = ""
        for Str in Dict_after_deal[item]:
            if len(Str) < Min:
                Min = len(Str)
                Min_str = Str
        for Str in Dict_after_deal[item]:
            fa_Final[Str] = Min_str
    return fa_Final

def First_cycle(Num_main, Name_Num_dict_main, Num_to_SLD, IP_dict):
    global head, NS_number, dfn, low, s, in_stack, scc, sz
    head = [0] * (Num_main + 1)
    NS_number = Num_main + 1
    dfn = [0] * 100 * (Num_main + 1)
    low = [0] * 100 * (Num_main + 1)
    s = [0] * 100 * (Num_main + 1)
    in_stack = [0] * (Num_main + 1)
    scc = [0] * (Num_main + 1)
    sz = [0] * (Num_main + 1)

    print("Step1:Sturcture similarity Start")
    S = time.time()
    NS_hosting_num, chengfen_copy = deal_file(Num_to_SLD, 0)
    T = time.time()
    for item in IP_dict:
        if len(IP_dict[item]) <= 1:
            continue
        L = list(IP_dict[item])
        Temp = set()
        for i in range(len(L)):
            NS = L[i]
            if NS not in NS_to_SLD:
                continue
            if NS_to_SLD[NS] in Temp:
                continue
            Temp.add(NS_to_SLD[NS])
            F = Find(Name_Num_dict_main[NS])
            for j in range(i+1, len(L)):
                NS_j = L[j]
                if NS_j not in NS_to_SLD:
                    continue
                if NS_to_SLD[NS_j]!= NS_to_SLD[NS]:
                    continue
                if Num_of_subdomain[F] != Num_of_subdomain[Find(Name_Num_dict_main[NS_j])]:
                    continue
                if TLD_of_ns_num[F] != TLD_of_ns_num[Find(Name_Num_dict_main[NS_j])] and (TLD_of_ns_num[F] in Ban_TLD or TLD_of_ns_num[Find(Name_Num_dict_main[NS_j])] in Ban_TLD):
                    continue
                if ((Find(Name_Num_dict_main[NS_j]), F)) not in Have_Edge:
                    AddEdge(Find(Name_Num_dict_main[NS_j]), F, True)
                if ((F, Find(Name_Num_dict_main[NS_j]))) not in Have_Edge:
                    AddEdge(F, Find(Name_Num_dict_main[NS_j]), True)

    Have_Edge.clear()
    SCC = Search_SCC(dfn, low, s, in_stack, scc, sz)
    for item in SCC:
        Max_key = Find(SCC[item][0])
        Max = NS_hosting_num[Max_key]
        for i in SCC[item]:
            if NS_hosting_num[Find(i)] > Max:
                Max_key = Find(i)
                Max = NS_hosting_num[Max_key]
        for i in SCC[item]:
            Fa[Find(i)] = Find(Max_key)
    print("End")

def Repeat_cycle_One(Num_main, Num_to_SLD):
    global head, NS_number, dfn, low, s, in_stack, scc, sz, Have_Edge
    Have_Edge.clear()
    head = [0] * (Num_main + 1)
    NS_number = Num_main + 1
    S = time.time()
    NS_hosting_num, chengfen_copy = deal_file(Num_to_SLD, 1)
    T = time.time()

    dfn = [0] * 100 * (Num_main + 1)
    low = [0] * 100 * (Num_main + 1)
    s = [0] * 100 * (Num_main + 1)
    in_stack = [0] * (Num_main + 1)
    scc = [0] * (Num_main + 1)
    sz = [0] * (Num_main + 1)
    SCC = Search_SCC(dfn, low, s, in_stack, scc, sz)

    if len(SCC) == 0:
        List = set()
        for item in NS_hosting_num:
            List.add((Find(item), NS_hosting_num[Find(item)]))
        List = list(List)
        List.sort(key=lambda x:x[1])
        Flag = False
        num = 0
        for item in List:
            NS_num = item[0]
            Host_num = item[1]
            if len(head) <= NS_num or head[NS_num] == 0:
                continue
            i = head[NS_num]
            Max = 0
            Max_key = 0
            while i != 0:
                To = Find(Edge_list[i].To)
                if NS_hosting_num[To] >= Max:
                    Max_key = To
                    Max = NS_hosting_num[To]
                i = Edge_list[i].Next
            if Max < Host_num:
                continue
            Fa[Find(NS_num)] = Find(Max_key)
            Flag = True
            num += 1
        return Flag, T-S

    for item in SCC:
        Max_key = Find(SCC[item][0])
        Max = NS_hosting_num[Max_key]
        for i in SCC[item]:
            if NS_hosting_num[Find(i)] > Max:
                Max_key = Find(i)
                Max = NS_hosting_num[Max_key]
        for i in SCC[item]:
            Fa[Find(i)] = Max_key
    return True, T-S

if __name__ == '__main__':
    filename = "Example_hosting_relationship.txt"
    WHOIS_file = "Example_whois.txt"
    Certificates_file = "Example_certificates.txt"
    IP_file = "Example_ips.txt"
    NS_set, Num_of_User_Name, user_Name_num_dict, Host_dict, Num_main, Name_Num_dict_main, Num_Name_dict_main, Fa, Hosted_by = Load_data.Load_zonefile(filename)
    WHOIS_data, Certificates, NS_IP, IP_dict = Load_data.load_other_data(WHOIS_file,
                                                                         Certificates_file,
                                                                         IP_file)
    Result_1_filename = "Result_of_identification_Provider_and_NS.txt"
    Result_3_filename = "Statistics_of_centralization.txt"
    Result_2_filename = "Result_of_identification_NS_and_Provider.txt"
    Num_of_NS = len(NS_set)
    Results_1 = dict()
    Results_2 = dict()
    Extract_set = set()
    NS_to_SLD = dict()
    NS_to_SLD_2 = dict()
    NS_to_SLD_3 = dict()
    Num_to_SLD = dict()
    for NS in NS_set:
        Extract = tldextract.extract(NS)
        NS_to_SLD_3[NS] = Extract.domain
        NS_to_SLD_2[NS] = Extract.domain+"."+Extract.suffix
        TLD_of_ns_num[Name_Num_dict_main[NS]] = Extract.suffix
        Subdomain = Extract.subdomain
        Subdomain = Subdomain.split(".")
        Num_of_subdomain[Name_Num_dict_main[NS]] = len(Subdomain)
        if len(Subdomain) <= 1:
            Subdomain = ""
        else:
            Subdomain = Subdomain[-1]
        Extract = Subdomain + Extract.domain
        Extract = Extract.lower()

        pattern = r"[^a-z0-9]+"
        Extract_copy = re.sub(pattern, '', Extract).lower()
        if Extract_copy != "":
            Extract = Extract_copy
            pattern = r"[^a-z]+"
            Extract_copy = re.sub(pattern, '', Extract).lower()
            if Extract_copy != "":
                Extract = Extract_copy
        NS_to_SLD[NS] = Extract
        Num_to_SLD[Name_Num_dict_main[NS]] = Extract
        Extract_set.add(Extract)

    F = open("Extract_set.txt", "w")
    for item in Extract_set:
        F.writelines(item+"\n")
    F.close()

    First_cycle(Num_main, Name_Num_dict_main, Num_to_SLD, IP_dict)
    Results_1_copy = Results_1.copy()
    for NS_num in Fa:
        Key = (False, Find(NS_num))
        if Key not in Results_1_copy:
            Results_1_copy[Key] = set()
        Results_1_copy[Key].add(Num_Name_dict_main[NS_num])
        Results_2[Num_Name_dict_main[NS_num]] = Key
        continue

    print("Step2: Co-hosting similarity Start")
    num = 1
    while True:
        print("Round",num,"begin")
        Flag,D = Repeat_cycle_One(Num_main, Num_to_SLD)
        print("Round", num, "End")
        num += 1
        if Flag == False:
            break
    print("Step2 done")

    for NS_num in Fa:
        Key = (False, Find(NS_num))
        if Key not in Results_1:
            Results_1[Key] = set()
        Results_1[Key].add(Num_Name_dict_main[NS_num])
        Results_2[Num_Name_dict_main[NS_num]] = Key
        continue

    Results_1_copy = Results_1.copy()

    for item in Results_1_copy:
        if item[0] == True:
            continue
        D = dict()
        for NS in Results_1_copy[item]:
            if NS_to_SLD[NS] not in D:
                D[NS_to_SLD[NS]] = 0
            D[NS_to_SLD[NS]] += 1
        Max = 0
        Max_key = ""
        for i in D:
            if D[i] > Max:
                Max_key = i
                Max = D[i]
        if (False, Max_key) not in Results_1:
            Results_1[(False, Max_key)] = set()
        for NS in Results_1_copy[item]:
            Results_1[(False, Max_key)].add(NS)
            Results_2[NS] = (False, Max_key)
        Results_1.pop(item)

    Results_1_copy = Results_1.copy()

    pbar = tqdm(total=len(Results_1_copy))
    print("Labeling and Merge Groups")
    for item in Results_1_copy:
        pbar.update(1)
        Score_list = dict()
        if item[0] == True:
            continue
        for NS_domain in Results_1_copy[item]:
            if NS_domain in NS_to_SLD_2:
                SLD = NS_to_SLD_2[NS_domain]
                if NS_to_SLD_3[NS_domain] not in Score_list:
                    Score_list[NS_to_SLD_3[NS_domain]] = 0
                Score_list[NS_to_SLD_3[NS_domain]] += 0.001*len(Host_dict[Name_Num_dict_main[NS_domain]])
            else:
                Extract = tldextract.extract(NS_domain)
                if Extract.domain not in Score_list:
                    Score_list[Extract.domain] = 0
                Score_list[Extract.domain] += 0.001*len(Host_dict[Name_Num_dict_main[NS_domain]])
                SLD = Extract.domain + "." + Extract.suffix
                NS_to_SLD_2[NS_domain] = SLD
            if NS_domain in WHOIS_data:
                Key = NS_domain
                for i in range(3):
                    Key_WHOIS = WHOIS_data[Key][i]
                    if Key_WHOIS == "":
                        continue
                    if Key_WHOIS not in Score_list:
                        Score_list[Key_WHOIS] = 0
                    Score_list[Key_WHOIS] += 1.0 * len(Host_dict[Name_Num_dict_main[NS_domain]])
            elif SLD in WHOIS_data:
                Key = SLD
                for i in range(3):
                    Key_WHOIS = WHOIS_data[Key][i]
                    if Key_WHOIS == "":
                        continue
                    if Key_WHOIS not in Score_list:
                        Score_list[Key_WHOIS] = 0
                    Score_list[Key_WHOIS] += 1.0 * len(Host_dict[Name_Num_dict_main[NS_domain]])
            OrganizationName = ""
            if NS_domain in Certificates:
                OrganizationName = Certificates[NS_domain]
            elif SLD in Certificates:
                OrganizationName = Certificates[SLD]
            if OrganizationName != "":
                if OrganizationName not in Score_list:
                    Score_list[OrganizationName] = 0
                Score_list[OrganizationName] += 1.0 * len(Host_dict[Name_Num_dict_main[NS_domain]])
        Temp_score = Score_list.copy()
        Fa = dict()
        Fa = Comp_str(list(Temp_score.keys())).copy()

        for key in Temp_score.keys():
            if Fa[key] == key:
                continue
            Fa[key] = Find(key)
            Score_list[Fa[key]] += Score_list[key]
            Score_list.pop(key)

        Key, Max = "", 0
        for key in Score_list.keys():
            if Score_list[key] > Max:
                Key = key
                Max = Score_list[key]
        if Key == "":
            continue

        Key = (True, Key)
        if Key not in Results_1:
            Results_1[Key] = set()
        for NS in Results_1_copy[item]:
            Results_1[Key].add(NS)
            Results_2[NS] = Key
        Results_1.pop(item)
    pbar.close()

    Results_1_copy = Results_1.copy()

    Fa = dict()
    for key in Results_1:
        Fa[key[1]] = key[1]
    Fa = Comp_str(list(Fa.keys()), True).copy()
    for key in Results_1.copy():
        if Fa[key[1]] == key[1]:
            continue
        Fa[key[1]] = Find(key[1])
        fa = Fa[key[1]]
        K = (True, fa)
        if K not in Results_1:
            Results_1[K] = set()
        for NS in Results_1[key]:
            Results_1[K].add(NS)
            Results_2[NS] = K
        Results_1.pop(key)

    Results_1_copy = Results_1.copy()
    for Key in Results_1_copy.copy():
        if Key[0] == True:
            continue
        Results_1_copy.pop(Key)

    Fa.clear()
    Fa = dict()
    for Key in Results_1:
        if Key[1] not in Name_Num_dict_main:
            Num_main += 1
            Name_Num_dict_main[Key[1]] = Num_main
            Num_Name_dict_main[Num_main] = Key[1]
        Fa[Name_Num_dict_main[Key[1]]] = Name_Num_dict_main[Key[1]]
        for NS in Results_1[Key]:
            Fa[Name_Num_dict_main[NS]] = Name_Num_dict_main[Key[1]]

    print("End")

    print("Step2 again")
    num = 1
    while True:
        print("Round", num, "begin")
        Flag, D = Repeat_cycle_One(Num_main, Num_to_SLD)
        print("Round", num, "End")
        num += 1
        if Flag == False:
            break
    print("Step2 again End")


    for item in Results_1.copy():
        K = Name_Num_dict_main[item[1]]
        if Find(K) == K:
            continue
        fa = Find(K)
        fa = Num_Name_dict_main[fa]
        if (True, fa) in Results_1:
            Key = (True, fa)
        else:
            Key = (False, fa)
        for NS in Results_1[item]:
            Results_1[Key].add(NS)
            Results_2[NS] = Key
        Results_1.pop(item)

    remained_NS = set()
    for Key in Results_1.copy():
        if Key[0] == True:
            continue
        for NS in Results_1[Key]:
            Results_2.pop(NS)
            remained_NS.add(NS)
        Results_1.pop(Key)


    Entity_Host = dict()
    sum_Host = set()
    for Entity in Results_1:
        Entity_Host[Entity] = set()
        for NS in Results_1[Entity]:
            for Name_num in Host_dict[Name_Num_dict_main[NS]]:
                Entity_Host[Entity].add(Name_num)
                sum_Host.add(Name_num)
    sum_of_Host = len(sum_Host)

    print("All done",
          "\nnum of NS:", Num_of_NS,
          "\nnum of Entity:", len(Results_1),
          "\nnum of recognized_NS:", len(Results_2),
          "\nnum of user domain:", len(sum_Host))

    F = open(Result_1_filename, "w")
    for item in Results_1:
        F.writelines(item[1] + "\t\t" + str(len(Results_1[item])) + "\n")
        for i in Results_1[item]:
            F.writelines("\t" + i + "\n")
        F.writelines("\n\n")
    F.close()

    F = open(Result_2_filename, "w")
    for item in Results_1:
        for NS in Results_1[item]:
            F.writelines(NS+"\t\t"+item[1]+"\n")
    F.close()

    F = open(Result_3_filename, "w")
    F.writelines("Sum of user name\t" + str(len(sum_Host)) + "\n")
    pbar = tqdm(total=len(Entity_Host))
    List = list()
    for item in Entity_Host:
        List.append((item, len(Entity_Host[item])))
    List.sort(key=lambda x: x[1], reverse=True)
    List_2 = List.copy()
    for item in List:
        Entity_Max = item[0]
        pbar.update(1)
        F.writelines(Entity_Max[1] + "\t" + str(len(Entity_Host[Entity_Max])) + "\n")
        Entity_Host.pop(Entity_Max)
    F.close()
    pbar.close()