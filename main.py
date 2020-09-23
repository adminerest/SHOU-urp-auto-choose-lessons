from urp.api import *


def start_choose(username: str = '', password: str = ''):
    username, password = get_username_and_password(username, password)
    session = login(username, password)
    lessons = read_lessons_from_file(username)
    count = 0
    while lessons:
        sleep(0.5)
        count += 1
        print("第%d次搜索课余量！" % count)
        if count == 1:
            choose_lesson(lessons, session)
            results = get_choose_status(lessons, session, username)
            judge_choose_status(lessons, results)
            continue
        choose_lessons, lessons = search_lessons(lessons, session)
        if choose_lessons:
            choose_lesson(choose_lessons, session)
            results = get_choose_status(choose_lessons, session, username)
            judge_choose_status(lessons, results)


if __name__ == "__main__":

    """
        请将所要选的课程放入名字为学号的csv文件中并将文件放入user_info
        格式：课程号、课序号、课程名称
        具体参照example.csv中格式
        重修请自己选课。。。
    """
    start_choose()
