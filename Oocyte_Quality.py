import os

# ✅ STEP 1: Install required packages
!pip install opencv-python kagglehub

# ✅ STEP 2: Import necessary libraries
import kagglehub
import cv2
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ✅ STEP 3: Download dataset from KaggleHub
path = kagglehub.dataset_download("nankairomiol/polarbody-yolo-segment")
print("✅ Dataset downloaded!")
print("📂 Path to dataset files:", path)

# ✅ STEP 4: Check the folder structure in the dataset
# List all files and directories in the downloaded dataset
print("📂 Checking dataset folder structure...")
for root, dirs, files in os.walk(path):
    print(f"Root: {root}")
    print(f"Dirs: {dirs}")
    print(f"Files: {files}")

# ✅ STEP 5: After inspecting the folder structure, update the image_folder path
# Example: If images are in a folder named 'image_data', update the path like this:
image_folder = "/kaggle/input/polarbody-yolo-segment/polar_body/image"
  # Correct path to the image folder

# ✅ STEP 6: Create a folder to save preprocessed images in a writable directory (outside /kaggle/input/)
output_folder = '/kaggle/working/preprocessed_images'  # Writable folder in Kaggle
os.makedirs(output_folder, exist_ok=True)

# ✅ STEP 7: Define valid image extensions
valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

# ✅ STEP 8: Process each image
image_count = 0
for filename in os.listdir(image_folder):
    if filename.lower().endswith(valid_extensions):
        file_path = os.path.join(image_folder, filename)
        img = cv2.imread(file_path)
        if img is None:
            print(f"⚠️ Skipping unreadable file: {file_path}")
            continue
        resized = cv2.resize(img, (224, 224))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        denoised = cv2.GaussianBlur(gray, (5, 5), 0)
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, denoised)
        image_count += 1
print(f"✅ Preprocessing complete! {image_count} images saved in:")
print("📂", output_folder)
import cv2
import numpy as np
import os
from skimage.feature import hog
from skimage import exposure
import matplotlib.pyplot as plt

# 1. Preprocess images (if this isn't already done in your code)
preprocessed_image_folder = '/kaggle/working/preprocessed_images'

# 2. Feature Extraction Functions

# Function to extract HOG features
def extract_hog_features(image):
    # Resize the image for consistency (if needed)
    resized_image = cv2.resize(image, (224, 224))
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    
    # Compute HOG features
    features, hog_image = hog(gray_image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True)

features_array = np.load('/kaggle/working/oocyte_features.npy')

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import silhouette_score

# 1. Clustering using KMeans with 2 clusters
# Assuming 'features_array' contains your extracted features

# Initialize the KMeans model with 2 clusters
kmeans = KMeans(n_clusters=2, n_init=10,random_state=42)

# Fit the model to the feature data
kmeans.fit(features_array)

# Get the cluster labels
cluster_labels = kmeans.labels_

print(f"Clustering complete. Cluster labels: {cluster_labels}")

# 2. Visualize the Clusters using PCA (Dimensionality Reduction)
pca = PCA(n_components=2)
reduced_features = pca.fit_transform(features_array)

# Plot the results
plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=cluster_labels, cmap='viridis')
plt.colorbar()
plt.title('Oocyte Assessment')
plt.xlabel('Matured Oocytes - Optimal for IVF')
plt.ylabel('Prematured Oocytes - Not Optimal for IVF')
plt.show()

# 3. Evaluate Clustering Performance (Optional)
# Compute the silhouette score to evaluate the clustering
silhouette_avg = silhouette_score(features_array, cluster_labels)
print(f"Silhouette Score: {silhouette_avg}")

# 4. Save the Cluster Labels (Optional)
# Assuming 'filenames' contains the names of the images
df = pd.DataFrame({'filename': filenames, 'cluster': cluster_labels})

# Save the DataFrame as a CSV file
df.to_csv('/kaggle/working/oocyte_clusters.csv', index=False)

print("Clustering results saved to 'oocyte_clusters.csv'")

features_array = np.load('/kaggle/working/oocyte_features.npy')
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

# Assuming 'features' contains the feature vectors from the images
pca = PCA(n_components=2)  # Reduce to 2 dimensions for visualization
reduced_features = pca.fit_transform(features_array)

# Plot the 2D projection
plt.figure(figsize=(8, 6))
plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=cluster_labels, cmap='viridis')
plt.colorbar()
plt.title('PCA of Oocyte Image Features')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.show()

import numpy as np
import cv2
import matplotlib.pyplot as plt
import joblib
import os

# Function to extract features from a single image (same as before)
def extract_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hog = cv2.HOGDescriptor()
    features = hog.compute(gray)
    return features.flatten()

# Load the pre-trained models
kmeans = joblib.load('kmeans_model.pkl')
pca = joblib.load('pca_model.pkl')

# Function to predict the cluster of a new image
def predict_cluster(image_path):
    # Load and process the image
    img = cv2.imread(image_path)
    features = extract_features(img)
    
    # Reduce dimensionality with the PCA model
    features_pca = pca.transform([features])  # Ensure it's a 2D array
    
    # Predict the cluster using the KMeans model
    cluster_label = kmeans.predict(features_pca)
    
    return cluster_label[0], img

# Function to display the image and its cluster label
def display_image_and_cluster(image_path):
    # Get the cluster label and image
    cluster_label, img = predict_cluster(image_path)
    
    # Convert BGR to RGB for proper visualization with matplotlib
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Display the image with its predicted cluster label
    plt.figure(figsize=(6, 6))
    plt.imshow(img_rgb)
    plt.title(f'Oocyte Image - Cluster: {cluster_label}')
    plt.axis('off')  # Hide axes
    plt.show()

# Path to an oocyte image from your dataset (replace with your actual image path)
image_path = 'path_to_uploaded_image.jpg'  # Example path
display_image_and_cluster(image_path)
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# Load the features (assumed to be extracted already)
features_array = np.load('/kaggle/working/oocyte_features.npy')
preprocessed_image_folder = '/kaggle/working/preprocessed_images'

# Initialize the KMeans model with 2 clusters (Good and Bad)
kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)
kmeans.fit(features_array)
cluster_labels = kmeans.labels_

# Visualize the Results as Images
def visualize_clusters_as_images():
    # Initialize a plot
    plt.figure(figsize=(12, 12))
    
    # Loop over each image and its corresponding cluster label
    for i, filename in enumerate(os.listdir(preprocessed_image_folder)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            image_path = os.path.join(preprocessed_image_folder, filename)
            image = cv2.imread(image_path)
            
            # Resize image to fit in the plot grid
            resized_image = cv2.resize(image, (64, 64))  # Adjust the size as needed
            plt.subplot(8, 8, i + 1)  # Create a subplot (you can adjust the grid size)

            # Set the title based on the cluster label
            title = "Quality Oocyte" if cluster_labels[i] == 0 else "Inferior Oocyte"
            plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
            plt.title(title, fontsize=10)
            plt.axis('off')
    
    # Show the plot with all the images
    plt.tight_layout()
    plt.show()

# Call the function to display the images
visualize_clusters_as_images()
