"""
Orthodontics Practice Management System
A comprehensive system for managing orthodontic patients, treatments, scheduling, and outcomes.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import uuid

app = Flask(__name__)

# Configuration
app.config['APP_TITLE'] = "Robb's Demo - Welcome to Your Orthodontics Practice"

# Custom template filters
@app.template_filter('escapejs')
def escapejs_filter(text):
    """Escape text for safe use in JavaScript strings."""
    if not text:
        return ""
    return (text.replace('\\', '\\\\')
               .replace('"', '\\"')
               .replace("'", "\\'")
               .replace('\n', '\\n')
               .replace('\r', '\\r'))

@app.template_filter('strftime')
def strftime_filter(date_string, format_string):
    """Format a date string using strftime format."""
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime(format_string)
    except:
        return date_string

# Data Models
@dataclass
class Patient:
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    email: str
    address: str
    emergency_contact: str
    emergency_phone: str
    insurance_provider: str
    insurance_id: str
    medical_history: str
    allergies: str
    referral_source: str
    created_date: str
    notes: str = ""
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TreatmentPlan:
    plan_id: str
    patient_id: str
    diagnosis: str
    treatment_type: str  # Braces, Invisalign, Retainers, etc.
    start_date: str
    estimated_duration_months: int
    total_cost: float
    insurance_coverage: float
    payment_plan: str
    treatment_goals: str
    appliances_needed: List[str]
    phases: List[Dict]  # Treatment phases with descriptions and timelines
    status: str = "Planned"  # Planned, Active, Completed, Discontinued
    notes: str = ""
    created_date: str = ""
    
    def to_dict(self):
        data = asdict(self)
        return data

@dataclass
class Appointment:
    appointment_id: str
    patient_id: str
    date: str
    time: str
    duration_minutes: int
    appointment_type: str  # Consultation, Adjustment, Follow-up, Emergency, etc.
    provider: str
    status: str = "Scheduled"  # Scheduled, Confirmed, Completed, No-Show, Cancelled
    notes: str = ""
    treatment_notes: str = ""
    next_appointment_recommended: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TreatmentRecord:
    record_id: str
    patient_id: str
    appointment_id: str
    date: str
    treatment_type: str
    appliances_adjusted: List[str]
    procedures_performed: List[str]
    progress_notes: str
    photos_taken: bool
    x_rays_taken: bool
    impressions_taken: bool
    next_steps: str
    provider: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ProgressPhoto:
    photo_id: str
    patient_id: str
    date: str
    photo_type: str  # Intraoral, Extraoral, X-ray
    file_path: str
    description: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Outcome:
    outcome_id: str
    patient_id: str
    treatment_plan_id: str
    completion_date: str
    final_photos: List[str]
    treatment_success_rating: int  # 1-10 scale
    patient_satisfaction: int  # 1-10 scale
    retention_appliance: str
    follow_up_schedule: str
    notes: str
    
    def to_dict(self):
        return asdict(self)

class OrthodonticsDataManager:
    def __init__(self, data_file='orthodontics_data.json'):
        self.data_file = data_file
        self.patients = {}
        self.treatment_plans = {}
        self.appointments = {}
        self.treatment_records = {}
        self.progress_photos = {}
        self.outcomes = {}
        self.load_data()
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'patients': {pid: p.to_dict() for pid, p in self.patients.items()},
            'treatment_plans': {tid: tp.to_dict() for tid, tp in self.treatment_plans.items()},
            'appointments': {aid: a.to_dict() for aid, a in self.appointments.items()},
            'treatment_records': {rid: tr.to_dict() for rid, tr in self.treatment_records.items()},
            'progress_photos': {pid: pp.to_dict() for pid, pp in self.progress_photos.items()},
            'outcomes': {oid: o.to_dict() for oid, o in self.outcomes.items()}
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load patients
                for pid, p_data in data.get('patients', {}).items():
                    self.patients[pid] = Patient(**p_data)
                
                # Load treatment plans
                for tid, tp_data in data.get('treatment_plans', {}).items():
                    self.treatment_plans[tid] = TreatmentPlan(**tp_data)
                
                # Load appointments
                for aid, a_data in data.get('appointments', {}).items():
                    self.appointments[aid] = Appointment(**a_data)
                
                # Load treatment records
                for rid, tr_data in data.get('treatment_records', {}).items():
                    self.treatment_records[rid] = TreatmentRecord(**tr_data)
                
                # Load progress photos
                for pid, pp_data in data.get('progress_photos', {}).items():
                    self.progress_photos[pid] = ProgressPhoto(**pp_data)
                
                # Load outcomes
                for oid, o_data in data.get('outcomes', {}).items():
                    self.outcomes[oid] = Outcome(**o_data)
                    
        except Exception as e:
            print(f"Load error: {e}")

# Global data manager
data_manager = OrthodonticsDataManager()

# Routes
@app.route('/')
def index():
    """Dashboard with practice overview"""
    total_patients = len(data_manager.patients)
    active_treatments = len([tp for tp in data_manager.treatment_plans.values() if tp.status == "Active"])
    today = datetime.now().strftime("%Y-%m-%d")
    today_appointments = [a for a in data_manager.appointments.values() if a.date == today]
    
    # Recent activity
    recent_patients = sorted(data_manager.patients.values(), key=lambda x: x.created_date, reverse=True)[:5]
    
    return render_template('orthodontics/dashboard.html',
                         total_patients=total_patients,
                         active_treatments=active_treatments,
                         today_appointments=len(today_appointments),
                         recent_patients=recent_patients)

@app.route('/patients')
def patients():
    """Patient management"""
    search = request.args.get('search', '').lower()
    
    filtered_patients = []
    for patient in data_manager.patients.values():
        if (not search or 
            search in patient.full_name.lower() or 
            search in patient.phone or 
            search in patient.email.lower()):
            filtered_patients.append(patient.to_dict())
    
    filtered_patients.sort(key=lambda x: f"{x['last_name']}, {x['first_name']}")
    
    return render_template('orthodontics/patients.html', 
                         patients=filtered_patients, 
                         search=search)

@app.route('/patient/<patient_id>')
def patient_detail(patient_id):
    """Individual patient detail view"""
    patient = data_manager.patients.get(patient_id)
    if not patient:
        return redirect(url_for('patients'))
    
    # Get patient's treatment plans
    patient_plans = [tp for tp in data_manager.treatment_plans.values() if tp.patient_id == patient_id]
    
    # Get patient's appointments
    patient_appointments = [a for a in data_manager.appointments.values() if a.patient_id == patient_id]
    patient_appointments.sort(key=lambda x: f"{x.date} {x.time}")
    
    # Get treatment records
    treatment_records = [tr for tr in data_manager.treatment_records.values() if tr.patient_id == patient_id]
    treatment_records.sort(key=lambda x: x.date, reverse=True)
    
    # Get progress photos
    progress_photos = [pp for pp in data_manager.progress_photos.values() if pp.patient_id == patient_id]
    progress_photos.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('orthodontics/patient_detail.html',
                         patient=patient.to_dict(),
                         treatment_plans=patient_plans,
                         appointments=patient_appointments,
                         treatment_records=treatment_records,
                         progress_photos=progress_photos)

@app.route('/schedule')
def schedule():
    """Appointment scheduling view"""
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    view_type = request.args.get('view', 'day')
    
    if view_type == 'week':
        # Week view
        start_date = datetime.strptime(selected_date, "%Y-%m-%d")
        week_appointments = {}
        
        for i in range(7):
            current_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            day_appointments = []
            
            for apt in data_manager.appointments.values():
                if apt.date == current_date:
                    patient = data_manager.patients.get(apt.patient_id)
                    if patient:
                        apt_dict = apt.to_dict()
                        apt_dict['patient_name'] = patient.full_name
                        apt_dict['patient_phone'] = patient.phone
                        day_appointments.append(apt_dict)
            
            day_appointments.sort(key=lambda x: x['time'])
            week_appointments[current_date] = day_appointments
        
        return render_template('orthodontics/schedule.html',
                             week_appointments=week_appointments,
                             selected_date=selected_date,
                             view_type=view_type)
    else:
        # Day view
        day_appointments = []
        for apt in data_manager.appointments.values():
            if apt.date == selected_date:
                patient = data_manager.patients.get(apt.patient_id)
                if patient:
                    apt_dict = apt.to_dict()
                    apt_dict['patient_name'] = patient.full_name
                    apt_dict['patient_phone'] = patient.phone
                    day_appointments.append(apt_dict)
        
        day_appointments.sort(key=lambda x: x['time'])
        
        return render_template('orthodontics/schedule.html',
                             appointments=day_appointments,
                             selected_date=selected_date,
                             view_type=view_type)

@app.route('/treatments')
def treatments():
    """Treatment planning and management"""
    status_filter = request.args.get('status', 'all')
    
    treatment_plans = list(data_manager.treatment_plans.values())
    if status_filter != 'all':
        treatment_plans = [tp for tp in treatment_plans if tp.status.lower() == status_filter.lower()]
    
    # Add patient names to treatment plans
    for tp in treatment_plans:
        patient = data_manager.patients.get(tp.patient_id)
        if patient:
            tp.patient_name = patient.full_name
        else:
            tp.patient_name = "Unknown Patient"
    
    treatment_plans.sort(key=lambda x: x.start_date, reverse=True)
    
    return render_template('orthodontics/treatments.html',
                         treatment_plans=treatment_plans,
                         status_filter=status_filter)

@app.route('/outcomes')
def outcomes():
    """Treatment outcomes and analytics"""
    outcomes_list = list(data_manager.outcomes.values())
    
    # Add patient and treatment plan info
    for outcome in outcomes_list:
        patient = data_manager.patients.get(outcome.patient_id)
        treatment_plan = data_manager.treatment_plans.get(outcome.treatment_plan_id)
        
        if patient:
            outcome.patient_name = patient.full_name
        if treatment_plan:
            outcome.treatment_type = treatment_plan.treatment_type
    
    # Sort by completion date, handle None values
    outcomes_list.sort(key=lambda x: x.completion_date if x.completion_date else '9999-12-31', reverse=True)
    
    # Calculate statistics
    completed_treatments = len([o for o in outcomes_list if o.completion_date])
    if outcomes_list:
        avg_success_rating = sum(o.treatment_success_rating for o in outcomes_list) / len(outcomes_list)
        # Only calculate satisfaction for outcomes that have ratings
        satisfaction_ratings = [o.patient_satisfaction for o in outcomes_list if o.patient_satisfaction]
        avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else 0
    else:
        avg_success_rating = 0
        avg_satisfaction = 0
    
    # Get all patients for the outcome form
    patients_list = list(data_manager.patients.values())
    
    return render_template('orthodontics/outcomes.html',
                         outcomes=outcomes_list,
                         completed_treatments=completed_treatments,
                         avg_success_rating=round(avg_success_rating, 1),
                         avg_satisfaction=round(avg_satisfaction, 1),
                         patients=patients_list)

# API Routes
@app.route('/api/patients', methods=['POST'])
def api_add_patient():
    """Add a new patient"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'phone']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    patient_id = str(uuid.uuid4())
    patient = Patient(
        patient_id=patient_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=data['date_of_birth'],
        phone=data['phone'],
        email=data.get('email', ''),
        address=data.get('address', ''),
        emergency_contact=data.get('emergency_contact', ''),
        emergency_phone=data.get('emergency_phone', ''),
        insurance_provider=data.get('insurance_provider', ''),
        insurance_id=data.get('insurance_id', ''),
        medical_history=data.get('medical_history', ''),
        allergies=data.get('allergies', ''),
        referral_source=data.get('referral_source', ''),
        created_date=datetime.now().isoformat(),
        notes=data.get('notes', '')
    )
    
    data_manager.patients[patient_id] = patient
    
    if data_manager.save_data():
        return jsonify({'success': True, 'patient': patient.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/appointments', methods=['POST'])
def api_add_appointment():
    """Schedule a new appointment"""
    data = request.get_json()
    
    required_fields = ['patient_id', 'date', 'time', 'appointment_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    appointment_id = str(uuid.uuid4())
    appointment = Appointment(
        appointment_id=appointment_id,
        patient_id=data['patient_id'],
        date=data['date'],
        time=data['time'],
        duration_minutes=int(data.get('duration_minutes', 60)),
        appointment_type=data['appointment_type'],
        provider=data.get('provider', 'Dr. Smith'),
        status=data.get('status', 'Scheduled'),
        notes=data.get('notes', ''),
        treatment_notes=data.get('treatment_notes', ''),
        next_appointment_recommended=data.get('next_appointment_recommended', '')
    )
    
    data_manager.appointments[appointment_id] = appointment
    
    if data_manager.save_data():
        return jsonify({'success': True, 'appointment': appointment.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/treatment-plans', methods=['POST'])
def api_add_treatment_plan():
    """Create a new treatment plan"""
    data = request.get_json()
    
    required_fields = ['patient_id', 'diagnosis', 'treatment_type', 'start_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    plan_id = str(uuid.uuid4())
    treatment_plan = TreatmentPlan(
        plan_id=plan_id,
        patient_id=data['patient_id'],
        diagnosis=data['diagnosis'],
        treatment_type=data['treatment_type'],
        start_date=data['start_date'],
        estimated_duration_months=int(data.get('estimated_duration_months', 18)),
        total_cost=float(data.get('total_cost', 0)),
        insurance_coverage=float(data.get('insurance_coverage', 0)),
        payment_plan=data.get('payment_plan', ''),
        treatment_goals=data.get('treatment_goals', ''),
        appliances_needed=data.get('appliances_needed', []),
        phases=data.get('phases', []),
        status=data.get('status', 'Planned'),
        notes=data.get('notes', ''),
        created_date=datetime.now().isoformat()
    )
    
    data_manager.treatment_plans[plan_id] = treatment_plan
    
    if data_manager.save_data():
        return jsonify({'success': True, 'treatment_plan': treatment_plan.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/treatment-plans', methods=['GET'])
def api_get_treatment_plans():
    """Get treatment plans for a patient"""
    patient_id = request.args.get('patient_id')
    
    if not patient_id:
        return jsonify({'success': False, 'error': 'patient_id is required'}), 400
    
    patient_plans = [tp.to_dict() for tp in data_manager.treatment_plans.values() 
                     if tp.patient_id == patient_id]
    
    return jsonify(patient_plans)

@app.route('/api/outcomes', methods=['POST'])
def api_add_outcome():
    """Record a treatment outcome"""
    data = request.get_json()
    
    required_fields = ['patient_id', 'treatment_plan_id', 'completion_date', 'success_rating']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    outcome_id = str(uuid.uuid4())
    outcome = Outcome(
        outcome_id=outcome_id,
        patient_id=data['patient_id'],
        treatment_plan_id=data['treatment_plan_id'],
        completion_date=data['completion_date'],
        treatment_success_rating=float(data['success_rating']),
        patient_satisfaction=int(data.get('patient_satisfaction', 0)) if data.get('patient_satisfaction') else None,
        final_cost=float(data.get('final_cost', 0)) if data.get('final_cost') else None,
        achieved_goals=data.get('achieved_goals', ''),
        complications=data.get('complications', ''),
        follow_up_needed=data.get('follow_up_needed', ''),
        notes=data.get('notes', ''),
        created_date=datetime.now().isoformat()
    )
    
    data_manager.outcomes[outcome_id] = outcome
    
    if data_manager.save_data():
        return jsonify({'success': True, 'outcome': outcome.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/treatment-records', methods=['POST'])
def api_add_treatment_record():
    """Add a treatment record"""
    data = request.get_json()
    
    required_fields = ['patient_id', 'date', 'procedure_type', 'description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    record_id = str(uuid.uuid4())
    treatment_record = TreatmentRecord(
        record_id=record_id,
        patient_id=data['patient_id'],
        treatment_plan_id=data.get('treatment_plan_id', ''),
        date=data['date'],
        procedure_type=data['procedure_type'],
        description=data['description'],
        provider=data.get('provider', 'Dr. Smith'),
        cost=float(data.get('cost', 0)) if data.get('cost') else None,
        next_steps=data.get('next_steps', ''),
        notes=data.get('notes', '')
    )
    
    data_manager.treatment_records[record_id] = treatment_record
    
    if data_manager.save_data():
        return jsonify({'success': True, 'treatment_record': treatment_record.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

@app.route('/api/progress-photos', methods=['POST'])
def api_add_progress_photo():
    """Add a progress photo record"""
    data = request.get_json()
    
    required_fields = ['patient_id', 'date', 'photo_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    photo_id = str(uuid.uuid4())
    progress_photo = ProgressPhoto(
        photo_id=photo_id,
        patient_id=data['patient_id'],
        treatment_plan_id=data.get('treatment_plan_id', ''),
        date=data['date'],
        photo_type=data['photo_type'],
        file_path=data.get('file_path', ''),
        notes=data.get('notes', ''),
        created_date=datetime.now().isoformat()
    )
    
    data_manager.progress_photos[photo_id] = progress_photo
    
    if data_manager.save_data():
        return jsonify({'success': True, 'progress_photo': progress_photo.to_dict()})
    else:
        return jsonify({'success': False, 'error': 'Failed to save data'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
