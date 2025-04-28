import time
import random
import string
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math

class ParkingManagementSystem:
    def __init__(self, total_slots=20):
        # Boolean flags for each parking slot (True = occupied, False = empty)
        self.slot_status = [False] * total_slots
        
        # Queue (FIFO) for vehicles waiting to entry
        self.entry_queue = deque()
        
        # Stack (LIFO) for priority exit in compact areas
        self.exit_stack = []
        
        # Hash Table (Dictionary) for vehicle records
        self.vehicle_records = {}
        
        # Graph representation (Adjacency List) for visualization
        self.parking_graph = {i: [] for i in range(total_slots)}
        
        # Connect adjacent parking spots in the graph
        rows = 4
        cols = total_slots // rows
        for i in range(total_slots):
            row, col = i // cols, i % cols
            # Connect to spots in same row
            if col > 0:
                self.parking_graph[i].append(i-1)
            if col < cols - 1:
                self.parking_graph[i].append(i+1)
            # Connect to spots in same column
            if row > 0:
                self.parking_graph[i].append(i-cols)
            if row < rows - 1:
                self.parking_graph[i].append(i+cols)
        
        self.total_slots = total_slots
        self.revenue = 0.0
        self.stats = {
            'total_entries': 0,
            'total_exits': 0,
            'peak_occupancy': 0,
            'avg_stay_time': 0,
            'total_stay_time': 0
        }
    
    def generate_license_plate(self):
        """String processing to generate random license plate"""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=4))
        return f"{letters}-{numbers}"
    
    def is_slot_available(self):
        """Check if any parking slot is available"""
        return False in self.slot_status
    
    def get_available_slot(self):
        """Get the index of an available parking slot"""
        for i, occupied in enumerate(self.slot_status):
            if not occupied:
                return i
        return -1
    
    def vehicle_entry(self, license_plate=None):
        """Process vehicle entry with ANPR simulation"""
        if license_plate is None:
            license_plate = self.generate_license_plate()
        
        if not self.is_slot_available():
            self.entry_queue.append(license_plate)
            return None
        
        slot = self.get_available_slot()
        self.slot_status[slot] = True
        entry_time = time.time()
        
        # Generate a random vehicle type
        vehicle_type = random.choice(['Car', 'SUV', 'Truck', 'Motorcycle'])
        color = random.choice(['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 'Silver'])
        
        # Store vehicle record in hash table
        self.vehicle_records[license_plate] = {
            'slot': slot,
            'entry_time': entry_time,
            'exit_time': None,
            'expected_stay': random.randint(20, 120),  # Random stay duration in seconds
            'vehicle_type': vehicle_type,
            'color': color
        }
        
        # Update statistics
        self.stats['total_entries'] += 1
        current_occupancy = sum(self.slot_status)
        if current_occupancy > self.stats['peak_occupancy']:
            self.stats['peak_occupancy'] = current_occupancy
        
        return slot
    
    def vehicle_exit(self, license_plate):
        """Process vehicle exit"""
        if license_plate not in self.vehicle_records:
            return False
        
        record = self.vehicle_records[license_plate]
        slot = record['slot']
        
        # Free up the slot
        self.slot_status[slot] = False
        record['exit_time'] = time.time()
        
        duration = record['exit_time'] - record['entry_time']
        fee = self.calculate_fee(duration, record['vehicle_type'])
        self.revenue += fee
        
        # Update statistics
        self.stats['total_exits'] += 1
        self.stats['total_stay_time'] += duration
        if self.stats['total_exits'] > 0:
            self.stats['avg_stay_time'] = self.stats['total_stay_time'] / self.stats['total_exits']
        
        # Process waiting vehicles if any
        if self.entry_queue:
            waiting_vehicle = self.entry_queue.popleft()
            self.vehicle_entry(waiting_vehicle)
        
        return True, fee, duration
    
    def calculate_fee(self, duration, vehicle_type):
        """Calculate parking fee based on duration (in seconds) and vehicle type"""
        # Base rate: $1 per minute
        base_rate = duration / 60
        
        # Apply multiplier based on vehicle type
        multipliers = {
            'Car': 1.0,
            'SUV': 1.2,
            'Truck': 1.5,
            'Motorcycle': 0.8
        }
        
        return base_rate * multipliers.get(vehicle_type, 1.0)
    
    def add_to_exit_stack(self, license_plate):
        """Add vehicle to priority exit stack"""
        if license_plate in self.vehicle_records:
            self.exit_stack.append(license_plate)
            return True
        return False
    
    def process_exit_stack(self):
        """Process vehicles in the exit stack (LIFO)"""
        if not self.exit_stack:
            return None
        
        license_plate = self.exit_stack.pop()
        result = self.vehicle_exit(license_plate)
        return license_plate if result[0] else None
    
    def get_parking_status(self):
        """Return current parking status for visualization"""
        status = []
        for i, occupied in enumerate(self.slot_status):
            vehicle_info = None
            if occupied:
                for lp, rec in self.vehicle_records.items():
                    if rec['slot'] == i and rec['exit_time'] is None:
                        vehicle_info = {
                            'license': lp,
                            'type': rec['vehicle_type'],
                            'color': rec['color'],
                            'entry_time': rec['entry_time']
                        }
                        break
            
        #     class ModernParkingGUI:
        #         def __init__(self, root):
        #             self.root = root
        #             self.root.title("Smart Parking Management System")
        #             self.root.geometry("1100x750")
        #             self.root.configure(bg="#f0f0f0")

        #             # Load Figma Dashboard design as an image
        #             self.dashboard_image = Image.open("path_to_your_figma_dashboard_image.png")
        #             self.dashboard_photo = ImageTk.PhotoImage(self.dashboard_image)

        #             # Add the image to the dashboard tab
        #             self.dashboard_tab = ttk.Frame(self.tab_control, padding=10)
        #             self.tab_control.add(self.dashboard_tab, text="Dashboard")
        #             self.dashboard_label = tk.Label(self.dashboard_tab, image=self.dashboard_photo)
        #             self.dashboard_label.pack(fill=tk.BOTH, expand=True)

        #             # Continue with the rest of your GUI setup...
        # return status
    
    def check_vehicles_to_exit(self):
        """Check if any vehicles should exit based on their expected stay time"""
        current_time = time.time()
        vehicles_to_exit = []
        
        for license_plate, record in self.vehicle_records.items():
            if record['exit_time'] is None:  # If vehicle hasn't exited yet
                # Check if expected stay time has elapsed
                if current_time - record['entry_time'] > record['expected_stay']:
                    vehicles_to_exit.append(license_plate)
        
        return vehicles_to_exit
    
    def get_statistics(self):
        """Get current parking statistics"""
        return {
            'total_entries': self.stats['total_entries'],
            'total_exits': self.stats['total_exits'],
            'current_occupancy': sum(self.slot_status),
            'peak_occupancy': self.stats['peak_occupancy'],
            'avg_stay_time': self.stats['avg_stay_time'],
            'revenue': self.revenue,
            'queue_length': len(self.entry_queue),
            'available_slots': self.slot_status.count(False)
        }

class ModernParkingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Parking Management System")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f0f0")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        self.style.configure('SubHeader.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        self.style.configure('Info.TLabel', font=('Arial', 10), background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), background='#007bff')
        self.style.map('TButton', background=[('active', '#0069d9')])
        
        # Create custom button styles
        self.style.configure('Primary.TButton', background='#007bff', foreground='white')
        self.style.configure('Success.TButton', background='#28a745', foreground='white')
        self.style.configure('Danger.TButton', background='#dc3545', foreground='white')
        self.style.configure('Warning.TButton', background='#ffc107', foreground='black')
        self.style.configure('Info.TButton', background='#17a2b8', foreground='white')
        
        # Automation control variables
        self.automation_active = False
        self.entry_rate = 8000  # milliseconds between automated entries
        self.exit_check_rate = 5000  # milliseconds between exit checks
        
        # Initialize the parking system
        self.parking_system = ParkingManagementSystem(total_slots=20)
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create top header
        self.create_header()
        
        # Create tab system
        self.create_tabs()
        
        # Start the update loop
        self.update_timer()
        
        # Initialize dynamic elements
        self.update_statistics()
        self.update_parking_display()
        
        # Create car animation variables
        self.car_animation_active = False
        self.car_x = 0
        self.car_y = 0
        self.car_destination_slot = None
        self.car_license = None
        self.car_color = "#ff0000"
        
    def create_header(self):
        """Create the app header"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App logo and title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="Smart Parking Management System", 
                 style='Header.TLabel').pack(side=tk.LEFT)
        
        # Time and date display
        self.time_label = ttk.Label(header_frame, text="", style='SubHeader.TLabel')
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.update_time()
    
    def create_tabs(self):
        """Create the tabbed interface"""
        self.tab_control = ttk.Notebook(self.main_container)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.tab_control, padding=10)
        self.parking_tab = ttk.Frame(self.tab_control, padding=10)
        self.queue_tab = ttk.Frame(self.tab_control, padding=10)
        self.logs_tab = ttk.Frame(self.tab_control, padding=10)
        self.settings_tab = ttk.Frame(self.tab_control, padding=10)
        
        # Add tabs to notebook
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.parking_tab, text="Parking Map")
        self.tab_control.add(self.queue_tab, text="Queue & Stack")
        self.tab_control.add(self.logs_tab, text="Activity Log")
        self.tab_control.add(self.settings_tab, text="Settings")
        
        self.tab_control.pack(expand=True, fill=tk.BOTH)
        
        # Populate tabs
        self.setup_dashboard_tab()
        self.setup_parking_tab()
        self.setup_queue_tab()
        self.setup_logs_tab()
        self.setup_settings_tab()
    
    def setup_dashboard_tab(self):
        """Set up the dashboard tab"""
        # Split into two columns
        left_frame = ttk.Frame(self.dashboard_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(self.dashboard_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Statistics section
        stats_frame = ttk.LabelFrame(left_frame, text="Parking Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create statistics labels
        self.stats_labels = {}
        stats = [
            ("current_occupancy", "Current Occupancy:"),
            ("available_slots", "Available Slots:"),
            ("queue_length", "Vehicles in Queue:"),
            ("total_entries", "Total Entries:"),
            ("total_exits", "Total Exits:"),
            ("peak_occupancy", "Peak Occupancy:"),
            ("avg_stay_time", "Average Stay Time:"),
            ("revenue", "Total Revenue:")
        ]
        
        for i, (key, text) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            label_frame = ttk.Frame(stats_frame)
            label_frame.grid(row=row, column=col, sticky="w", padx=10, pady=5)
            
            ttk.Label(label_frame, text=text, style='Info.TLabel').pack(anchor="w")
            value_label = ttk.Label(label_frame, text="0", font=('Arial', 14, 'bold'))
            value_label.pack(anchor="w")
            
            self.stats_labels[key] = value_label
        
        # ANPR Camera simulation
        anpr_frame = ttk.LabelFrame(left_frame, text="ANPR Camera", padding=10)
        anpr_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for "camera feed"
        self.anpr_canvas = tk.Canvas(anpr_frame, width=400, height=100, bg="black")
        self.anpr_canvas.pack(pady=10)
        
        self.anpr_text = self.anpr_canvas.create_text(200, 30, text="Waiting for vehicle...", 
                                                    fill="green", font=('Courier', 12))
        self.license_text = self.anpr_canvas.create_text(200, 70, text="", 
                                                       fill="yellow", font=('Courier', 18, 'bold'))
        
        # Control buttons
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Car Entry", command=self.manual_car_entry, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Car Exit", command=self.manual_car_exit, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Add to Exit Stack", command=self.add_to_exit_stack_dialog, 
                  style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Process Exit Stack", command=self.process_exit_stack, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        # Recent activities log
        log_frame = ttk.LabelFrame(right_frame, text="Recent Activities", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=15, width=40, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)
        
        # Automation controls
        automation_frame = ttk.LabelFrame(right_frame, text="Automation", padding=10)
        automation_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.automation_btn = ttk.Button(automation_frame, text="Start Simulation", 
                                       command=self.toggle_automation, style='Success.TButton')
        self.automation_btn.pack(side=tk.LEFT, padx=5)
        
        # Speed controls
        speed_frame = ttk.Frame(automation_frame)
        speed_frame.pack(side=tk.RIGHT)
        
        ttk.Label(speed_frame, text="Entry Rate (ms):").pack(side=tk.LEFT)
        self.entry_rate_var = tk.StringVar(value=str(self.entry_rate))
        entry_rate_entry = ttk.Entry(speed_frame, width=8, textvariable=self.entry_rate_var)
        entry_rate_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(speed_frame, text="Exit Check Rate (ms):").pack(side=tk.LEFT, padx=(10, 0))
        self.exit_rate_var = tk.StringVar(value=str(self.exit_check_rate))
        exit_rate_entry = ttk.Entry(speed_frame, width=8, textvariable=self.exit_rate_var)
        exit_rate_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(speed_frame, text="Apply", command=self.apply_sim_settings).pack(side=tk.LEFT, padx=5)
    
    def setup_parking_tab(self):
        """Set up the parking map tab"""
        # Create canvas for parking visualization
        self.parking_canvas = tk.Canvas(self.parking_tab, bg="white")
        self.parking_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set up the parking visualization
        self.parking_slots = []
        self.draw_parking_layout()
    
    def setup_queue_tab(self):
        """Set up the queue and stack tab"""
        top_frame = ttk.Frame(self.queue_tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Entry queue section
        queue_frame = ttk.LabelFrame(self.queue_tab, text="Entry Queue (FIFO)", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.queue_canvas = tk.Canvas(queue_frame, height=150, bg="white")
        self.queue_canvas.pack(fill=tk.X)
        
        # Exit stack section
        stack_frame = ttk.LabelFrame(self.queue_tab, text="Exit Stack (LIFO)", padding=10)
        stack_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stack_canvas = tk.Canvas(stack_frame, height=150, bg="white")
        self.stack_canvas.pack(fill=tk.X)
    
    def setup_logs_tab(self):
        """Set up the activity logs tab"""
        # Full activity log
        log_frame = ttk.Frame(self.logs_tab)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.full_log_text = tk.Text(log_frame, wrap=tk.WORD)
        self.full_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.full_log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.full_log_text.config(yscrollcommand=scrollbar.set)
        self.full_log_text.config(state=tk.DISABLED)
        
        # Controls
        control_frame = ttk.Frame(self.logs_tab)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        settings_frame = ttk.LabelFrame(self.settings_tab, text="System Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Parking capacity setting
        capacity_frame = ttk.Frame(settings_frame)
        capacity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(capacity_frame, text="Total Parking Slots:").pack(side=tk.LEFT)
        self.capacity_var = tk.StringVar(value=str(self.parking_system.total_slots))
        capacity_entry = ttk.Entry(capacity_frame, width=10, textvariable=self.capacity_var)
        capacity_entry.pack(side=tk.LEFT, padx=5)
        
        # Fee structure settings
        fee_frame = ttk.LabelFrame(settings_frame, text="Fee Structure", padding=10)
        fee_frame.pack(fill=tk.X, pady=10)
        
        vehicle_types = ['Car', 'SUV', 'Truck', 'Motorcycle']
        self.fee_multipliers = {}
        
        for i, vehicle_type in enumerate(vehicle_types):
            row_frame = ttk.Frame(fee_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{vehicle_type} Rate Multiplier:").pack(side=tk.LEFT)
            
            multiplier_var = tk.StringVar(value="1.0" if vehicle_type == 'Car' else 
                                        "1.2" if vehicle_type == 'SUV' else
                                        "1.5" if vehicle_type == 'Truck' else "0.8")
            multiplier_entry = ttk.Entry(row_frame, width=10, textvariable=multiplier_var)
            multiplier_entry.pack(side=tk.LEFT, padx=5)
            
            self.fee_multipliers[vehicle_type] = multiplier_var
        
        # Apply settings button
        ttk.Button(settings_frame, text="Apply Settings", 
                  command=self.apply_settings, style='Primary.TButton').pack(pady=10)
    
    def update_time(self):
        """Update the time display"""
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_timer(self):
        """Timer for updating dynamic elements"""
        self.update_statistics()
        self.update_parking_display()
        self.update_queue_display()
        self.update_stack_display()
        
        # Check for automated operations if automation is active
        if self.automation_active:
            self.check_automatic_exits()
        
        self.root.after(1000, self.update_timer)
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.parking_system.get_statistics()
        
        for key, label in self.stats_labels.items():
            value = stats[key]
            
            # Format certain values
            if key == 'avg_stay_time':
                value = f"{value:.1f} sec"
            elif key == 'revenue':
                value = f"${value:.2f}"
            else:
                value = str(value)
            
            label.config(text=value)
    
    def draw_parking_layout(self):
        """Draw the parking lot layout"""
        self.parking_canvas.delete("all")
        
        width = self.parking_canvas.winfo_width()
        height = self.parking_canvas.winfo_height()
        
        if width <= 1:  # Canvas not fully initialized yet
            self.root.after(100, self.draw_parking_layout)
            return
        
        # Calculate slot dimensions and layout
        slots = self.parking_system.total_slots
        cols = 5
        rows = math.ceil(slots / cols)
        
        slot_width = min(width / (cols + 1), 100)
        slot_height = min(height / (rows + 1), 80)
        
        margin_x = (width - (cols * slot_width)) / 2
        margin_y = (height - (rows * slot_height)) / 2
        
        # Draw entry and exit points
        entry_x = margin_x - 100
        entry_y = margin_y + slot_height
        
        self.parking_canvas.create_rectangle(entry_x, entry_y, entry_x + 80, entry_y + 40, 
                                           fill="#b3ffb3", outline="black")
        self.parking_canvas.create_text(entry_x + 40, entry_y + 20, text="ENTRY")
        
        exit_x = margin_x + (cols * slot_width) + 20
        exit_y = margin_y + slot_height
        
        self.parking_canvas.create_rectangle(exit_x, exit_y, exit_x + 80, exit_y + 40, 
                                           fill="#ffb3b3", outline="black")
        self.parking_canvas.create_text(exit_x + 40, exit_y + 20, text="EXIT")
        
        # Draw road
        road_y = entry_y + 20
        self.parking_canvas.create_line(entry_x + 80, road_y, exit_x, road_y, 
                                      width=3, fill="gray")
        
        # Draw parking slots
        self.parking_slots = []
        
        for i in range(slots):
            row = i // cols
            col = i % cols
            
            x1 = margin_x + (col * slot_width)
            y1 = margin_y + ((row + 1) * slot_height) + 50
            x2 = x1 + slot_width - 5
            y2 = y1 + slot_height - 5
            
            slot = self.parking_canvas.create_rectangle(x1, y1, x2, y2, outline="black", 
                                                     fill="lightgray", width=2)
            slot_text = self.parking_canvas.create_text(x1 + slot_width/2, y1 + 15, 
                                                      text=f"Slot {i+1}")
            
            self.parking_slots.append({
                'id': i,
                'rect': slot,
                'text': slot_text,
                'coords': (x1, y1, x2, y2),
                'center': (x1 + slot_width/2, y1 + slot_height/2)
            })
            
            # Draw road to each slot
            if row == 0:
                self.parking_canvas.create_line(x1 + slot_width/2, y1, 
                                              x1 + slot_width/2, road_y, 
                                              width=1, fill="gray", dash=(4, 4))
            else:
                self.parking_canvas.create_line(x1 + slot_width/2, y1, 
                                              x1 + slot_width/2, y1 - 30, 
                                              width=1, fill="gray", dash=(4, 4))
        
        self.update_parking_display()
    
    def update_parking_display(self):
        """Update the parking slot display with current status"""
        if not hasattr(self, 'parking_slots') or not self.parking_slots:
            return
        
        status = self.parking_system.get_parking_status()
        
        for slot_info, slot_status in zip(self.parking_slots, status):
            slot_rect = slot_info['rect']
            
            if slot_status['occupied']:
                vehicle = slot_status['vehicle']
                if vehicle:
                    # Map color name to hex color
                    color_map = {
                        'Red': '#ff6666', 'Blue': '#6666ff', 'Green': '#66ff66',
                        'Yellow': '#ffff66', 'Black': '#333333', 'White': '#f0f0f0',
                        'Silver': '#cccccc'
                    }
                    color = color_map.get(vehicle['color'], '#888888')
                    
                    self.parking_canvas.itemconfig(slot_rect, fill=color)
                    
                    # Display license plate and vehicle type on the slot
                    x1, y1, x2, y2 = slot_info['coords']
                    
                    # Remove old vehicle info if exists
                    self.parking_canvas.delete(f"vehicle_info_{slot_info['id']}")
                    
                    # Add new vehicle info
                    self.parking_canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text=f"{vehicle['license']}\n{vehicle['type']}",
                        tags=(f"vehicle_info_{slot_info['id']}"),
                        fill="black" if vehicle['color'] in ['Yellow', 'White', 'Silver'] else "white",
                        font=('Arial', 8)
                    )
                else:
                    self.parking_canvas.itemconfig(slot_rect, fill="#ff9999")
            else:
                self.parking_canvas.itemconfig(slot_rect, fill="lightgray")
                
                # Remove any vehicle info
                self.parking_canvas.delete(f"vehicle_info_{slot_info['id']}")
    
    def update_queue_display(self):
        """Update the entry queue display"""
        self.queue_canvas.delete("all")
        
        queue = list(self.parking_system.entry_queue)
        if not queue:
            self.queue_canvas.create_text(self.queue_canvas.winfo_width() / 2, 
                                         self.queue_canvas.winfo_height() / 2, 
                                         text="Queue is empty", fill="gray")
            return
        
        width = self.queue_canvas.winfo_width()
        if width <= 1:  # Canvas not fully initialized yet
            return
        
        car_width = min(80, width / (len(queue) + 1))
        margin = (width - (len(queue) * car_width)) / (len(queue) + 1)
        
        for i, license_plate in enumerate(queue):
            x = margin + i * (car_width + margin)
            y = self.queue_canvas.winfo_height() / 2
            
            # Draw car
            self.queue_canvas.create_rectangle(x, y - 20, x + car_width, y + 20, 
                                             fill="#66b3ff", outline="black")
            
            # Draw license plate
            self.queue_canvas.create_text(x + car_width / 2, y, 
                                        text=license_plate, font=('Arial', 8))
    
    def update_stack_display(self):
        """Update the exit stack display"""
        self.stack_canvas.delete("all")
        
        stack = list(self.parking_system.exit_stack)
        if not stack:
            self.stack_canvas.create_text(self.stack_canvas.winfo_width() / 2, 
                                         self.stack_canvas.winfo_height() / 2, 
                                         text="Stack is empty", fill="gray")
            return
        
        width = self.stack_canvas.winfo_width()
        if width <= 1:  # Canvas not fully initialized yet
            return
        
        car_width = min(80, width / (len(stack) + 1))
        margin = (width - (len(stack) * car_width)) / (len(stack) + 1)
        
        for i, license_plate in enumerate(stack):
            x = margin + i * (car_width + margin)
            y = self.stack_canvas.winfo_height() / 2
            
            # Draw car
            self.stack_canvas.create_rectangle(x, y - 20, x + car_width, y + 20, 
                                             fill="#ff9980", outline="black")
            
            # Draw license plate
            self.stack_canvas.create_text(x + car_width / 2, y, 
                                        text=license_plate, font=('Arial', 8))
    
    def manual_car_entry(self):
        """Handle manual car entry"""
        license_plate = self.parking_system.generate_license_plate()
        
        # ANPR animation
        self.anpr_canvas.itemconfig(self.anpr_text, text="Vehicle detected...")
        self.anpr_canvas.itemconfig(self.license_text, text=license_plate)
        
        # Simulate entry delay
        self.root.after(1000, lambda: self.complete_car_entry(license_plate))
    
    def complete_car_entry(self, license_plate):
        """Complete car entry after ANPR animation"""
        slot = self.parking_system.vehicle_entry(license_plate)
        
        if slot is None:
            self.anpr_canvas.itemconfig(self.anpr_text, text="Parking full! Added to queue.")
            self.log_activity(f"Vehicle {license_plate} added to entry queue.")
        else:
            self.anpr_canvas.itemconfig(self.anpr_text, text=f"Vehicle assigned to slot {slot+1}")
            self.log_activity(f"Vehicle {license_plate} entered and parked in slot {slot+1}.")
            
            # Animate car entry
            self.animate_car_entry(license_plate, slot)
        
        # Reset ANPR screen after a delay
        self.root.after(2000, self.reset_anpr)
    
    def reset_anpr(self):
        """Reset ANPR camera display"""
        self.anpr_canvas.itemconfig(self.anpr_text, text="Waiting for vehicle...")
        self.anpr_canvas.itemconfig(self.license_text, text="")
    
    def manual_car_exit(self):
        """Handle manual car exit"""
        # Get list of vehicles currently in the parking
        vehicles = []
        for lp, record in self.parking_system.vehicle_records.items():
            if record['exit_time'] is None:
                vehicles.append(lp)
        
        if not vehicles:
            messagebox.showinfo("Exit", "No vehicles in parking.")
            return
        
        # Create a dialog to select a vehicle
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Vehicle to Exit")
        dialog.geometry("300x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a vehicle to exit:").pack(pady=10)
        
        listbox = tk.Listbox(dialog, width=40, height=10)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        for lp in vehicles:
            slot = self.parking_system.vehicle_records[lp]['slot']
            listbox.insert(tk.END, f"{lp} (Slot {slot+1})")
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                license_plate = vehicles[index]
                dialog.destroy()
                self.process_exit(license_plate)
            else:
                messagebox.showwarning("Selection", "Please select a vehicle.")
        
        ttk.Button(dialog, text="Exit Vehicle", command=on_select).pack(pady=10)
    
    def process_exit(self, license_plate):
        """Process a vehicle exit"""
        result, fee, duration = self.parking_system.vehicle_exit(license_plate)
        
        if result:
            slot = self.parking_system.vehicle_records[license_plate]['slot']
            duration_mins = duration / 60
            
            # Show exit information
            messagebox.showinfo("Exit", 
                             f"Vehicle {license_plate} exited from slot {slot+1}\n"
                             f"Duration: {duration_mins:.1f} minutes\n"
                             f"Fee: ${fee:.2f}")
            
            self.log_activity(f"Vehicle {license_plate} exited from slot {slot+1}. "
                            f"Duration: {duration_mins:.1f} min. Fee: ${fee:.2f}")
        else:
            messagebox.showerror("Error", "Vehicle not found in records.")
    
    def add_to_exit_stack_dialog(self):
        """Show dialog to add vehicle to exit stack"""
        # Get list of vehicles currently in the parking
        vehicles = []
        for lp, record in self.parking_system.vehicle_records.items():
            if record['exit_time'] is None:
                vehicles.append(lp)
        
        if not vehicles:
            messagebox.showinfo("Exit Stack", "No vehicles in parking.")
            return
        
        # Create a dialog to select a vehicle
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Exit Stack")
        dialog.geometry("300x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a vehicle to add to exit stack:").pack(pady=10)
        
        listbox = tk.Listbox(dialog, width=40, height=10)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        for lp in vehicles:
            slot = self.parking_system.vehicle_records[lp]['slot']
            listbox.insert(tk.END, f"{lp} (Slot {slot+1})")
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                license_plate = vehicles[index]
                dialog.destroy()
                
                # Add to exit stack
                if self.parking_system.add_to_exit_stack(license_plate):
                    messagebox.showinfo("Exit Stack", 
                                     f"Vehicle {license_plate} added to exit stack.")
                    self.log_activity(f"Vehicle {license_plate} added to exit stack.")
                else:
                    messagebox.showerror("Error", "Failed to add vehicle to exit stack.")
            else:
                messagebox.showwarning("Selection", "Please select a vehicle.")
        
        ttk.Button(dialog, text="Add to Stack", command=on_select).pack(pady=10)
    
    def process_exit_stack(self):
        """Process the next vehicle in the exit stack"""
        if not self.parking_system.exit_stack:
            messagebox.showinfo("Exit Stack", "Exit stack is empty.")
            return
        
        license_plate = self.parking_system.process_exit_stack()
        
        if license_plate:
            slot = self.parking_system.vehicle_records[license_plate]['slot']
            result, fee, duration = self.parking_system.vehicle_exit(license_plate)
            duration_mins = duration / 60
            
            messagebox.showinfo("Exit Stack", 
                             f"Vehicle {license_plate} exited from slot {slot+1}\n"
                             f"Duration: {duration_mins:.1f} minutes\n"
                             f"Fee: ${fee:.2f}")
            
            self.log_activity(f"Vehicle {license_plate} exited from exit stack. "
                            f"Duration: {duration_mins:.1f} min. Fee: ${fee:.2f}")
        else:
            messagebox.showerror("Error", "Failed to process exit stack.")
    
    def log_activity(self, message):
        """Log an activity to both logs"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to full log
        self.full_log_text.config(state=tk.NORMAL)
        self.full_log_text.insert(tk.END, log_entry)
        self.full_log_text.see(tk.END)
        self.full_log_text.config(state=tk.DISABLED)
        
        # Add to dashboard log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        
        # Limit dashboard log to last 10 entries
        num_lines = int(self.log_text.index('end-1c').split('.')[0])
        if num_lines > 10:
            self.log_text.delete('1.0', '2.0')
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Clear the logs"""
        self.full_log_text.config(state=tk.NORMAL)
        self.full_log_text.delete('1.0', tk.END)
        self.full_log_text.config(state=tk.DISABLED)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def export_logs(self):
        """Export logs to a file"""
        filename = f"parking_logs_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w') as f:
            f.write(self.full_log_text.get('1.0', tk.END))
        
        messagebox.showinfo("Export", f"Logs exported to {filename}")
    
    def toggle_automation(self):
        """Toggle automation simulation"""
        self.automation_active = not self.automation_active
        
        if self.automation_active:
            self.automation_btn.config(text="Stop Simulation")
            self.log_activity("Automated simulation started.")
            
            # Schedule the first automated entry
            self.root.after(self.entry_rate, self.automated_entry)
        else:
            self.automation_btn.config(text="Start Simulation")
            self.log_activity("Automated simulation stopped.")
    
    def automated_entry(self):
        """Automated vehicle entry"""
        if self.automation_active:
            self.manual_car_entry()
            # Schedule the next entry
            self.root.after(self.entry_rate, self.automated_entry)
    
    def check_automatic_exits(self):
        """Check for vehicles that should exit based on their expected stay time"""
        vehicles_to_exit = self.parking_system.check_vehicles_to_exit()
        
        for license_plate in vehicles_to_exit:
            slot = self.parking_system.vehicle_records[license_plate]['slot']
            self.log_activity(f"Vehicle {license_plate} automatically exiting from slot {slot+1}.")
            
            result, fee, duration = self.parking_system.vehicle_exit(license_plate)
            duration_mins = duration / 60
            
            self.log_activity(f"Vehicle {license_plate} exited. "
                            f"Duration: {duration_mins:.1f} min. Fee: ${fee:.2f}")
    
    def apply_sim_settings(self):
        """Apply simulation settings"""
        try:
            self.entry_rate = int(self.entry_rate_var.get())
            self.exit_check_rate = int(self.exit_rate_var.get())
            
            self.log_activity(f"Simulation settings updated. Entry rate: {self.entry_rate}ms, "
                            f"Exit check rate: {self.exit_check_rate}ms")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for rates.")
    
    def apply_settings(self):
        """Apply general settings"""
        try:
            new_capacity = int(self.capacity_var.get())
            
            # Verify capacity can only be increased
            if new_capacity < self.parking_system.total_slots:
                messagebox.showerror("Error", "Parking capacity can only be increased.")
                return
            
            # Update parking system capacity
            old_capacity = self.parking_system.total_slots
            
            # Add new slots to slot_status
            additional_slots = new_capacity - old_capacity
            if additional_slots > 0:
                self.parking_system.slot_status.extend([False] * additional_slots)
                self.parking_system.total_slots = new_capacity
                
                # Update graph
                for i in range(old_capacity, new_capacity):
                    self.parking_system.parking_graph[i] = []
                
                # Rebuild slot connections
                rows = 4
                cols = new_capacity // rows
                for i in range(new_capacity):
                    row, col = i // cols, i % cols
                    
                    # Clear previous connections
                    self.parking_system.parking_graph[i] = []
                    
                    # Connect to spots in same row
                    if col > 0:
                        self.parking_system.parking_graph[i].append(i-1)
                    if col < cols - 1:
                        self.parking_system.parking_graph[i].append(i+1)
                    # Connect to spots in same column
                    if row > 0:
                        self.parking_system.parking_graph[i].append(i-cols)
                    if row < rows - 1:
                        self.parking_system.parking_graph[i].append(i+cols)
            
            # Redraw the parking layout
            self.draw_parking_layout()
            
            self.log_activity(f"Parking capacity increased from {old_capacity} to {new_capacity}.")
            
            messagebox.showinfo("Settings", "Parking capacity updated successfully.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for capacity.")
    
    def animate_car_entry(self, license_plate, slot):
        """Animate a car entering the parking lot"""
        # Get the target slot coordinates
        target_slot = None
        for slot_info in self.parking_slots:
            if slot_info['id'] == slot:
                target_slot = slot_info
                break
        
        if target_slot is None:
            return
        
        # Get vehicle color
        vehicle_record = self.parking_system.vehicle_records[license_plate]
        color_map = {
            'Red': '#ff6666', 'Blue': '#6666ff', 'Green': '#66ff66',
            'Yellow': '#ffff66', 'Black': '#333333', 'White': '#f0f0f0',
            'Silver': '#cccccc'
        }
        color = color_map.get(vehicle_record['color'], '#888888')
        
        # Create car at entry point
        entry_x = 50  # Left side of canvas
        entry_y = 100  # Near the top
        
        car = self.parking_canvas.create_rectangle(entry_x, entry_y, entry_x + 40, entry_y + 30, 
                                                 fill=color, outline="black")
        car_text = self.parking_canvas.create_text(entry_x + 20, entry_y + 15, 
                                                text=license_plate[:3], font=('Arial', 8))
        
        # Animate car movement
        self.animate_car_movement(car, car_text, target_slot['center'])
    
    def animate_car_movement(self, car, car_text, target_pos, step=0):
        """Animate car movement to target position"""
        if step >= 50:  # Animation completed
            self.parking_canvas.delete(car)
            self.parking_canvas.delete(car_text)
            return
        
        # Get current position
        x1, y1, x2, y2 = self.parking_canvas.coords(car)
        current_x = (x1 + x2) / 2
        current_y = (y1 + y2) / 2
        
        # Calculate movement
        target_x, target_y = target_pos
        dx = (target_x - current_x) / (50 - step)
        dy = (target_y - current_y) / (50 - step)
        
        # Move car
        self.parking_canvas.move(car, dx, dy)
        self.parking_canvas.move(car_text, dx, dy)
        
        # Schedule next step
        self.root.after(30, lambda: self.animate_car_movement(car, car_text, target_pos, step + 1))

def main():
    root = tk.Tk()
    app = ModernParkingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()