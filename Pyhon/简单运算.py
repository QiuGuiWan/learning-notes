'''
编写程序，接受用户输入输出的两个整数，计算并输出它们的和，差，积，商，取余结果
'''
a=int(input("请输入第一个整数："))
b=int(input("请输入第二个整数："))
print("和：",a+b)
print("差：",a-b)
print("积：",a*b)
if b!=0:
    print("商：", a // b)
    print("取余：", a % b)
else:
    print("false，除数不可为0")
