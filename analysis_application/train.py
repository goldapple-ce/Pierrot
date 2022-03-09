# -*- coding: utf-8 -*-
"""train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rd49yCJM4jNwSSPukAEEeTYqjBJo6SuY

#colab 사용을 위한 사전 작업
"""

# from google.colab import drive
# drive.mount('/content/drive')
#
# import sys
# sys.path.append('/content/drive/My Drive/analysis_application')
# print(sys.path)
#
# !pip install sktime

"""#import
 tracknet: test 폴더 안에 있는 코드
"""

import cv2
import argparse
import queue
import numpy
import pandas
import pickle
import time
import trackplayers
from collections import deque
import pandas as pd
import numpy as np
from copy import deepcopy

# from sktime.datatypes._panel._convert import from_2d_array_to_nested
from PIL import Image, ImageDraw
from pickle import load
from tracknet import trackNet
from bounce import *

"""# 변수 정의 및 사전 작업"""

# 변수정의
current_frame = 0
tracknet_width, tracknet_height = 640, 360
bounce = 1
coords = []
check_time = []
frames = []

# 궤도를 그리기위한 프레임 7장 저장
trajectory_ball = deque()
for i in range(0, 8):
    trajectory_ball.appendleft(None)

path = '/content/drive/MyDrive/analysis_application'
input_video_path = path + '/video/video_cut.mp4'
output_video_path = path + '/video/video_output.mp4'
model1_path = path + '/weight_ball/model.1'
bounce_clf_path = path + '/Weight_ball/clf.pkl'
yolo_label_path = path + '/Yolov3/yolov3.txt'
yolo_weight_path = path + '/Yolov3/yolov3.weights'
yolo_cfg_path = path + '/Yolov3/yolov3.cfg'
tracking_players_path = path + '/tracking_players.csv'

# 영상불러오기 및 영상정보 추출
video = cv2.VideoCapture(input_video_path)
fps = int(video.get(cv2.CAP_PROP_FPS))
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# 영상정보 출력
print('fps : {}'.format(fps))
print('frame sizee : {}x{}'.format(frame_width, frame_height))
print('num_frames :{}'.format(num_frames))

# 트렉넷 모델 불러오기 및 컴파일
modelFN = trackNet
model = modelFN(256, tracknet_height, tracknet_width)
model.compile(loss='categorical_crossentropy',
              optimizer='adadelta', metrics=['accuracy'])
model.load_weights(model1_path)

# 영상 저장을 위한 셋팅
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_video = cv2.VideoWriter(
    output_video_path, fourcc, fps, (frame_width, frame_height))

"""# 선수트래킹

"""

# yolov3
LABELS = open(yolo_label_path).read().strip().split("\n")
# 네트워크 불러오기 -> opencv로 딥러닝을 실행하기 위해 생성
net = cv2.dnn.readNet(yolo_weight_path, yolo_cfg_path)

# 플레이어 트래커
ct_players = trackplayers.CentroidTracker()
# 선수 위치 저장할 변수
players_positions = {'x_0': [], 'y_0': [], 'x_1': [], 'y_1': []}

