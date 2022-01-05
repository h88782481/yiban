import base64
import time
import json
import requests
import time
from apscheduler.schedulers.blocking import BlockingScheduler
#第一次登录链接，等号后边放自己的token
tokenurl = "http://211.68.191.30/epidemic/index?token="
#签到链接
qiandaourl = "http://211.68.191.30/epidemic/student/sign"
#验证码链接
captchaurl = "http://211.68.191.30/epidemic/captcha"
#验证码识别链接
apiurl="https://api.laladama.com"
#保持会话链接
indexurl="http://211.68.191.30/epidemic/student/index"
#以application/json形式上传验证码图片，图片经base64编码，识别验证码
def uploadJson(base64string, authcode, typeno, author, remark):
    data=json.dumps({"base64string":base64string,"authcode":authcode,"typeno":typeno,"author":author,"remark":remark})
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(apiurl+"/member/uploadjson",data=data,headers=headers)
    except:
        return {"status":-1,"msg":"访问接口出错"}
    else:
        if r.status_code==200:
            return json.loads(r.content)
        else:
            return {"status":-1,"msg":"访问接口出错"}
#查询答案接口
def queryJson(authcode,subjectno):
    data=json.dumps({"authcode":authcode,"subjectno":subjectno})
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(apiurl+"/member/queryjson",data=data,headers=headers)
    except:
        return {"status":-1,"msg":"访问接口出错"}
    else:
        if r.status_code==200:
            return json.loads(r.content)
        else:
            return {"status":-1,"msg":"访问接口出错"}
#建立session连接
def jllj():
    s = requests.session()
    return s
#获取一次验证码，识别并返回    
def yzm(s):
    captcha=s.get(url=captchaurl)
    base64_data = base64.b64encode(captcha.content)
    img = base64_data.decode()
    result=uploadJson('data:image/jpeg;base64,'+str(img), "自己的授权码", "自己的题型", "自己的账号", "字母区分大小写")
    time.sleep(20)
    result=queryJson("自己的授权码",result['msg'])
    return result


#保持session会话
def bchh(s):
    s.get(url=indexurl)
    print("保持会话活动成功")



#签到
def qiandao(s,result):
    data = {
        "data": r"""这里放自己的请求信息""",  # 直接抓post数据然后填
        "captcha": result['msg']
    }
    req=s.post(url=qiandaourl,data=data)
    code = req.json()
    if code["code"] == -1:
        print("签到失败")
        return code
    else:
        print("签到成功")
        return code
    


if __name__ == "__main__":
    s=jllj()
    s.get(url=tokenurl)
    print(s.cookies)
    result=yzm(s)
    code=qiandao(s,result)
    while code["code"] == -1:
        result=yzm(s)
        code=qiandao(s,result)
    scheduler = BlockingScheduler()
    #设置15分钟自动活动一次会话
    scheduler.add_job(bchh, 'interval', minutes=15 ,args=[s])
    #设置三点一分自动签到
    scheduler.add_job(qiandao, 'cron', hour='3', minute='1' ,args=[s,result])
    #启动自动任务
    scheduler.start()
