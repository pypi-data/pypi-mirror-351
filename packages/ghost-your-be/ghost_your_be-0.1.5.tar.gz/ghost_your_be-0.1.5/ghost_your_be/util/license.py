import os
import json
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Danh sách key hợp lệ (thay bằng cơ chế kiểm tra thực tế, ví dụ: gọi API)
VALID_KEYS = {
    "VALID_KEY_123": True,
    "PRO_KEY_456": True,
}

CONFIG_FILE = os.path.expanduser("~/.ghost-your-be-config")

def hash_key(key):
    """Tạo hash của license key để lưu trữ an toàn."""
    return hashlib.sha256(key.encode()).hexdigest()

def save_license(key):
    """Lưu license key đã hash vào file cấu hình."""
    try:
        config = {"license_key": hash_key(key), "pro_activated": True}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        logger.info("License key đã được lưu.")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu license key: {e}")
        return False

def load_license():
    """Đọc trạng thái license từ file cấu hình."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"license_key": None, "pro_activated": False}
    except Exception as e:
        logger.error(f"Lỗi khi đọc license key: {e}")
        return {"license_key": None, "pro_activated": False}

def validate_license(key):
    """Kiểm tra license key."""
    if key in VALID_KEYS:
        if save_license(key):
            logger.info("Kích hoạt bản Pro thành công!")
            return True
        else:
            logger.error("Lỗi khi lưu license key.")
            return False
    else:
        logger.error("License key không hợp lệ!")
        return False

def is_pro_activated():
    """Kiểm tra trạng thái bản Pro."""
    config = load_license()
    return config.get("pro_activated", False)