while True:
    ret, frame = video.read()
    current_frame += 1
    print('tracking the players : {}%, number of frames : {}'.format(
        round((current_frame/num_frames)*100), current_frame))
    if not ret:
      break
    # 프레임 사이즈 및 타입 수정을 위한 복사

    output_frame = frame

    #################### 선수 #############################
    scale = 0.00392
    # 입력 영상을 blob 객체로 만들기 -> 해당 인자들은 모델 파일의 학습에 맞게 입력되어있음
    # blob: Binary Large Object 의 약자. 즉, 바이너리 형태로 큰 객체(이미지, 사운드 등)를 저장
    blob = cv2.dnn.blobFromImage(
        frame, scale, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)  # 네트워크 입력 설정
    # 네트워크 순방향 실행을 위한 코드
    # input: 출력 레이어 이름 리스트
    # output: 지정한 레이어의 출력 블롭 리스트
    outs = net.forward(trackplayers.get_output_layer(net))
    # 선수들 위치
    detected_players = trackplayers.predict_players(outs, LABELS, frame, 0.8)
    # print(detected_players)

    # map 함수는 첫번째 매개변수에 함수, 두번째 매개변수에 반복 가능한 자료형(리스트, 튜플 등)
    # map 함수의 반환 값은 map 객체-> 해당 자료형을 list 혹은 tuple 로 형변환 필요
    # map(적용시킬 함수, 적용할 값들)
    # track players with a unique ID
    format_detected_players = list(
        map(trackplayers.update_boxes, list(detected_players)))
    players_objects = ct_players.update(format_detected_players)

    # players positions frame by frame

    players_positions['x_0'].append(tuple(players_objects[0])[0])
    players_positions['y_0'].append(tuple(players_objects[0])[1])
    players_positions['x_1'].append(tuple(players_objects[1])[0])
    players_positions['y_1'].append(tuple(players_objects[1])[1])

    # draw players boxes
    color_box = (0, 0, 255)

    # 선수 draw
    if len(detected_players) > 0:
        for box in detected_players:
            print(box)
            x, y, w, h = box
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), color_box, 2)

    # draw tracking id of each player
    for (objectID, centroid_player) in players_objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(output_frame, text, (centroid_player[0] - 50, centroid_player[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.circle(
            output_frame, (centroid_player[0], centroid_player[1]), 1, (0, 255, 0), 2)
    frames.append(output_frame)
video.release
output_video.release
current_frame = 0
print("complete tracking the players")

"""# 공트래킹"""

last = time.time()  # start counting
# 프레임단위로 반복
for frame in frames :
    current_frame += 1
    print('percentage of video processed : {}%, number of frames : {}frame'.format(round((current_frame/num_frames)*100), current_frame))

    # 프레임 사이즈 및 타입 수정을 위한 복사
    output_frame = frame

    # 프레임 사이즈 및 타임 수정
    frame = cv2.resize(frame, (tracknet_width, tracknet_height))
    frame = frame.astype(numpy.float32)

    #
    X = numpy.rollaxis(frame, 2, 0)

    # 히트맵 예측
    predict = model.predict(numpy.array([X]))[0]
    predict = predict.reshape(
        (tracknet_height, tracknet_width, 256)).argmax(axis=2)

    # cv2이미지 uint8로 변경해야만함
    predict = predict.astype(numpy.uint8)
    heatmap = cv2.resize(predict, (frame_width, frame_height))

    # 이미지 이진화작업 및 공 후보 트래킹 출력
    ret, heatmap = cv2.threshold(heatmap, 127, 255, cv2.THRESH_BINARY)
    circles = cv2.HoughCircles(heatmap, cv2.HOUGH_GRADIENT, dp=1,
                               minDist=1, param1=50, param2=2, minRadius=2, maxRadius=7)
    PIL_image = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
    PIL_image = Image.fromarray(PIL_image)

    # 공후보 트래킹 성공 시 트래킹 표시
    if circles is not None:
        print("공후보 트랙킹 성공")
        # 공후보가 하나 일 시 트래킹 표시
        if len(circles) == 1:
            print("공후보 하나")
            x = int(circles[0][0][0])
            y = int(circles[0][0][1])

            coords.append([x, y])
            check_time.append(time.time()-last)
            trajectory_ball.appendleft([x, y])
            trajectory_ball.pop()

        # 두 개 이상일 시 트래킹 표시하지 않음
        else:
            print("공후보 두개 이상")
            coords.append(None)
            check_time.append(time.time()-last)
            trajectory_ball.appendleft(None)
            trajectory_ball.pop()

    # 공 후보 트래킹 실패 시 트래킹 표시하지 않음
    else:
        coords.append(None)
        check_time.append(time.time()-last)
        trajectory_ball.appendleft(None)
        trajectory_ball.pop()


    # 전 7장의 프레임 후보공 draw
    for i in range(0, 8):
        if trajectory_ball[i] is not None:
            draw_x = trajectory_ball[i][0]
            draw_y = trajectory_ball[i][1]
            position_circle = (draw_x - 2, draw_y-2, draw_x+2, draw_y+2)
            draw = ImageDraw.Draw(PIL_image)
            draw.ellipse(position_circle, outline='yellow')
            del draw

    opencvImage = cv2.cvtColor(numpy.array(PIL_image), cv2.COLOR_RGB2BGR)
    output_video.write(opencvImage)
    current_frame += 1

video.release()
output_video.release()

"""# 선수 위치 저장"""

# players positions
df_players_positions = pd.DataFrame()
df_players_positions['x_0'] = players_positions['x_0']
df_players_positions['y_0'] = players_positions['y_0']
df_players_positions['x_1'] = players_positions['x_1']
df_players_positions['y_1'] = players_positions['y_1']
df_players_positions.to_csv("tracking_players.csv")

"""# 바운드체크"""

# 전 프레임의 공과 위치 비교 및 이상값제거
for _ in range(3):
    x, y = diff_xy(coords)
    remove_outliers(x, y, coords)

# 보간법. 트래킹이 안되었을 시 예측값삽입
coords = interpolation(coords)

# velocity
Vx = []
Vy = []
V = []
frames = [*range(len(coords))]
print("frames : {}".format(frames))

for i in range(len(coords)-1):
    p1 = coords[i]
    p2 = coords[i+1]
    t1 = check_time[i]
    t2 = check_time[i+1]
    x = (p1[0]-p2[0])/(t1-t2)
    y = (p1[1]-p2[1])/(t1-t2)
    Vx.append(x)
    Vy.append(y)

for i in range(len(Vx)):
    vx = Vx[i]
    vy = Vy[i]
    v = (vx**2+vy**2)**0.5
    V.append(v)

xy = coords[:]

if bounce == 1:
    # Predicting Bounces
    test_df = pandas.DataFrame(
        {'x': [coord[0] for coord in xy[:-1]], 'y': [coord[1] for coord in xy[:-1]], 'V': V})

    # df.shift
    for i in range(20, 0, -1):
        test_df[f'lagX_{i}'] = test_df['x'].shift(i, fill_value=0)
    for i in range(20, 0, -1):
        test_df[f'lagY_{i}'] = test_df['y'].shift(i, fill_value=0)
    for i in range(20, 0, -1):
        test_df[f'lagV_{i}'] = test_df['V'].shift(i, fill_value=0)

    test_df.drop(['x', 'y', 'V'], 1, inplace=True)

    Xs = test_df[['lagX_20', 'lagX_19', 'lagX_18', 'lagX_17', 'lagX_16',
                  'lagX_15', 'lagX_14', 'lagX_13', 'lagX_12', 'lagX_11', 'lagX_10',
                  'lagX_9', 'lagX_8', 'lagX_7', 'lagX_6', 'lagX_5', 'lagX_4', 'lagX_3',
                  'lagX_2', 'lagX_1']]
    Xs = from_2d_array_to_nested(Xs.to_numpy())

    Ys = test_df[['lagY_20', 'lagY_19', 'lagY_18', 'lagY_17',
                  'lagY_16', 'lagY_15', 'lagY_14', 'lagY_13', 'lagY_12', 'lagY_11',
                  'lagY_10', 'lagY_9', 'lagY_8', 'lagY_7', 'lagY_6', 'lagY_5', 'lagY_4',
                  'lagY_3', 'lagY_2', 'lagY_1']]
    Ys = from_2d_array_to_nested(Ys.to_numpy())

    Vs = test_df[['lagV_20', 'lagV_19', 'lagV_18',
                  'lagV_17', 'lagV_16', 'lagV_15', 'lagV_14', 'lagV_13', 'lagV_12',
                  'lagV_11', 'lagV_10', 'lagV_9', 'lagV_8', 'lagV_7', 'lagV_6', 'lagV_5',
                  'lagV_4', 'lagV_3', 'lagV_2', 'lagV_1']]
    Vs = from_2d_array_to_nested(Vs.to_numpy())

    X = pandas.concat([Xs, Ys, Vs], 1)

    # load the pre-trained classifier
    clf = load(open(path + '/weight_ball/clf.pkl', 'rb'))

    predcted = clf.predict(X)
    idx = list(numpy.where(predcted == 1)[0])
    idx = numpy.array(idx) - 10

    video = cv2.VideoCapture(output_video_path)

    output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    print('fps : {}'.format(fps))
    print('frame sizee : {}x{}'.format(output_width, output_height))
    print('num_frames :{}'.format(num_frames))

    output_video = cv2.VideoWriter(path + '/video/final_video.mp4', fourcc, fps, (output_width, output_height))
    i = 0
    while True:
        ret, frame = video.read()
        if ret:
          if coords[i] is not None:
            if i in idx:
                center_coordinates = int(xy[i][0]), int(xy[i][1])
                radius = 3
                color = (255, 0, 0)
                thickness = -1
                cv2.circle(frame, center_coordinates, 10, color, thickness)
            i += 1
            output_video.write(frame)
        else:
            break
    video.release()
    output_video.release()

"""# 선수, 탑 뷰에서 보이는 것처럼"""

# input 으로 받은 좌표를 직사각형으로 바꿔주는 작업
def order_points(pts):
    # 4, 2 배열을 0으로 초기화 하여 만듦 타입은 float
    rect = np.zeros((4, 2), dtype="float32")
    # pts 는 4x2배열이고 이 배열을 axis 를 1을 기준으로 더하여 4x1배열로 만들어 반환
    # 이를 하는 이유는 바운딩 박스는 두 좌표만 존재하면 구현이 가능하므로
    # 좌 상단은 x,y 의 좌표의 합이 가장 작은 곳이고,
    # 우 하단은 x,y 의 좌표의 합이 가장 큰 곳이기에
    # 두 좌표의 합을 비교하여 좌 상단은 rect[0],
    # 우 하단은 rect[2] 에
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # diff 를 x에서 y를 뺏을 때의 값을 구함
    # 우 상단은 diff 의 값이 가장 작은 곳
    # 좌 하단은 diff 의 값이 가장 큰 곳이기에
    # rect[1] 에는 우 상단, rect[3] 은 좌 하단
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


# 코트의 좌표를 생성하는 모듈
def transition_matrix(image_pts, bev_pts):
    rect_image = order_points(image_pts)
    rect_bev = order_points(bev_pts)
    # getPerspectiveTransform 해당 함수는 직사각형이 아닌 좌표를 경기장 규격에 맞게 투시 변환을 해주기 위해 사용
    M = cv2.getPerspectiveTransform(rect_image, rect_bev)
    return M


# width 기준으로 코드 비율 맞춰 코드 변환
def court_coord(width, pad):
    height = int(width * (1 - pad) * 2 * (1 + pad))
    x_1, y_1 = int(width * pad), int(height * pad)
    x_2, y_2 = int(width * (1 - pad)), int(height * pad)
    x_3, y_3 = int(width * (1 - pad)), int(height * (1 - pad))
    x_4, y_4 = int(width * pad), int(height * (1 - pad))
    return [(x_1, y_1), (x_2, y_2), (x_3, y_3), (x_4, y_4)]


def player_coord(coord_image, M):
    X = list(coord_image)
    X.append(1)
    X = np.array(X)
    # X의 행렬 곱의 결과
    Y = M.dot(X)
    Y = tuple(map(lambda x: round(x / Y[2]), Y))
    return (Y[0], Y[1])


class top_view_court:
    def __init__(self, width, pad):
        line_color = (255, 255, 255)
        court_color_1 = (192, 158, 128)
        court_color_2 = (153, 112, 80)

        height = int(width * (1 - pad) * 2 * (1 + pad))
        self.court = np.zeros((height, width, 3), np.uint8)

        cv2.rectangle(self.court, (0, 0), (width, height), court_color_1, -1)

        # 외곽선
        x_1, y_1 = int(width * pad), int(height * pad)
        x_2, y_2 = int(width * (1 - pad)), int(height * pad)
        x_3, y_3 = int(width * (1 - pad)), int(height * (1 - pad))
        x_4, y_4 = int(width * pad), int(height * (1 - pad))

        cv2.rectangle(self.court, (x_1, y_1), (x_3, y_3), court_color_2, -1)
        cv2.line(self.court, (x_1, y_1), (x_2, y_2), line_color, 2)
        cv2.line(self.court, (x_2, y_2), (x_3, y_3), line_color, 2)
        cv2.line(self.court, (x_3, y_3), (x_4, y_4), line_color, 2)
        cv2.line(self.court, (x_4, y_4), (x_1, y_1), line_color, 2)

        # 실제 경기장 비율
        x_ratio = (x_2 - x_1) / 10.97
        y_ratio = (y_3 - y_2) / 23.78

        # 복식 라인
        xc_1, yc_1 = int(x_1 + x_ratio * 1.372), y_1
        xc_2, yc_2 = int(x_2 - x_ratio * 1.372), y_2
        xc_3, yc_3 = int(x_3 - x_ratio * 1.372), y_3
        xc_4, yc_4 = int(x_4 + x_ratio * 1.372), y_4

        cv2.line(self.court, (xc_1, yc_1), (xc_4, yc_4), line_color, 2)
        cv2.line(self.court, (xc_2, yc_2), (xc_3, yc_3), line_color, 2)

        # 서브라인
        xs_1, ys_1 = xc_1, int(y_1 + 5.50 * y_ratio)
        xs_2, ys_2 = xc_2, int(y_2 + 5.50 * y_ratio)
        xs_3, ys_3 = xc_3, int(y_3 - 5.50 * y_ratio)
        xs_4, ys_4 = xc_4, int(y_4 - 5.50 * y_ratio)

        cv2.line(self.court, (xs_1, ys_1), (xs_2, ys_2), line_color, 2)
        cv2.line(self.court, (xs_3, ys_3), (xs_4, ys_4), line_color, 2)

        # 네트
        xnet_1, ynet_1 = x_1, int((y_4 - y_1) / 2 + y_1)
        xnet_2, ynet_2 = x_2, int((y_4 - y_1) / 2 + y_1)

        cv2.line(self.court, (xnet_1, ynet_1), (xnet_2, ynet_2), line_color, 2)

        # 가운데 서브 라인
        xv_1, yv_1 = int((x_2 - x_1) / 2 + x_1), ys_1
        xv_2, yv_2 = int((x_2 - x_1) / 2 + x_1), ys_3
        cv2.line(self.court, (xv_1, yv_1,), (xv_2, yv_2), line_color, 2)

        # 중앙 마크 표시
        xm = int((x_2 - x_1) / 2 + x_1)
        ym_1 = y_1
        ym_2 = int(y_1 + 10)
        ym_3 = int(y_4 - 10)
        ym_4 = y_4

        cv2.line(self.court, (xm, ym_1), (xm, ym_2), line_color, 2)
        cv2.line(self.court, (xm, ym_3), (xm, ym_4), line_color, 2)

    # 선수 그리기
    def add_player(self, coord_bev, n_player, color_player_1, color_player_2):
        x, y = coord_bev
        if n_player == 0:
            cv2.circle(self.court, (x, y), radius=7, color=color_player_1, thickness=-1)
            cv2.circle(self.court, (x, y), radius=7, color=(255, 255, 255), thickness=2)
        elif n_player == 1:
            cv2.circle(self.court, (x, y), radius=7, color=color_player_2, thickness=-1)
            cv2.circle(self.court, (x, y), radius=7, color=(255, 255, 255), thickness=2)

    def add_ball(self, coord_bev, color):
      x, y = coord_bev
      cv2.circle(self.court, (x,y), radius = 4, color=color, thickness = -1)

    # 선수 이동 경로 그리기
    def add_path_player(self, coord_bev, color_path=(255, 255, 255)):
        x, y = coord_bev
        cv2.circle(self.court, (x, y), radius=1, color=color_path, thickness=-1)

    def add_path_ball(self, coord_bev, color_path=(0,0,0)):
        x, y = coord_bev
        cv2.circle(self.court, (x, y), radius=1, color=color_path, thickness=-1)


# 영상출력 크기
output_width = 1000
pad = 0.22
output_height = int(output_width * (1 - pad) * 2 * (1 + pad))

# 코트의 상하좌우 좌표 -> 영상마다 바꿔야 함
image_pts = np.array([(574, 307), (1338, 307), (1566, 871), (363, 871)]).reshape(4, 2)
bev_pts = np.array(court_coord(output_width, pad)).reshape(4, 2)
# 촬영한 영상을 탑 뷰에서 보여주기 위해 두 좌표의 차이를 반환
M = transition_matrix(image_pts, bev_pts)

# 이미 트래킹을 끝낸 후 가공된 csv 파일 불러오기
position_df = pd.read_csv('/content/drive/MyDrive/analysis_application/tracking_players.csv')
position_df['cp_0'] = list(zip(position_df.x_0, position_df.y_0))
position_df['cp_1'] = list(zip(position_df.x_1, position_df.y_1))
position_df['coord_bev_0'] = position_df['cp_0'].apply(lambda x: player_coord(x, M))
position_df['coord_bev_1'] = position_df['cp_1'].apply(lambda x: player_coord(x, M))
position_0 = list(position_df['coord_bev_0'])  # 선수 1
position_1 = list(position_df['coord_bev_1'])  # 선수 2

# 이미 트래킹을 끝낸 공 위치 csv 파일 불러오기
position_ball_df = pd.read_csv('/content/drive/MyDrive/analysis_application/tracking_ball.csv')
position_ball_df['cp'] = list(zip(position_ball_df.x_0, position_ball_df.y_0))
position_ball_df['coord_bev'] = position_ball_df['cp'].apply(lambda x: player_coord(x, M))
position_ball = list(position_ball_df['coord_bev'])  # 선수 1

# top view 영상 저장
# path = '/content/drive/MyDrive/analysis_application'
output_video_path = path + '/video/output_top_view.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 60

output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, output_height))

court_base = top_view_court(output_width, pad)

# top view 영상 저장을 위해
i = 0
while True:
    if len(position_0) == i:
        print("break")
        break
    if len(position_ball) == i:
      print("ball break")
      break
    # 선수 경로같은 경우는 계속해서 축적되어야 하고, 선수같은 경우 해당 프레임에서만 그려줘야 하므로
    court = deepcopy(court_base)
    # 색상 변경 하자
    court.add_player(position_0[i], 0, (255, 0, 0), (0, 0, 0))
    court.add_player(position_1[i], 0, (38, 19, 15), (0, 0, 0))
    court.add_ball(position_ball[i], (0,255,0,))

    court_base.add_path_player(position_0[i])
    court_base.add_path_player(position_1[i])
    # court_base.add_path_ball(position_ball[i])

    output_video.write(court.court)
    i += 1

output_video.release()

