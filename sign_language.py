import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import kagglehub
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from torch.utils.data import DataLoader, TensorDataset
import torch.optim as optim

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device: {device}")

import kagglehub

# Download latest version
path = kagglehub.dataset_download("prathumarikeri/indian-sign-language-isl")

print("Path to dataset files:", path)

# Cell 3: Dataset Structure and Sample Images
dataset_path = os.path.join(path, "Indian")
class_names = sorted(os.listdir(dataset_path))

print(f"📁 Dataset path: {dataset_path}")
print(f"🏷️ Total classes: {len(class_names)}")
print(f"📝 Classes: {class_names}")

# Sample images visualization
fig, axes = plt.subplots(1, 5, figsize=(15, 3))
for i, cls in enumerate(class_names[:5]):
  folder = os.path.join(dataset_path, cls)
  files = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]
  count = len(files)
  print(f"   {cls}: {count} images")

  if files:
    img_path = os.path.join(folder, files[0])
    img = Image.open(img_path).convert('L')
    axes[i].imshow(img, cmap='gray')
    axes[i].set_title(f'{cls}\n({count} images)', fontweight='bold')
    axes[i].axis('off')

plt.suptitle('Sample ISL Gestures', fontweight='bold')
plt.tight_layout()
plt.show()

# Cell 4: Image Preprocessing
X, y = [], []
for i, cls in enumerate(class_names):
  folder = os.path.join(dataset_path, cls)
  for file in os.listdir(folder)[:50]: # 50 images per class
    if file.endswith('.jpg'):
      img = Image.open(os.path.join(folder, file))
      img = img.convert('L').resize((64, 64)) # Grayscale + Resize
      img = np.array(img) / 255.0 # Normalize to 0-1
      img = (img - img.mean()) / (img.std() + 1e-5) # Standardize
      X.append(img)
      y.append(i)

X = np.array(X)[:, None] # Add channel: (N, 1, 64, 64)
y = np.array(y)

print(f"Data: X={X.shape}, y={y.shape}")
print(f"Range: [{X.min():.2f}, {X.max():.2f}]")

# Cell 5: Train-Test Split
x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Convert to PyTorch tensors
x_train = torch.tensor(x_train, dtype=torch.float32)
x_test = torch.tensor(x_test, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

# Create data loaders
train_dataset = TensorDataset(x_train, y_train)
test_dataset = TensorDataset(x_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

print(f"✅ Train: {x_train.shape[0]} images")
print(f"🧪 Test: {x_test.shape[0]} images")
print(f"📦 Batch size: 64")
print(f"🔄 Train batches: {len(train_loader)})")

# Cell 6: CNN Model Definition (FIXED)
class ISL_CNN(nn.Module):
    def __init__(self, num_classes):
        super(ISL_CNN, self).__init__()

        self.features = nn.Sequential(
            # Block 1: 1→32 channels, 64×64→32×32
            nn.Conv2d(1, 32, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2),
            # Block 2: 32→64 channels, 32×32→16×16
            nn.Conv2d(32, 64, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2),
            # Block 3: 64→128 channels, 16×16→8×8
            nn.Conv2d(64, 128, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2),
            # Block 4: 128→256 channels, 8×8→4×4
            nn.Conv2d(128, 256, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2)
        )

        self.classifier = nn.Sequential(
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.reshape(x.size(0), -1)  # FIXED: Use reshape instead of view
        x = self.classifier(x)
        return x

model = ISL_CNN(num_classes=len(class_names)).to(device)
total_params = sum(p.numel() for p in model.parameters())

print(f"🧠 CNN Model created!")
print(f"📊 Parameters: {total_params:,}")
print(f"💻 Device: {device}")
print(f"🎯 Classes: {len(class_names)}")

# Cell 7: Train Model with visualization
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), 0.001)

print("🚀 Starting training...")

losses, accuracies = [], []

for epoch in range(3):
  model.train()
  running_loss = 0.0
  correct = 0
  total = 0

  for data, target in train_loader:
    data, target = data.to(device), target.to(device)

    optimizer.zero_grad()
    output = model(data)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()
    running_loss += loss.item()
    _, predicted = torch.max(output, 1)
    total += target.size(0)
    correct += (predicted == target).sum().item()

  epoch_loss = running_loss / len(train_loader)
  epoch_acc = 100. * correct / total

  losses.append(epoch_loss)
  accuracies.append(epoch_acc)

  print(f"✅ Epoch {epoch + 1}/3: Loss = {epoch_loss:.4f}, Acc = {epoch_acc:.1f}%")

print("🎉 Training completed")

# Cell 8: Plot Training Progress
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Loss plot
ax1.plot(range(1, len(losses) + 1), losses, 'r-o', linewidth=2, markersize=8)
ax1.set_title('📉 Training Loss', fontweight='bold')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.grid(True, alpha=0.3)

# Accuracy plot
ax2.plot(range(1, len(accuracies) + 1), accuracies, 'g-s', linewidth=2, markersize=8)
ax2.set_title('🎯 Training Accuracy', fontweight='bold')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy (%)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Cell 9: Test Model Performance
print("🔍 Testing model on unseen data...")

model.eval()
test_loss = 0
correct = 0
total = 0
all_predictions = []
all_targets = []

with torch.no_grad():
    for data, target in test_loader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        test_loss += criterion(output, target).item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)

        all_predictions.extend(pred.cpu().numpy())
        all_targets.extend(target.cpu().numpy())

