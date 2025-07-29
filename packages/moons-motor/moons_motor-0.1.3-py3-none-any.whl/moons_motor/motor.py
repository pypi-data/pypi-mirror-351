import serial
import serial.rs485
from serial.tools import list_ports
import re
import threading
from rich import print
from rich.console import Console
from rich.panel import Panel
import queue
from moons_motor.subject import Subject
import time
import threading

from dataclasses import dataclass


class StepperModules:
    STM17S_3RN = "STM17S-3RN"


@dataclass(frozen=True)
class StepperCommand:
    JOG: str = "CJ"  # Start jogging
    JOG_SPEED: str = "JS"  # Jogging speed (Need to set before start jogging)
    CHANGE_JOG_SPEED: str = "CS"  # Change jogging speed while jogging
    STOP_JOG: str = "SJ"  # Stop jogging with deceleration
    STOP: str = "ST"  # Stop immediately (No deceleration)
    STOP_DECEL: str = "STD"  # Stop with deceleration
    STOP_KILL: str = (
        "SK"  # Stop with deceleration(Control by AM) and kill all unexecuted commands
    )
    STOP_KILL_DECEL: str = (
        "SKD"  # Stop and kill all unexecuted commands with deceleration(Control by DE)
    )
    ENABLE: str = "ME"  # Enable motor
    DISABLE: str = "MD"  # Disable motor
    MOVE_ABSOLUTE: str = "FP"  # Move to absolute position
    MOVE_FIXED_DISTANCE: str = "FL"  # Move to fixed distance
    POSITION: str = "IP"  # Motor absolute position(Calculated trajectory position)
    TEMPERATURE: str = "IT"  # Motor temperature
    VOLTAGE: str = "IU"  # Motor voltage

    ENCODER_POSITION: str = "EP"  # Encoder position
    SET_POSITION: str = "SP"  # Set encoder position

    HOME: str = "SH"  # Home position
    VELOCITY: str = "VE"  # Set velocity

    ALARM_RESET: str = "AR"  # Reset alarm

    SET_RETURN_FORMAT_DECIMAL: str = "IFD"  # Set return format to decimal
    SET_RETURN_FORMAT_HEXADECIMAL: str = "IFH"  # Set return format to hexadecimal

    SET_TRANSMIT_DELAY: str = "TD"  # Set transmit delay


