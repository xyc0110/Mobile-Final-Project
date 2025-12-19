import os
import cv2
import pathlib
import requests
from datetime import datetime

class SitupDetection:
    """
    仰卧起坐检测计数与上传
    """
    HOST = 'http://127.0.0.1:8000'  # Django 服务地址

    def __init__(self, up_threshold=400, down_threshold=280, username='xiayucheng', password='xiayucheng1', video_id=None):
        """
        up_threshold: 仰卧起坐坐起时的高度阈值
        down_threshold: 仰卧起坐躺下时的高度阈值
        username, password: Django 用户认证
        video_id: 可选，视频ID或标识，用于上传
        """
        self.prev_state = "DOWN"
        self.count = 0
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.username = username
        self.password = password
        self.token = None
        self.last_image = None
        self.video_id = video_id

        # 获取 Django Token
        try:
            res = requests.post(
                f'{self.HOST}/api-token-auth/',
                data={'username': self.username, 'password': self.password},
                timeout=5
            )
            res.raise_for_status()
            self.token = res.json().get('token', None)
            if self.token:
                print("[SitupDetection] Token 获取成功")
            else:
                print("[SitupDetection] Token 未返回")
        except Exception as e:
            print("[SitupDetection] Token 获取失败:", e)

    def update(self, bbox, image):
        """
        更新仰卧起坐状态并计数
        """
        if bbox is None:
            return

        x1, y1, x2, y2 = bbox
        height = y2 - y1

        if height < self.down_threshold:
            current_state = "DOWN"
        elif height > self.up_threshold:
            current_state = "UP"
        else:
            current_state = self.prev_state

        print(f"height: {height}, state: {current_state}")

        # 完整动作 DOWN -> UP -> DOWN 后计数
        if self.prev_state == "UP" and current_state == "DOWN":
            self.count += 1
            print(f"[SitupDetection] COUNT +1 = {self.count}")
            self.last_image = image.copy()

        self.prev_state = current_state

    def send_last(self):
        """
        上传最后一次动作的图片到 Django（multipart/form-data 上传）
        """
        if self.token is None:
            print("[SitupDetection] No token, skip upload")
            return
        if self.last_image is None:
            print("[SitupDetection] No image to send")
            return

        now = datetime.now()
        save_path = pathlib.Path("runs/detect/detected") / now.strftime("%Y/%m/%d")
        save_path.mkdir(parents=True, exist_ok=True)

        filename = now.strftime("%H-%M-%S-%f.jpg")
        full_path = save_path / filename

        
        dst = cv2.resize(self.last_image, (320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(full_path), dst)

        headers = {
            'Authorization': f'Token {self.token}',
            'Accept': 'application/json'
        }

        
        data = {
            'author': 1,  
            'title': 'situp',
            'text': f'situp count = {self.count}',
            'created_date': now.isoformat(),
            'published_date': now.isoformat(),
        }

        if self.video_id:
            data['video_id'] = self.video_id  

        try:
            with open(full_path, 'rb') as img_file:
                files = {'image': img_file}
                r = requests.post(
                    f'{self.HOST}/api_root/posts/',
                    data=data,      
                    files=files,
                    headers=headers,
                    timeout=10
                )
            print(f"[SitupDetection] POST status: {r.status_code}")
            print(f"[SitupDetection] Response: {r.text}")
        except Exception as e:
            print("[SitupDetection] 上传失败:", e)
