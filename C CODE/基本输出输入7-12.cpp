//基本输入输出题目
//输入一名学生姓名，年龄，身高，考试分数，按格式打印，保留两位小数输出身高与分数
#include <stdio.h>
int main()
{
	char name[20];
	int age;
	float height,score;
	printf("请输入学生的姓名，年龄，身高，考试分数:");
	scanf("%s %d %f %f",name,&age,&height,&score);
	printf("姓名：%s \n",name);
	printf("年龄：%d \n",age);
	printf("身高：%.2f \n",height);
	printf("考试分数：%.2f \n",score);
	return 0;
}
