import cv2, face_recognition, os

os.makedirs("test_faces", exist_ok=True)
cam = cv2.VideoCapture(0)
print("Press S to snap a test photo, ESC to quit")

while True:
    ret, frame = cam.read()
    cv2.imshow("Test - Press S", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        cv2.imwrite("test_faces/test.jpg", frame)  # saves COLOR
        img = face_recognition.load_image_file("test_faces/test.jpg")
        encs = face_recognition.face_encodings(img)
        print("🎉 Face detected! Camera works." if encs else "❌ No face found. Check lighting.")
        break
    elif key == 27:
        break

cam.release()
cv2.destroyAllWindows()