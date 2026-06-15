"""ESP32S3 IO コマンドプロトコル定義"""

CMD_PING = "ping"
CMD_GET_STATUS = "get_status"
CMD_GET_IO_STATE = "get_io_state"
CMD_READ_DI = "read_di"
CMD_SET_DO = "set_do"
CMD_READ_ADC = "read_adc"
CMD_SET_PWM = "set_pwm"
CMD_GET_PWM_CONFIG = "get_pwm_config"
CMD_SET_PWM_CONFIG = "set_pwm_config"
CMD_SET_RGB = "set_rgb"
CMD_LED_OFF = "led_off"
CMD_SET_LED_MODE = "set_led_mode"
CMD_GET_LED_STATE = "get_led_state"
CMD_HELP = "help"
CMD_I2C_SCAN = "i2c_scan"
CMD_I2C_READ = "i2c_read"
CMD_I2C_WRITE = "i2c_write"
CMD_GET_SENSORS = "get_sensors"
CMD_SET_OLED = "set_oled"

ALL_COMMANDS = (
    CMD_PING,
    CMD_GET_STATUS,
    CMD_GET_IO_STATE,
    CMD_READ_DI,
    CMD_SET_DO,
    CMD_READ_ADC,
    CMD_SET_PWM,
    CMD_GET_PWM_CONFIG,
    CMD_SET_PWM_CONFIG,
    CMD_SET_RGB,
    CMD_LED_OFF,
    CMD_SET_LED_MODE,
    CMD_GET_LED_STATE,
    CMD_HELP,
    CMD_I2C_SCAN,
    CMD_I2C_READ,
    CMD_I2C_WRITE,
    CMD_GET_SENSORS,
    CMD_SET_OLED,
)