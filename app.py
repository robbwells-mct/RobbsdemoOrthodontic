from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Add a custom filter for JavaScript escaping
@app.template_filter('escapejs')
def escapejs_filter(text):
    """Escape text for safe use in JavaScript strings."""
    if text is None:
        return ''
    return (str(text)
            .replace('\\', '\\\\')
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))

# Add a custom filter for date formatting
@app.template_filter('strftime')
def strftime_filter(date_string, format_string):
    """Format a date string using strftime format."""
    if date_string is None:
        return ''
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime(format_string)
    except (ValueError, TypeError):
        return date_string

class Patient:
    def __init__(self, patient_id, name, phone, email, dob, insurance=""):
        self.patient_id = patient_id
        self.name = name
        self.phone = phone
        self.email = email
        self.dob = dob
        self.insurance = insurance
        self.notes = ""
    
    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'dob': self.dob,
            'insurance': self.insurance,
            'notes': self.notes
        }

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
    
    def to_dict(self):
        return {
            'apt_id': self.apt_id,
            'patient_id': self.patient_id,
            'date': self.date,
            'time': self.time,
            'duration': self.duration,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes
        }

class SchedulerData:
    def __init__(self):
        self.patients = {}
        self.appointments = {}
        self.next_patient_id = 1
        self.next_apt_id = 1
        self.load_data()
    
    def save_data(self):
        data = {
            'patients': {pid: p.to_dict() for pid, p in self.patients.items()},
            'appointments': {aid: a.to_dict() for aid, a in self.appointments.items()},
            'next_patient_id': self.next_patient_id,
            'next_apt_id': self.next_apt_id
        }
        
        try:
            with open('np_scheduler_data.json', 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
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
            print(f"Load error: {e}")

# Global scheduler data instance
scheduler_data = SchedulerData()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule')
"""
Handles the '/schedule' route to display appointment schedules.
Depending on the 'view' query parameter, this function supports two modes:
- 'day': Displays appointments for a single selected date.
- 'range': Displays appointments for a 4-week range starting from the selected date.
Query Parameters:
    view (str): Determines the view type ('day' or 'range'). Defaults to 'day'.
    date (str): The selected date in 'YYYY-MM-DD' format. Defaults to today's date.
Returns:
    Renders the 'schedule.html' template with the following context:
        - For 'range' view:
            range_appointments (dict): Appointments grouped by date within the range.
            selected_date (str): The selected start date.
            view_type (str): The current view type.
            start_date (str): The start date of the range.
            end_date (str): The end date of the range.
        - For 'day' view:
            appointments (list): List of appointments for the selected date.
            selected_date (str): The selected date.
            view_type (str): The current view type.
"""
def schedule():
    from datetime import timedelta
    
    view_type = request.args.get('view', 'day')  # 'day' or 'range'
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    if view_type == 'range':
        # Get date range (next 4 weeks from selected date)
        start_date = datetime.strptime(selected_date, "%Y-%m-%d")
        end_date = start_date + timedelta(weeks=4)
        
        # Get appointments for date range
        range_appointments = {}
        for apt in scheduler_data.appointments.values():
            apt_date = datetime.strptime(apt.date, "%Y-%m-%d")
            if start_date <= apt_date <= end_date:
                patient = scheduler_data.patients.get(apt.patient_id)
                if patient:
                    apt_dict = apt.to_dict()
                    apt_dict['patient_name'] = patient.name
                    apt_dict['patient_phone'] = patient.phone
                    
                    if apt.date not in range_appointments:
                        range_appointments[apt.date] = []
                    range_appointments[apt.date].append(apt_dict)
        
        # Sort appointments within each date
        for date in range_appointments:
            range_appointments[date].sort(key=lambda x: x['time'])
        
        return render_template('schedule.html', 
                             range_appointments=range_appointments,
                             selected_date=selected_date,
                             view_type=view_type,
                             start_date=start_date.strftime("%Y-%m-%d"),
                             end_date=end_date.strftime("%Y-%m-%d"))
    else:
        # Single day view (existing functionality)
        day_appointments = []
        for apt in scheduler_data.appointments.values():
            if apt.date == selected_date:
                patient = scheduler_data.patients.get(apt.patient_id)
                if patient:
                    apt_dict = apt.to_dict()
                    apt_dict['patient_name'] = patient.name
                    apt_dict['patient_phone'] = patient.phone
                    day_appointments.append(apt_dict)
        
        # Sort by time
        day_appointments.sort(key=lambda x: x['time'])
        
        return render_template('schedule.html', 
                             appointments=day_appointments, 
                             selected_date=selected_date,
                             view_type=view_type)

@app.route('/patients')
def patients():
    search = request.args.get('search', '').lower()
    
    # Filter patients based on search
    filtered_patients = []
    for patient in scheduler_data.patients.values():
        if (not search or 
            search in patient.name.lower() or 
            search in patient.phone or 
            search in patient.email.lower()):
            filtered_patients.append(patient.to_dict())
    
    # Sort by name
    filtered_patients.sort(key=lambda x: x['name'])
    
    return render_template('patients.html', 
                         patients=filtered_patients, 
                         search=search)

@app.route('/appointments')
def appointments():
    # Get all patients for dropdown
    patients = [p.to_dict() for p in scheduler_data.patients.values()]
    patients.sort(key=lambda x: x['name'])
    
    # Generate time slots
    time_slots = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]]
    
    return render_template('appointments.html', 
                         patients=patients, 
                         time_slots=time_slots)

