#!/usr/bin/env python3
"""
Setup script for Robb's Demo - Orthodontics Practice Management System
Helps developers quickly set up and run the demonstration application
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_sample_data():
    """Create sample data for demonstration"""
    print("\n📝 Creating sample data...")
    
    sample_data = {
        "patients": {
            "1": {
                "patient_id": "1",
                "first_name": "John",
                "last_name": "Smith",
                "date_of_birth": "1990-05-15",
                "phone": "(555) 123-4567",
                "email": "john.smith@email.com",
                "address": "123 Main St, City, State 12345",
                "emergency_contact": "Jane Smith",
                "emergency_phone": "(555) 123-4568",
                "insurance_provider": "Dental Plus Insurance",
                "insurance_id": "DP123456789",
                "medical_history": "No significant medical history",
                "allergies": "None known",
                "referral_source": "Dr. Johnson",
                "created_date": datetime.now().isoformat(),
                "notes": "Patient is interested in Invisalign treatment"
            },
            "2": {
                "patient_id": "2",
                "first_name": "Emily",
                "last_name": "Davis",
                "date_of_birth": "1985-08-22",
                "phone": "(555) 987-6543",
                "email": "emily.davis@email.com",
                "address": "456 Oak Ave, City, State 12345",
                "emergency_contact": "Mike Davis",
                "emergency_phone": "(555) 987-6544",
                "insurance_provider": "HealthCare Partners",
                "insurance_id": "HCP987654321",
                "medical_history": "Diabetes Type 2, well controlled",
                "allergies": "Penicillin",
                "referral_source": "Online Search",
                "created_date": datetime.now().isoformat(),
                "notes": "Requires traditional braces, complex case"
            }
        },
        "treatment_plans": {
            "1": {
                "plan_id": "1",
                "patient_id": "1",
                "diagnosis": "Class II malocclusion with crowding",
                "treatment_type": "Invisalign",
                "start_date": "2024-06-01",
                "estimated_duration_months": 18,
                "total_cost": 5500.0,
                "insurance_coverage": 1500.0,
                "payment_plan": "Monthly payments of $250",
                "treatment_goals": "Correct bite alignment and resolve crowding",
                "appliances_needed": ["Invisalign aligners", "Retainers"],
                "phases": ["Initial alignment", "Bite correction", "Retention"],
                "status": "Active",
                "notes": "Patient compliance excellent",
                "created_date": datetime.now().isoformat()
            }
        },
        "appointments": {
            "1": {
                "appointment_id": "1",
                "patient_id": "1",
                "date": "2024-06-15",
                "time": "10:00",
                "duration_minutes": 60,
                "appointment_type": "Follow-up",
                "provider": "Dr. Smith",
                "status": "Scheduled",
                "notes": "Aligner check and adjustment",
                "treatment_notes": "",
                "next_appointment_recommended": "4 weeks"
            }
        },
        "treatment_records": {},
        "progress_photos": {},
        "outcomes": {}
    }
    
    try:
        with open("orthodontics_data.json", "w") as f:
            json.dump(sample_data, f, indent=2)
        print("✅ Sample data created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def run_application():
    """Start the Flask application"""
    print("\n🚀 Starting the application...")
    print("Application will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "orthodontics_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

def main():
    """Main setup function"""
    print("🦷 Robb's Demo - Orthodontics Practice Management System Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Ask about sample data
    response = input("\n❓ Would you like to create sample data for testing? (y/n): ").lower()
    if response in ['y', 'yes']:
        create_sample_data()
    
    # Ask about starting the application
    response = input("\n❓ Would you like to start the application now? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_application()
    else:
        print("\n✅ Setup complete!")
        print("To start the application later, run: python orthodontics_app.py")
        print("Then visit: http://localhost:5001")

if __name__ == "__main__":
    main()
