#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import requests
import time
import json
import numpy as np

class SmartGlasses:
    def __init__(self, config_file):
        """
        初始化智能眼镜对象，加载配置并初始化摄像头
        """
        self.config_file = config_file
        self.config = self.load_config(self.config_file)
        # 从配置文件中读取参数
        self.server_url = self.config.get("server_url", "http://localhost:8000/ollama")
        # 请求类型：可选 "image_request"（图片请求）或 "text_request"（文字请求）
        self.mode = self.config.get("mode", "image_request")
        # 请求时要求大模型解释的字数
        self.explanation_word_count = self.config.get("explanation_word_count", 100)
        # 摄像头采集分辨率：[宽, 高]
        self.capture_resolution = self.config.get("capture_resolution", [640, 480])
        # 显示模块的分辨率（模拟眼镜显示区域）
        self.display_resolution = self.config.get("display_resolution", [800, 600])
        # 是否启用手势识别模式
        self.gesture_mode = self.config.get("gesture_mode", False)
        # 定时请求的频率（单位：秒），在非手势识别模式下使用
        self.periodic_frequency = self.config.get("periodic_frequency", 5)
        
        # 初始化摄像头（默认使用0号摄像头）
        self.cap = cv2.VideoCapture(0)
        # 设置摄像头分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_resolution[1])
        
    def load_config(self, config_file):
        """
        从 JSON 文件中加载配置参数
        """
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config

    def update_config(self):
        """
        动态更新配置，运行过程中可以通过修改 JSON 文件调整参数
        """
        self.config = self.load_config(self.config_file)
        self.server_url = self.config.get("server_url", self.server_url)
        self.mode = self.config.get("mode", self.mode)
        self.explanation_word_count = self.config.get("explanation_word_count", self.explanation_word_count)
        self.capture_resolution = self.config.get("capture_resolution", self.capture_resolution)
        self.display_resolution = self.config.get("display_resolution", self.display_resolution)
        self.gesture_mode = self.config.get("gesture_mode", self.gesture_mode)
        self.periodic_frequency = self.config.get("periodic_frequency", self.periodic_frequency)
        # 更新摄像头分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_resolution[1])
        print("动态配置更新：", self.config)

    def adjust_resolution(self, image, resolution):
        """
        调整图像分辨率，参数resolution为[宽, 高]
        """
        return cv2.resize(image, (resolution[0], resolution[1]))

    def capture_image(self):
        """
        从摄像头采集图像，并调整至设定分辨率
        """
        ret, frame = self.cap.read()
        if not ret:
            print("无法从摄像头获取图像")
            return None
        # 调整图像分辨率
        frame = self.adjust_resolution(frame, self.capture_resolution)
        return frame

    def send_request_image(self, image):
        """
        将图像通过 HTTP POST 请求发送至核心网的 Ollama 服务器，
        并附带解释字数等参数，记录请求时延
        """
        # 对图像进行JPEG编码
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        ret, buffer = cv2.imencode('.jpg', image, encode_param)
        if not ret:
            print("图片编码失败")
            return None, None
        files = {'image': ('image.jpg', buffer.tobytes(), 'image/jpeg')}
        # 附带参数包括解释要求的字数和请求模式
        data = {'explanation_word_count': self.explanation_word_count, 'mode': self.mode}
        start_time = time.time()  # 记录发送请求时间
        try:
            response = requests.post(self.server_url, files=files, data=data)
        except Exception as e:
            print("请求发送失败:", e)
            return None, None
        end_time = time.time()  # 记录接收响应时间
        latency = end_time - start_time
        if response.status_code == 200:
            return response.text, latency
        else:
            print("服务器返回错误，状态码：", response.status_code)
            return None, latency

    def send_request_text(self, text):
        """
        将文本通过 HTTP POST 请求发送至核心网的 Ollama 服务器，
        并记录请求时延
        """
        data = {'text': text, 'mode': self.mode}
        start_time = time.time()
        try:
            response = requests.post(self.server_url, data=data)
        except Exception as e:
            print("请求发送失败:", e)
            return None, None
        end_time = time.time()
        latency = end_time - start_time
        if response.status_code == 200:
            return response.text, latency
        else:
            print("服务器返回错误，状态码：", response.status_code)
            return None, latency

    def display_result(self, result_text):
        """
        使用 OpenCV 显示解释结果，背景为纯黑色，文字为亮色
        """
        # 创建一个黑色背景图像（注意：真实智能眼镜可能采用透明背景，此处为模拟）
        background = np.zeros((self.display_resolution[1], self.display_resolution[0], 3), np.uint8)
        # 设置文字属性
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)  # 白色亮色文字
        thickness = 2
        # 将解释文本按行分割后显示，避免文字过长无法显示完整
        y0, dy = 50, 30
        for i, line in enumerate(result_text.split('\n')):
            y = y0 + i * dy
            cv2.putText(background, line, (50, y), font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.imshow("智能眼镜显示", background)
        # 显示一定时间后自动关闭窗口（例如3秒）
        cv2.waitKey(3000)
        cv2.destroyWindow("智能眼镜显示")

    def detect_gesture(self):
        """
        模拟手势检测模块：等待用户按下 'g' 键来模拟检测到五指手势
        实际应用中可接入深度学习模型进行实时手势识别
        """
        print("检测手势中：请比划五指手势，然后按 'g' 键模拟检测到手势。")
        key = cv2.waitKey(0) & 0xFF
        if key == ord('g'):
            return True
        else:
            return False

    def print_measurements(self, image, result_text, latency):
        """
        一次性打印测量结果：
        1. 发送图片分辨率
        2. 接收文字字节数
        3. 请求时延
        """
        # 获取图像的高和宽
        height, width = image.shape[:2]
        # 计算返回文字的字节数
        text_bytes = len(result_text.encode('utf-8'))
        print("====== 测量结果 ======")
        print("发送图片分辨率：{} x {}".format(width, height))
        print("接收文字字节数：", text_bytes)
        print("请求时延：{:.3f} 秒".format(latency))
        print("====================")

    def run(self):
        """
        主循环，根据配置决定使用手势识别模式或定时请求模式，
        同时支持图片请求和文字请求两种上行/下行模式
        """
        try:
            while True:
                # 动态加载并更新配置参数（运行过程中修改 config.json 可即时生效）
                self.update_config()
                if self.gesture_mode:
                    # 手势识别模式：不断检测是否有五指手势
                    print("当前为手势识别模式，等待检测五指手势...")
                    if self.detect_gesture():
                        print("检测到五指手势，开始采集图像并发送请求...")
                        image = self.capture_image()
                        if image is None:
                            continue
                        # 根据模式选择发送图片请求或文字请求
                        if self.mode == "image_request":
                            result, latency = self.send_request_image(image)
                        else:
                            # 这里简单模拟文字请求，实际可集成OCR或其它文本获取模块
                            result, latency = self.send_request_text("预设文字请求")
                        if result:
                            self.display_result(result)
                            self.print_measurements(image, result, latency)
                else:
                    # 定时请求模式：按照设定频率自动发送请求
                    print("当前为定时请求模式，每 {} 秒发送一次请求".format(self.periodic_frequency))
                    image = self.capture_image()
                    if image is None:
                        continue
                    if self.mode == "image_request":
                        result, latency = self.send_request_image(image)
                    else:
                        result, latency = self.send_request_text("预设文字请求")
                    if result:
                        self.display_result(result)
                        self.print_measurements(image, result, latency)
                    time.sleep(self.periodic_frequency)
        except KeyboardInterrupt:
            print("程序手动终止")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    # 运行程序时从config.json中读取配置参数
    sg = SmartGlasses("config.json")
    sg.run()