class MoonsStepper(Subject):
    motorAdress = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
        ":",
        ";",
        "<",
        "=",
        ">",
        "?",
        "@",
    ]

    def __init__(
        self,
        model: StepperModules,
        VID,
        PID,
        SERIAL_NUM,
        only_simlate=False,
        universe=0,
    ):
        super().__init__()
        self.universe = universe
        self.model = model  # Motor model
        self.only_simulate = only_simlate
        self.device = ""  # COM port description
        self.VID = VID
        self.PID = PID
        self.SERIAL_NUM = SERIAL_NUM  # ID for determent the deivice had same VID and PID, can be config using chips manufacturer tool
        self.ser = None
        self.Opened = False
        self.recvQueue = queue.Queue()
        self.sendQueue = queue.Queue()
        self.pending_callbacks = queue.Queue()
        self.update_thread = None
        self.is_updating = False
        self.readBuffer = ""

        self.console = Console()

        self.is_log_message = True

        self.microstep = {
            0: 200,
            1: 400,
            3: 2000,
            4: 5000,
            5: 10000,
            6: 12800,
            7: 18000,
            8: 20000,
            9: 21600,
            10: 25000,
            11: 25400,
            12: 25600,
            13: 36000,
            14: 50000,
            15: 50800,
        }

    # region connection & main functions
    @staticmethod
    def list_all_ports():
        ports = list(list_ports.comports())
        simple_ports = []
        port_info = ""
        for p in ports:
            port_info += f"■ {p.device} {p.description} [blue]{p.usb_info()}[/blue]"
            if p != ports[-1]:
                port_info += "\n"
            simple_ports.append(p.description)
        print(Panel(port_info, title="All COMPorts"))
        return simple_ports

    @staticmethod
    def process_response(response):
        equal_sign_index = response.index("=")
        address = response[0]
        command = response[1:equal_sign_index]
        value = response[equal_sign_index + 1 :]

        if command == "IT" or command == "IU":
            # Handle temperature response
            value = int(value) / 10.0
        return {
            "address": address,
            "command": command,
            "value": value,
        }

    def __start_update_thread(self):
        self.update_thread = threading.Thread(target=self.update, daemon=True)
        self.is_updating = True
        self.update_thread.start()

    def connect(self, COM=None, baudrate=9600, callback=None):
        # Simulate mode
        if self.only_simulate:
            self.Opened = True
            self.device = f"Simulate-{self.universe}"
            print(f"{self.device} connected")
            if callback:
                callback(self.device, self.Opened)
            return

        def attempt_connect(COM, baudrate):
            try:
                # self.ser = serial.Serial(
                #     port=COM,
                #     baudrate=baudrate,
                #     bytesize=serial.EIGHTBITS,
                #     parity=serial.PARITY_NONE,
                #     stopbits=serial.STOPBITS_ONE,
                #     timeout=0.5,
                # )
                self.ser = serial.rs485.RS485(port=COM, baudrate=baudrate)
                self.ser.rs485_mode = serial.rs485.RS485Settings(
                    rts_level_for_tx=True,
                    rts_level_for_rx=False,
                    loopback=False,
                    delay_before_tx=0.02,
                    delay_before_rx=0.02,
                )
                if self.ser is None:
                    self.Opened = False
                if self.ser.is_open:
                    self.Opened = True
                    print(f"[bold green]Device connected[/bold green]: {self.device}")

            except Exception as e:
                print(f"[bold red]Device error:[/bold red] {e} ")
                self.Opened = False

        ports = list(list_ports.comports())
        if COM is not None and not self.only_simulate:
            attempt_connect(COM, baudrate)
            if callback:
                callback(self.device, self.Opened)
        else:
            for p in ports:
                m = re.match(
                    r"USB\s*VID:PID=(\w+):(\w+)\s*SER=([A-Za-z0-9]*)", p.usb_info()
                )
                print(p.usb_info())
                if (
                    m
                    and m.group(1) == self.VID
                    and m.group(2) == self.PID
                    # and m.group(3) == self.SERIAL_NUM
                ):
                    if m.group(3) == self.SERIAL_NUM or self.SERIAL_NUM == "":
                        print(
                            f"[bold yellow]Device founded:[/bold yellow] {p.description} | VID: {m.group(1)} | PID: {m.group(2)} | SER: {m.group(3)}"
                        )

                        self.device = p.description

                        attempt_connect(p.device, baudrate)

                        break

                if self.only_simulate:
                    self.device = "Simulate"
                    self.Opened = True
        time.sleep(0.5)
        self.__start_update_thread()
        if callback:
            callback(self.device, self.Opened)

        if not self.Opened:
            print(f"[bold red]Device not found[/bold red]")
            if callback:
                callback(self.device, self.Opened)

    def disconnect(self):
        self.send_command(command=StepperCommand.STOP_KILL)
        time.sleep(0.5)
        self.sendQueue.queue.clear()
        self.recvQueue.queue.clear()
        self.is_updating = False
        self.update_thread = None
        if self.only_simulate:
            self.listen = False
            self.is_sending = False
            self.Opened = False
            print(f"Simulate-{self.universe} disconnected")
            return
        if self.ser is not None and self.ser.is_open:
            self.listen = False
            self.is_sending = False
            self.Opened = False
            self.ser.flush()
            self.ser.close()
            print(f"[bold red]Device disconnected[/bold red]: {self.device}")

    def send(self, command, eol=b"\r"):
        if (self.ser != None and self.ser.is_open) or self.only_simulate:
            self.temp_cmd = command + "\r"

            if self.ser is not None or not self.only_simulate:
                self.ser.write(self.temp_cmd.encode("ascii"))
            if self.is_log_message:
                print(
                    f"[bold green]Send to {self.device}:[/bold green] {self.temp_cmd}"
                )
            super().notify_observers(f"{self.universe}-{self.temp_cmd}")
        else:
            print(f"Target device is not opened. Command: {command}")

    def send_command(self, address="", command="", value=None):
        if command == "":
            print("Command can't be empty")
            return
        if value is not None:
            command = self.addressed_cmd(address, command + str(value))
        else:
            command = self.addressed_cmd(address, command)

        self.sendQueue.put_nowait(command)

    def update(self):

        while self.is_updating:
            if self.ser is not None:
                if self.ser.in_waiting > 0:
                    response = self.ser.read(self.ser.in_waiting)
                    response = response.decode("ascii", errors="ignore").strip()
                    response = response.split("\r")

                    for r in response:
                        if r != "":
                            self.readBuffer += r
                            self.handle_recv(r)

            if self.sendQueue.empty() != True:
                # time.sleep(
                #     0.02
                # )  # Time for RS485 converter to switch between Transmit and Receive mode
                while not self.sendQueue.empty():
                    # time.sleep(
                    #     0.05
                    # )  # Time for RS485 converter to switch between Transmit and Receive mode
                    cmd = self.sendQueue.get_nowait()
                    self.send(cmd)
                    self.sendQueue.task_done()

    def handle_recv(self, response):
        if "*" in response:
            print(f"[bold green](o)buffered_ack[/bold green]")
        elif "%" in response:
            print(f"[bold green](v)success_ack[/bold green]")
        elif "?" in response:
            print(f"[bold red](x)fail_ack[/bold red]")
        else:
            print(f"[bold blue]Received from {self.device}: [/bold blue]", response)
            self.recvQueue.put_nowait(response)

            if "=" in response:
                callback = self.pending_callbacks.get_nowait()
                if callback:
                    callback(response)
            # for command, callback in list(self.pending_callbacks.items()):
            #     if command in response:
            #         if callback:
            #             callback(response)
            #         del self.pending_callbacks[command]
            #         break

    # endregion

    # region motor motion functions

    # def setup_motor(self, motor_address="", kill=False):
    #     if kill:
    #         self.stop_and_kill(motor_address)
    #     self.set_transmit_delay(motor_address, 25)
    #     self.set_return_format_dexcimal(motor_address)

    def home(self, motor_address="", speed=0.3, onComplete=None):
        self.send_command(
            address=motor_address, command=StepperCommand.VELOCITY, value=speed
        )
        self.send_command(
            address=motor_address, command=StepperCommand.HOME, value="3F"
        )
        self.send_command(
            address=motor_address, command=StepperCommand.ENCODER_POSITION
        )
        self.send_command(
            address=motor_address, command=StepperCommand.SET_POSITION, value=0
        )
        if onComplete:
            self.get_status(
                motor_address, StepperCommand.SET_POSITION, callback=onComplete
            )

    # endregion
    def get_status(self, motor_address, command: StepperCommand, callback=None):
        command = self.addressed_cmd(motor_address, command)
        if callback:
            self.pending_callbacks.put_nowait(callback)
        self.sendQueue.put_nowait(command)

    # endregion

    # region utility functions

    def addressed_cmd(self, motor_address, command):
        return f"{motor_address}{command}"


# endregion

# SERIAL => 上次已知父系(尾巴+A) 或是事件分頁
# reg USB\s*VID:PID=(\w+):(\w+)\s*SER=([A-Za-z0-9]+)

# serial_num  裝置例項路徑
# TD(Tramsmit Delay) = 15
