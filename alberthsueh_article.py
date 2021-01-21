import os
import argparse
import json
import time
import glob
import requests
from lxml import etree



def line_broadcast(pid):
    with open('line_config.json', 'r') as f:
        config = json.load(f)
    f.close()
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(config['token'])
    }
    page = "http://www.alberthsueh.com/phpBB2/viewtopic.php?t={0}".format(pid)
    payload = json.dumps({"messages":[{"type":"text", "text":"{0}".format(page)}]})
    requests.request(
        "POST", url, headers=headers,
        data=payload)


def parse_args():
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="image path", type=str)
    parser.add_argument("-p", "--password", help="cofigure file path", type=str)
    args = parser.parse_args()
    return args


def main():
    url = "http://www.alberthsueh.com/phpBB2/login.php"
    response = requests.request("GET", url)
    sid = response.cookies.get_dict()["phpbb2mysql_sid"]

    args = parse_args()
    url = "http://www.alberthsueh.com/phpBB2/login.php"
    payload = {
        "username": args.user,
        "password": args.password,
        "redirect": "",
        "login": "登入",
    }
    headers = {
        "Host": "www.alberthsueh.com",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "http://www.alberthsueh.com/phpBB2/viewforum.php?f=140",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        "Cookie": "phpbb2mysql_sid={}".format(sid),
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    url = "http://www.alberthsueh.com/phpBB2/viewforum.php?f=140"
    response = requests.request("GET", url, headers=headers)

    html = etree.HTML(response.content)
    urls = html.xpath("//span[@class='topictitle']/a/@href")
    new_article = [i.split("t=")[1].replace("&view=newest", "") for i in urls]
    new_article.sort()
    html_folder = os.path.join(os.getenv("HOME"), "alberthsueh")
    saved_article = [
        i.split("_")[1].replace(".html", "")
        for i in glob.glob("{}/*.html".format(html_folder))
    ]
    saved_article.sort()

    pid = int(saved_article[-1])
    while pid < int(new_article[-1]):
        pid += 1
        url = "http://www.alberthsueh.com/phpBB2/viewtopic.php?t={}".format(pid)
        try:
            response = requests.request("GET", url, headers=headers)
            path = os.path.join(html_folder, "article_{}.html".format(pid))
            with open(path, "wb") as f:
                f.write(response.content)
            f.close()
            line_broadcast(pid)
            time.sleep(1)

        except:
            print("{} is bad".format(pid))


if __name__ == "__main__":
    main()
