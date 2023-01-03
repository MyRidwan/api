from base64 import b64encode, b64decode
import json, os

domain_path = "/etc/xray/domain"
data_path = "/etc/xray/config.json"
user_data = "/etc/xray/user.json"
domain = open(domain_path, "r").read()

def random_uuid():
    id = os.popen("cat /proc/sys/kernel/random/uuid").read()
    return id.replace("\n","")

def decode(data):
    data = b64decode(data)
    return data.decode('utf-8')

def encode(msg):
    msg_bytes = msg.encode('utf-8')
    base64_bytes = b64encode(msg_bytes)
    return base64_bytes.decode('utf-8')

def read_config():
    return json.loads(open(data_path,"r").read())

def save_config(data):
    open(data_path,"w").write(json.dumps(data, indent=4))
    return read_config()

def read_user():
    return json.loads(open(user_data,"r").read())

def save_user(data):
    open(user_data,"w").write(json.dumps(data, indent=4))
    return read_user()


def cek_user(name):
    user = read_user()
    if name in user: 
        return user
    return False

def create_config(name):
    uuid = random_uuid()
    config = read_config()
    inbounds = []
    for i in config["inbounds"]:
        if i["protocol"] == "vless" or i["protocol"] == "vmess":
            new_user = {"id": str(uuid), "email": name}
            i["settings"]["clients"].append(new_user)
        if i["protocol"] == "trojan":
            new_user = {"password": str(uuid), "email": name}
            i["settings"]["clients"].append(new_user)
    save_config(config)
    return uuid

def create_acount(name):
    if  cek_user(name): return {"status": 404, "message": "user already exist.."}
    uuid = create_config(name)
    data_vmessWs =  {"add": domain,"aid": "0", "host": "","id": str(uuid),"net": "ws","path": "/xrayvws","port": "443","ps": name,"scy": "auto","sni": "","tls": "tls","type": "","v": "2"}
    data_vmessGrpc = {"add":domain,"aid":"0","host":"","id":str(uuid),"net":"grpc","path":"vmess-grpc","port":"443","ps":name,"scy":"auto","sni":"","tls":"tls","type":"gun","v":"2"}
    vmess_ws = "vmess://"+encode(json.dumps(data_vmessWs))
    vmess_grpc = "vmess://"+encode(json.dumps(data_vmessGrpc))
    vless_ws = f"vless://{uuid}@{domain}:443?path=/xrayws&security=tls&encryption=none&type=ws&sni=&host=#{name}"
    vless_grpc = f"vless://{uuid}@{domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc&sni=#{name}"
    trojan_ws = f"trojan://{uuid}@{domain}:443?path=/xraytrojanws&security=tls&host=&type=ws&sni=#{name}"
    trojan_grpc = f"trojan://{uuid}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni=#{name}"
    
    res = {"vmess_ws": vmess_ws,"vmess_grpc": vmess_grpc, "vless_ws": vless_ws, "vless_grpc": vless_grpc, "trojan_ws": trojan_ws, "trojan_grpc": trojan_grpc}
    user = read_user()
    user[name] = res
    save_user(user)
    os.system("restart-xray")
    return res


def get_acount(name):
    cek = cek_user(name)
    if cek:
        return cek[name]
    else:
        return {"status": 400, "message": "User not found"}

def get_all_acount():
    return read_user()

def del_acount(name):
    cek = cek_user(name)
    if cek:
        data = json.loads(open(data_path,"r").read())
        ls = []
        for i in data["inbounds"]:
            if i["protocol"] == "vless" or i["protocol"] == "vmess" or i["protocol"] == "trojan":
                for a in i["settings"]["clients"]:
                    if "email" in a and a["email"] == name:
                        continue
                    ls.append(a)
                i["settings"]["clients"] = []
                i["settings"]["clients"] = ls
                open(data_path,"w").write(json.dumps(data, indent=4))
                ls=[]
        del cek[name]
        save_user(cek)
        os.system("restart-xray")
        return {"status": 200, "message": f"User {name} deleted..."}
    else:
        return {"status": 404, "message": "User not found.."}