@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    
    if not data.get('name', '').strip():
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    patient = Patient(
        scheduler_data.next_patient_id,
        data['name'].strip(),
        data.get('phone', '').strip(),
        data.get('email', '').strip(),
        data.get('dob', '').strip(),
        data.get('insurance', '').strip()
    )
    
    scheduler_data.patients[scheduler_data.next_patient_id] = patient
    scheduler_data.next_patient_id += 1
    
    if scheduler_data.save_data():
        return jsonify({'success': True, 'patient': patient.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def edit_patient(patient_id):
    if patient_id not in scheduler_data.patients:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    
    data = request.get_json()
    patient = scheduler_data.patients[patient_id]
    
    if not data.get('name', '').strip():
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    patient.name = data['name'].strip()
    patient.phone = data.get('phone', '').strip()
    patient.email = data.get('email', '').strip()
    patient.dob = data.get('dob', '').strip()
    patient.insurance = data.get('insurance', '').strip()
    
    if scheduler_data.save_data():
        return jsonify({'success': True, 'patient': patient.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    if patient_id not in scheduler_data.patients:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    
    del scheduler_data.patients[patient_id]
    
    if scheduler_data.save_data():
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json()
    
    required_fields = ['patient_id', 'date', 'time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    patient_id = int(data['patient_id'])
    if patient_id not in scheduler_data.patients:
        return jsonify({'success': False, 'error': 'Invalid patient'}), 400
    
    appointment = Appointment(
        scheduler_data.next_apt_id,
        patient_id,
        data['date'],
        data['time'],
        int(data.get('duration', 30)),
        data.get('reason', '')
    )
    
    scheduler_data.appointments[scheduler_data.next_apt_id] = appointment
    scheduler_data.next_apt_id += 1
    
    if scheduler_data.save_data():
        return jsonify({'success': True, 'appointment': appointment.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/appointments/<int:apt_id>', methods=['PUT'])
def edit_appointment(apt_id):
    if apt_id not in scheduler_data.appointments:
        return jsonify({'success': False, 'error': 'Appointment not found'}), 404
    
    data = request.get_json()
    appointment = scheduler_data.appointments[apt_id]
    
    appointment.status = data.get('status', appointment.status)
    appointment.notes = data.get('notes', appointment.notes)
    
    if scheduler_data.save_data():
        return jsonify({'success': True, 'appointment': appointment.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/appointments/<int:apt_id>')
def get_appointment(apt_id):
    if apt_id not in scheduler_data.appointments:
        return jsonify({'success': False, 'error': 'Appointment not found'}), 404
    
    appointment = scheduler_data.appointments[apt_id]
    patient = scheduler_data.patients.get(appointment.patient_id)
    
    apt_dict = appointment.to_dict()
    if patient:
        apt_dict['patient'] = patient.to_dict()
    
    return jsonify({'success': True, 'appointment': apt_dict})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
