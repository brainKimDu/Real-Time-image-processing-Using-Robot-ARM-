#include <Braccio.h>
#include <Servo.h>

Servo base; // M1
Servo shoulder; // M2
Servo elbow; // M3
Servo wrist_ver; // M4
Servo wrist_rot; // M5
Servo gripper; // M6

#define Number_of_Controled_Motor 4 //통신으로 제어하는 모터의 수 ##필요시 수정
#define MoterSerialFormError 'F' //시리얼입력방식에러코드 (입력형식 M1,M2 Mn은 정수 )
#define MoterError 'M' //모터각에러코드 (오버플로우)
#define SerialIsEmpty  'E' //빈 데이터 에러 코드
#define TooLongInput 'L' //너무 긴 입력 에러코드
#define RsNumError 'R'

int Offset[6] = {0, 100, 90, 80, 90, 0};
String MSerial = "0,0,0,0";
int M[6] = {0, 0, 0, 0, 0, 0};
int NumOfRestsymbol;
boolean Error = false;
String ErrorCode = "";

void setup()
{
  Serial.begin(115200); //시리얼 포트0 사용
  Serial1.begin(115200); //시리얼 포트1 사용
  pinMode(LED_BUILTIN, OUTPUT);
  Braccio.begin();
  Serial.println("SerialReady");
  digitalWrite(LED_BUILTIN, HIGH); //빌트인LED로 통신가능을 알림
  WaitForPyCmSetReady();
}
void WaitForPyCmSetReady()
{
  while(Serial1.read()!='s'){Serial.println("wait");} //컴퓨터의 준비완료 플래그를 기다림.
}
//입력받은 버퍼들을 하나의 문자열로 합쳐주는 함수
String readSerial()
{
  String str = "";
  char ch;
  NumOfRestsymbol=0;
  
  //통신중인경우
  while (Serial1.available())
  {
    ch = Serial1.read();
    //입력받는 형식에 맞는지 판별
    if(ch==',')
      NumOfRestsymbol++;
    if(ch<':' && ch>'/' || ch==',' || ch=='-' || ch=='f') 
    {
      str.concat(ch); //문자열에 추가
    }
    else //입력형식에 맞지 않은 경우
    {
      Error = true; //오류코드발생
    }
  }
  if(NumOfRestsymbol > Number_of_Controled_Motor-1) 
  {
    Error=true;
    ErrorCode.concat(RsNumError);
  }
  if(Error==true) ErrorCode.concat(MoterSerialFormError);
  return str; //문자열반환
}


void loop() {
  String MString[Number_of_Controled_Motor];
  int RestSymbolAdress[Number_of_Controled_Motor] = {}; //,의 위치를 저장하고 모터값입력을 위한 위치배열
  RestSymbolAdress[0] = -1; //최초 모터정보 시작 위치 - 문장 시작지점으로 설정
  Error = false; //에러플래그초기화
  ErrorCode = ""; //에러코드 초기화
  digitalWrite(LED_BUILTIN, HIGH); //빌트인LED OFF상태
   
  String FSerial = readSerial(); //통신확인
  if( FSerial[0] == 'f'){
    MSerial = FSerial.substring(1,FSerial.length());
  }
  //입력된 문자열이 너무 긴경우 오류처리
  if (MSerial.length() > 3*Number_of_Controled_Motor)  //#최대 문자열 길이는 모터각 최대값의 자리수, 쉼표수까지 고려해서 정한값
  {
    Error = true; //오류코드발생
    ErrorCode.concat(TooLongInput); //오류코드 저장
    digitalWrite(LED_BUILTIN, LOW); //에러코드출력
    Serial.println(ErrorCode);
  }
  else if (MSerial != "")
  {
    Serial.println("입력이 확인됨: "+MSerial);
    
    RestSymbolAdress[Number_of_Controled_Motor] = MSerial.length()+1; //문자열의 끝을 확인. 
    //시리얼입력방식지정: 모터값을 구분하기 위한 기호를 ','로 한다 
    for(int i=0; i < Number_of_Controled_Motor-1; i++)
    {
      RestSymbolAdress[i+1] = MSerial.indexOf(",", RestSymbolAdress[i] + 1);
      if (RestSymbolAdress[i+1] < 0) 
      {
        Error = true; //쉼표위치가 -1이 된경우(쉼표가 없음) 시리얼폼에러 활성화
        ErrorCode.concat(MoterSerialFormError);
      }
    }

    
    //모터값 문자열 확인 루프
    for (int i = 0; i < Number_of_Controled_Motor-1; i++)
    {
      MString[i] = MSerial.substring(RestSymbolAdress[i] + 1, RestSymbolAdress[i + 1]);
      if (MString[i].toInt() > 32767)//모터값 오버플로우
      {
       Error = true; //오류코드발생
       ErrorCode.concat(MoterError);
      }
      if (MString[i] == NULL)//모터값이 비어있는경우
      {
        Error = true; //오류코드발생
        ErrorCode.concat(SerialIsEmpty);
      }
    }
    MString[3] = MSerial.substring(RestSymbolAdress[3]+1,MSerial.length());

    //정상상태인경우 모터값 세팅
    if (Error==false)
      {
      //모터 값 세팅
      for (int i = 0; i < Number_of_Controled_Motor; i++)
      {
        M[i] = MString[i].toInt();

        //모터 각도 표기
        Serial.println("M[" + String(i) + "]:" + String(M[i]));
        Serial.println("MS[" + String(i) + "]:" + String(MString[i]));
      }
      if(M[3]==0) M[5] = 0;
      else if(M[3]==1) M[5] = 50;
      
      int M1=M[1], M2=M[2];
      if(M[1]<15-90)      M1=-75;
      else if(M[1]>165-90)M1=75;
      if(M[2]>90)         M2=90;
      M[3]=90-M1-M2;
    }
    //에러발생시 빌트인LED를 깜빡여서 알려줌
    else if(Error==true)
    {
      digitalWrite(LED_BUILTIN, LOW);
      //에러코드출력
      Serial.println(ErrorCode);
    }
    Serial1.print('s'); //모터셋작동중을 알림
  }    
  Braccio.ServoMovement(10, M[0]+Offset[0], M[1]+Offset[1], M[2]+Offset[2], M[3]+Offset[3], M[4]+Offset[4], M[5]);
  Serial1.print('r'); //통신준비완료를 알림
}
