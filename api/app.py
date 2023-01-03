# app.py
from flask import Flask, abort, redirect, request, send_file, Response, make_response
from xray import create_acount, del_acount, get_acount, get_all_acount
import os, json, requests, traceback, codecs, string



app = Flask(__name__)
err_msg = {"status": 404 , "msg": "Error! Terjadi kesalahan..."}
key = open("key.txt","r").read()



def randomStr(count):
    tx = string.ascii_letters + string.digits
    ret = ''.join(random.choices(tx, k=count))
    return ret

def jsonify(data, status=200):
    response = make_response(json.dumps(data, indent=4, sort_keys=True))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response



@app.route('/api/<cmd>', methods=['POST', 'GET'])
def api(cmd):
    apikey = request.args.get("key")
    if apikey not in key: return jsonify({"ststus": 403, "message": "Key access denied"}, 403)
    if cmd == "create_acount":
        name = request.args.get("name")
        if not name: return jsonify({"ststus": 404, "message": "Please input query name.."}, 404)
        r = create_acount(name)
        if "status" in r and r["status"] == 404: return jsonify(r, 404)
        return jsonify(r)
        
    elif cmd == "del_acount":
        name = request.args.get("name")
        if not name: return jsonify({"ststus": 404, "message": "Please input query name.."}, 404)
        r = del_acount(name)
        if "status" in r and r["status"] == 404: return jsonify(r, 404)
        return jsonify(r)
        
    elif cmd == "get_acount":
        name = request.args.get("name")
        if not name: return jsonify({"ststus": 404, "message": "Please input query name.."}, 404)
        r = get_acount(name)
        if "status" in r and r["status"] == 404: return jsonify(r, 404)
        return jsonify(r)
        
    elif cmd == "get_all_acount":
        r = get_all_acount()
        return jsonify(r)
        

    
# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    app.run(host= "0.0.0.0", threaded=True, port=5000) 