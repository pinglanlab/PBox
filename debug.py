import sys
import traceback

# 重定向标准输出和标准错误
class StreamCapture:
    def __init__(self):
        self.buffer = []
    def write(self, data):
        self.buffer.append(data)
    def flush(self):
        pass

stdout_original = sys.stdout
stderr_original = sys.stderr

stdout_capture = StreamCapture()
stderr_capture = StreamCapture()

sys.stdout = stdout_capture
sys.stderr = stderr_capture

try:
    print("Starting application...")
    from main import MainWindow
    print("MainWindow imported successfully")
    print("Creating MainWindow instance...")
    app = MainWindow()
    print("MainWindow created successfully")
    print("Starting main loop...")
    app.mainloop()
    print("Main loop exited normally")
except Exception as e:
    print(f"Exception caught: {type(e).__name__}: {e}")
    print("\nTraceback:")
    traceback.print_exc()
finally:
    # 恢复标准输出和标准错误
    sys.stdout = stdout_original
    sys.stderr = stderr_original
    
    # 打印捕获的输出
    print("\n=== Captured stdout ===")
    print(''.join(stdout_capture.buffer))
    print("\n=== Captured stderr ===")
    print(''.join(stderr_capture.buffer))