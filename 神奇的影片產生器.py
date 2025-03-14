# 匯入所需的庫
import tkinter as tk          # 用於建立圖形使用者介面 (GUI)
from tkinter import filedialog, ttk, messagebox  # messagebox 用於彈出窗口
import hashlib                # 用於計算 MD5 和 SHA256 雜湊值
import numpy as np            # 用於數學運算和陣列處理
import cv2                    # 用於影片生成和處理
import os                     # 用於檔案路徑操作

# 定義檔案轉影片的類別，支援深色/淺色模式和多種影片模式
class FileToVideoConverter:
    def __init__(self, root):
        # 初始化 GUI 視窗
        self.root = root
        self.root.title("檔案轉影片工具-By TNTAPPLE")  # 設定視窗標題
        self.root.geometry("800x600")      # 調整視窗大小，寬度增加以容納左右分區
        self.root.resizable(True, True)  # 禁止調整視窗大小

        # 定義深色和淺色模式的配色
        self.themes = {
            "light": {
                "bg_color": "#F5F6F5", "accent_color": "#0078D4", "text_color": "#333333",
                "button_color": "#0078D4", "hover_color": "#005EA6",
                "entry_bg": "#FFFFFF", "entry_fg": "#333333"
            },
            "dark": {
                "bg_color": "#1F1F1F", "accent_color": "#4DA8FF", "text_color": "#E0E0E0",
                "button_color": "#4DA8FF", "hover_color": "#3B86CC",
                "entry_bg": "#333333", "entry_fg": "#E0E0E0"
            }
        }
        self.current_theme = "light"

        # 頂部標題框架
        self.header_frame = tk.Frame(root)
        self.header_frame.pack(fill="x", pady=(20, 10))
        self.label = tk.Label(self.header_frame, text="檔案轉影片工具", 
                            font=("微軟正黑體", 18, "bold"))
        self.label.pack()

        # 主內容框架，分為左右兩區
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20)

        # 左側框架：檔案選擇、數據模式、影片模式
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=(0, 20))

        # 檔案選擇區域
        self.file_frame = tk.Frame(self.left_frame)
        self.file_frame.pack(fill="x", pady=10)
        self.file_button = tk.Button(self.file_frame, text="選擇檔案", 
                                   command=self.select_file, font=("微軟正黑體", 12), 
                                   bd=0, pady=10, padx=20, relief="flat")
        self.file_button.pack()
        self.file_path_label = tk.Label(self.file_frame, text="尚未選擇檔案", 
                                      font=("微軟正黑體", 10), wraplength=300)
        self.file_path_label.pack(pady=5)

        # 數據模式選擇框架
        self.mode_frame = tk.Frame(self.left_frame)
        self.mode_frame.pack(fill="x", pady=15)
        self.mode_label = tk.Label(self.mode_frame, text="選擇數據模式", 
                                 font=("微軟正黑體", 12, "bold"))
        self.mode_label.pack()
        self.data_mode_var = tk.StringVar(value="original")
        self.data_modes = [("原始二進位", "original"), ("MD5 雜湊", "md5"), ("SHA256 雜湊", "sha256")]
        for text, mode in self.data_modes:
            radio = tk.Radiobutton(self.mode_frame, text=text, variable=self.data_mode_var, value=mode,
                                 font=("微軟正黑體", 10))
            radio.pack(anchor="w", pady=5)

        # 影片模式選擇框架
        self.video_mode_frame = tk.Frame(self.left_frame)
        self.video_mode_frame.pack(fill="x", pady=15)
        self.video_mode_label = tk.Label(self.video_mode_frame, text="選擇影片模式", 
                                       font=("微軟正黑體", 12, "bold"))
        self.video_mode_label.pack()
        self.video_mode_var = tk.StringVar(value="original")
        self.video_modes = [
            ("原始顯示", "original"), 
            ("波形", "waveform"), 
            ("彩虹漸變", "rainbow"), 
            ("噪點漩渦", "vortex"), 
            ("像素雨", "pixel_rain")
        ]
        for text, mode in self.video_modes:
            radio = tk.Radiobutton(self.video_mode_frame, text=text, variable=self.video_mode_var, value=mode,
                                 font=("微軟正黑體", 10))
            radio.pack(anchor="w", pady=5)

        # 右側框架：解析度與幀數設定、儲存路徑、按鈕、進度條、狀態
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # 解析度和 FPS 設定框架
        self.settings_frame = tk.Frame(self.right_frame)
        self.settings_frame.pack(fill="x", pady=15)
        tk.Label(self.settings_frame, text="解析度與幀數設定", 
                font=("微軟正黑體", 12, "bold")).pack()
        self.width_var = tk.IntVar(value=640)
        self.height_var = tk.IntVar(value=480)
        self.fps_var = tk.IntVar(value=30)
        for text, var in [("寬度 (pixels):", self.width_var), 
                         ("高度 (pixels):", self.height_var), 
                         ("幀數 (FPS):", self.fps_var)]:
            frame = tk.Frame(self.settings_frame)
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=text, font=("微軟正黑體", 10), width=15).pack(side="left", padx=5)
            tk.Entry(frame, textvariable=var, width=10, font=("微軟正黑體", 10), 
                    bd=1, relief="solid").pack(side="left")

        # 儲存路徑設定
        self.path_frame = tk.Frame(self.right_frame)
        self.path_frame.pack(fill="x", pady=15)
        tk.Label(self.path_frame, text="儲存路徑:", font=("微軟正黑體", 10)).pack(side="left", padx=5)
        self.path_var = tk.StringVar(value=os.getcwd())
        self.path_entry = tk.Entry(self.path_frame, textvariable=self.path_var, width=35, 
                                 font=("微軟正黑體", 10), bd=1, relief="solid")
        self.path_entry.pack(side="left", padx=5)
        self.path_button = tk.Button(self.path_frame, text="瀏覽", command=self.select_path,
                                   font=("微軟正黑體", 10), bd=0, pady=5, padx=10, relief="flat")
        self.path_button.pack(side="left")

        # 轉換按鈕
        self.convert_button = tk.Button(self.right_frame, text="開始轉換", 
                                      command=self.convert_to_video,
                                      font=("微軟正黑體", 12), 
                                      bd=0, pady=12, padx=25, relief="flat")
        self.convert_button.pack(pady=20)

        # 深色/淺色模式切換按鈕
        self.theme_button = tk.Button(self.right_frame, text="切換深色模式", 
                                    command=self.toggle_theme,
                                    font=("微軟正黑體", 10), 
                                    bd=0, pady=5, padx=15, relief="flat")
        self.theme_button.pack(pady=5)

        # 進度條
        self.progress = ttk.Progressbar(self.right_frame, length=400, mode='determinate', 
                                      style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=15)
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="#D3D3D3", 
                       background=self.themes["light"]["accent_color"])

        # 狀態訊息
        self.status_label = tk.Label(self.right_frame, text="", 
                                   font=("微軟正黑體", 10), wraplength=400)
        self.status_label.pack(pady=10)

        self.file_path = None
        self.vortex_angle = None  # 用於預計算旋渦模式的 angle
        self.vortex_radius = None  # 用於預計算旋渦模式的 radius
        self.apply_theme()

    # 套用當前主題的函數
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg_color"])
        self.header_frame.configure(bg=theme["bg_color"])
        self.label.configure(bg=theme["bg_color"], fg=theme["accent_color"])
        self.main_frame.configure(bg=theme["bg_color"])
        self.left_frame.configure(bg=theme["bg_color"])
        self.right_frame.configure(bg=theme["bg_color"])
        self.file_frame.configure(bg=theme["bg_color"])
        self.file_button.configure(bg=theme["button_color"], fg="white")
        self.file_path_label.configure(bg=theme["bg_color"], fg=theme["text_color"])
        self.mode_frame.configure(bg=theme["bg_color"])
        self.mode_label.configure(bg=theme["bg_color"], fg=theme["text_color"])
        for widget in self.mode_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.configure(bg=theme["bg_color"], fg=theme["text_color"], 
                               selectcolor=theme["bg_color"], activebackground=theme["bg_color"])
        self.video_mode_frame.configure(bg=theme["bg_color"])
        self.video_mode_label.configure(bg=theme["bg_color"], fg=theme["text_color"])
        for widget in self.video_mode_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.configure(bg=theme["bg_color"], fg=theme["text_color"], 
                               selectcolor=theme["bg_color"], activebackground=theme["bg_color"])
        self.settings_frame.configure(bg=theme["bg_color"])
        for widget in self.settings_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg_color"], fg=theme["text_color"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg_color"])
                for sub_widget in widget.winfo_children():
                    sub_widget.configure(bg=theme["bg_color"] if isinstance(sub_widget, tk.Label) else theme["entry_bg"], 
                                       fg=theme["text_color"] if isinstance(sub_widget, tk.Label) else theme["entry_fg"])
        self.path_frame.configure(bg=theme["bg_color"])
        self.path_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["text_color"])
        for widget in self.path_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg_color"], fg=theme["text_color"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=theme["button_color"], fg="white")
        self.convert_button.configure(bg=theme["button_color"], fg="white")
        self.theme_button.configure(bg=theme["button_color"], fg="white")
        self.status_label.configure(bg=theme["bg_color"], fg=theme["text_color"])
        
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="#D3D3D3" if self.current_theme == "light" else "#555555",
                       background=theme["accent_color"])

        for btn in [self.file_button, self.convert_button, self.theme_button, self.path_button]:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=theme["hover_color"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=theme["button_color"]))

    # 切換深色/淺色模式的函數
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_button.config(text="切換" + ("淺色模式" if self.current_theme == "dark" else "深色模式"))
        self.apply_theme()

    # 選擇檔案的函數
    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.file_path_label.config(text=f"已選擇: {os.path.basename(self.file_path)}")
        else:
            self.file_path_label.config(text="尚未選擇檔案")

    # 選擇儲存路徑的函數
    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    # 獲取二進位數據
    def get_binary_data(self, file_path, mode):
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        if mode == "md5":
            return hashlib.md5(binary_data).digest()
        elif mode == "sha256":
            return hashlib.sha256(binary_data).digest()
        else:
            return binary_data

    # 生成影片的函數
    def convert_to_video(self):
        if not self.file_path:
            self.status_label.config(text="請先選擇檔案！")
            return

        self.status_label.config(text="轉換中...")
        self.root.update()

        data_mode = self.data_mode_var.get()
        video_mode = self.video_mode_var.get()
        binary_data = self.get_binary_data(self.file_path, data_mode)
        try:
            frame_width = self.width_var.get()
            frame_height = self.height_var.get()
            fps = self.fps_var.get()
        except tk.TclError:
            self.status_label.config(text="請輸入有效的數字（寬度、高度、FPS）！")
            return
        save_path = os.path.join(self.path_var.get(), f"output_{data_mode}_{video_mode}.avi")

        if frame_width <= 0 or frame_height <= 0 or fps <= 0:
            self.status_label.config(text="解析度或 FPS 必須大於 0！")
            return

        min_duration = 5
        min_frames = min_duration * fps
        bytes_per_frame = frame_width * frame_height * 3
        total_bytes_needed = min_frames * bytes_per_frame

        natural_frames = (len(binary_data) + bytes_per_frame - 1) // bytes_per_frame
        total_frames = max(natural_frames, min_frames)

        if len(binary_data) < total_bytes_needed:
            repeats = (total_bytes_needed // len(binary_data)) + 1
            binary_data = (binary_data * repeats)[:total_bytes_needed]

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(save_path, fourcc, fps, (frame_width, frame_height))
        self.progress['maximum'] = total_frames

        # 預計算旋渦模式的靜態數據（僅在第一次使用時計算）
        if video_mode == "vortex" and (self.vortex_angle is None or self.vortex_radius is None):
            y, x = np.indices((frame_height, frame_width))
            center = (frame_width // 2, frame_height // 2)
            self.vortex_angle = np.arctan2(y - center[1], x - center[0])
            self.vortex_radius = np.sqrt((x - center[0])**2 + (y - center[1])**2)

        for i in range(total_frames):
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            start_idx = i * bytes_per_frame
            frame_data = binary_data[start_idx:start_idx + bytes_per_frame]
            if len(frame_data) < bytes_per_frame:
                frame_data += b'\x00' * (bytes_per_frame - len(frame_data))

            if video_mode == "original":
                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, 3))
            elif video_mode == "waveform":
                values = np.frombuffer(frame_data, dtype=np.uint8)[:frame_width]
                for x, val in enumerate(values):
                    y = int(frame_height - (val / 255) * frame_height)
                    cv2.line(frame, (x, frame_height), (x, y), (255, 255, 255), 1)
            elif video_mode == "rainbow":
                # 使用數據影響色調
                data_offset = start_idx % len(binary_data)
                hue_base = (i % 180) / 180.0 * 180  # 基礎色調
                hue_mod = (binary_data[data_offset] / 255.0) * 60  # 數據影響色調範圍
                hue = (hue_base + hue_mod) % 180  # 最終色調
                hsv = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                hsv[..., 0] = hue  # 色調 (H)
                hsv[..., 1] = 255  # 飽和度 (S)
                hsv[..., 2] = 255  # 明度 (V)
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                frame = cv2.addWeighted(frame, 0.7, 
                                      np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, 3)), 
                                      0.3, 0)
            elif video_mode == "vortex":
                # 使用數據影響旋渦強度
                data_offset = start_idx % len(binary_data)
                intensity_scale = (binary_data[data_offset] / 255.0) * 0.5 + 0.5  # 數據控制強度範圍 0.5-1.0
                angle = self.vortex_angle + i * 0.1 * intensity_scale  # 數據影響旋轉速度
                radius = self.vortex_radius * 0.05
                intensity = 127 + 127 * np.sin(angle + radius)
                frame[..., 0] = intensity.astype(np.uint8)  # B 通道
                frame[..., 1] = intensity.astype(np.uint8)  # G 通道
                frame[..., 2] = intensity.astype(np.uint8)  # R 通道
            elif video_mode == "pixel_rain":
                # 使用數據影響雨滴密度
                frame.fill(0)
                data_offset = (i * 50) % len(binary_data)
                rain_density = int((binary_data[data_offset] / 255.0) * 100)  # 數據控制密度
                for j in range(min(50, rain_density)):  # 根據數據動態調整雨滴數量
                    x = np.random.randint(0, frame_width)
                    y = (i + j) % frame_height
                    color = binary_data[(i * 50 + j) % len(binary_data)]
                    frame[y, x] = [color, color, color]

            out.write(frame)
            self.progress['value'] = i
            self.root.update()

        out.release()
        duration = total_frames / fps
        self.status_label.config(text=f"轉換完成！影片長度: {duration:.2f}秒")
        messagebox.showinfo("完成", f"影片已生成完成！\n儲存路徑: {save_path}")

# 主函數
def main():
    root = tk.Tk()
    app = FileToVideoConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()