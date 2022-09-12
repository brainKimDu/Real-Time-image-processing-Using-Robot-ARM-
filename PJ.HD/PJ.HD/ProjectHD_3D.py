"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:: Project HDbot ::
 - Team: G.W.
 - Date: 2022.08.31
 - Version: 0.3.2
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import math
import cv2
import numpy as np
import time # sleep 사용
import HDpsk.HD_CnM as CnM #호두 데이터 관리 패키지(로드, 초기화(HDdataset.exe사용), 통신)


# 실행중 콘솔에 구분기호 표기 매소드 가독성 향상을 위함
def print_boundary() :
    print("--------------------------------")

#호두 프레임분석 및 통신 매소드
def HD_Video(Cam,roboAngle, Azimuth, LM):
    grab = False
    MaxDistance = 400
    MinRadius = 30
    MaxRadius = 100
    CC_RED = (0x00,0x00,0xff)
    CC_BLUE = (0xff,0x00,0x00)
    CC_BLACK = (0x00,0x00,0x00)

    LR = LM[0]+LM[1]
    LRSquare = LR*LR #외각제한구역의 반지름의 제곱
    SRSquare = 2*LM[0]*LM[1] #내각제한구역의 반지름의 제곱 LM[0]과 LM[1]가 같을때(직각이등변삼각형)
    print("Short Restricted area boundary radius Square: "+str(SRSquare))
    print("Long Restricted area boundary radius Square: "+str(LRSquare))
    print()
    
    try:
        print_boundary()
        print('카메라를 구동합니다.')
        cap = cv2.VideoCapture(Cam)
    except:
        print("Cam Open Error!!! Press Enter to Exit Program")
        input()
        exit(0) 

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    print_boundary()
    print("높이"+str(height))
    print("넓이"+str(width))
    print_boundary()
    CircleColor = CC_RED #원의 칼라코드 초기화 최초상태 빨강
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read Error!!! Press Enter to Exit Program")
            input()
            exit(0) 
       
        frame_Blur = frame.copy()
        frame_Blur = cv2.GaussianBlur(frame_Blur, (3,3), 0)

        frame_gray = cv2.cvtColor(frame_Blur,cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(
            frame_gray,cv2.HOUGH_GRADIENT, 
            1, 
            10, 
            param1 = 60, 
            param2 = 50, 
            minRadius = MinRadius, 
            maxRadius = MaxRadius
            )        

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
                Distance = int(MaxDistance - MaxDistance * radius/MaxRadius)
                if count == 1 :
                    break
                               
                x=center_x
                y=height-center_y

                print('목표를 찾았습니다.')
                print('목표의 중심 좌표 : (%d,%d)'%(x,y))
                print('목표의 반지름 : %d cm'%radius)
                print('캠과의 거리 : %d' %Distance)
                
                # 시리얼 통신                
                XXPYY = x*x+y*y
                if( (XXPYY <= LRSquare) and (XXPYY >= SRSquare) ):
                    CircleColor = CC_RED #원 빨강
                    if grab==True:
                        G=',1'
                    else:
                        G=',0'
                    Trans = 'f' + str(Azimuth[x][Distance]) + ',' + str(roboAngle[x][y]) + G
                    #Cm.send(ARD,Trans)
                    print('각데이터전송:'+Trans)
                else:
                    CircleColor = CC_BLUE #원 파랑
                    print('out of range')
                print_boundary()
                count = count+1

                cv2.circle(frame, (center_x,center_y), radius, CircleColor, 2)  
                cv2.circle(frame, (center_x,center_y), 1, CircleColor, 2)
        else:
            print('목표를 찾지 못해 재탐색 합니다.')            
            print_boundary()
        cv2.circle(frame, (0,height), int(math.sqrt(LRSquare)), CC_BLACK, 2)  
        cv2.circle(frame, (0,height), int(math.sqrt(SRSquare)), CC_BLACK, 2) 
        cv2.imshow('test1',frame)

        #time.sleep(0.1) #하드웨어 성능에 따라 알아서 딜레이 조절할것. 미설정시 30fps(카메라 퍼포먼스에 근거)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        elif k==71 or k==103:
            grab = not(grab and True)
            print("G:"+str(grab))
    
    cap.release()
    cv2.destroyAllWindows()

#############################################################################################
def run(CmPort,Cam,Ldata,Mdata,Adata):
    Cm = CnM.HDSerialCM
    Dt = CnM.HDdata

    #데이터 및 통신 로딩
    #ARD=Cm.setCM(CmPort)
    Llength = Dt.LDataRead(Ldata)
    print("Llength[0]: %d" %Llength[0])
    print("Llength[1]: %d\n" %Llength[1])
    print("-RoboData-")
    RoboAngle = Dt.AngleDataFileSlice(Mdata,Llength)
    print("-AzimuthData-")
    Azimuth = Dt.AngleDataFileSlice(Adata,Llength)

    #영상 프레임분석 및 통신
    print_boundary()
    HD_Video(Cam,RoboAngle,Azimuth,Llength)

    return True #종료값 리턴
#############################################################################################