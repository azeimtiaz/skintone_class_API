from flask import Flask,request, jsonify
import face_detect
import kMeansImgPy
import cv2
import allotSkinTone
import urllib.request
import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import io
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup
import json
 
 
app = Flask(__name__)
 
# Load pre-trained ResNet model
resnet = models.resnet50(pretrained=True)
# Remove the last fully connected layer
resnet = nn.Sequential(*list(resnet.children())[:-2])
# Set the model to evaluation mode
resnet.eval()
 
# Define image transformation
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
 
 
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
 
 
def compute_similarity(feature1, feature2):
    feature1_flat = feature1.flatten().reshape(1, -1)
    feature2_flat = feature2.flatten().reshape(1, -1)
 
    # Compute cosine similarity
    similarity = cosine_similarity(feature1_flat, feature2_flat)
    return similarity[0][0]
 
 
def extract_features(image_url):
    try:
        # Download the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for non-successful HTTP responses
 
        # Open the downloaded image using PIL
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        # Transform and process the image as needed
        image = transform(image).unsqueeze(0)
        with torch.no_grad():
            features = resnet(image)
        return features.squeeze().numpy()
 
    except Exception as e:
        print(f"Error processing image from URL: {e}")
        return None
 
def extract_data(html):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
 
    # Find all script tags
    script_elements = soup.find_all('script')
 
    raw_data = ""
    offset = 2
 
    for element in script_elements:
        # The data is placed in the script tag content that contains "AF_initDataCallback"
        if "AF_initDataCallback" in element.text:
            if offset == 0:
                raw_data = element.text
                break
            else:
                offset -= 1
 
    start = raw_data.find("data:") + 5
    end = raw_data.find("sideChannel") - 2
    json_data = json.loads(raw_data[start:end])
 
    jason = []
 
    # This is used because sometimes the information is in json_data[1][0] and other times in json_data[1][1]
    try:
        jason = json_data[1][1][1][8][8][0][12] if len(json_data[1]) == 2 else json_data[1][0][1][8][8][0][12]
    except Exception as e:
        print("The data is not in the expected format:", e)
 
    filtered_items = []
 
    for item in jason:
        if isinstance(item, list) and len(item) >= 14:
            url_found = False
            first_line = None
            product_page_url = None
            for sub_item in item:
                if isinstance(sub_item, list):
                    for sub_sub_item in sub_item:
                        if isinstance(sub_sub_item, str):
                            if 'amazon.com' in sub_sub_item or 'ebay.com' in sub_sub_item:
                                url_found = True
                                product_page_url = sub_sub_item
                            elif first_line is None:
                                first_line = sub_sub_item
                elif isinstance(sub_item, str):
                    if 'amazon.com' in sub_item or 'ebay.com' in sub_item:
                        url_found = True
                        product_page_url = sub_item
                    elif first_line is None:
                        first_line = sub_item
            if url_found and first_line and product_page_url:
                filtered_items.append({'image': first_line, 'product_page_url': product_page_url})
 
    # print(json.dumps(filtered_items, indent=2))
    return filtered_items
 
 
def search_products_by_image(image_path):
    google_lens_url = f"https://lens.google.com/uploadbyurl?url={image_path}"
    print(google_lens_url)
 
    # Set headers for the request
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        "Accept": "application/json"
    }
 
    response = requests.get(google_lens_url, headers=headers)
    if response.status_code == 200:
        print("Success")
        return extract_data(response.text)
 
    else:
        print(f"Error: Failed to fetch data. Status code: {response.status_code}")
        return None
 
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
 
 
 
class ImageUrls(BaseModel):
    search_image_url: str
    wardrobe_images: List[str]
 
@app.route('/similar', methods=['POST'])
def get_similar_images():
# def get_similar_images(image_urls: ImageUrls, threshold: float = 0.4):
    # search_image_url = image_urls.search_image_url
    # similar_images_urls = image_urls.wardrobe_images
    data = request.json
    search_image_url = data['search_image_url']
    wardrobe_images = data['wardrobe_images']
    threshold = data['threshold']
 
    if not search_image_url or not wardrobe_images:
        return {"error": "Please provide both search_image_url and similar_images_urls in the JSON request."}
 
    feature_vector_search = extract_features(search_image_url)
    similar_images = []
 
    for similar_image_url in wardrobe_images:
        feature_vector_similar = extract_features(similar_image_url)
        similarity_score = compute_similarity(feature_vector_search, feature_vector_similar)
 
        if similarity_score > threshold:
            similar_images.append({"image_url": similar_image_url, "similarity_score": similarity_score.tolist()})
 
    return {"similar_images": similar_images}
 
@app.route('/web-search', methods=['POST'])
def search_web(search_image_url:str):
# def search_web(search_image_url:str):
    data = request.json
    search_image_url = data['search_image_url']
    # image_path_to_search = "https://img.freepik.com/free-photo/fashion-woman-with-clothes_1203-8302.jpg"
    product_list = search_products_by_image(search_image_url)
 
    return {"product_list": product_list}
 
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
 