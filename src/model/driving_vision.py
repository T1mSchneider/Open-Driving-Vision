# -*- coding: utf-8 -*-
"""Driving-Vision

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LJ8CJWWVYewpQ8X5Psj6SsqlYzdX1T64
"""

import os
import shutil
import cv2
import numpy as np
from tensorflow_examples.models.pix2pix import pix2pix
import tensorflow as tf
import matplotlib.pyplot as plt
from IPython.display import clear_output

from .dataset.CreateDataset import CreateTensorflowDataset
from .UnetModel import Unet
from .Config import Config
from ..const.constants import (IMG_OUTPUT_PATH, MASKS_OUTPUT_PATH)

dataset = CreateTensorflowDataset().get_dataset(test=Config.TEST_MODE)

def display(display_list):
  plt.figure(figsize=(15, 15))

  title = ['Input Image', 'True Mask', 'Predicted Mask']

  for i in range(len(display_list)):
    plt.subplot(1, len(display_list), i+1)
    plt.title(title[i])
    plt.imshow(tf.keras.utils.array_to_img(display_list[i]))
    plt.axis('off')
  plt.show()

for images, masks in dataset.take(2):
  sample_image, sample_mask = images[0], masks[0]
  display([sample_image, sample_mask])


model = Unet(output_channels=Config.OUTPUT_CLASSES).generate_model()

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

def create_mask(pred_mask):
  pred_mask = tf.math.argmax(pred_mask, axis=-1)
  pred_mask = pred_mask[..., tf.newaxis]
  return pred_mask[0]

def show_predictions(dataset=None, num=1):
  if dataset:
    for image, mask in dataset.take(num):
      pred_mask = model.predict(image)
      display([image[0], mask[0], create_mask(pred_mask)])
  else:
    display([sample_image, sample_mask,
             create_mask(model.predict(sample_image[tf.newaxis, ...]))])

class DisplayCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs=None):
    clear_output(wait=True)
    show_predictions()
    print ('\nSample Prediction after epoch {}\n'.format(epoch+1))

# Load the most recently trained model
model.load_weights(Config.WEIGHTS)

if not Config.TEST_MODE:
  model_history = model.fit(dataset, epochs=Config.EPOCHS,
                            steps_per_epoch=Config.STEPS_PER_EPOCH,
                            callbacks=[DisplayCallback()])
  # Save weights
  model.save_weights("/src/model/weights/modelv2_run_5_weights.weights.h5")  # HDF5
  print("Weights saved!")

  show_predictions(dataset, 3)

if Config.TEST_MODE:
  preds = []
  for batch in dataset:
    images, masks = batch
    preds.append(model.predict(images))

# Define the scaling factor
scale_factor = 15  # Example: 2x upscale

def resize_mask(mask):
  # Resize the segmentation mask
  mask = cv2.resize(mask, None, fx=1216/128, fy=800/128, interpolation=cv2.INTER_NEAREST)
  return image, mask

def segment_image(image, mask, i):
  # Get number of classes from last dimension
  num_classes = mask.shape[2]

  # Assign random colors for each class
  np.random.seed(42)
  colors = {i: np.random.randint(0, 255, (3,)).tolist() for i in range(1, num_classes)}

  # Process each class separately
  for class_label in range(1, num_classes):  # Skip background class (0)
      # Extract single-class mask
      binary_mask = (mask[:, :, class_label] > 0).astype(np.uint8) * 255  # Ensure single-channel (CV_8UC1)
      # Find contours for the current class
      contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      # Draw bounding boxes for each detected object
      for contour in contours:
          x, y, w, h = cv2.boundingRect(contour)
          if w * h > 500:
            cv2.rectangle(image, (x, y), (x + w, y + h), colors[class_label], 2)
            cv2.putText(image, f'Class {Config.label_to_name[class_label]}', (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[class_label], 2)
  img_filename = f"output_{str(i).zfill(3)}.png"
  cv2.imwrite(f"segmented_images/{img_filename}", image)

#@TODO Fix paths to images in this file
if Config.TEST_MODE:
  output = 0
  for i, batch in enumerate(dataset):
    batch_images, batch_masks = batch
    batch_preds = preds[i]
    for j in range(len(batch_images)):
      image, mask = resize_mask(batch_preds[j])
      img_filename = f"output_{str(output).zfill(3)}.png"
      image = cv2.imread(f"dataset/images_and_masks/images/{img_filename}")
      segment_image(image, mask, output)
      output += 1


if Config.TEST_MODE:
  # Define folder path and output zip file
  folder_path = "/content/segmented_images"
  zip_file_path = "/content/segmented_images.zip"

  # Zip the folder
  shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', folder_path)

  print(f"Folder zipped successfully: {zip_file_path}")