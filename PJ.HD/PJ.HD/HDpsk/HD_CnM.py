"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:: HoDoo Data Comunicate And Management ::
    - Version: 0.1.0    
    - ParkHoyoun
    - 2021.04.15
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import subprocess #외부프로그램 실행을 위한 툴
import serial # 시리얼 통신

class HDdata:      
    #비어있는 X by Y 크기의 행렬 생성 함수
    def CreateMatrix(Xmax, Ymax):
        try:
            #비어있는 공간 M 생성
            M = []
            #M에 빈배열을 N개 삽입하고 각각의 빈배열에 N개의 None인자를 넣는다.
            for i in range(0,Xmax+1):
                M.append([])
            for i in range(0,Xmax+1):
                for j in range(0,Ymax+1):
                    M[i].append(None)
            #생성된 X by Y 크기의 공간 M 반환
            return M
        except MemoryError:
            print("Memory Error!!! Press Enter to Exit Program")
            input()
            exit(0) 
    
    #문자열 슬라이스 데이터 분석, 초기화 매소드
    def AngleDataFileSlice(Fileaddress,LM):
        #로봇데이터파일 열기    
        try:
            fp = open(Fileaddress, 'r')
        except:
            print("File Open Error!!! Open Create Data Program And Restart Process")            
            HDdata.HDdataSet()
            try:
                fp = open(Fileaddress, 'r')
            except:
                print("File Open Error!!! Enter to Exit Program.")
                input()
                exit(0)                

        #빈좌표계생성
        AngleData = HDdata.CreateMatrix(LM[0]+LM[1], LM[0]+LM[1])
    
        print("Data load...")
        #데이터의 시작플래그를 P로하며, 소괄호안이 위치정보, 대괄호안이 각도정보이다    
        data=fp.readline()  #파일을 한줄씩 불러와서 분석한다
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
            AngleData[int(X)][int(Y)]=Angle
            data=fp.readline()  #파일을 한줄씩 불러와서 분석한다
        print("Success")
        fp.close()
        print()
        return AngleData

    #링크데이터 초기화 매소드
    def LDataRead(FLaddress):
        L = [0,0]

        #로봇데이터파일 열기    
        try:
            fL = open(FLaddress, 'r')
        except:
            print("Link File Open Error!!! Open Create Data Program And Restart Process")
            HDdata.HDdataSet()   
            try:
                fL = open(FLaddress, 'r')
            except:
                print("File Open Error!!! Enter to Exit Program.")
                input()
                exit(0) 

        #링크길이데이터를 읽어들인다
        print("Ldata load...")
        L[0] =int(fL.readline())
        L[1] =int(fL.readline())
        fL.close()
        print("Success")
        L[0] = L[0]
        L[1] = L[1]    
        print()
        return L   

    def HDdataSet():
        print('L1,L2?')
        try:
            subprocess.run(['HDdataset.exe'])
        except:
            print('Open Error!!! Check Data generate Program. Enter to Exit Program.')
            exit(0)
        print("--------------------------------")
        return 0

class HDSerialCM:
    #통신설정함수
    def setCM(PORTname):
        try:
            # Set a PORT Number & baud rate
            PORT = PORTname
            BaudRate = 115200   
            print("wait for BTC ready.")
            CM= serial.Serial(PORT,BaudRate)
            CM.write('s'.encode('utf-8'))  #통신준비완료신호 송신
            print("Success")
            print()
            return CM
        except:
            print("Communication Error!!! Press Enter to Exit Program")
            input()
            exit(0) 

    #문자열 송신
    def send(SCMname,Trans):
        print("Trans:" + Trans)
        Trans = Trans.encode('utf-8')
        SCMname.write(Trans)