import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os

class Patient:
    def __init__(self, patient_id, name, phone, email, dob, insurance=""):
        self.patient_id = patient_id
        self.name = name
        self.phone = phone
        self.email = email
        self.dob = dob
        self.insurance = insurance
        self.notes = ""

class Appointment:
    def __init__(self, apt_id, patient_id, date, time, duration, reason, status="Scheduled"):
        self.apt_id = apt_id
        self.patient_id = patient_id
        self.date = date
        self.time = time
        self.duration = duration
        self.reason = reason
        self.status = status
        self.notes = ""

class NPScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("NP Practice Scheduler")
        self.root.geometry("1200x800")
        
        # Data storage
        self.patients = {}
        self.appointments = {}
        self.next_patient_id = 1
        self.next_apt_id = 1
        
        # Load data
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Schedule tab
        self.schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_frame, text="Daily Schedule")
        self.create_schedule_tab()
        
        # Patients tab
        self.patients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.patients_frame, text="Patients")
        self.create_patients_tab()
        
        # Appointments tab
        self.appointments_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.appointments_frame, text="New Appointment")
        self.create_appointments_tab()
    
    def create_schedule_tab(self):
        # Date selection
        date_frame = ttk.Frame(self.schedule_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT)
        self.schedule_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.schedule_date, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(date_frame, text="Today", 
                  command=lambda: self.schedule_date.set(datetime.now().strftime("%Y-%m-%d"))).pack(side=tk.LEFT, padx=5)
        ttk.Button(date_frame, text="Refresh", command=self.refresh_schedule).pack(side=tk.LEFT, padx=5)
        
        # Schedule treeview
        columns = ("Time", "Patient", "Phone", "Reason", "Duration", "Status")
        self.schedule_tree = ttk.Treeview(self.schedule_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=150)
        
        # Scrollbar for schedule
        schedule_scroll = ttk.Scrollbar(self.schedule_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=schedule_scroll.set)
        
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        schedule_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit appointment
        self.schedule_tree.bind("<Double-1>", self.edit_appointment)
        
        self.refresh_schedule()
    
    def create_patients_tab(self):
        # Patient management frame
        patient_controls = ttk.Frame(self.patients_frame)
        patient_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(patient_controls, text="Add Patient", command=self.add_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(patient_controls, text="Edit Patient", command=self.edit_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(patient_controls, text="Delete Patient", command=self.delete_patient).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.patients_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.patient_search = tk.StringVar()
        self.patient_search.trace("w", self.filter_patients)
        ttk.Entry(search_frame, textvariable=self.patient_search, width=30).pack(side=tk.LEFT, padx=5)
        
        # Patients treeview
        patient_columns = ("ID", "Name", "Phone", "Email", "DOB", "Insurance")
        self.patients_tree = ttk.Treeview(self.patients_frame, columns=patient_columns, show="headings", height=25)
        
        for col in patient_columns:
            self.patients_tree.heading(col, text=col)
            if col == "ID":
                self.patients_tree.column(col, width=50)
            else:
                self.patients_tree.column(col, width=150)
        
        # Scrollbar for patients
        patients_scroll = ttk.Scrollbar(self.patients_frame, orient=tk.VERTICAL, command=self.patients_tree.yview)
        self.patients_tree.configure(yscrollcommand=patients_scroll.set)
        
        self.patients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        patients_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_patients()
    
    def create_appointments_tab(self):
        # Appointment form
        form_frame = ttk.LabelFrame(self.appointments_frame, text="New Appointment")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Patient selection
        ttk.Label(form_frame, text="Patient:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.apt_patient = ttk.Combobox(form_frame, width=30)
        self.apt_patient.grid(row=0, column=1, padx=5, pady=5)
        
        # Date
        ttk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.apt_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_frame, textvariable=self.apt_date, width=32).grid(row=1, column=1, padx=5, pady=5)
        
        # Time
        ttk.Label(form_frame, text="Time:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.apt_time = ttk.Combobox(form_frame, width=30)
        self.apt_time['values'] = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]]
        self.apt_time.grid(row=2, column=1, padx=5, pady=5)
        
        # Duration
        ttk.Label(form_frame, text="Duration (min):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.apt_duration = ttk.Combobox(form_frame, width=30)
        self.apt_duration['values'] = ['15', '30', '45', '60', '90']
        self.apt_duration.set('30')
        self.apt_duration.grid(row=3, column=1, padx=5, pady=5)
        
        # Reason
        ttk.Label(form_frame, text="Reason:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.apt_reason = ttk.Combobox(form_frame, width=30)
        self.apt_reason['values'] = ['Annual Physical', 'Follow-up', 'Sick Visit', 'Vaccination', 'Consultation', 'Other']
        self.apt_reason.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Schedule Appointment", command=self.schedule_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_appointment_form).pack(side=tk.LEFT, padx=5)
        
        self.refresh_patient_combo()
    
    def add_patient(self):
        dialog = PatientDialog(self.root, "Add Patient")
        if dialog.result:
            patient = Patient(
                self.next_patient_id,
                dialog.result['name'],
                dialog.result['phone'],
                dialog.result['email'],
                dialog.result['dob'],
                dialog.result['insurance']
            )
            self.patients[self.next_patient_id] = patient
            self.next_patient_id += 1
            self.refresh_patients()
            self.refresh_patient_combo()
            self.save_data()
    
    def edit_patient(self):
        selected = self.patients_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a patient to edit.")
            return
        
        patient_id = int(self.patients_tree.item(selected[0])['values'][0])
        patient = self.patients[patient_id]
        
        dialog = PatientDialog(self.root, "Edit Patient", patient)
        if dialog.result:
            patient.name = dialog.result['name']
            patient.phone = dialog.result['phone']
            patient.email = dialog.result['email']
            patient.dob = dialog.result['dob']
            patient.insurance = dialog.result['insurance']
            self.refresh_patients()
            self.refresh_patient_combo()
            self.save_data()
    
    def delete_patient(self):
        selected = self.patients_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a patient to delete.")
            return
        
        patient_id = int(self.patients_tree.item(selected[0])['values'][0])
        patient_name = self.patients[patient_id].name
        
        if messagebox.askyesno("Confirm Delete", f"Delete patient {patient_name}?"):
            del self.patients[patient_id]
            self.refresh_patients()
            self.refresh_patient_combo()
            self.save_data()
    
    def schedule_appointment(self):
        if not self.apt_patient.get() or not self.apt_date.get() or not self.apt_time.get():
            messagebox.showerror("Missing Information", "Please fill in all required fields.")
            return
        
        # Get patient ID from selection
        patient_name = self.apt_patient.get()
        patient_id = None
        for pid, patient in self.patients.items():
            if patient.name == patient_name:
                patient_id = pid
                break
        
        if not patient_id:
            messagebox.showerror("Invalid Patient", "Please select a valid patient.")
            return
        
        appointment = Appointment(
            self.next_apt_id,
            patient_id,
            self.apt_date.get(),
            self.apt_time.get(),
            int(self.apt_duration.get()),
            self.apt_reason.get()
        )
        
        self.appointments[self.next_apt_id] = appointment
        self.next_apt_id += 1
        
        self.clear_appointment_form()
        self.refresh_schedule()
        self.save_data()
        
        messagebox.showinfo("Success", "Appointment scheduled successfully!")
    
    def clear_appointment_form(self):
        self.apt_patient.set('')
        self.apt_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.apt_time.set('')
        self.apt_duration.set('30')
        self.apt_reason.set('')
    
    def edit_appointment(self, event):
        selected = self.schedule_tree.selection()
        if not selected:
            return
        
        # Find appointment by matching time and patient
        item = self.schedule_tree.item(selected[0])
        time_str = item['values'][0]
        patient_name = item['values'][1]
        
        # Find the appointment
        for apt_id, apt in self.appointments.items():
            if apt.date == self.schedule_date.get() and apt.time == time_str:
                patient = self.patients[apt.patient_id]
                if patient.name == patient_name:
                    self.show_appointment_details(apt)
                    break
    
    def show_appointment_details(self, appointment):
        dialog = AppointmentDetailsDialog(self.root, appointment, self.patients[appointment.patient_id])
        if dialog.result:
            appointment.status = dialog.result['status']
            appointment.notes = dialog.result['notes']
            self.refresh_schedule()
            self.save_data()
    
    def refresh_schedule(self):
        # Clear existing items
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        # Get appointments for selected date
        selected_date = self.schedule_date.get()
        day_appointments = []
        
        for apt in self.appointments.values():
            if apt.date == selected_date:
                patient = self.patients.get(apt.patient_id)
                if patient:
                    day_appointments.append((apt, patient))
        
        # Sort by time
        day_appointments.sort(key=lambda x: x[0].time)
        
        # Add to treeview
        for apt, patient in day_appointments:
            self.schedule_tree.insert('', 'end', values=(
                apt.time,
                patient.name,
                patient.phone,
                apt.reason,
                f"{apt.duration} min",
                apt.status
            ))
    
    def refresh_patients(self):
        # Clear existing items
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
        
        # Filter patients based on search
        search_term = self.patient_search.get().lower()
        
        for patient in self.patients.values():
            if (not search_term or 
                search_term in patient.name.lower() or 
                search_term in patient.phone or 
                search_term in patient.email.lower()):
                
                self.patients_tree.insert('', 'end', values=(
                    patient.patient_id,
                    patient.name,
                    patient.phone,
                    patient.email,
                    patient.dob,
                    patient.insurance
                ))
    
    def filter_patients(self, *args):
        self.refresh_patients()
    
    def refresh_patient_combo(self):
        patient_names = [patient.name for patient in self.patients.values()]
        self.apt_patient['values'] = sorted(patient_names)
    
    def save_data(self):
        data = {
            'patients': {pid: {
                'patient_id': p.patient_id,
                'name': p.name,
                'phone': p.phone,
                'email': p.email,
                'dob': p.dob,
                'insurance': p.insurance,
                'notes': p.notes
            } for pid, p in self.patients.items()},
            'appointments': {aid: {
                'apt_id': a.apt_id,
                'patient_id': a.patient_id,
                'date': a.date,
                'time': a.time,
                'duration': a.duration,
                'reason': a.reason,
                'status': a.status,
                'notes': a.notes
            } for aid, a in self.appointments.items()},
            'next_patient_id': self.next_patient_id,
            'next_apt_id': self.next_apt_id
        }
        
        try:
            with open('np_scheduler_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {str(e)}")
    
    def load_data(self):
        try:
            if os.path.exists('np_scheduler_data.json'):
                with open('np_scheduler_data.json', 'r') as f:
                    data = json.load(f)
                
                # Load patients
                for pid, p_data in data.get('patients', {}).items():
                    patient = Patient(
                        p_data['patient_id'],
                        p_data['name'],
                        p_data['phone'],
                        p_data['email'],
                        p_data['dob'],
                        p_data.get('insurance', '')
                    )
                    patient.notes = p_data.get('notes', '')
                    self.patients[int(pid)] = patient
                
                # Load appointments
                for aid, a_data in data.get('appointments', {}).items():
                    appointment = Appointment(
                        a_data['apt_id'],
                        a_data['patient_id'],
                        a_data['date'],
                        a_data['time'],
                        a_data['duration'],
                        a_data['reason'],
                        a_data.get('status', 'Scheduled')
                    )
                    appointment.notes = a_data.get('notes', '')
                    self.appointments[int(aid)] = appointment
                
                self.next_patient_id = data.get('next_patient_id', 1)
                self.next_apt_id = data.get('next_apt_id', 1)
        
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load data: {str(e)}")
    
    def on_closing(self):
        self.save_data()
        self.root.destroy()

class PatientDialog:
    def __init__(self, parent, title, patient=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.grab_set()
        
        # Form fields
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=patient.name if patient else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Phone:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.phone_var = tk.StringVar(value=patient.phone if patient else "")
        ttk.Entry(self.dialog, textvariable=self.phone_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.email_var = tk.StringVar(value=patient.email if patient else "")
        ttk.Entry(self.dialog, textvariable=self.email_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Date of Birth:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.dob_var = tk.StringVar(value=patient.dob if patient else "")
        ttk.Entry(self.dialog, textvariable=self.dob_var, width=30).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Insurance:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.insurance_var = tk.StringVar(value=patient.insurance if patient else "")
        ttk.Entry(self.dialog, textvariable=self.insurance_var, width=30).grid(row=4, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=10)
        
        self.dialog.wait_window()
    
    def save(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Name is required.")
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip(),
            'dob': self.dob_var.get().strip(),
            'insurance': self.insurance_var.get().strip()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class AppointmentDetailsDialog:
    def __init__(self, parent, appointment, patient):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Appointment Details")
        self.dialog.geometry("500x400")
        self.dialog.grab_set()
        
        # Patient info (read-only)
        info_frame = ttk.LabelFrame(self.dialog, text="Patient Information")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Name: {patient.name}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Phone: {patient.phone}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Date: {appointment.date} at {appointment.time}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Reason: {appointment.reason}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Status selection
        status_frame = ttk.Frame(self.dialog)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value=appointment.status)
        status_combo = ttk.Combobox(status_frame, textvariable=self.status_var, width=20)
        status_combo['values'] = ['Scheduled', 'Confirmed', 'Completed', 'No Show', 'Cancelled']
        status_combo.pack(side=tk.LEFT, padx=10)
        
        # Notes
        notes_frame = ttk.LabelFrame(self.dialog, text="Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.notes_text = tk.Text(notes_frame, height=8, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notes_text.insert('1.0', appointment.notes)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.wait_window()
    
    def save(self):
        self.result = {
            'status': self.status_var.get(),
            'notes': self.notes_text.get('1.0', tk.END).strip()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NPScheduler(root)
    root.mainloop()