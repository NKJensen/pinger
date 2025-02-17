import tkinter as tk
import subprocess
import time

class PingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ping Monitor")
        self.canvas = tk.Canvas(root, width=300, height=400)
        self.canvas.pack()

        # First square for gateway
        self.gateway_status_rect = self.canvas.create_rectangle(50, 50, 250, 150, fill="green")
        self.gateway_status_text = self.canvas.create_text(150, 100, text="Measuring max ping length", font=("Helvetica", 16))

        # Second square for tv2.dk
        self.tv2_status_rect = self.canvas.create_rectangle(50, 200, 250, 300, fill="green")
        self.tv2_status_text = self.canvas.create_text(150, 250, text="Measuring max ping length", font=("Helvetica", 16))

        # Third text item for the timestamp of the last poll
        self.last_poll_text = self.canvas.create_text(150, 350, text="Last Poll: N/A", font=("Helvetica", 12))

        self.gateway_last_status = None
        self.tv2_last_status = None

        # Set initial text before measuring
        self.canvas.itemconfig(self.gateway_status_text, text="Measuring max ping length")
        self.canvas.itemconfig(self.gateway_status_rect, fill="yellow")
        self.canvas.itemconfig(self.tv2_status_text, text="Measuring max ping length")
        self.canvas.itemconfig(self.tv2_status_rect, fill="yellow")

        # Call update_ping after a short delay to ensure initial text is displayed
        self.root.after(1000, self.update_ping)

    def get_gateway(self):
        try:
            result = subprocess.run(["route", "print"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            gateway = None
            for line in lines:
                if line.strip().startswith("0.0.0.0"):
                    parts = line.split()
                    if len(parts) >= 5:
                        gateway = parts[2]
                        break # first gateway is the one we want
                    
            return gateway
        except Exception as e:
            print(f"Error getting gateway: {e}")
        return None

    def ping(self, host, packet_size):
        try:
            result = subprocess.run(["ping", host, "-n", "1", "-l", str(packet_size), "-w", "100"], capture_output=True, text=True)
            if "Request timed out" in result.stdout or "Destination host unreachable" in result.stdout:
                return False
            return True
        except Exception as e:
            print(f"Error pinging {host} with packet size {packet_size}: {e}")
            return False

    def find_max_ping_size(self, host):
        low, high = 0, 4096
        max_successful_size = 0

        while low <= high:
            mid = (low + high) // 2
            if self.ping(host, mid):
                max_successful_size = mid
                low = mid + 1
            else:
                high = mid - 1

        # Print the gateway address
        print(f"Host: {host} : {max_successful_size}")


        return max_successful_size

    def update_ping(self):
        self.update_gateway_ping()
        self.update_tv2_ping()
        self.update_last_poll()
        self.root.after(60000, self.update_ping)

    def update_gateway_ping(self):
        gateway = self.get_gateway()
        if not gateway:
            new_status = ("No Gateway", "red")
            if new_status != self.gateway_last_status:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                self.canvas.itemconfig(self.gateway_status_text, text=f"No Gateway\n{timestamp}")
                self.canvas.itemconfig(self.gateway_status_rect, fill="red")
                self.gateway_last_status = new_status
                self.canvas.tag_raise(self.gateway_status_text)
            return

        # Print the gateway address
        print(f"Gateway: {gateway}")

        max_ping_size = self.find_max_ping_size(gateway)
        if max_ping_size >= 4096:
            new_status = (f"Gateway: {gateway}\nMax Ping Size >= 4096", "green")
        else:
            new_status = (f"Gateway: {gateway}\nMax Ping Size: {max_ping_size}", "red")

        if new_status != self.gateway_last_status:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.canvas.itemconfig(self.gateway_status_text, text=f"{new_status[0]}\n{timestamp}")
            self.canvas.itemconfig(self.gateway_status_rect, fill=new_status[1])
            self.gateway_last_status = new_status
            self.canvas.tag_raise(self.gateway_status_text)

    def update_tv2_ping(self):
        target = "tv2.dk"

        max_ping_size = self.find_max_ping_size(target)
        if max_ping_size >= 4096:
            new_status = ("Max Ping Size >= 4096", "green")
        else:
            new_status = (f"Max Ping Size: {max_ping_size}", "red")

        if new_status != self.tv2_last_status:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.canvas.itemconfig(self.tv2_status_text, text=f"tv2.dk: {new_status[0]}\n{timestamp}")
            self.canvas.itemconfig(self.tv2_status_rect, fill=new_status[1])
            self.tv2_last_status = new_status
            self.canvas.tag_raise(self.tv2_status_text)

    def update_last_poll(self):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.canvas.itemconfig(self.last_poll_text, text=f"Last Poll: {timestamp}")

def main():
    root = tk.Tk()
    app = PingApp(root)
    root.iconify()  # Minimize the root window
    root.deiconify()  # Restore the root window to show only the Ping Monitor window
    root.mainloop()

if __name__ == "__main__":
    main()