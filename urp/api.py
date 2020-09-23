from io import BytesIO
from typing import List, Tuple
from PIL.Image import open as img_open
from requests import Session, ConnectionError, HTTPError, Timeout, RequestException, Response
from hashlib import md5
from re import findall
from .lesson import Lesson
from json import loads
from lxml.etree import HTML
from time import sleep
from csv import reader
from os.path import exists
from getopt import getopt
from sys import argv


def get_username_and_password(username: str, password: str) -> Tuple[str, str]:
    opts, args = getopt(argv[1:], 'u:p:', ['username=', 'password='])
    for opt in opts:
        if (opt[0] == '--username' or opt[0] == '-u') and not username:
            username = opt[1]
        elif (opt[0] == '--password' or opt[0] == '-p') and not password:
            password = opt[1]
    if not username:
        username = input('学号：')
    if not password:
        password = input('密码：')
    return username, password


def read_lessons_from_file(username: str) -> List[Lesson]:
    """
    从csv文件中读取选课信息

    :param username: 学号
    :return: 所有要选的课的列表
    """
    path = "user_info/" + username + ".csv"
    if not exists(path):  # 导入选课内容
        print("选课文件不存在！请检查！")
        exit(0)
    fp = open(path, mode='r', encoding='utf-8')
    lessons = [Lesson(lesson[0], lesson[1], lesson[2]) for lesson in reader(fp)]
    fp.close()
    return lessons


def judge_choose_status(lessons: List[Lesson], results: List[str]) -> None:
    """
    判断选课结果

    :param lessons: 所有课程
    :param results: 选课结果列表
    :return: None
    """
    for result in results:
        lesson_info, info = result.split(':')
        if info != "你选择的课程没有课余量！":
            for i in range(len(lessons)):
                if lesson_info == lessons[i].lesson_id + '_' + lessons[i].class_id:
                    lessons.pop(i)
                    print(lesson_info + ":" + info)
                    break


def get_choose_status(lessons: List[Lesson], session: Session, username: str) -> List[str]:
    """
    获取选课结果

    :param lessons: 可选的课程列表
    :param session: 登录好的session
    :param username: 学号
    :return: 要选的课程的选课结果
    """
    data = {
        'kcNum': len(lessons),
        'redisKey': username + '5'
    }
    count = 0
    result = {}
    for _ in range(10):
        sleep(1)
        count += 1
        try:  # 查询选课结果
            rp = session.post(url="https://urp.shou.edu.cn/student/courseSelect/selectResult/query",
                              data=data,
                              timeout=10)
        except ConnectionError:
            print("获取选课结果失败！连接错误！")
            print('第%d次重试！' % count)
            continue
        except HTTPError:
            print("获取选课结果失败！请求网页有问题！")
            print('第%d次重试！' % count)
            continue
        except Timeout:
            print("获取选课结果失败！请求超时！")
            print('第%d次重试！' % count)
            continue
        except RequestException as e:
            print('获取选课结果失败！' + str(e))
            print('第%d次重试' % count)
            continue
        else:
            judge_logout(rp)
            result = loads(rp.text)
            if not result['isFinish']:  # 判断是否完成
                continue
            else:
                break
    if count >= 10:
        print("获取选课结果失败！请检查urp！")
        exit(0)
    return result['result']


def _first_choose(lessons: List[Lesson], session: Session, token_value: str, major_id: str) -> dict:
    """
    选课两次提交中的第一次提交

    :param lessons: 可选的课程列表
    :param session: 登录好的session
    :param token_value: 获取到的token_value
    :param major_id: 培养方案id
    :return: 第一次提交表单中的内容
    """
    # 将课程信息格式化
    lessons_info = lessons[0].get_standard_type()
    lessons_info_unicode = lessons[0].get_unicode_type()
    for i in range(1, len(lessons)):  # 汇总所有课程信息
        lessons_info += ',' + lessons[i].get_standard_type()
        lessons_info_unicode += '44,' + lessons[i].get_unicode_type()
    data = {
        'dealType': '5',
        'kcIds': lessons_info,
        'kcms': lessons_info_unicode,
        'fajhh': major_id,
        'sj': '0_0',
        'searchtj': '',
        'kclbdm': '',
        'inputCode': '',
        'tokenValue': token_value
    }
    count = 0
    rp = None
    for _ in range(10):
        count += 1
        try:  # 第一次提交
            rp = session.post(url="https://urp.shou.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit",
                              data=data,
                              timeout=10)
        except ConnectionError:
            print("选课第一次提交失败！连接错误！")
            print('第%d次重试！' % count)
            continue
        except HTTPError:
            print("选课第一次提交失败！请求网页有问题！")
            print('第%d次重试！' % count)
            continue
        except Timeout:
            print("选课第一次提交失败！请求超时！")
            print('第%d次重试！' % count)
            continue
        except RequestException as e:
            print('选课第一次提交失败！' + str(e))
            print('第%d次重试' % count)
            continue
        else:
            break
    if count >= 10:
        print("选课第一次提交失败！请检查urp！")
        exit(0)
    judge_logout(rp)
    return data


