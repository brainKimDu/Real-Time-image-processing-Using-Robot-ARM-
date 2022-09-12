from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse
import math
import HDpsk.HD_CnM as CnM #호두 데이터 관리 패키지(로드, 초기화(HDdataset.exe사용), 통신)

def HandTrackingHD(RoboAngle,Ldata,CamNum, CmPort):
    grab = False
    CC_RED = (0x00,0x00,0xff)
    CC_BLUE = (0xff,0x00,0x00)
    CC_BLACK = (0x00,0x00,0x00)
    PointColor = CC_RED

    #데이터 및 통신 로딩
    Cm = CnM.HDSerialCM
    #ARD=CnM.HDSerialCM.setCM(CmPort)

    LR = Ldata[0]+Ldata[1]
    WorkspaceMaxRadiusSQR = LR*LR #작업반경의 외각 반지름의 제곱
    WorkspaceMinRadiusSQR = 2*Ldata[0]*Ldata[1] #작업반경의 내각 반지름의 제곱 Ldata[0]과 Ldata[1]가 같을때(직각이등변삼각형)
    print("Short Restricted area boundary radius Square: "+str(WorkspaceMinRadiusSQR))
    print("Long Restricted area boundary radius Square: "+str(WorkspaceMaxRadiusSQR))
    print()

    try:
        detection_graph, sess = detector_utils.load_inference_graph()
    except:
        print("?")


    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-sth',
        '--scorethreshold',
        dest='score_thresh',
        type=float,
        default=0.2,
        help='Score threshold for displaying bounding boxes')
    parser.add_argument(
        '-fps',
        '--fps',
        dest='fps',
        type=int,
        default=1,
        help='Show FPS on detection/display visualization')
    parser.add_argument(
        '-src',
        '--source',
        dest='video_source',
        default=CamNum,
        help='Device index of the camera.')
    parser.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=640,
        help='Width of the frames in the video stream.')
    parser.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=480,
        help='Height of the frames in the video stream.')
    parser.add_argument(
        '-ds',
        '--display',
        dest='display',
        type=int,
        default=1,
        help='Display the detected images using OpenCV. This reduces FPS')
    parser.add_argument(
        '-num-w',
        '--num-workers',
        dest='num_workers',
        type=int,
        default=4,
        help='Number of workers.')
    parser.add_argument(
        '-q-size',
        '--queue-size',
        dest='queue_size',
        type=int,
        default=5,
        help='Size of the queue.')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video_source)
    start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (cap.get(3), cap.get(4))
    # max number of hands we want to detect/track
    num_hands_detect = 1

    cv2.namedWindow('Single-Threaded Detection', cv2.WINDOW_NORMAL)

    while True:
        Frameheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        Framewidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        PointOffset = (0,Frameheight)

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        ret, image_np = cap.read()
        image_np = cv2.flip(image_np, 1)
        
        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
        # while scores contains the confidence for each of these boxes.
        # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

        boxes, scores = detector_utils.detect_objects(image_np,
                                                        detection_graph, sess)

        # draw bounding boxes on frame
        Point = detector_utils.draw_box_on_image(num_hands_detect, args.score_thresh,
                                            scores, boxes, im_width, im_height,
                                            image_np)
        
        x=Point[0]
        y=Frameheight-Point[1]
        if(x==0 and y==480):
            print('Not found.\n\n')
            print("--------------------------------")
        else:
            print('목표를 찾았습니다.')
            print('좌표 : (%d,%d)'%(x,y))
            # 시리얼 통신                
            XXPYY = x*x+y*y
            if( (XXPYY <= WorkspaceMaxRadiusSQR) and (XXPYY >= WorkspaceMinRadiusSQR) ):
                PointColor = CC_RED #원 빨강
                if(grab==True):
                    G=',1'
                else:
                    G=',0'
                Trans = 'f0,' + str(RoboAngle[x][y])+G
                #Cm.send(ARD,Trans)
                print('각데이터전송:'+Trans)
            else:
                PointColor =  CC_BLUE#원 파랑
                print('out of range')
            print("--------------------------------")
            
        # Calculate Frames per second (FPS)
        num_frames += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time
        src = cv2.resize(image_np,dsize=(480,640),interpolation=cv2.INTER_AREA)
        if (args.display > 0):
            # Display FPS on frame
            if (args.fps > 0):
                detector_utils.draw_fps_on_image("FPS : " + str(int(fps)), src)
            image_np=cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            cv2.circle(image_np, PointOffset, int(math.sqrt(WorkspaceMaxRadiusSQR)), CC_BLACK, 2)  
            cv2.circle(image_np, PointOffset, int(math.sqrt(WorkspaceMinRadiusSQR)), CC_BLACK, 2) 
            cv2.circle(image_np, Point, 1, PointColor, 2)
            cv2.imshow('Single-Threaded Detection',image_np)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                break
            elif k==71 or k==103:
                grab = not(grab and True)
                print("G:"+str(grab))
            else:
                print(k)
        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                    elapsed_time, "fps: ", str(int(fps)))