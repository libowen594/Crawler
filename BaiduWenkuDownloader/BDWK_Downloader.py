import json
import time
import requests
import bs4
import Config
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class BaiduWenKu:
    @staticmethod
    def get_pageLoadUrls(url):
        pageLoadUrls = []
        title = ""
        doc_id = ""
        res = requests.get(url=url,
                           headers=Config.headers, verify=False)
        soup = bs4.BeautifulSoup(res.text, 'html5lib')
        scripts = soup.find_all('script')
        pattern = re.compile(r'varpageData=(.+?);')
        for script in scripts:
            s = script.get_text().replace(" ", "").replace("\n", "")
            text = re.findall(pattern, s)
            if text:
                doc_id = json.loads(text[0]).get("docInfo2019").get("doc_info").get("show_doc_id")
                title = json.loads(text[0]).get("docInfo2019").get("doc_info").get("title")
                for i in json.loads(json.loads(text[0]).get("readerInfo2019").get("htmlUrls")).get("json"):
                    pageLoadUrls.append(i["pageLoadUrl"])
                break
        return pageLoadUrls, title, doc_id

    @staticmethod
    def get_wenKuJson(url):
        response = requests.get(
            url=url,
            headers=Config.h, verify=False)
        pattern = re.compile(r'wenku_(\d+)' + r'\(' + '(.+)' + r'\)')
        json_str = re.findall(pattern, response.text)
        if json_str: return json_str[0]

    @staticmethod
    def get_textDict(json_str):
        position_list = []
        textDict = {}
        pageNum = json_str[0]
        body = json.loads(json_str[1]).get("body")
        for i in body:
            if i["t"] == "word":
                position = i["p"]["y"]
                text = i["c"]
                if position in position_list:
                    textDict[position] = textDict[position] + text
                else:
                    position_list.append(position)
                    textDict[position] = text
        return {pageNum: (position_list, textDict)}

    @staticmethod
    def printDoc(info):
        position_list = info[0]
        data = info[1]
        position_list.sort()
        for i in position_list:
            txt = data[i]
            print(txt)

    def run(self, url):
        start_time = time.time()
        pageLoadUrls, title, doc_id = self.get_pageLoadUrls(url)
        print(f"文档标题：{title}")
        print(f"文档id：{doc_id}")
        data = {}
        for i in pageLoadUrls:
            wenKuJson = self.get_wenKuJson(i)
            textDict = self.get_textDict(wenKuJson)
            data.update(textDict)
        pageNumList = [int(i) for i in data.keys()]
        pageNumList.sort()
        for i in pageNumList:
            info = data[str(i)]
            self.printDoc(info)
        end_time = time.time()
        print(f"解析完成: 文档标题={title},文档id={doc_id}, 总共用时{end_time-start_time}秒")


if __name__ == '__main__':
    BaiduWenKu().run(
        url="https://wenku.baidu.com/view/766985613c1ec5da50e2709e.html?fr=search-1-wk_sea_vip-income5&fixfr=mgtbbILMnPeckWEx5wss0w%3D%3D")