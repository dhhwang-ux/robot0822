import threading
import tkinter as tk
from tkinter import messagebox, ttk
from time import sleep
from motion_controller import execute_motion

# pyserial의 포트 목록 함수 사용 (없으면 빈 리스트)
def list_serial_ports():
    try:
        from serial.tools import list_ports
        return [p.device for p in list_ports.comports()]
    except Exception:
        return []

def start_motion():
    port = port_var.get().strip()
    s = motion_var.get().strip()
    if not port:
        messagebox.showwarning("입력 오류", "시리얼 포트를 선택하세요.")
        return
    try:
        motion = int(s)
        if not (0 <= motion <= 255):
            raise ValueError
    except ValueError:
        messagebox.showwarning("입력 오류", "모션 번호는 0~255 범위의 정수여야 합니다.")
        return

    start_btn.config(state='disabled')
    port_combo.config(state='disabled')
    motion_entry.config(state='disabled')
    status_var.set(f"모션 {motion} 전송 중...")

    def worker():
        try:
            execute_motion(port, motion)
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("오류", str(e)))
        finally:
            sleep(7)
            root.after(0, restore_ui)

    threading.Thread(target=worker, daemon=True).start()

def restore_ui():
    start_btn.config(state='normal')
    # 콤보박스가 readonly이면 복구 시 readonly로 되돌림
    if port_combo_has_values:
        port_combo.config(state='readonly')
    else:
        port_combo.config(state='normal')
    motion_entry.config(state='normal')
    status_var.set("준비")

def refresh_ports():
    global port_combo_has_values
    ports = list_serial_ports()
    if ports:
        port_combo_has_values = True
        port_combo['values'] = ports
        port_var.set(ports[0])
        port_combo.config(state='readonly')
    else:
        port_combo_has_values = False
        port_combo['values'] = []
        port_var.set("COM7")
        port_combo.config(state='normal')

root = tk.Tk()
root.title("모션 실행 GUI")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="시리얼 포트:").grid(row=0, column=0, sticky='e')
port_var = tk.StringVar()
port_combo = ttk.Combobox(frame, textvariable=port_var, width=12)
port_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

refresh_btn = tk.Button(frame, text="갱신", width=6, command=refresh_ports)
refresh_btn.grid(row=0, column=2, padx=(5,0), pady=5)

# 초기 포트 목록 로드
port_combo_has_values = False
refresh_ports()

tk.Label(frame, text="모션 번호 (0-255):").grid(row=1, column=0, sticky='e')
motion_var = tk.StringVar(value="0")
motion_entry = tk.Entry(frame, textvariable=motion_var, width=15)
motion_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky='w')

start_btn = tk.Button(frame, text="실행", width=10, command=start_motion)
start_btn.grid(row=2, column=0, columnspan=3, pady=(8,0))

status_var = tk.StringVar(value="준비")
status_label = tk.Label(frame, textvariable=status_var)
status_label.grid(row=3, column=0, columnspan=3, pady=(8,0))

root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()