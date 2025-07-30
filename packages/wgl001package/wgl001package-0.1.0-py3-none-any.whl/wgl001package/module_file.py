# 这是一个示例模块文件，包含函数和类的实现

def my_function(name: str) -> str:
    """一个简单的示例函数"""
    return f"Hello, {name}!"


class MyClass:
    """一个示例类，演示类的用法"""

    def __init__(self, value: int):
        self.value = value

    def multiply(self, factor: int) -> int:
        """将内部值乘以给定因子"""
        return self.value * factor

    def get_info(self) -> dict:
        """返回对象信息"""
        return {
            "value": self.value,
            "type": type(self.value).__name__
        }