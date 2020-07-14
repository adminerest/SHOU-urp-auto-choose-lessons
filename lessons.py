import requests
import csv
from hashlib import md5
from os import path
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from time import sleep


class Lessons:

    def __init__(self, dealType):
        """
            dealType : 选课的类型
        """
        self.session = requests.session()
        self.lessons_list = []
        self.dealType = dealType

    def deal_info(self, lessons_info):  # 将课程信息进行转换
        deal_lessons = []
        for lesson_info in lessons_info:
            lesson = {}
            kcIds = lesson_info["no"] + "_" + lesson_info["id"] + "_" + lesson_info["term"]
            lesson["kcIds"] = kcIds
            kcms = ""
            for c in lesson_info["name"]:
                c = str(ord(c))
                kcms += c + ','
            kcms += "95,"
            for c in lesson_info["id"]:
                c = str(ord(c))
                kcms += c + ','
            lesson["kcms"] = kcms
            deal_lessons.append(lesson)
        return deal_lessons

    def sum_lessons(self, tokenValue, lessons_list):  # 将所有课程转换后的信息进行集中
        data = {"dealType": self.dealType, "fajhh": self.fajhh, "sj": "0_0", "searchtj": "",
                "kclbdm": "", "inputCode": "", "tokenValue": tokenValue}
        kcIds = ""
        kcms = ""
        not_first = False
        for lesson in lessons_list:
            if not_first:
                kcIds += ','
                kcms += '44,'
            kcIds += lesson["kcIds"]
            kcms += lesson["kcms"]
            not_first = True
        data["kcIds"] = kcIds
        data["kcms"] = kcms
        return data

    def login(self):  # 登录模块
        self.id = str(input("用户名为："))
        passwd = md5(bytes(str(input("密码为："))))
        try:
            login_img = self.session.get("https://urp.shou.edu.cn/img/captcha.jpg", timeout=10)
        except requests.ConnectionError:
            print("获取验证码失败！连接错误！")
            exit(0)
        except requests.HTTPError:
            print("获取验证码失败！请求网页有问题！")
            exit(0)
        except requests.Timeout:
            print("获取验证码失败！请求超时！")
            exit(0)
        else:
            if login_img.text == '':
                print("获取验证码失败！验证码为空！")
                exit(0)
            byteio = BytesIO()
            byteio.write(login_img.content)
            img = Image.open(byteio)
            img.show()  # 可能会出现没有验证码情况，未解决！！！
            code = str(input("验证码为："))
            data = {"j_username": self.id, "j_password": passwd, "j_captcha": code,
                    "_spring_security_remember_me": "on"}
            try:
                rp = self.session.post(url="https://urp.shou.edu.cn/j_spring_security_check",
                                       data=data,
                                       timeout=10)
            except requests.ConnectionError:
                print("登录失败！连接错误！")
                exit(0)
            except requests.HTTPError:
                print("登录失败！请求网页有问题！")
                exit(0)
            except requests.Timeout:
                print("登录失败！请求超时！")
                exit(0)
            else:
                if rp.url == "https://urp.shou.edu.cn/login?errorCode=badCaptcha":
                    print("验证码输入错误！")
                    exit(0)
                elif rp.url == "https://urp.shou.edu.cn/login?errorCode=badCredentials":
                    print("用户名或密码输入错误！")
                    exit(0)
        return

    def judge_info(self, lesson_no, info):  # 对选课结果进行判断
        if info != "你选择的课程没有课余量！":
            for i in range(len(self.lessons_list)):
                if lesson_no == self.lessons_list[i]['no']:
                    self.lessons_list.pop(i)
                    print(lesson_no + ":" + info)
                    break
        return

    def judge_logout(self, html):  # 账号在其他地方被登录时报错
        if html.url == "https://urp.shou.edu.cn/login?errorCode=concurrentSessionExpired":
            print("有人登陆了您的账号！")
            exit(0)
        return

    def judge_choose(self, bs):
        alart = bs.find("div", {"class": "alert alert-block alert-danger"})  # 判断是否可以选课
        if alart is not None:
            print("对不起，当前为非选课阶段！")
            exit(0)

    def get_tokenvalue(self, bs):
        tokenValue = bs.find("input", {"type": "hidden", "id": "tokenValue"})["value"]
        return tokenValue

    def get_term(self, bs):
        term = bs.find("h4").text.split('(')[1].split('\r')[0]
        if term[-1] == '春':
            self.term = term[:9] + "-2-1"
        else:
            self.term = term[:9] + "-1-1"

    def get_fajhh(self, bs):
        self.fajhh = bs.find("li", {"title": "校任选课", "id": "xarxk"})["onclick"].split('=')[1].split("'")[0]

    def get_lesson_page(self):
        try:
            html = self.session.get(url="https://urp.shou.edu.cn/student/courseSelect/courseSelect/index",
                                    timeout=10)
        except requests.ConnectionError:
            print("选课页面无法加载！连接错误！")
            exit(0)
        except requests.HTTPError:
            print("选课页面无法加载！请求网页有问题！")
            exit(0)
        except requests.Timeout:
            print("选课页面无法加载！请求超时！")
            exit(0)
        else:
            self.judge_logout(html)
            bs = BeautifulSoup(html.text, "html.parser")
            return bs

    def get_lessons_list(self):
        road = "user_info/" + str(self.id) + ".csv"
        if not path.exists(road):  # 导入选课内容
            print("选课文件不存在！请检查！")
            exit(0)
        file = open(road, mode='r', encoding='utf-8')
        lessons = csv.reader(file)
        for lesson in lessons:
            lesson_info = {"no": lesson[0], "id": lesson[1], "term": self.term, "name": lesson[2]}
            self.lessons_list.append(lesson_info)
        file.close()

    def search_lessons_info(self):
        lessons_list = []
        for lesson in self.lessons_list:
            data = {'searchtj': lesson['no'], 'xq': '0', 'jc': '0', 'kclbdm': ''}
            url = 'https://urp.shou.edu.cn/student/courseSelect/freeCourse/courseList'
            for count in range(1, 11):
                try:
                    rp = self.session.post(url=url, data=data, timeout=10)
                except requests.ConnectionError:
                    print("课余量查询失败！连接错误！")
                    print('第%d次重试' % count)
                    continue
                except requests.HTTPError:
                    print("课余量查询失败！请求网页有问题！")
                    print('第%d次重试' % count)
                    continue
                except requests.Timeout:
                    print("课余量查询失败！请求超时！")
                    print('第%d次重试' % count)
                    continue
                else:
                    self.judge_logout(rp)
                    infos = eval(eval(rp.text)['rwRxkZlList'])
                    if len(infos) == 0:
                        print("未找到或已选%s！" % lesson['name'])
                        for i in range(len(self.lessons_list)):
                            if lesson['no'] == self.lessons_list[i]['no']:
                                self.lessons_list.pop(i)
                        break
                    for info in infos:
                        if info['kxh'] == lesson['id'] and int(info['bkskyl']) > 0:
                            lessons_list.append(lesson)
                            break
                    break
            if count == 10:
                print('课余量查询失败！请检查urp！')
                exit(0)
        return lessons_list

    def choose_lessons(self, tokenValue, lesson_list):
        deal_lessons = self.deal_info(lesson_list)
        data = self.sum_lessons(tokenValue, deal_lessons)
        for flag in range(1, 11):
            try:  # 提交选课表单
                rq = self.session.post(url="https://urp.shou.edu.cn/student/courseSelect"
                                           "/selectCourse/checkInputCodeAndSubmit",
                                       data=data,
                                       timeout=10)
            except requests.ConnectionError:
                print("选课提交失败！连接错误！")
                print('第%d次重试！' % flag)
                continue
            except requests.HTTPError:
                print("选课提交失败！请求网页有问题！")
                print('第%d次重试！' % flag)
                continue
            except requests.Timeout:
                print("选课提交失败！请求超时！")
                print('第%d次重试！' % flag)
                continue
            else:
                break
        if flag == 10:
            print("选课提交失败！请检查urp！")
            exit(0)
        self.judge_logout(rq)
        data.pop("tokenValue")
        data.pop("inputCode")
        for flag in range(1, 11):
            try:  # 网站要求的选课二次确认
                self.session.post(url="https://urp.shou.edu.cn/student/courseSelect/selectCourses/waitingfor",
                                  data=data,
                                  timeout=10)
            except requests.ConnectionError:
                print("选课提交确认失败！连接错误！")
                print('第%d次重试！' % flag)
                continue
            except requests.HTTPError:
                print("选课提交确认失败！请求网页有问题！")
                print('第%d次重试！' % flag)
                continue
            except requests.Timeout:
                print("选课提交确认失败！请求超时！")
                print('第%d次重试！' % flag)
                continue
            else:
                break
        if flag == 10:
            print("选课提交确认失败！请检查urp！")
            exit(0)
        self.judge_logout(rq)
        data = {"kcNum": str(len(lesson_list)), "redisKey": self.id + self.dealType}
        i = 1
        while True:
            sleep(1)  # 让服务器处理选课的等待时间，严禁删除！！！
            try:  # 获取选课结果
                rq = self.session.post(url="https://urp.shou.edu.cn/student/"
                                           "  courseSelect/selectResult/query",
                                       data=data,
                                       timeout=10)
            except requests.ConnectionError:
                print("获取选课结果失败！连接错误！")
                exit(0)
            except requests.HTTPError:
                print("获取选课结果失败！请求网页有问题！")
                exit(0)
            except requests.Timeout:
                print("获取选课结果失败！请求超时！")
                exit(0)
            else:
                self.judge_logout(rq)
                if "true" in rq.text:
                    break
                if i > 10:
                    print("获取选课结果失败！请到urp进行确认！")
                    exit(0)
                print("第" + str(i) + "次获取选课结果失败！正在重试！")
                i += 1
        infos = eval(rq.text.replace("true", '"true"'))
        infos = infos["result"]
        for info in infos:  # 判断选课结果并输出
            self.judge_info(info.split("_")[0], info.split(":")[-1])

    def auto_spider(self):  # 自动选课部分
        self.login()  # 进行登录操作
        count = 0
        while self.lessons_list or count == 0:
            sleep(0.5)
            count += 1
            print("第%d次搜索课余量！" % count)
            if count == 1:
                """
                    导入培养方案编号以及选课的学期
                """
                bs = self.get_lesson_page()
                self.judge_choose(bs=bs)
                self.get_term(bs=bs)
                self.get_fajhh(bs=bs)
                self.get_lessons_list()
                token_Value = self.get_tokenvalue(bs=bs)
                self.choose_lessons(tokenValue=token_Value, lesson_list=self.lessons_list)
                bs = self.get_lesson_page()
                self.judge_choose(bs=bs)
                token_Value = self.get_tokenvalue(bs=bs)

            lessons_list = self.search_lessons_info()
            if len(lessons_list) != 0:
                self.choose_lessons(tokenValue=token_Value, lesson_list=self.lessons_list)
                bs = self.get_lesson_page()
                self.judge_choose(bs=bs)
                token_Value = self.get_tokenvalue(bs=bs)
