"""
This code assumes that images used for calibration are of the same arUco marker board provided with code

"""

import cv2
from cv2 import aruco
import yaml
import numpy as np
from pathlib import Path

# root directory of repo for relative path specification.
root = Path(__file__).parent.absolute()

# Set this flsg True for calibrating camera and False for validating results real time
calibrate_camera = True

# Set path to the images
calib_imgs_path = root.joinpath("aruco_data")

# For validating results, show aruco board to camera.
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )

#Provide length of the marker's side
markerLength = 3.75  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.5   # Here, measurement unit is centimetre.

# create arUco board
board = aruco.GridBoard_create(4, 5, markerLength, markerSeparation, aruco_dict)

'''uncomment following block to draw and show the board'''
#img = board.draw((864,1080))
#cv2.imshow("aruco", img)

arucoParams = aruco.DetectorParameters_create()

if calibrate_camera == True:
    img_list = []
    calib_fnms = calib_imgs_path.glob('*.jpg')
    print('Using ...', end='')
    for idx, fn in enumerate(calib_fnms):
        img = cv2.imread( str(root.joinpath(fn) ))
        img_list.append( (img,fn) )
        h, w, c = img.shape
    print(len(img_list),'calibration images')

    counter, corners_list, id_list = [], [], []
    first = True
    for im in img_list:
        img_gray = cv2.cvtColor(im[0],cv2.COLOR_RGB2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img_gray, aruco_dict, parameters=arucoParams)
        if ids is None:
            ids = []
        print("Processing: ",im[1])
        print("Detected:   ",len(corners)," corners, ",len(ids)," IDs, ",len(rejectedImgPoints)," fails")
        for c in corners:
            corners_list.append(c[0])
        for i in ids:
            id_list.append(ids[0])
        if len(ids) > 0:
            counter.append(len(ids))
            aruco.drawDetectedMarkers(im[0],corners,ids)
            cv2.imshow("foo",im[0])
        cv2.waitKey(100)

    counter = np.array(counter)
    id_list = np.array(id_list)
    print ("Calibrating camera .... Please wait...")
    #mat = np.zeros((3,3), float)
    ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraAruco(corners_list, id_list, counter, board, img_gray.shape, None, None )

    print("Camera matrix is \n", mtx, "\n And is stored in calibration.yaml file along with distortion coefficients : \n", dist)
    data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}
    with open("calibration.yaml", "w") as f:
        yaml.dump(data, f)

    # end result should look like (cf. https://stackoverflow.com/a/69678079)
    # DATA="<?xml version=\"1.0\"?><opencv_storage><cameraMatrix type_id=\"opencv-matrix\"><rows>3</rows><cols>3</cols><dt>d</dt><data>2.85762378e+03 0. 1.93922961e+03 0. 2.84566113e+03 1.12195850e+03 0. 0. 1.</data></cameraMatrix><distCoeffs type_id=\"opencv-matrix\"><rows>5</rows><cols>1</cols><dt>d</dt><data>-6.14039421e-01 4.00045455e-01 1.47132971e-03 2.46772077e-04 -1.20407566e-01</data></distCoeffs></opencv_storage>"
    s = cv2.FileStorage("calibration.xml", cv2.FileStorage_WRITE)
    s.write("cameraMatrix",mtx)
    s.write("distCoeffs",cv2.transpose(dist))
    s.release()

else:
    camera = cv2.VideoCapture(0)
    ret, img = camera.read()

    with open('calibration.yaml') as f:
        loadeddict = yaml.load(f)
    mtx = loadeddict.get('camera_matrix')
    dist = loadeddict.get('dist_coeff')
    mtx = np.array(mtx)
    dist = np.array(dist)

    ret, img = camera.read()
    img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    h,  w = img_gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

    pose_r, pose_t = [], []
    while True:
        ret, img = camera.read()
        img_aruco = img
        im_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        h,  w = im_gray.shape[:2]
        dst = cv2.undistort(im_gray, mtx, dist, None, newcameramtx)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(dst, aruco_dict, parameters=arucoParams)
        #cv2.imshow("original", img_gray)
        if corners == None:
            print ("pass")
        else:

            ret, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, newcameramtx, dist) # For a board
            print ("Rotation ", rvec, "Translation", tvec)
            if ret != 0:
                img_aruco = aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))
                img_aruco = aruco.drawAxis(img_aruco, newcameramtx, dist, rvec, tvec, 10)    # axis length 100 can be changed according to your requirement

            if cv2.waitKey(0) & 0xFF == ord('q'):
                break;
        cv2.imshow("World co-ordinate frame axes", img_aruco)

cv2.destroyAllWindows()
