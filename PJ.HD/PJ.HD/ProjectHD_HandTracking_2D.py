"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:: Project HDbot ::
 - Team: G.W.
 - Date: 2021.05.17
 - Version: 1.0.2
 - Ex: ProjectHD using Real-time Hand-Detection by Neural Networks

 Development environment:
    python3.7
    tensorflow2.5.0

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import HDpsk.HD_CnM as CnM #호두 데이터 관리 패키지(로드, 초기화(HDdataset.exe사용), 통신)
import HandTrackingHD_2D as HTHD

#############################################################################################
def run(CmPort,Cam,Ldata,Mdata,AData):
    Dt = CnM.HDdata
 
    Llength = Dt.LDataRead(Ldata)
    print("Llength[0]: %d" %Llength[0])
    print("Llength[1]: %d\n" %Llength[1])

    print("-RoboData-")
    RoboAngle = Dt.AngleDataFileSlice(Mdata,Llength)

    #영상 프레임분석 및 통신
    HTHD.HandTrackingHD(RoboAngle,Llength,Cam,CmPort)
#############################################################################################