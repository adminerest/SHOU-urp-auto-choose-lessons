from lessons import Lessons

if __name__ == "__main__":

    """
        所选课程输入格式如下，no = 课程号，id = 课序号，term = 学期，name = 课程名称
        使用lessons.deal_info(lesson_info)将数据导入，否则数据无效！
        例如：
        lesson_info = {"no": "7603503", "id": "01", "term": "2019-2020-1-1", "name": "电影美学"}
        lessons.deal_info(lesson_info)
        lesson_info = {"no": "E0202017", "id": "02", "term": "2019-2020-1-1", "name": "大学生安全文化(在线课程）"}
        lessons.deal_info(lesson_info)
    """
    dealType = "2"
    lessons = Lessons(dealType)
    lesson_info = {"no": "5208551", "id": "03", "term": "2019-2020-2-1", "name": "软件工程I"}
    lessons.deal_info(lesson_info)
    lessons.auto_spider()  # 开始自动选课
    print("全部课程已成功选上！请去urp查收！")
