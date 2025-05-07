This is the source code of *Decoding DNS Centralization: Measuring and Identifying NS Domains Across Hosting Providers*. We provide a complete example of the code, including its full input and the output files generated when run locally.

Here we will mainly outlines the input and output formats and examples for the provided code.

## Usage
Before the usage, please install all packages required.
```
pip install -r requirements.txt
```

If you want to run this tool, just run the main file.
```
python3 main.py
```
If it helps, we use Python 3.12 during the development of this tool.
## Input File Formats
In the source code, we require four input datasets: hosting relationships, WHOIS data, certificate data, and IP data. The input files are named `Example_hosting_relationship.txt`, `Example_whois.txt`, `Example_certificates.txt`, and `Example_ips.txt`, respectively. The code for input file naming is shown below, and you may modify it as needed.
```python
filename = "Example_hosting_relationship.txt"
WHOIS_file = "Example_whois.txt"
Certificates_file = "Example_certificates.txt"
IP_file = "Example_ips.txt"
NS_set, Num_of_User_Name, user_Name_num_dict, Host_dict, Num_main, Name_Num_dict_main, Num_Name_dict_main, Fa, Hosted_by = Load_data.Load_zonefile(filename)
WHOIS_data, Certificates, NS_IP, IP_dict = Load_data.load_other_data(WHOIS_file,
                                                                     Certificates_file,
                                                                     IP_file)
```
The code for reading the files is separated into `Load_data.py`.
### Hosting Relationships File
**Format:**
```plaintext
<user domain>\t\t<NS domain>\n
```
**Example:**
```
0-0-2.org.		ns-cloud-b1.googledomains.com
0-1-1.org.		ns31.domaincontrol.com
```

### WHOIS File
**Format:**
```plaintext
<Domain>\t\t\t<Registrant Organization>\t<Administrative Organization>\t<Technical Organization>\n  
```
If any of the three required fields are missing, `None` should be used as a replacement.

**Example:**
```
cloudflare.com			CloudFlare, Inc.	CloudFlare, Inc.	CloudFlare, Inc.
dns03.nexties.net			None	NEXTIES NEXTIES
```

### Certificate File
**Format:**
```plaintext
<domain>\t<Organization Name>\n
```
**Example:**
```
cloudflare.com	Cloudflare, Inc.
nicolas.ns.cloudflare.com	Cloudflare, Inc.
```

### IP File
**Format:**
```plaintext
<domain>\t<IP_1> <IP_2> ... <IP_n>\n
```
**Example:**
```
ns-cloud-a4.googledomains.com	216.239.38.106 
kim.ns.cloudflare.com	172.64.32.126 108.162.192.126 173.245.58.126
```

## Output File Formats
The program generates three output files: `Result_of_identification_Provider_and_NS.txt`, `Result_of_identification_NS_and_Provider.txt` and `Statistics_of_centralization.txt`. Their contents are as follows:

* `Result_of_identification_Provider_and_NS.txt`: NS domain names owned by each provider.

* `Result_of_identification_NS_and_Provider.txt`: NS domain names and their corresponding providers.

* `Statistics_of_centralization.txt`: Statistics on the domains hosted by each provider.