def _second_choose(session: Session, data: dict) -> None:
    """
    选课两次提交中的第二次提交

    :param session: 登录好的session
    :param data: 第一次提交的表单数据
    :return: None
    """
    # 删除第一次提交的表单数据中多余字段
    data.pop("tokenValue")
    data.pop("inputCode")
    count = 0
    rp = None
    for _ in range(10):
        count += 1
        try:  # 第二次提交
            rp = session.post(url="https://urp.shou.edu.cn/student/courseSelect/selectCourses/waitingfor",
                              data=data,
                              timeout=10)
        except ConnectionError:
            print("选课第二次提交失败！连接错误！")
            print('第%d次重试！' % count)
            continue
        except HTTPError:
            print("选课第二次提交失败！请求网页有问题！")
            print('第%d次重试！' % count)
            continue
        except Timeout:
            print("选课第二次提交失败！请求超时！")
            print('第%d次重试！' % count)
            continue
        except RequestException as e:
            print('选课第二次提交失败！' + str(e))
            print('第%d次重试' % count)
            continue
        else:
            break
    if count >= 10:
        print("选课第二次提交失败！请检查urp！")
        exit(0)
    judge_logout(rp)


def choose_lesson(lessons: List[Lesson], session: Session) -> None:
    """
    提交选课

    :param lessons: 可选的课程
    :param session: 登录好的session
    :return: None
    """
    choose_lesson_page = get_choose_lesson_page(session)  # 获取选课页面树来获取token和培养方案id
    token_value = get_token_value(choose_lesson_page)
    major_id = get_major_id(choose_lesson_page)
    data = _first_choose(lessons, session, token_value, major_id)
    _second_choose(session, data)


def get_choose_lesson_page(session: Session):
    """
    获取选课页面

    :param session: 登录好的session
    :return: 选课页面树
    """
    count = 0
    rp = None
    for _ in range(10):
        count += 1
        try:
            rp = session.get(url="https://urp.shou.edu.cn/student/courseSelect/courseSelect/index",
                             timeout=10)
        except ConnectionError:
            print("选课页面无法加载！连接错误！")
            print('第%d次重试！' % count)
            continue
        except HTTPError:
            print("选课页面无法加载！请求网页有问题！")
            print('第%d次重试！' % count)
            continue
        except Timeout:
            print("选课页面无法加载！请求超时！")
            print('第%d次重试！' % count)
            continue
        except RequestException as e:
            print('选课页面无法加载！' + str(e))
            print('第%d次重试' % count)
            continue
        else:
            break
    if count >= 10:
        print("选课页面无法加载！请检查urp！")
        exit(0)
    judge_logout(rp)
    return HTML(rp.text)


