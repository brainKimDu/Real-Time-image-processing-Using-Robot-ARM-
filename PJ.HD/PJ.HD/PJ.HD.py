"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
 - Team: G.W.
 - Date: 2022.08.31
 - Version: 1.1
 """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import ProjectHD_HandTracking_3D
import ProjectHD_HandTracking_2D
import ProjectHD_3D
import ProjectHD_2D

def setHanOrBall():
	User = input('H or B :')
	if(User=='H' or User=='h'):
		return 0
	elif(User=='B' or User=='b'):
		return 1
	else:
		print("What?");
		return -1

CmPort= 'COM3'
Cam = 0
Ldata = 'Ldata.txt'
Mdata= 'Mdata.txt'
AData = 'AzimuthData.txt'
end = False
while(not end):    
	DM = input('Dimention : ')
	print(DM)
	if(DM == '2'):
		set = setHanOrBall()
		if(set == 0):
			end = ProjectHD_HandTracking_2D.run(CmPort,Cam,Ldata,Mdata,AData)
		elif(set == 1):
			end = ProjectHD_2D.run(CmPort,Cam,Ldata,Mdata)
		else:
			print("What?");
	elif(DM == '3'):
		set = setHanOrBall()
		if(set == 0):
			end = ProjectHD_HandTracking_3D.run(CmPort,Cam,Ldata,Mdata,AData)
		elif(set == 1):
			end = ProjectHD_3D.run(CmPort,Cam,Ldata,Mdata,AData)
		else:
			print("What?");
	else:
		print("What?");

		

print("End.");
		