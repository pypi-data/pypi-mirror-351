import cv2
import numpy as np
from ultralytics import YOLO

def get_ballPix_coors(video_path):
    # video_path = "C:/Users/samuel901213/Downloads/PythonComputerVision-6-CameraCalibration-master/PythonComputerVision-6-CameraCalibration-master/throwoutputviews/throwoutputview1.mp4"
    cap = cv2.VideoCapture(video_path)

    # 確保影片能成功開啟
    if not cap.isOpened():
        print("❌ 無法開啟影片，請確認影片路徑或格式是否正確")
        exit()

    # 影片解析度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"✅ 影片解析度：{width}x{height}")

    # 建立 CSRT 追蹤器
    tracker = cv2.TrackerMIL_create()

    # 讀取第一幀
    ret, frame = cap.read()
    if not ret:
        print("❌ 讀取第一幀失敗")
        cap.release()
        exit()

    # 確保顯示正確大小
    frame = cv2.resize(frame, (int(width/3), int(height/3)))

    # 預設追蹤區域（x, y, w, h）-> 確保座標合理
    # bbox = (int(181/3), int(1250/3), 50, 50)  # 確保這些座標不超過畫面範圍
    bbox = cv2.selectROI("選擇追蹤物件", frame, fromCenter=False, showCrosshair=True)
    tracker.init(frame, bbox)


    # 存儲追蹤到的點
    ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 編碼格式 (你也可以使用其他編碼格式，如 'XVID', 'MJPG', etc.)
    out = cv2.VideoWriter("C:/Users/samuel901213/Downloads/PythonComputerVision-6-CameraCalibration-master/PythonComputerVision-6-CameraCalibration-master/米聽resource/gg2.mp4", fourcc, 60.0, (width//3, height//3))  # 設定影片輸出
    while True:


        ret, frame = cap.read()
        if not ret:
            print("🎥 影片播放結束")
            break

        # 確保顯示正確大小
        frame = cv2.resize(frame, (int(width/3), int(height/3)))

        # 更新追蹤器
        success, bbox = tracker.update(frame)

        if success:
            # 追蹤成功，畫出矩形框
            x, y, w, h = map(int, bbox)
            
            ballpixs = np.vstack((ballpixs, np.array([x, y])))  

            if(x > 200): 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else: 
                break
        
        else:
            cv2.putText(frame, "track failed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print("failed")
            break
        
        out.write(frame)
        cv2.imshow("track", frame)

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    ballpixs = ballpixs * 3
    print("⚽ 追蹤到的座標：")
    print("catched_ball (pixel)", ballpixs)
    print("catched_number", ballpixs.size)

    return ballpixs


def get_ballPix_coors_YOLO(video_path):
    
    model = YOLO("C:/Users/samuel901213/Desktop/yolov8-master/runs/train/train13/weights/best.pt")

    # 讀取影片
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 建立影片寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output_detecteddd.mp4", fourcc, fps, (width//3, height//3))
    ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列
    stop = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # YOLOv8 偵測
        results = model(frame, imgsz=320, conf=0.1)
        # 繪圖顯示
        # if(len(results[0].boxes) == 0):
        #     ballpixs = np.vstack((ballpixs, np.array([0, 0]))) 

        annotated_frame = results[0].plot()       
        annotated_frame=cv2.resize(annotated_frame,(int(width/3), int(height/3)))
        if len(results[0].boxes) > 0:
            # 找出最大信心值對應的框
            confs = results[0].boxes.conf
            best_idx = confs.argmax()
            best_box = results[0].boxes.xywh[best_idx]
            x_center, y_center, w, h = map(int, best_box)

            # 停止條件：x_center 太靠左
            # if x_center < 600:
            #     stop = True

            # 儲存該中心點
            ballpixs = np.vstack((ballpixs, np.array([x_center, y_center])))

        else:
            # 沒有偵測結果時記錄 (0, 0)
            ballpixs = np.vstack((ballpixs, np.array([0, 0])))
        if(stop):
            break
        cv2.imshow("YOLOv8 Detection", annotated_frame)

        # 儲存影片
        out.write(annotated_frame)

        # 按 q 結束
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # ballpixs = ballpixs * 3

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("catched_number", ballpixs.size)
    return ballpixs




