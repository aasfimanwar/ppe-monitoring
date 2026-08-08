from ultralytics import YOLO

model = YOLO("models/ppe_best.pt")
print("Model loaded successfully")
print("Classes:", model.names)