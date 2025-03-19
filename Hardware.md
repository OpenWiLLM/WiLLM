# WiLLM's Hardware

WiLLM is an open-source wireless communication system designed specifically for deploying, optimizing, and validating large language model (LLM) services on mobile platforms. Its hardware architecture is meticulously crafted to support efficient LLM service deployment, optimization, and experimental validation. This report details all the critical hardware components used in the WiLLM system, including their models, specifications, functionalities, and roles in the system.

---

## Table of Contents
1. [WiLLM Testbed Hardware](#willm-testbed-hardware)
   - [gNB Host](#gnb-host)
   - [RF Front-End](#rf-front-end)
   - [Core Network Server](#core-network-server)
   - [Connection Components](#connection-components)
2. [Smart Glasses Case Study Hardware](#smart-glasses-case-study-hardware)
   - [Smart Glasses](#smart-glasses)
   - [MiniPC](#minipc)
   - [5G Module](#5g-module)
   - [Connection Cable](#connection-cable)
3. [Mapping Hardware to System Architecture](#mapping-hardware-to-system-architecture)
4. [Supplementary Notes](#supplementary-notes)

---

## WiLLM Testbed Hardware
The WiLLM testbed serves as the core infrastructure for system validation, supporting multi-user and multi-slice concurrent testing scenarios. Below are the specific hardware components used in the testbed:

### gNB Host
- **Model**: Intel Core i9-14900KF Processor
- **Specifications**:
  - Cores: 24 (8 Performance-cores + 16 Efficiency-cores)
  - Threads: 32
  - Max Turbo Frequency: 6.0 GHz
  - L3 Cache: 36MB
  - [Official Specifications](https://www.intel.com/content/www/us/en/products/sku/236773/intel-core-i9-processor-14900kf-36m-cache-up-to-6-00-ghz/specifications.html)
- **Functionality**:
  - Acts as the gNB (base station) host, managing and coordinating network operations.
  - Runs the gNB subsystem, including "Tree-Branch-Fruit" slice management and resource scheduling.
- **Role in the System**:
  - Handles radio access network (RAN) layer tasks, ensuring smooth communication between UE (User Equipment) and gNB.
  - Connects with the RF front-end (USRP B210) and core network server (NVIDIA RTX 4090) to form a complete signal chain.

### RF Front-End
- **Model**: USRP B210
- **Specifications**:
  - Frequency Range: 70 MHz to 6 GHz
  - MIMO: 2x2
  - Interface: USB 3.0
  - Bandwidth: Up to 56 MHz
  - [Official Product Page](https://www.ettus.com/all-products/ub210-kit/)
- **Functionality**:
  - Serves as a software-defined radio (SDR) for transmitting and receiving wireless signals.
  - Supports flexible wireless communication experiments, compatible with the OpenAirInterface framework.
- **Role in the System**:
  - Acts as the RF front-end for the gNB, enabling physical layer communication between UE and gNB.
  - Connects to the gNB host via a USB 3.0 interface.

### Core Network Server
- **Model**: NVIDIA RTX 4090
- **Specifications**:
  - VRAM: 24GB GDDR6X
  - CUDA Cores: 9728
  - Base Clock: 1.7 GHz
  - Boost Clock: 2.52 GHz
  - [Official Product Page](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/)
- **Functionality**:
  - Runs the core network (CN) subsystem, including Open5GS functionalities such as AMF, SMF, and UPF.
  - Executes distributed LLM inference, handling high computational workloads.
- **Role in the System**:
  - Serves as the computational platform for the core network and edge computing, supporting LLM service deployment and optimization.
  - Connects to the gNB host via Ethernet to establish the complete UE-gNB-CN communication chain.
- **Note**:
  - The RTX 4090 is a GPU and needs to be paired with a motherboard, CPU, and storage devices to form a complete server. See [Supplementary Notes](#supplementary-notes) for details.

### Connection Components
- **Description**: Cables for connecting the gNB host, USRP B210, and core network server.
- **Specifications**:
  - **USB 3.0 Cable**: Connects the USRP B210 to the gNB host, with a transfer rate of 5 Gbps.
  - **Cat6 Ethernet Cable**: Connects the gNB host to the core network server, with a transfer rate of 1 Gbps.
- **Functionality**:
  - Ensures high-speed data transfer and power delivery between testbed components.
- **Role in the System**:
  - Establishes the physical connections between hardware components, enabling system-wide collaboration.

---

## Smart Glasses Case Study Hardware
The smart glasses case study demonstrates the practical application of WiLLM, showcasing its feasibility on resource-constrained devices. Below are the specific hardware components used in the case study:

### Smart Glasses
- **Model**: Rokid Max Pro (Computing Module Removed)
- **Specifications**:
  - Field of View (FOV): 50°
  - Display: 1920x1080 OLED
  - Sensors: 9-axis IMU
  - Camera: Front-facing camera (exact resolution not disclosed, assumed to be 8MP or higher)
  - Weight: ~75g
  - [Official Product Page](https://global.rokid.com/products/rokid-max)
- **Functionality**:
  - Captures images from the user's perspective for LLM interpretation.
  - Displays LLM-generated responses, providing an augmented reality experience.
- **Role in the System**:
  - Serves as the visual input/output interface for the UE, relying on the MiniPC (NanoPC T6) for computational support.
- **User Specification**:
  - The computing module is removed, and computational tasks are outsourced to the NanoPC T6.

### MiniPC
- **Model**: NanoPC T6
- **Specifications**:
  - SoC: Rockchip RK3588 (4x Cortex-A76 @ 2.4 GHz + 4x Cortex-A55 @ 1.8 GHz)
  - GPU: Mali-G610 MP4
  - RAM: 16GB LPDDR4x
  - Storage: 256GB eMMC, supports M.2 NVMe SSD expansion
  - Interfaces: 1x USB-C (DP Output), 2x USB 3.0, 1x HDMI 2.1, 1x 2.5Gbps Ethernet
  - [Official Product Page](https://www.friendlyelec.com/index.php?route=product/product&product_id=289)
- **Functionality**:
  - Runs UE subsystem modules for configuration management, slice control, and performance measurement.
  - Houses the RM520N-GL 5G module, providing computational support.
- **Role in the System**:
  - Acts as the computational unit for the smart glasses, processing data and communicating with the gNB.
  - Hosts the 5G module via the M.2 interface and connects to the smart glasses via a USB-C interface.

### 5G Module
- **Model**: RM520N-GL
- **Specifications**:
  - Network Modes: 5G NSA/SA
  - Downlink Speed: Up to 4.67 Gbps
  - Uplink Speed: Up to 1.25 Gbps
  - Interface: M.2
  - Frequency Bands: Global bands supported
  - [Official Product Page](https://www.quectel.com/product/5g-rm520n-gl)
- **Functionality**:
  - Provides high-speed wireless connectivity, enabling communication between the smart glasses, gNB, and core network.
- **Role in the System**:
  - Installed in the NanoPC T6's M.2 slot as the wireless communication module for the UE.

### Connection Cable
- **Description**: Full-featured Type-C Cable
- **Specifications**:
  - Standard: USB 3.2 Gen 2
  - Data Transfer Rate: 10 Gbps
  - Power Delivery: Supports PD protocol, up to 100W
  - Length: Recommended 0.5-1 meter
  - Suggested Brands: Anker, Belkin, etc.
- **Functionality**:
  - Connects the Rokid Max Pro and NanoPC T6, transmitting image data, LLM responses, and power.
- **Role in the System**:
  - Ensures seamless integration and stable communication between the smart glasses and MiniPC.

---

## Mapping Hardware to System Architecture
The WiLLM system architecture includes the UE (User Equipment), gNB (Base Station), CN (Core Network), and Edge Server. Below is the mapping of hardware components to the system architecture:

| **System Component** | **Corresponding Hardware**                                  |
|-----------------------|------------------------------------------------------------|
| **UE**               | Smart Glasses (Rokid Max Pro), MiniPC (NanoPC T6), 5G Module (RM520N-GL), Connection Cable (Full-featured Type-C Cable) |
| **gNB**              | gNB Host (Intel Core i9-14900KF), RF Front-End (USRP B210)  |
| **CN & Edge Server** | Core Network Server (NVIDIA RTX 4090)                       |

These hardware components are interconnected via connection components (e.g., USB cables and Ethernet cables) to form a complete wireless communication chain that supports end-to-end LLM service delivery.

---

## Supplementary Notes
- **Additional Components for Core Network Server**:
  - The NVIDIA RTX 4090 is a GPU and requires additional components to form a complete server system, such as:
    - Motherboard: PCIe 4.0 compatible (e.g., ASUS ROG Strix Z790)
    - CPU: High-performance models (e.g., Intel i7/i9)
    - RAM: High-capacity DDR5 (e.g., 64GB)
    - Storage: NVMe SSD (e.g., 1TB Samsung 990 Pro)
  - Specific configurations may vary based on computational requirements.
- **NanoPC T6 Configuration**:
  - The NanoPC T6 is a high-performance single-board computer. Its M.2 interface supports the RM520N-GL 5G module, and its USB-C interface supports DP output, compatible with the Rokid Max Pro's display requirements. The 16GB RAM and RK3588 SoC are sufficient for UE computational tasks.
- **Smart Glasses Camera**:
  - The Rokid Max Pro's official page does not specify the camera resolution, but AR glasses typically feature 8MP or 13MP cameras, which are sufficient for scene interpretation tasks.

This report provides a comprehensive description of the WiLLM system hardware, including models, specifications, functionalities, and roles, with official links for reference. For further information, please refer to the relevant papers or hardware documentation. We hope this report serves as a strong foundation for replicating and extending the WiLLM system!
