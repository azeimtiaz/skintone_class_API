from flask import Flask,request, jsonify
import face_detect
import kMeansImgPy
import cv2
import allotSkinTone
import urllib.request
import os



app = Flask(__name__)

def read_image(img_link):
    if img_link.startswith('http://') or img_link.startswith('https://'):
        # If the URL starts with http:// or https://, it's an internet URL
        try:
            # Download the image from the URL
            img_temp = '/tmp/temp_image.jpg'
            urllib.request.urlretrieve(img_link, img_temp)
            # Read the downloaded image
            image = cv2.imread(img_temp)
            # Cleanup: remove the temporary image file
            os.remove(img_temp)
            return image
        except Exception as e:
            print("Error downloading image from URL:", e)
            return None
    else:
        # Otherwise, treat it as a local file path
        return cv2.imread(img_link)


def get_skintone(img_link):

    # image = cv2.imread(img_link)

    image = read_image(img_link)
    if image is None:
        return {"error": "Failed to read image from URL or local file path"}

    # Detect face and extract
    face_extracted = face_detect.detect_face(image)
    # Pass extracted face to kMeans and get Max color list 
    colorsList = kMeansImgPy.kMeansImage(face_extracted)

    # print("Main File : ")
    # print("Red Component : "+str(colorsList[0]))
    # print("Green Component : "+str(colorsList[1]))
    # print("Blue Component : "+str(colorsList[2]))

    # Allot the actual skinTone to a certain shade
    allotedSkinToneVal = allotSkinTone.allotSkin(colorsList)
    print("input image: " + img_link)
    print("alloted skin tone : " + str(allotedSkinToneVal))
    # return str(allotedSkinToneVal)
    return {"image": img_link, "skin_tone": str(allotedSkinToneVal)}


@app.route('/') 
def hello_world(): 
    return 'Hello World!' 

@app.route('/getSkinTone', methods=['POST'])
def get_skintone_endpoint():
    data = request.json
    if 'image_url' in data:
        image_url = data['image_url']
        result = get_skintone(image_url)
        return jsonify(result)
    else:
        return jsonify({"error": "No image URL provided in the request body"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


