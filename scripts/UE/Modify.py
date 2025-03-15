#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PS: 
1：打印测量结果的函数中添加了一个数据存储功能，另外建议除了使用输入分辨率，输出字节数外，最好添加输入token，输出token，这和LLM的推理时延密切相关
使用token可以准确的衡量推理时延，但对于传输不太直观，分辨率和字节则有利于传输
2：三个界面：一个显示实时的视频，就是眼镜看到的，一个显示捕获的上传帧，一个显示文本结果
3：加上了流式推理
4：ollama本身支持4个批推理，配置一下参数即可
5：我是按照UE直接调用核心网上的ollama服务器改的，感觉是这种方式
要是只是单纯的上传请求到核心网，然后核心网进一步处理在调用LLM的方式的话，还需要修改
"""

import cv2
from pynput import keyboard
import numpy as np
import time
import json
import requests
import base64

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
        self.LLM_model = self.config.get("LLM_model", "llava")
        # 定时请求的频率（单位：秒），在非手势识别模式下使用
        self.periodic_frequency = self.config.get("periodic_frequency", 5)
        #配置流式响应
        self.is_stream = self.config.get("is_stream", False)
        self.start_time = time.time()
        
        # 初始化摄像头（默认使用0号摄像头）
        self.cap = cv2.VideoCapture(4)
        if not self.cap.isOpened():
            print("无法打开摄像头")
            exit()
        # 设置摄像头分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_resolution[1])

        # 捕获的当前帧（目前只是一张且是静态的，后续可扩展一个发送缓存，或者在服务器端开一个）
        self.capture_frame = None

        self.text_buffer = ""

        #开启键盘监听事件
        self.litener = keyboard.Listener(on_press=self.on_press)
        self.litener.start()

        #初始设置三个窗口，分别用来显示实时的视频流，捕获的当前帧和眼镜的模拟显示结果
        cv2.namedWindow("Camera Frame", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Captured Frame", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Glasses screen", cv2.WINDOW_NORMAL)

        cv2.resizeWindow("Camera Frame", 640, 480) 
        cv2.resizeWindow("Captured Frame", 640,480)
        # cv2.resizeWindow("Glasses screen", 640,480)
        cv2.resizeWindow("Glasses screen", 800, 600)

        cv2.moveWindow("Camera Frame", 100, 100)  # 将 "Camera Frame" 窗口移动到屏幕坐标 (100, 100) 位置可能还需要调整
        cv2.moveWindow("Captured Frame", 700, 100)  
        cv2.moveWindow("Glasses screen", 100,500)

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
        self.LLM_model = self.config.get("LLM_model", self.LLM_model)
        # 更新摄像头分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_resolution[1])

        #更新推理模式
        self.is_stream = self.config.get("is_stream", self.is_stream)
        print("动态配置更新：", self.config)

    def adjust_resolution(self, image, resolution):
        """
        调整图像分辨率，参数resolution为[宽, 高]
        """
        return cv2.resize(image, (resolution[0], resolution[1]))

    def capture_image(self):
        """
        从摄像头采集图像，并调整至设定分辨率，采集的是个静态的，g触发一次调用一次
        """
        ret, frame = self.cap.read()
        if not ret:
            print("无法从摄像头获取图像")
            return None
        # 调整图像分辨率
        self.capture_frame = self.adjust_resolution(frame, self.capture_resolution)

    def real_time_image(self):
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
        PS:这里是用户直接调用核心网的服务器，不需要核心网的进一步处理
        并附带解释字数等参数，记录请求时延
        file data的形式好像ollama不接受这种形式的请求，或许是我ollama版本变了
        之前的方案是可以将图片和text直接到服务器的，然后服务器还需要一个程序来调用ollama
        我不太清楚是不是这个意思，我先改成直接UE调用了
        然后这里只是整体返回的，流式输出后边在加
        """
        #将图片编码为JPEG
        _, img_encoded = cv2.imencode(".jpg", image)
        #Base64编码 这是为了适配json序列化 但这样会放大输入的token数量
        image_base64 = base64.b64encode(img_encoded).decode("utf-8")

        #更合适的做法是在data中控制max token参数，但是token和字数不是一一对应的，可能不够直观
        prompt = "描述这张图片，不超过" + str(self.explanation_word_count) + "个字"

        #这里使用max_token参数可能比输出最大字符限制要好一些，LLM推理是按照max_token来做的，但不利于衡量无线部分
        data = {
            "model": self.LLM_model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": self.is_stream
        }

        self.text_buffer = ""

        self.start_time = time.time()
        #流式推理
        if self.is_stream is True:
            print("当前为流式推理")
            try:
                with requests.post(self.server_url, json=data, stream=True) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            new_text = chunk.get("response","")
                            if new_text:
                                self.text_buffer += new_text
                                self.display_result(self.text_buffer)

            except requests.exceptions.RequestException as e:
                print(f"请求发送失败: {e}")

        else:
            try:
                response = requests.post(self.server_url, json=data)
                response.raise_for_status()
                result = response.json()
                self.text_buffer = result.get("response", "No response generated.")
                self.display_result(self.text_buffer)

            except requests.exceptions.RequestException as e:
                print(f"请求发送失败: {e}")
        
        latency = time.time() - self.start_time
        return latency

    def send_request_text(self, text):
        """
        文本 暂未测试
        """
        data = {
            "model": "llava",
            "prompt": text,
            "stream": self.is_stream
        }

        self.text_buffer = ""

        self.start_time = time.time()
        #流式推理
        if self.is_stream is True:
            print("当前为流式推理")
            try:
                with requests.post(self.server_url, json=data, stream=True) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            new_text = chunk.get("response","")
                            if new_text:
                                self.text_buffer += new_text
                                self.display_result(self.text_buffer)

            except requests.exceptions.RequestException as e:
                print(f"请求发送失败: {e}")

        else:
            try:
                response = requests.post(self.server_url, json=data)
                response.raise_for_status()
                result = response.json()
                self.text_buffer = result.get("response", "No response generated.")
                self.display_result(self.text_buffer)

            except requests.exceptions.RequestException as e:
                print(f"请求发送失败: {e}")
        
        latency = time.time() - self.start_time
        return latency

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
        max_width = self.display_resolution[0] - 50

        lines = []
        words = result_text.split(' ')
        current_line = ''

        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            (w,h), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
            if w < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            y = y0 + i * dy
            if y > self.display_resolution[1] - dy:
                break
            cv2.putText(background, line, (50, y), font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.imshow('Glasses screen', background)

        cv2.waitKey(1)
        # 显示一定时间后自动关闭窗口（例如3秒）先注释掉
        # cv2.waitKey(3000)
        # cv2.destroyWindow("Glass screen")

    def print_measurements(self, image, result_text, latency, start_time, filename="stored_data.json"):
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

        #将图片编码为JPEG
        #后边这些代码可以服用，当输入图片很大时，用一个全局变量会更快
        _, img_encoded = cv2.imencode(".jpg", image)
        #Base64编码 这是为了适配json序列化 但这样会放大输入的token数量
        image_base64 = base64.b64encode(img_encoded).decode("utf-8")

        #添加一个存储数据的功能
        data = {
            "timestamp": start_time,
            "image": image_base64,
            "latency": latency,
            "width": width,
            "height": height,
            "text_bytes": text_bytes
        }

        # 尝试打开文件，若文件不存在，则创建一个新的文件并写入表头
        try:
            with open(filename, 'r') as f:
                stored_data = json.load(f)
        except FileNotFoundError:
            stored_data = {"header": ["timestamp", "image", "latency", "width", "height", "text_bytes"], "data": []}
        
        # 将新的数据记录添加到 "data" 部分
        stored_data["data"].append(data)

        # 将数据存储到 JSON 文件中
        with open(filename, 'w') as f:
            json.dump(stored_data, f, indent=4)

        print(f"Data stored successfully at {time.time()}")

    def on_press(self, key):
        """
        模拟手势检测模块：等待用户按下 'g' 键来模拟检测到五指手势
        实际应用中可接入深度学习模型进行实时手势识别
        有问题 检测不到手势
        """
        try:
            if key.char == 'g':
                self.capture_image()

        except AttributeError:
            pass


    def run(self):
        """
        主循环，根据配置决定使用手势识别模式或定时请求模式，
        同时支持图片请求和文字请求两种上行/下行模式
        """
        last_capture_time = time.time()
        try:
            while True:
                self.update_config
                #显示当前帧
                current_frame = self.real_time_image()
                cv2.imshow('Camera Frame', current_frame)  #若是注释掉这句话则必须使用键盘监听，否则的话cv2.waitkey不生效

                #手势上传模式
                if self.gesture_mode:
                    print("当前为手势识别模式，等待检测五指手势...")
                    if self.capture_frame is not None:
                        print("检测到五指手势，开始采集图像并发送请求...")
                        cv2.imshow('Captured Frame', self.capture_frame)
                        if self.mode == "image_request":
                            latency = self.send_request_image(self.capture_frame)
                        else:
                            #这个文本暂时还未起作用
                            latency =self.send_request_text("预设文字请求")

                        if latency is not None:
                            # self.display_result(result)
                            self.print_measurements(self.capture_frame, self.text_buffer, latency, self.start_time)

                            self.capture_frame = None

                #周期上传模式
                else:
                    # 定时请求模式：按照设定频率自动发送请求
                    current_time= time.time()
                    if current_time - last_capture_time >= self.periodic_frequency:
                        print("当前为定时请求模式，每 {} 秒发送一次请求".format(self.periodic_frequency))
                        image = self.real_time_image()
                        cv2.imshow('Captured Frame', image)
                        if self.mode == "image_request":
                            latency = self.send_request_image(image)
                        else:
                            latency = self.send_request_text("预设文字请求")

                        if latency is not None:
                            # self.display_result(result)
                            self.print_measurements(image,self.text_buffer, latency, self.start_time)
                        last_capture_time = current_time
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("程序手动终止")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    # 运行程序时从config.json中读取配置参数
    sg = SmartGlasses("config.json")
    sg.run()
