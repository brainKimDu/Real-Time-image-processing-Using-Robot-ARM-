import ProjectHD_HandTracking_3D
import ProjectHD_HandTracking_2D
import ProjectHD_3D
import ProjectHD_2D

CmPort= 'COM3'
Cam = 0
Ldata = 'Ldata.txt'
Mdata= 'Mdata.txt'
AData = 'AzimuthData.txt'
Finish = False
while(not Finish):    
    set = input('Dimention : ')
    if(set=='2'):
        while(1):            
            set = input('H or B :')
            if(set=='H'):
                ProjectHD_HandTracking_2D.run(CmPort,Cam,Ldata,Mdata,AData)
                Finish = True
            elif(set=='B'):
                ProjectHD_2D.run(CmPort,Cam,Ldata,Mdata)
                Finish = True
            break

    elif(set == '3'):
        while(1):
            set = input('H or B :')
            if(set=='H'):
                ProjectHD_HandTracking_3D.run(CmPort,Cam,Ldata,Mdata,AData)
                Finish = True
            elif(set=='B'):
                ProjectHD_3D.run(CmPort,Cam,Ldata,Mdata,AData)
                Finish = True
            break
