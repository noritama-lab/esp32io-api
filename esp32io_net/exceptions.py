class ESP32S3IOError(Exception):
    """esp32io_net ライブラリの基底例外"""
    pass

class ESP32S3IODeviceError(ESP32S3IOError):
    """ESP32 が status=error を返したときの例外 (ロジックエラー)"""
    pass

class ESP32S3IONetworkError(ESP32S3IOError, RuntimeError):
    """HTTP 通信自体に失敗したときの例外"""
    pass

class ESP32S3IOSerialError(ESP32S3IOError, RuntimeError):
    """シリアル通信に失敗したときの例外"""
    pass

class ESP32S3IOProtocolError(ESP32S3IOError, RuntimeError):
    """デバイスから不正な JSON や予期しない応答が返ったときの例外"""
    pass