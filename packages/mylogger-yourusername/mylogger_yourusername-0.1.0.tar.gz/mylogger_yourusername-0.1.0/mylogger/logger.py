import datetime

def log(message, level="INFO"):
    """记录日志到控制台"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level.upper()}: {message}")