import requests
from bs4 import BeautifulSoup
import cv2
import numpy
from time import sleep


class Lessons:

    def __init__(self):
        self.session = requests.session()
        self.lessons_list = []

    def deal_info(self, lesson_info):  # 将课程信息进行转换
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
        self.lessons_list.append(str(lesson))
        return

    def sum_lessons(self, tokenValue):  # 将所有课程转换后的信息进行集中
        data = {"dealType": "3", "fajhh": "4672", "sj": "0_0", "searchtj": "",
                "kclbdm": "", "inputCode": "", "tokenValue": tokenValue}
        kcIds = ""
        kcms = ""
        not_first = False
        for lesson in self.lessons_list:
            lesson = eval(lesson)
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
        passwd = str(input("密码为："))
        try:
            login_img = self.session.get("https://urp.shou.edu.cn/img/captcha.jpg")
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
            # 验证码显示部分，暂时用的opencv，还请各位大佬指教
            img = cv2.imdecode(numpy.frombuffer(login_img.content, numpy.uint8), 0)  # 可能会出现没有验证码情况，未解决！！！
            cv2.imshow("验证码", img)
            cv2.waitKey(0)
            code = str(input("验证码为："))
            cv2.destroyAllWindows()
            data = {"j_username": self.id, "j_password": passwd, "j_captcha": code,
                    "_spring_security_remember_me": "on"}
            try:
                rp = self.session.post(url="https://urp.shou.edu.cn/j_spring_security_check", data=data)
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
                if lesson_no in self.lessons_list[i]:
                    self.lessons_list.pop(i)
                    print(lesson_no + ":" + info)
        return

    def judge_logout(self, html):  # 账号在其他地方被登录时报错
        if html.url == "https://urp.shou.edu.cn/login?errorCode=concurrentSessionExpired":
            print("有人登陆了您的账号！")
            exit(0)
        return

    def auto_spider(self):  # 自动选课部分
        self.login()  # 进行登录操作
        count = 0
        while self.lessons_list:
            count += 1
            print("第" + str(count) + "次选课！")
            try:
                html = self.session.get(url="https://urp.shou.edu.cn/student/courseSelect/courseSelect/index")
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
                alart = bs.find("div", {"class": "alert alert-block alert-danger"})  # 判断是否可以选课
                if alart != None:
                    print("对不起，当前为非选课阶段！")
                    exit(0)
                tokenValue = bs.find("input", {"type": "hidden", "id": "tokenValue"})["value"]
                data = self.sum_lessons(tokenValue)
                try:  # 提交选课表单
                    rq = self.session.post(url="https://urp.shou.edu.cn/student/courseSelect"
                                               "/selectCourse/checkInputCodeAndSubmit",
                                           data=data)
                except requests.ConnectionError:
                    print("选课提交失败！连接错误！")
                    exit(0)
                except requests.HTTPError:
                    print("选课提交失败！请求网页有问题！")
                    exit(0)
                except requests.Timeout:
                    print("选课提交失败！请求超时！")
                    exit(0)
                else:
                    self.judge_logout(rq)
                    data.pop("tokenValue")
                    data.pop("inputCode")
                    try:  # 网站要求的选课二次确认
                        self.session.post(url="https://urp.shou.edu.cn/student/courseSelect/selectCourses/waitingfor",
                                          data=data)
                    except requests.ConnectionError:
                        print("选课提交确认失败！连接错误！")
                        exit(0)
                    except requests.HTTPError:
                        print("选课提交确认失败！请求网页有问题！")
                        exit(0)
                    except requests.Timeout:
                        print("选课提交确认失败！请求超时！")
                        exit(0)
                    else:
                        self.judge_logout(rq)
                        data = {"kcNum": str(len(self.lessons_list)), "redisKey": self.id + "3"}
                        i = 1
                        while True:
                            sleep(1)  # 让服务器处理选课的等待时间，严禁删除！！！
                            try:  # 获取选课结果
                                rq = self.session.post(url="https://urp.shou.edu.cn/student/"
                                                           "  courseSelect/selectResult/query",
                                                       data=data)
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
                            self.judge_info(info.split(":")[0], info.split(":")[-1])
