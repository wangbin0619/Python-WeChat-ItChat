'''获取一个公众号的所有历史发文urls，以utf-8的编码格式记录到一个csv文件中
使用说明：
需修改的参数：
savefile_name---保存的文件路径
num_pages---在公众号后台查看一共有多少页的数据
fakeid，token，cookie信息-----在浏览器开发者模式中查看
'''

import requests
import csv
import time
import json
from lxml import etree

import wechatsogou
ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)

from datetime import date, datetime, timedelta
today_date = date.today()
today = datetime(today_date.year, today_date.month, today_date.day, 00, 00, 00)
n_days_ago = today - timedelta(days=3)
tomorrow = today + timedelta(days=1)

def endable_request_debug():

    import logging
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.

    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1 #
    log_level = logging.DEBUG # logging.DEBUG

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(log_level)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(log_level)
    requests_log.propagate = True

#参数设置：
savefile_name = 'artical_list.csv' #需要自定义

#在公众号后台查看该公众号一共有多少页的发文数据，每页会显示5条记录,从0开始编号
num_pages = 1 #需要自定义
#注意不同时间，不同公众号的fakeid，token是不同的，使用时需要手动去公众号后台查询实时的值
fakeid = 'MzUyOTAxMjYzNQ=='
token = 1795502216
gzh = '北京日报'
query = '新增点位'
cookie = 'rewardsn=; wxtokenkey=777; ua_id=pKTI8NNRIj1MxlGcAAAAAHah7LJs7OUMigy6Ui4n47w=; wxuin=69451184656939; mm_lang=zh_CN; media_ticket=2fd1922395ebf54a1dcb7fb000dc3f86c53f420a; media_ticket_id=gh_9e353cf5f750; _clck=3290306867|1|f6w|0; sig=h01499401d03c943c5a9691ea494b7b611fd994ee639a7f36aa547c74c7146ee4e93e74c1a4db8eea38; uuid=2bede77325b060edafeabd1c3d34f58c; pgv_info=ssid=s4085553170; pgv_pvid=7170267550; rand_info=CAESIMDN0A1+bdJHVHazF2oOIIPfDeui6/SQ1G3fW19dqcZ4; slave_bizuin=3290306867; data_bizuin=3290306867; bizuin=3290306867; data_ticket=RTAvvdL1AdlfRZ04I7nqqY/teQ1jJP1ShbNKJ/5Q4x2P5kS1/o80ZpArBm6GuSgU; slave_sid=RGJaU2NhbVRMZG1xU3d1YVoyenVLOW1FMUhSSXpubGoyM2c2YWJSNkxZV2dyekVfX0RlQmNhQWs4eDdoeGY1NjI4bWdDbUlDVXNPSzJURkUyYXVuS0xkbDhadU1BdGZETUZhcDlhRjJaTkFQbmtkR1Y5NjRBU21VdlVxMEpIS085Z2VxMWJCczV2VE1JUW1L; slave_user=gh_494186280c34; xid=3d04dee501a337df821dc5f9bd963050'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

def generate_request_info(num):

    #查询内容
    param = {
        'action': 'list_ex',
        'begin': num,
        'count': 5,
        'fakeid': fakeid,
        'type': 9,
        'query': query,
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': 1,
    }
    #伪装头和登陆信息cookie
    header = {
        'user-agent': user_agent,
        'cookie': cookie
    }
    
    return param, header

def get_full_article(page_source):
    '''
    获取正文全文
    :page_source: 文章页面源代码
    :return: 列表形式文章全文
    '''

    # rich_media_content js_underline_content             autoTypeSetting24psection

    html = etree.HTML(page_source)
    text_list = []
    text_parsed = html.xpath("//div[contains(@class,'rich_media_content')]//text()")
    for text in text_parsed:
        clean_text = text.replace(' ', '').replace('\n', '').replace('：',':')
        index = clean_text.find(':')
        length = len(clean_text)

        condition = True
        condition = condition and (clean_text) and (length>1)
        condition = condition and (index>0) and (index < length-1)
        condition = condition and clean_text[index-1].isdigit()
        condition = condition and clean_text[index+1].isdigit()

        if condition:
            text_list.append(clean_text)
            print(clean_text)
    return text_list


##################### Main function part #####################   
if __name__ == '__main__' :

    # 设置保存文件
    # f = open(savefile_name,mode='w',newline='',encoding='utf-8')
    # csvwriter = csv.writer(f)

    max_count = (num_pages-1)*5 + 5
    for count in range(0,max_count,5):
        #基准url,不需要改动
        url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
        param, header = generate_request_info(count)

        #发送请求
        res = requests.get(url,headers=header,params=param)
        # print(json.dumps(res.json(), indent=4))
        #获取服务器端返回的json内容
        article_list = res.json()['app_msg_list']
        #关闭请求
        res.close()
        #记录文章信息
        for art in article_list:
            title = art['title']#文章标题
            aid = art['appmsgid']#文章识别ID
            link = art['link']#文章链接
            digest = art['digest']#文章摘要
            create_time = datetime.fromtimestamp(art['create_time'])#文章创建时间

            # csvwriter.writerow([title,aid,digest,create_time,link])
            if create_time > n_days_ago:

                print(f'{title} {create_time}')
                try:
                    content_info_raw = ws_api.get_article_content(link, raw=True)
                except:
                    print(f'{title} 文章下载异常！')

                content_info = get_full_article(content_info_raw)
                # print(f'{content_info}')

        time.sleep(3)