def search_lessons(lessons: List[Lesson], session: Session) -> Tuple[List[Lesson], List[Lesson]]:
    """
    搜索课余量

    :param lessons: 要搜索的课
    :param session: 登录好的session
    :return: (有课余量的课, 存在的课)
    """
    choose_list = []  # 有课余量的课的列表
    new_lessons_list = []  # 存在的课的列表
    for i in range(len(lessons)):
        data = {
            'searchtj': lessons[i].lesson_id,
            'xq': '0',
            'jc': '0',
            'kclbdm': ''
        }
        count = 0
        rp = None
        for _ in range(10):
            count += 1
            try:  # 根据课程号搜索课程
                rp = session.post('https://urp.shou.edu.cn/student/courseSelect/freeCourse/courseList',
                                  data=data,
                                  timeout=10)
            except ConnectionError:
                print("课余量查询失败！连接错误！")
                print('第%d次重试' % count)
                continue
            except HTTPError:
                print("课余量查询失败！请求网页有问题！")
                print('第%d次重试' % count)
                continue
            except Timeout:
                print("课余量查询失败！请求超时！")
                print('第%d次重试' % count)
                continue
            except RequestException as e:
                print('课余量查询失败！' + str(e))
                print('第%d次重试' % count)
                continue
            else:
                break
        if count >= 10:
            print('课余量查询失败！请检查urp！')
            exit(0)
        judge_logout(rp)  # 判断账号是否注销
        rp_lessons_list = loads(loads(rp.text)['rwRxkZlList'])  # 获取搜索到的课程的列表
        if len(rp_lessons_list) == 0:  # 如果列表一节课都没有
            print("未找到或已选%s！" % lessons[i].lesson_name)
        else:
            find = False
            for rp_lesson in rp_lessons_list:
                if rp_lesson['kxh'] == lessons[i].class_id:  # 如果搜索到的课有课序号和要选的课程相同
                    find = True
                    lessons[i].term = rp_lesson['zxjxjhh']
                    new_lessons_list.append(lessons[i])  # 加入到存在的课的列表里
                    if int(rp_lesson['bkskyl']) > 0:  # 如果有课余量
                        choose_list.append(lessons[i])
            if not find:
                print("未找到或已选%s！" % lessons[i].lesson_name)
    return choose_list, new_lessons_list


def get_token_value(tree) -> str:
    """
    获取token_value

    :param tree: https://urp.shou.edu.cn/student/courseSelect/courseSelect/index解析后的树
    :return: token_value的值
    """
    return tree.xpath('//input[@id="tokenValue"]/@value')[0]


def get_major_id(tree) -> str:
    """
    获取培养方案id

    :param tree: https://urp.shou.edu.cn/student/courseSelect/courseSelect/index解析后的树
    :return: 培养方案id
    """
    return findall(r'fajhh=[0-9]*', tree.xpath('//li[@id="zyxk"]/@onclick')[0])[0].split('=')[1]


def judge_logout(html: Response) -> None:
    """
    判断账号是否被注销

    :param html: 请求返回
    :return: None
    """
    if html.url == "https://urp.shou.edu.cn/login?errorCode=concurrentSessionExpired":
        print("有人登陆了您的账号！")
        exit(0)


def login(username: str, password: str) -> Session:
    """
    urp登录

    :param username: 用户名
    :param password: 密码
    :return: 登录好的Session
    """
    session = Session()
    password = md5(bytes(password, encoding='utf-8')).hexdigest()  # 密码MD5加密
    # 获取验证码
    try:
        cache_img = session.get('https://urp.shou.edu.cn/img/captcha.jpg', timeout=10)
    except ConnectionError:
        print('获取验证码失败！连接错误！')
        exit(0)
    except HTTPError:
        print('获取验证码失败！请求网页有问题！')
        exit(0)
    except Timeout:
        print('获取验证码失败！请求超时！')
        exit(0)
    except RequestException as e:
        print('获取验证码失败！' + str(e))
    else:
        # 处理图像并显示
        if cache_img.text == '':
            print('获取验证码失败！验证码为空！')
            exit(0)
        byte_io = BytesIO()
        byte_io.write(cache_img.content)
        img = img_open(byte_io)
        img.show()  # TODO: 可能会出现没有验证码情况，未解决！！！
        cache = str(input('验证码为：'))
        data = {
            'j_username': username,
            'j_password': password,
            'j_captcha': cache,
            '_spring_security_remember_me': 'on'}
        try:  # 登录
            rp = session.post(url="https://urp.shou.edu.cn/j_spring_security_check",
                              data=data,
                              timeout=10)
        except ConnectionError:
            print("登录失败！连接错误！")
            exit(0)
        except HTTPError:
            print("登录失败！请求网页有问题！")
            exit(0)
        except Timeout:
            print("登录失败！请求超时！")
            exit(0)
        except RequestException as e:
            print('登录失败！' + str(e))
            exit(0)
        else:
            # 判断登录结果
            if rp.url == 'https://urp.shou.edu.cn/':  # 登录成功
                return session
            elif rp.url == "https://urp.shou.edu.cn/login?errorCode=badCaptcha":
                print("验证码输入错误！")
                exit(0)
            elif rp.url == "https://urp.shou.edu.cn/login?errorCode=badCredentials":
                print("用户名或密码输入错误！")
                exit(0)
            elif rp.url == 'https://urp.shou.edu.cn/login?errorCode=concurrentSessionExpired':
                print('有人登陆了您的账号！')
                exit(0)
            else:
                print('未知返回url！网址：' + rp.url)
                exit(0)
