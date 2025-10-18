import cv2

face_cap = cv2.CascadeClassifier(
    "C:/Users/pritish/AppData/Local/Programs/Python/Python312/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"
)

video_cap = cv2.VideoCapture(0)

while True:
    ret, video_data = video_cap.read()
    if not ret:
        break
    video_data = cv2.flip(video_data, 1)

    col = cv2.cvtColor(video_data, cv2.COLOR_BGR2GRAY)

    faces = face_cap.detectMultiScale(
        col,
        scaleFactor=1.1,
        minNeighbors=10,
        minSize=(60, 60),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        if w > 60 and h > 60:
            cv2.rectangle(video_data, (x, y), (x + w, y + h), (0, 200, 0), 2)
    cv2.imshow("video_live", video_data)

    if cv2.waitKey(10) == ord("q"):
        break

video_cap.release()
cv2.destroyAllWindows()

