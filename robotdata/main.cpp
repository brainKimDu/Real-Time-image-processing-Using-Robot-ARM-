#define _CRT_SECURE_NO_WARNINGS
/*
* 저자: 박호윤
* 목적: 데이터 세팅 프로그램
* last date: 2021.04.13
* Version: 1.0.0
*/

#include <stdio.h>
#include <math.h>
#define PI  3.141592654


void createTMatrix(int jointNo, double param[3][4], double T[4][4]);
void multTransform(double A[4][4], double B[4][4], double C[4][4]);
void print4x4Mtx(char* str, double A[4][4]);
void print3x4Mtx(char* str, double A[3][4]);
void mult_Tr_Vector(double A[4][4], double B[4], double C[4]);
void print4x1Vector(char* str, double A[4]);

int main(void)
{
	FILE* Mfp;
	FILE* Lfp;
	FILE* Afp;
	int err;
	double tool[5][2] = { 500,0,600,100, 500,100, 500,-100, 600,-100 };
	double apos[4] = { 0,0,0,1 }, bpos[4] = { 0,0,0,1 };

	int jointNo;
	double theta1 = 0, theta2 = 0;

	int  L1 = 1000;			// L1
	int L2 = 1000;			// L2
	//**** 사용자에게서 링크길이를 받는다  	
	scanf("%d", &L1);	
	scanf("%d", &L2);
	printf("L1: %d\n", L1);
	printf("L2: %d\n", L2);
	puts("");

	//링크 길이(XY좌표에대한비율) 정보 저장
	err = fopen_s(&Lfp, "Ldata.txt", "wt");		// 파일 오픈
	printf("Ldata.txt Opening...");
	if (err == 0) {								// 성공
		puts("Success");
	}
	else {
		puts("Open Failure. Press Enter.");	// 실패
		getchar();
		return -1;
	}
	fprintf(Lfp, "%d\n%d", L1, L2);
	puts("Ldata saved.\n");
	fclose(Lfp);

	//좌표-모터각 정보 저장
	err = fopen_s(&Mfp, "Mdata.txt", "wt");		// 파일 오픈
	printf("Mdata.txt Opening...");
	if (err == 0) {								// 성공
		puts("Success");
	}

	else {
		puts("Open Failure. Press Enter.");	// 실패
		getchar();
		return -1;
	}

	printf("File writing ... \n");

	for (int x = 0; x <= L1 + L2; x++)
	{
		for (int y = 0; y <= L1 + L2; y++)
		{
			if ( (sqrt(pow(x, 2) + pow(y, 2)) >= sqrt(pow(L1, 2) + pow(L2, 2))) && (sqrt(pow(x, 2) + pow(y, 2)) <= (L1 + L2)) )
			{
				theta1 = atan2(x, y) - acos((pow(x, 2) + pow(y, 2) + pow(L1, 2) - pow(L2, 2)) / (2 * L1 * sqrt(pow(x, 2) + pow(y, 2))));
				theta2 = 1 * acos((pow(x, 2) + pow(y, 2) - pow(L1, 2) - pow(L2, 2)) / (2 * L1 * L2));

				fprintf(Mfp, "P(%d,%d)=[%.0f,%.0f]\n", x, y, theta1 * 180 / PI, theta2 * 180 / PI);
			}
		}
	}

	fclose(Mfp);
	puts("Mdata saved \n");

	//방위각-각도 정보 저장 
	printf("AzimuthData.txt Opening...");
	Afp = fopen("AzimuthData.txt", "w");
	if (Afp == NULL)
	{
		puts("Open Failure. Press Ente");
		getchar();
		return -1;
	}
	else
	{
		puts("Success");
	}
	printf("File writing ... \n");
	float Azimuth;
	for (int i = 0; i < L1 + L2; i++)
	{
		for (int j = 0; j < L1 + L2; j++)
		{
			Azimuth = atan2(j, i) * (180 / PI);
			fprintf(Afp, "P(%d,%d)=[%d] \n", i, j, (int)Azimuth);
		}
	}
	puts("Azinuth data saved.\n");
	fclose(Afp);

	puts("End of program. Press Enter");

	return 0;
}

void createTMatrix(int jointNo, double param[3][4], double T[4][4])
{
	// 입력
	//		int jointNo        : 관절 번호. 0,1,2
	//		double param[3][4] : 파라미터 행렬
	// 반환
	//		double T[4][4]     : 계산된 변환행렬. 식 (3.6) 을 계산하여 반환한다. 
	//
	double alpha_i_1, a_i_1, d_i, theta_i;
	alpha_i_1 = param[jointNo][0];
	a_i_1 = param[jointNo][1];
	d_i = param[jointNo][2];
	theta_i = param[jointNo][3];

	//[코딩]  식 (3.6)을 여기에 코딩.
	T[0][0] = cos(theta_i);
	T[0][1] = -sin(theta_i);
	T[0][2] = 0.0;
	T[0][3] = a_i_1;

	T[1][0] = sin(theta_i) * cos(alpha_i_1);
	T[1][1] = cos(theta_i) * cos(alpha_i_1);
	T[1][2] = -sin(alpha_i_1);
	T[1][3] = -sin(alpha_i_1) * d_i;

	T[2][0] = sin(theta_i) * sin(alpha_i_1);
	T[2][1] = cos(theta_i) * sin(alpha_i_1);
	T[2][2] = cos(alpha_i_1);
	T[2][3] = cos(alpha_i_1) * d_i;

	T[3][0] = T[3][1] = T[3][2] = 0.0;
	T[3][3] = 1.0;

	return;
}

void mult_Tr_Vector(double A[4][4], double B[4], double C[4])
{
	int i, j;

	for (i = 0; i < 4; i++) {
		C[i] = 0.0;
		for (j = 0; j < 4; j++) {
			C[i] += A[i][j] * B[j];
		}
	}
}


void multTransform(double A[4][4], double B[4][4], double C[4][4])
{
	// 입력 :  두개의 변환 행렬 A[4][4],  B[4][4]
	//
	// 반환 :  C 행렬 = A * B
	int i, j, k;

	for (i = 0; i < 4; i++) {
		for (j = 0; j < 4; j++) {
			C[i][j] = 0.0;
			for (k = 0; k < 4; k++)
				C[i][j] += A[i][k] * B[k][j];
		}
	}
}

void print4x4Mtx(char* str, double A[4][4])
{
	int i, j;

	puts(str);
	for (i = 0; i < 4; i++) {
		for (j = 0; j < 4; j++)
			printf("\t%.1f ", A[i][j]);
		printf("\n");
	}
}

void print3x4Mtx(char* str, double A[3][4])
{
	int i, j;

	puts(str);
	for (i = 0; i < 3; i++) {
		for (j = 0; j < 4; j++)
			printf("\t%.1f ", A[i][j]);
		printf("\n");
	}
}

void print4x1Vector(char* str, double A[4])
{
	int i;

	printf("%s : ", str);
	for (i = 0; i < 4; i++)
		printf("%.2f ", A[i]);
	printf("\n");
}
