

# 🌩️ Poridhi Cloud Python SDK

[![PyPI - Version](https://img.shields.io/pypi/v/poridhi-cloud?label=PyPI\&color=blue)](https://pypi.org/project/poridhi-cloud/)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)

> 🧠 **GPU-backed interactive environments (VSCode & Jupyter) with NVIDIA RTX 4500 — built for AI development and data science**

---

## 🧭 Overview

The **Poridhi Cloud Python SDK** enables:

* ⚙️ Creating & managing users
* 🧠 Allocating **GPU-powered containers** for interactive coding
* 🔍 Monitoring session status
* 🧮 Accessing high-performance **NVIDIA RTX 4500** for AI/ML tasks

> 🖥️ **Supported Services**: <img src="https://img.shields.io/badge/VSCode-007ACC?logo=visual-studio-code&logoColor=white" height="20"/> <img src="https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white" height="20"/> <img src="https://img.shields.io/badge/NVIDIA-76B900?logo=nvidia&logoColor=white" height="20"/>

---

## 📦 Installation

```bash
pip install poridhi-cloud
```

---

## 🚀 Quick Start

<details>
<summary><strong>🔐 Initialize the Client</strong></summary>

```python
from poridhi_cloud import PoridihCloud

# Option 1: Use environment variable
client = PoridihCloud()

# Option 2: Provide API key directly
client = PoridihCloud(api_key='your-api-key-here')
```

</details>

---

## 🔧 Features

### 🧑‍💻 Create a New User

```python
response = client.create_user()
print(response)
```

---

### 💻 Get Available Machines

```python
machines = client.get_machineId()
print(machines)
```

---

### 🧠 Allocate a GPU Worker

<details>
<summary><strong>🖥️ Start a VSCode or Jupyter Session</strong></summary>

`For VSCode port=8080`
`For Jupyter port = 8888`

```python
worker = client.codeserver(
    cpu=2,
    memory=4096,
    gpu='nvidia-rtx-4500',   # Optional (GPU model)
    port=8080,
    serviceType='vscode',    # or 'jupyter'
    duration=3600            # Optional: in seconds
)
print(worker)
```

> 💡 Both VSCode and Jupyter sessions run on **NVIDIA RTX 4500** <img src="https://img.shields.io/badge/VSCode-007ACC?logo=visual-studio-code&logoColor=white" height="20"/> <img src="https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white" height="20"/> <img src="https://img.shields.io/badge/NVIDIA-76B900?logo=nvidia&logoColor=white" height="20"/>

</details>

---

### 📶 Check Pod Status

```python
status = client.podStatus(deploymentname='vscode-session-abc123')
print(status)
```

> 🔍 Essential for `vscode`  sessions to verify if your pod is active and ready.

---

## 🔐 Authentication

You can provide your API key via:

### 1️⃣ Environment Variable

```bash
export PORIDHI_CLOUD_API_KEY='your-api-key-here'
```

### 2️⃣ Direct in Code

```python
client = PoridihCloud(api_key='your-api-key-here')
```

---

## ⚙️ Environment Configuration

| Variable Name           | Description                   |
| ----------------------- | ----------------------------- |
| `PORIDHI_CLOUD_API_KEY` | 🔐 API key for authentication |

---

## 🚨 Error Handling

```python
from poridhi_cloud import PoridihCloud, PoridihCloudError

try:
    result = client.get_machineId()
except PoridihCloudError as e:
    print(f"Error: {e}")
```

---

## 🧪 Full Example Workflow

<details>
<summary><strong>🎯 Run Complete Session</strong></summary>

```python
from poridhi_cloud import PoridihCloud

# Step 1: Initialize
client = PoridihCloud(api_key='your-api-key')

# Step 2: Create user
user = client.create_user()
print("User Created:", user)

# Step 3: List available machines
machines = client.get_machineId()
print("Machines:", machines)

# Step 4: Launch VSCode or Jupyter
worker = client.codeserver(
    cpu=2,
    memory=4096,
    gpu='nvidia-rtx-4500',
    port=8080,
    serviceType='vscode',
    duration=3600
)
print("Worker Allocated:", worker)

# Step 5: Check session status
status = client.podStatus(deploymentname=worker.get('deploymentName'))
print("Pod Status:", status)
```

</details>

---



