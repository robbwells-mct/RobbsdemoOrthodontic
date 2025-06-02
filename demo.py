#!/usr/bin/env python3
"""
Demo Script for Robb's Demo - Orthodontics Practice Management System
Demonstrates key features and functionality of the demonstration system
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(BASE_URL)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def demo_patient_management():
    """Demonstrate patient management features"""
    print("\n🧑‍⚕️ Patient Management Demo")
    print("-" * 30)
    
    # Add a demo patient
    patient_data = {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "date_of_birth": "1995-03-10",
        "phone": "(555) 444-3333",
        "email": "sarah.johnson@email.com",
        "address": "789 Pine St, City, State 12345",
        "emergency_contact": "Bob Johnson",
        "emergency_phone": "(555) 444-3334",
        "insurance_provider": "SmileCare Insurance",
        "insurance_id": "SC789012345",
        "medical_history": "No significant medical history",
        "allergies": "None",
        "referral_source": "Google Search",
        "notes": "Interested in Invisalign treatment for crowding"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/patients", json=patient_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Added patient: {patient_data['first_name']} {patient_data['last_name']}")
                return result['patient']['patient_id']
            else:
                print(f"❌ Failed to add patient: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    return None

def demo_appointment_scheduling(patient_id):
    """Demonstrate appointment scheduling"""
    print("\n📅 Appointment Scheduling Demo")
    print("-" * 35)
    
    if not patient_id:
        print("❌ No patient ID available for appointment")
        return
    
    # Schedule an appointment
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    appointment_data = {
        "patient_id": patient_id,
        "date": tomorrow,
        "time": "14:00",
        "duration_minutes": 60,
        "appointment_type": "Consultation",
        "provider": "Dr. Smith",
        "notes": "Initial consultation for Invisalign treatment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Scheduled appointment for {tomorrow} at 14:00")
            else:
                print(f"❌ Failed to schedule: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def demo_treatment_planning(patient_id):
    """Demonstrate treatment planning"""
    print("\n🦷 Treatment Planning Demo")
    print("-" * 30)
    
    if not patient_id:
        print("❌ No patient ID available for treatment plan")
        return
    
    # Create a treatment plan
    treatment_data = {
        "patient_id": patient_id,
        "diagnosis": "Moderate crowding with mild overbite",
        "treatment_type": "Invisalign",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "estimated_duration_months": 12,
        "total_cost": 4800.0,
        "insurance_coverage": 1200.0,
        "payment_plan": "Monthly payments of $300",
        "treatment_goals": "Correct crowding and improve bite alignment",
        "appliances_needed": ["Invisalign aligners", "Vivera retainers"],
        "phases": ["Initial alignment", "Space closure", "Bite correction", "Retention"],
        "status": "Planned",
        "notes": "Patient prefers clear aligners over traditional braces"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/treatment-plans", json=treatment_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Created treatment plan: {treatment_data['treatment_type']}")
                print(f"   Duration: {treatment_data['estimated_duration_months']} months")
                print(f"   Cost: ${treatment_data['total_cost']}")
            else:
                print(f"❌ Failed to create plan: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def demo_features():
    """Demonstrate key application features"""
    print("🦷 Robb's Demo - Orthodontics Practice Management System")
    print("=" * 60)
    
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the application first:")
        print("   python orthodontics_app.py")
        return
    
    print("✅ Server is running at http://localhost:5001")
    
    # Demo patient management
    patient_id = demo_patient_management()
    time.sleep(1)
    
    # Demo appointment scheduling
    demo_appointment_scheduling(patient_id)
    time.sleep(1)
    
    # Demo treatment planning
    demo_treatment_planning(patient_id)
    
    print("\n🎉 Demo Complete!")
    print("-" * 20)
    print("Visit http://localhost:5001 to see the results in the web interface")
    print("You can now:")
    print("  • View the dashboard with updated statistics")
    print("  • See the new patient in the patient list")
    print("  • Check the scheduled appointment")
    print("  • Review the treatment plan")

def main():
    """Main demo function"""
    try:
        demo_features()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
