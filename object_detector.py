import cv2
import numpy as np

# Load class labels (from COCO dataset)
class_names = []
with open("coco.names", "r") as f:
    class_names = f.read().strip().split("\n")

# Load the pre-trained model (MobileNet SSD in this case)
net = cv2.dnn.readNetFromCaffe("ssd_mobilenet_v3.prototxt", 
                               "ssd_mobilenet_v3.caffemodel")

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    (h, w) = frame.shape[:2]

    # Convert frame to blob (input format for network)
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

    # Pass blob through network
    net.setInput(blob)
    detections = net.forward()

    # Loop over detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # Filter weak detections
        if confidence > 0.5:
            idx = int(detections[0, 0, i, 1])  # Class ID
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Display label & confidence
            label = f"{class_names[idx]}: {confidence*100:.1f}%"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, (0, 255, 0), 2)

    # Show output
    cv2.imshow("Object Detection", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
