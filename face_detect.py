def detect_face(img):
    import cv2

    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    image = img
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100,100)
    )

    print("Found {0} faces !".format(len(faces)))

    # Draw rect around faces
    for(x,y,w,h) in faces:
        cv2.rectangle(image, (x,y),(x+w,y+h),(255,255,255),0)

    x = faces[1][0]
    y = faces[1][1]
    w = faces[1][2]
    h = faces[1][3]
    print("x :: "+str(x)+"|| y :: "+str(y)+"|| w :: "+str(w)+"|| h :: "+str(h))

    sub_face = image[y:y+h, x:x+w]

    FaceFileName = "unknownfaces/face_" + str(y) + ".jpg"
    cv2.imwrite(FaceFileName, sub_face)
    print('Saved image !')
    cv2.imshow("Face crop", sub_face)
    # camera.release
    cv2.imshow("Faces found",image)
    cv2.waitKey(0)
    del(cv2)
    return sub_face

