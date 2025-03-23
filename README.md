# WiLLM: An Open Wireless LLM Communication System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://github.com/willm/platform)
[![Dataset](https://img.shields.io/badge/dataset-available-orange.svg)](https://github.com/willm/platform)

## Overview
<div align="center">
  <img src="logo.png" alt="Overview" width="150">
</div>

**WiLLM** is the first open-source wireless communication system designed specifically for **Large Language Model (LLM) services**. As LLMs continue to evolve, supporting them in wireless networks presents challenges in **resource allocation, network slicing, and low-latency communication**. willm addresses these challenges by integrating **network slicing, GPU computing, and multi-layer scheduling** into wireless networks.

### 📌 Key Features

- **Novel Network Paradigm**: Deploys **GPU resources** in the core network for distributed LLM inference, optimizing latency and computation efficiency.
- **"Tree-Branch-Fruit" Slicing Architecture**: Introduces **Fruit Slices** dedicated to LLM services, enhancing dynamic resource allocation and multi-user scheduling.
- **Wireless Communication System for LLM Services**:
  - **Dynamic slice compatibility**
  - **Universal UE compatibility**
  - **Multi-UE-Multi-Slice scheduling**
  - **Dual-mode scheduling**
  - **Cross-layer APIs**
- **LLM Wireless Communication Dataset**: Provides **100,000 records** with synchronized **20-dimensional metrics** for performance analysis.
- **Smart Glasses Case Study**: Demonstrates WiLLM in resource-constrained scenarios.

## 📂 Repository Structure

```
📁 WiLLM
│── 📂 docs/             # Documentation and technical papers
│── 📂 datasets/         # LLM Wireless Communication Dataset
│── 📂 src/              # Core system implementation
│── 📂 scripts/          # Utility scripts for experiments
│── 📜 LICENSE           # Open-source license
│── 📜 README.md         # This file
```

## 🚀 Installation Guide

### Prerequisites

The prerequisites vary by component:

- **User Equipment (UE):**
  - Ubuntu 20.04 or later
  - Python 3.8+

- **gNB (Base Station):**
  - Ubuntu 18.04 or 20.04
  - Compatible CPU (e.g., Intel i7 or higher)
  - USRP hardware (e.g., B210)
  - **UHD libraries and drivers** (for USRP support)

- **Core Network (CN) with Edge Server:**
  - Ubuntu 20.04 or later
  - NVIDIA GPU (Recommended RTX 3090 or higher, used for LLM inference)
  - Python 3.8+

### Installation Steps

#### 1. User Equipment (UE)

WiLLM provides Python-based UE code. Install it as follows:

1. **Clone the repository**
   ```sh
   git clone https://github.com/willm.git
   cd platform/UE
   ```

2. **Set up a virtual environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the UE program**
   ```sh
   python ue_main.py
   ```

#### 2. gNB (Base Station)

The gNB installation is based on a modified version of OpenAirInterface (OAI) for WiLLM. For detailed guidance, refer to the [NR_SA_Tutorial_COTS_UE](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_COTS_UE.md) document. Key steps include:

1. **Install dependencies**
   ```sh
   sudo apt-get update
   sudo apt-get install -y git cmake build-essential libboost-all-dev
   ```

2. **Install UHD for USRP support**
   - Install UHD libraries and drivers. For example:
     ```sh
     sudo apt-get install -y libuhd-dev uhd-host
     ```
   - Verify the UHD installation:
     ```sh
     uhd_find_devices
     ```
   (For more details, please refer to the UHD section in the NR_SA_Tutorial_COTS_UE document.)

3. **Clone the WiLLM gNB repository**
   ```sh
   git clone https://github.com/willm/gNB.git
   cd gNB
   ```

4. **Set up the environment**
   ```sh
   source oaienv
   cd cmake_targets
   ```

5. **Compile gNB**
   ```sh
   ./build_oai -I
   ./build_oai --eNB --UE
   ```

6. **Configure gNB**
   - Edit the configuration file (e.g., `gnb.conf`) to set the correct frequency band, hardware parameters, and UHD options.

7. **Run gNB**
   ```sh
   sudo ./nr-softmodem -O gnb.conf
   ```

#### 3. Core Network (CN) with Edge Server

In WiLLM, the Core Network is implemented using Open5gs (which serves as the CN). The installation follows guidelines similar to those in the Zhihu article: [CN Installation Guide](https://zhuanlan.zhihu.com/p/471681564). A summary of the steps is as follows:

1. **Install prerequisites**
   ```sh
   sudo apt update
   sudo apt install -y software-properties-common
   sudo add-apt-repository ppa:open5gs/latest
   sudo apt update
   sudo apt install -y open5gs
   ```

2. **Configure the core network**
   - Edit the YAML configuration files in `/etc/open5gs/` to set the appropriate network parameters and database settings.

3. **Start the core network services**
   ```sh
   sudo systemctl start open5gs-mmed
   sudo systemctl start open5gs-sgwcd
   sudo systemctl start open5gs-smfd
   sudo systemctl start open5gs-amfd
   ```

4. **Set up the Edge Server for LLM inference**
   - Install NVIDIA drivers and the necessary deep learning frameworks (e.g., TensorFlow or PyTorch). Note that CUDA is not required.
   - **Install Ollama for LLM Inference:**
     1. **Clone the Ollama repository:**
        ```sh
        git clone https://github.com/ollama/ollama.git
        cd ollama
        ```
     2. **Build Ollama:**
        - Ensure you have Go installed (version 1.16 or higher recommended). Then run:
          ```sh
          go build -o ollama .
          ```
        - Alternatively, if a Makefile is provided, run:
          ```sh
          make
          ```
     3. **Configure and Run Ollama:**
        - Modify the sample configuration file (e.g., `config.yaml`) as needed for your hardware and model requirements.
        - Start the Ollama server:
          ```sh
          ./ollama --config config.yaml
          ```
     4. **Verify the Installation:**
        - Send a test inference request to ensure that Ollama is running correctly.
   
For detailed instructions, please refer to the [Ollama GitHub repository](https://github.com/ollama/ollama) and the [CN Installation Guide](https://zhuanlan.zhihu.com/p/471681564).

## 📊 Dataset

WiLLM provides the first dataset dedicated to LLM wireless communication, including **100,000 records** with multi-layer synchronized metrics:

- **UE Metrics**: Latency, interaction mode, request size, etc.
- **RAN Metrics**: Throughput, packet loss rate, signal quality, etc.
- **CN & Edge Server Metrics**: GPU utilization, inference time, resource scheduling, etc.

📥 **[Download Dataset](https://github.com/willm/platform/datasets/)**

## 🛠 API Usage

We are currently drafting documentation for APIs.


## 🏗 Contribution Guide

We welcome contributions from the research community! Follow these steps:

1. Fork this repository and create a new branch.
2. Implement your feature or bug fix.
3. Submit a pull request (PR) with a clear description.

📜 **Please read the [Contribution Guide](CONTRIBUTING.md) before submitting PRs.**

## 📄 License

This project is basd on OAI, licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🔗 References

- 📜 Research Paper: To be announced
- 📂 Dataset: [LLM Wireless Communication Dataset](https://mega.nz/folder/dN5QDLZZ#ck8V_Wugqgsd4BstTNXRYg)
- 🌐 gNB UHD & OAI Tutorial: [NR_SA_Tutorial_COTS_UE](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_COTS_UE.md)

💡 **WiLLM aims to accelerate innovation in LLM-powered wireless communication. Join us and contribute to the future of AI-driven networking!** 🚀
