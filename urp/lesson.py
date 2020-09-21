class Lesson(object):

    lesson_id: str
    class_id: str
    lesson_name: str
    term: str

    def __init__(self, lesson_id: str, class_id: str, lesson_name: str, term: str = None):
        """
        :param lesson_id: 课程号，例如：1109906
        :param class_id: 课序号，例如：01
        :param lesson_name: 课程名称，例如：舌尖上来自大海的馈赠
        :param term: 学期，例如：2020-2021-1-1
        """
        self.lesson_id = lesson_id
        self.class_id = class_id
        self.lesson_name = lesson_name
        self.term = term

    def get_standard_type(self) -> str:
        """
        将课程信息转换成表单格式，格式如下：
        1109906@01@2020-2021-1-1

        :return: 表单格式，如1109906@01@2020-2021-1-1
        """
        return '%s@%s@%s' % (self.lesson_id, self.class_id, self.term)

    def get_unicode_type(self) -> str:
        """
        将课程信息转换成表单格式，格式如下
        原始信息：舌尖上来自大海的馈赠(1706303@01)
        表单格式：25968,23398,19982,32463,27982,40,49,49,48,57,57,48,54,64,48,49,41,

        :return: 表单格式，如25968,23398,19982,32463,27982,40,49,49,48,57,57,48,54,64,48,49,41,
        """
        return ''.join([str(ord(letter)) + ','
                        for letter in '%s(%s@%s)' % (self.lesson_name, self.lesson_id, self.class_id)])
