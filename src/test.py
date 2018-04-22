import face_recognition
import cv2

cap = cv2.VideoCapture('Django Unchained Trailer.mp4')

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fps = int(cap.get(cv2.CAP_PROP_FPS))
frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_length = int(frames_count / fps)

print(f'{width}x{height} {fps}fps, {frames_count}frames, {video_length}s')

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))

cast = [
    "Jamie Foxx(Django)",
    "Christoph Waltz(Dr. King Schultz)",
    "Leonardo DiCaprio(Calvin Candie)",
    "Kerry Washington(Broomhilda von Shaft)",
    "Samuel L. Jackson(Stephen)"
]

cast_photos = [
    "Jamie Foxx.jpg",
    "Christoph Waltz.jpg",
    "Leonardo DiCaprio.jpg",
    "Kerry Washington.jpg",
    "Samuel L. Jackson.jpg"
]

known_face_encodings = []

for ph in cast_photos:
    max_image = face_recognition.load_image_file(ph)
    known_face_encodings.append(face_recognition.face_encodings(max_image)[0])

# Create arrays of known face encodings and their names
known_face_names = cast

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


frame_n = 0
while True:
    ret, frame = cap.read()
    if ret:
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        out.write(frame)

        if frame_n % fps == 0:
            print(f'{frame_n // fps}s out of {video_length}s')

        frame_n += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

out.release()
cap.release()
cv2.destroyAllWindows()
