from lessons import Lessons

if __name__ == "__main__":

    """
        请将所要选的课程放入名字为学号的csv文件中并将文件放入user_info
        格式：课程号、课序号、课程名称
        具体参照example.csv中格式
        下方dealType是选课的类型
        务必确保所选课程和课程类型一致！！！
        现在目测3是校任选课（大概也就是任选课），2是专业选修（包括体育课）
        不过好像2的话校任选和专业选修都可以选。。。
        重修请自己选课。。。
    """
    dealType = "2"
    lessons = Lessons(dealType)
    lessons.auto_spider()  # 开始自动选课
    print("全部课程已成功选上！请去urp查收！")