test_accuracy = 100. * correct / total
avg_test_loss = test_loss / len(test_loader)

print(f"📊 Test Results:")
print(f"   🎯 Test Accuracy: {test_accuracy:.1f}%")
print(f"   📉 Test Loss: {avg_test_loss:.4f}")
print(f"   ✅ Correct: {correct}/{total}")

# Cell 11: Test Model with Visual Predictions
import random
import matplotlib.pyplot as plt

print("🔍 Testing model with random sample images...")

# Get random test samples
num_samples = 12
random_indices = random.sample(range(len(x_test)), num_samples)

# Make predictions
model.eval()
sample_images = []
true_labels = []
predictions = []
confidences = []

with torch.no_grad():
    for idx in random_indices:
        # Get image and true label
        img_tensor = x_test[idx:idx+1].to(device)  # Single image
        true_label = y_test[idx].item()

        # Make prediction
        output = model(img_tensor)
        prob = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(prob, 1)

        sample_images.append(x_test[idx].squeeze())  # Remove channel dim for display
        true_labels.append(true_label)
        predictions.append(predicted.item())
        confidences.append(confidence.item())

# Display results in 3x4 grid
fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle('🎯 ISL Model Predictions on Test Images', fontsize=16, fontweight='bold')

for i in range(num_samples):
    row = i // 4
    col = i % 4

    # Display image
    axes[row, col].imshow(sample_images[i], cmap='gray')

    # Create title with prediction info
    true_class = class_names[true_labels[i]]
    pred_class = class_names[predictions[i]]
    confidence = confidences[i]

    # Color based on correctness
    if true_labels[i] == predictions[i]:
        color = 'green'
        status = '✅ CORRECT'
    else:
        color = 'red'
        status = '❌ WRONG'

    title = f'{status}\nTrue: {true_class} | Pred: {pred_class}\nConfidence: {confidence:.1%}'
    axes[row, col].set_title(title, fontsize=10, color=color, fontweight='bold')
    axes[row, col].axis('off')

plt.tight_layout()
plt.show()

# Print detailed results
print(f"\n📊 Detailed Prediction Results:")
print("=" * 70)
correct_count = 0
for i in range(num_samples):
    true_class = class_names[true_labels[i]]
    pred_class = class_names[predictions[i]]
    confidence = confidences[i]
    is_correct = true_labels[i] == predictions[i]

    if is_correct:
        correct_count += 1
        status = "✅ CORRECT"
    else:
        status = "❌ WRONG"

    print(f"Sample {i+1:2d}: {status}")
    print(f"   True Label: {true_class}")
    print(f"   Predicted:  {pred_class}")
    print(f"   Confidence: {confidence:.1%}")
    print("-" * 40)

# Calculate accuracy on these samples
sample_accuracy = 100 * correct_count / num_samples
print(f"\n🎯 Sample Test Results:")
print(f"   Correct Predictions: {correct_count}/{num_samples}")
print(f"   Sample Accuracy: {sample_accuracy:.1f}%")
print(f"   Overall Test Accuracy: {test_accuracy:.1f}%")