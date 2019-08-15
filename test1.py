import robot

frame = robot.color_detection.cv2.imread('./test/201.jpg')

robot.judge(frame)
