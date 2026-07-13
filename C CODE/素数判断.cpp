//输出整数num，判断该数字是否为素数。
#include<stdio.h>
int main(){
	int num,i;
	int flag=1;
	printf("输入整数num：");
	scanf("%d",&num);
	if(num<2){
		printf("不是素数\n");
		return 0;
	}
	for(i=2;i*i<=num;i++){
		if(num%i==0){
			flag=0;
			 break;
		}
	
	}
	if(flag==1)
	printf("%d 是素数\n",num);
	else
	printf("%d 不是素数\n",num);
	return 0;
	
}
