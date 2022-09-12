########################################################################################
#Project HDbot2D
"""
Team: G.W.
Date: 2021 03 30
Version: 0.1.0 re
Circle
"""
########################################################################################
import math
import cv2
import numpy as np
import serial # 시리얼 통신
import time # sleep 사용

font = cv2.FONT_HERSHEY_SIMPLEX
global LRSquare, SRSquare #제한구역 경계 반지름 제곱 글로벌 변수로 선언

# 출력할 때, 진행과정을 분류하는 역할을 하여, 가독성 향상을 위함
def print_boundary() :
    print("--------------------------------")

#비어있는 n by n크기의 Angle행렬 생성 함수
def CreateNxNMatrix(Xmax,Ymax):
    #비어있는 A배열에 빈배열을 N개 삽입하고 각각의 빈배열에 N개의 인자를 넣는다.
    A=[]
    for i in range(0,Xmax+Ymax+1):
        A.append([])
    for i in range(0,Xmax+Ymax+1):
        for j in range(0,Xmax+Ymax+1):
            A[i].append(None)
    return A

#통신설정함수
def setCM(PORTname):
    # Set a PORT Number & baud rate
    PORT = PORTname
    BaudRate = 115200   
    print("wait for BTC ready.")
    CM= serial.Serial(PORT,BaudRate)
    CM.write('s'.encode('utf-8'))  #통신준비완료신호 송신
    print("Success")
    print()
    return CM

#문자열 슬라이스를 이용한 데이터 분석 
def DataSlice(FLaddress, FMaddress):
    #로봇데이터파일 열기    
    fL = open(FLaddress, 'r')
    fM = open(FMaddress, 'r')
    
    global LRSquare, SRSquare #글로벌 변수 호출
    #링크길이데이터를 읽어들인다
    print("Ldata load...")
    L1 =int(fL.readline())
    L2 =int(fL.readline())
    fL.close()
    print("L1: "+str(L1)+"\nL2: "+str(L2))

    LR = L1+L2
    LRSquare = LR*LR
    SRSquare = 2*L1*L2 #L1과 L2가 같을때(직각이등변삼각형) SR = sqrt(2)*L1
    print("Short Restricted area boundary radius Square: "+str(SRSquare))
    print("Long Restricted area boundary radius Square: "+str(LRSquare))
    #빈좌표계생성
    AM=CreateNxNMatrix(L1,L2)
    
    print("Mdata load...")
    #데이터의 시작플래그를 P로하며, 소괄호안이 위치정보, 대괄호안이 각도정보이다
    data=fM.readline()  #파일을 한줄씩 불러와서 분석한다
    while(data[0:1]=='P'):
        for j in range(0,len(data)):
            if(data[j:j+1]=='('):
                Slocation=j
            if(data[j:j+1]==')'):
                Elocation=j
            if(data[j:j+1]=='['):
                Sangle=j
            if(data[j:j+1]==']'):
                Eangle=j
        Location=data[Slocation+1:Elocation]
        Angle=data[Sangle+1:Eangle]
        spot=0
        #좌표 구분을 반점으로 하여 좌표정보를 잘라넣는다.
        for i in range(0,len(Location)):
            if(Location[i:i+1]==','):
                spot=i

        X=Location[0:spot]
        Y=Location[spot+1:len(Location)]
        AM[int(X)][int(Y)]=Angle
        data=fM.readline()
    print("Success")
    fM.close()
    print()
    return AM

def SAngle(select,Angle):    
     #좌표를 입력받아 각도정보 보내기.
    if(select=='q'):
        return 0
    indexX,indexY=map(int,select.split(','))
    if(indexX>2000 or indexY>2000):
        print("IndexError!")
    else:
        Trans=str(Angle[indexX][indexY]).encode('utf-8')
    return Trans
    

def show_Video(Cam,Angle):
    grab = False
    try:
        print_boundary()
        print('카메라를 구동합니다.')
        cap = cv2.VideoCapture(Cam)
    except:
        print('카메라 구동 실패')
        print_boundary()
        return

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    print_boundary()
    print("높이"+str(height))
    print("넓이"+str(width))
    print_boundary()
    CircleColor = (0x00,0x00,0xff) #원의 칼라코드 초기화 최초상태 빨강

    PointOffset = (0,height)

    while True:
        ret, frame = cap.read()

        if not ret:

            print('비디오 읽기 오류')
            print_boundary()
            break

        frame_Blur = frame.copy()
        frame_Blur = cv2.GaussianBlur(frame_Blur, (3,3), 0)

        frame_gray = cv2.cvtColor(frame_Blur,cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(frame_gray,cv2.HOUGH_GRADIENT, 1, 10, param1 = 60, param2 = 50, minRadius = 10, maxRadius = 100)

        if circles is not None:
            circles = np.uint16(np.around(circles))

            center_x = 0
            center_y = 0
            radius = 0
            count = 0

            for i in circles[0,:]:
                center_x = int(i[0])
                center_y = int(i[1])
                radius = int(i[2])
                radius_cm = int(radius/10)
                
                if count == 1 :
                    break
                
                cv2.putText(frame,'tool',(center_x-10,center_y),font,1,(0,0,255),1)
                cv2.circle(frame, (center_x,center_y), radius, CircleColor, 2)                

                x=center_x
                y=height-center_y

                print('목표를 찾았습니다.')
                print('목표의 중심 좌표 : (%d,%d)'%(x,y))
                # 넣어도 되고... 안 넣어도 되고...
                print('목표의 반지름 : %d cm'%radius_cm)
                print_boundary()
                
                # 시리얼 통신
                global LRSquare, SRSquare #글로벌 변수 호출
                XXPYY = x*x+y*y
                if( (XXPYY <= LRSquare) and (XXPYY >= SRSquare) ):
                    if(grab == True):
                        G=',1'
                    else:
                        G=',0'
                    CircleColor = (0x00,0x00,0xff) #원 빨강
                    Trans = "f"+"0,"+str(Angle[x][y])+G
                    print("Trans: "+Trans)
                    print(str(x)+', '+str(y))
                    Trans = Trans.encode('utf-8')
                    #ARD.write(Trans)        #전송1
                    print('각데이터전송.')
                else:
                    CircleColor = (0xff,0x00,0x00) #원 파랑
                    print('out of range')
                print_boundary()
                count = count+1
        else:
            print('목표를 찾지 못해 재탐색 합니다.')
            print_boundary()


        cv2.circle(frame, PointOffset, int(math.sqrt(160000)), 0xffffff, 2)  
        cv2.circle(frame, PointOffset, int(math.sqrt(80000)), 0xffffff, 2) 
        cv2.imshow('test1',frame)
        time.sleep(0.1)

        k = cv2.waitKey(1) & 0xFF
        
        if k == 27:
            break
        elif k == 71 or k == 103:
            grab = not(grab and True)
            print(grab)
    
    cap.release()
    cv2.destroyAllWindows()


########################################################################################
#main
def run(CmPort,Cam,Ldata,Mdata):
    #데이터 및 통신 로딩
    #ARD=setCM(CmPort)
    L=Ldata
    M=Mdata
    Angle=DataSlice(L,M)
    print_boundary()
    show_Video(Cam,Angle)

#########################################################################################