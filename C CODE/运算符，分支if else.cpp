//输出一个整数，判断该数是正数，负数还是0，并输出对应文字；同时计算该数绝对值输出
#include<stdio.h>
int main(){
	int n,i;
	printf("请输入整数：");
	scanf("%d",&n);
	if (n>0)
	{
		printf("该数是正数\n");
		i=n;
	}
	else if (n<0)
	{
		printf("该数是负数\n");
		i=-n;
	}
	else
	{
		printf("该数等于0\n");
		i=0;
	}
	return 0;
}
