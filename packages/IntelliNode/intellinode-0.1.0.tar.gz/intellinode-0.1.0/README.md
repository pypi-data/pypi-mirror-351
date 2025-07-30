# 🧠 PerceptronLib: A Flexible Perceptron Model in Pure Python

**PerceptronLib** is a Python library that implements a fully functional perceptron from scratch — supporting **linear regression**, **binary classification**, and **multi-class classification** — all without relying on machine learning libraries like scikit-learn or PyTorch for the core logic.

---

## 🚀 Features

* ✅ Train a perceptron for **regression**, **binary**, or **multi-class classification**
* ✅ Implements **custom gradient descent** with proper loss functions:

  * MSE (Linear)
  * Binary Cross-Entropy (Binary)
  * Log Loss with Softmax (Multi-class)
* ✅ Includes **data scaling enforcement** (standard or min-max scaled)
* ✅ Automatically detects problem type from the dataset
* ✅ Custom `predict()` and internal `score()` method (optional)
* ⚠️ Includes warnings when using a single-layer perceptron on unsuitable tasks

---

## 📦 Installation

```bash
pip install IntelliNode
```

---

## 🥪 Quickstart

```python
from IntelliNode.PerceptronX import Perceptron
import pandas as pd

# Load or create your DataFrame (last column = target)
df = pd.read_csv("your_dataset.csv")

model = Perceptron()
model.fit(df)
predictions = model.predict(df.iloc[:, :-1])
```

---

## ⚠️ Scaling Required

All input features **must be either Standard Scaled or Min-Max Scaled**:

* Use `sklearn.preprocessing.StandardScaler` or
* Use the helper `s_scaler_fn()` or `m_scaler_fn()` defined in the code

---

## 📊 Supported Problems

| Type        | Detected Automatically | Activation | Loss                 |
| ----------- | ---------------------- | ---------- | -------------------- |
| Linear      | Regression target      | Linear     | MSE                  |
| Binary      | 2 classes              | Sigmoid    | Binary Cross-Entropy |
| Multi-Class | 3–19 classes           | Softmax    | Log Loss             |

---

## 🧠 Educational Value

This project is ideal for students, educators, or practitioners who want to:

* Understand perceptrons and gradient descent under the hood
* Learn about activation functions, loss functions, and convergence
* Customize and extend models beyond black-box libraries

---

## 📄 License

MIT License © 2025 Your Name

### Resume Entry

#### 🧠 Perceptron Model Library — Python (2025)

**Built a complete perceptron library from scratch** to handle regression, binary, and multi-class classification problems using custom gradient descent algorithms.

* Implemented MSE, Binary Cross-Entropy, and Softmax Log Loss from first principles.
* Added automatic detection of problem type, input validation, and warning systems for misuse.
* Enforced preprocessing standards (standard or min-max scaling) before training.
* Designed `fit()` and `predict()` APIs to mimic real-world ML libraries and structured code for reuse and publication.

### Portfolio Website Description

#### 🧠 PerceptronLib – Custom Machine Learning from Scratch

**A custom Python machine learning library implementing a perceptron model capable of linear regression, binary, and multi-class classification.**

* Uses custom-coded gradient descent and loss functions for different problem types.
* Automatically validates data and enforces feature scaling (standard or min-max).
* Predict function supports batch and row-wise inputs; softmax-based multiclass prediction included.
* Designed with educational clarity and reusability in mind. Fully prepared for packaging and public release.
* **Technologies:** Python, NumPy, Pandas, Scikit-learn (for scaling only)
