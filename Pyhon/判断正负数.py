"""
输入一个数字，判断该数字是正数，负数还是零，输出对应提示
"""
num=float(input("请输入数字："))
if num>0:
    print("正数")
elif num<0:
    print("负数")
else :
    print("数字为0")