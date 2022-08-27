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
import HandTrackingHD_3D as HTHD

#############################################################################################
def run(CmPort,Cam,LF,Mdata,AData):
    Dt = CnM.HDdata
 
    Ldata = Dt.LDataRead(LF)
    print("Ldata[0]: %d" %Ldata[0])
    print("Ldata[1]: %d\n" %Ldata[1])

    print("-RoboData-")
    RoboAngle = Dt.AngleDataFileSlice(Mdata,Ldata)
    print("-AzimuthData-")
    Azimuth = Dt.AngleDataFileSlice(AData,Ldata)

    #영상 프레임분석 및 통신
    HTHD.HandTrackingHD(RoboAngle,Azimuth,Ldata,Cam,CmPort)
#############################################################################################