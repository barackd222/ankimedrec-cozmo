#!/usr/bin/env python
# title           :extensions_medrec.py
# description     :Uses the Medrec REST API integrated with Anki Cozmo
# author          :Jason.Lowe
# date            :10-Jul-2017
# version         :0.1
# notes           :Uses API Platform with API Key to interact with REST API which is being managed by API Platform
# python_version  :3.x
# ==============================================================================

import requests
import json

# set use_code_url to True to use #OracleCode hosted environment
# set use_code_url to False to use locally hosted environment
# set code_api_key to application key provided by API Platform Cloud Service (if None it will default to locally hosted environment)
use_code_url = False
code_api_url = 'https://apip.oracleau.cloud/api/medrec'
code_apikey_key = 'X-App-Key'
code_apikey_value = ''

# locally hosted environment URL
local_api_url = "http://localhost:3000"

headers = {'Content-Type' : 'application/json'}

patient_id = None
physician_id = None

# sample data to be used for the lab
patient = {
  "Patients": [
    {
      "FullName": "John Mills",
      "Age": "65",
      "Address": "25 Grenfell St, 5000, Adelaide, SA, Australia",
      "Mobile": "61558755883",
      "Email": "jmills@medrec.com",
      "ContactMethod": "Email|SMS|VoiceCall|Carer"
    }
  ]
}

physician = {
  "Physicians": [
    {
      "FullName": "Mark Ridless",
      "MedicalSpeciality": "Geriatric"
    }
  ]
}

observation = {
  "MedicalObservations": [
    {
      "Name": "Blood Pressure",
      "Unit": "kg|c|f|bps",
      "Value": "76",
      "Producer": "Physician",
      "RecordingDevice": "iHealth|SamsungWatch|Manual",
      "Date": "2017-05-22T09:00:00",
      "Notes": "Observation taken while relaxed and seated for a while.",
      "PatientId": "592bc1692f497f75335a89ad"
    }
  ]
}

consultation = {
  "MedicalConsultations": [
    {
      "VisitReason": "Severe cough",
      "ConsultationDate": "2017-05-22T09:00:00",
      "SubjectiveNote": "Patient complained about chest pain",
      "Diagnosis": "Chest infection",
      "PatientId": "592bc1692f497f75335a89ad"
    }
  ]
}

prescription = {
  "Prescriptions": [
    {
      "Name": "Treatment to reduce allergic rhinitis",
      "PhysicianId": "592bc1692f497f75335a89ad",
      "Notes": "Keep medicine in the refrigerator.",
      "IssueDate": "2017-05-22T09:00:00",
      "Drug": {
        "Name": "Aluminum Hydroxychloride",
        "Dosage": "500mg",
        "Frequency": "1 tablet every 8 hrs",
        "Repeat": "3",
        "CurrentRepeat": "1",
        "Formula": "Al2OH5Cl2H2",
        "SideEffects": [
          {
            "Name": "Itching and Rash",
            "Description": "An irritating skin sensation causing a desire to scratch"
          }
        ]
      },
      "PatientId": "592bc1692f497f75335a89ad"
    }
  ]
}

class APIError(Exception):
  """An API Error Exception"""

  def __init__(self, status):
    self.status = status

  def __str__(self):
    return "APIError: status={}".format(self.status)

# Some basic logic to help the transition from local environment to OracleCode environment
if use_code_url and code_apikey_value != '':
  api_url = code_api_url
  if code_apikey_key:
    headers.update({code_apikey_key: code_apikey_value})
else:
  api_url = local_api_url

def dummy():
  resp = requests.post(api_url + '/physicians', data=json.dumps(physician), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /physicians/ {}'.format(resp.status_code))

  print('Created Physician', json.dumps(physician))

def create_patient():
  resp = requests.post(api_url + '/patients', data=json.dumps(patient), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /patients/ {}'.format(resp.status_code))
  patients = resp.json()
  patient_id = patients['Patients'][0]['_id']
  print('Created Patient ', patient_id)
  return patient_id

def create_physician():
  resp = requests.post(api_url + '/physicians', data=json.dumps(physician), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /physicians/ {}'.format(resp.status_code))
  physicians = resp.json()
  physician_id = physicians['Physicians'][0]['_id']
  print('Created Physician ', physician_id)
  return physician_id

def create_observation(patient_id, robot, obj = None, cubeid = None, condition = None, selfdiagnosis = None):
  print('Patient ',patient_id)
  print('Robot ',robot)
  print('TappedObj ',obj)
  print('CubeId ',cubeid)
  print('Condition ',condition)
  print('SelfDiagnosis ',selfdiagnosis)
  resp = requests.post(api_url + '/patients/' + patient_id + '/observations', data=json.dumps(observation), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /patients/' + patient_id + '/observations {}'.format(resp.status_code))
  # dummy()

def create_consultation(patient_id, physician_id, robot, face):
  print('Physician ',physician_id)
  print('Patient ',patient_id)
  print('Robot ', robot)
  print('Face ', face)
  resp = requests.post(api_url + '/patients/' + patient_id + '/consultations', data=json.dumps(consultation), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /patients/' + patient_id + '/consultations {}'.format(resp.status_code))
  # dummy()

def create_prescription(patient_id, physician_id, robot):
  print('Physician ',physician_id)
  print('Patient ',patient_id)
  print('Robot ', robot)
  resp = requests.post(api_url + '/patients/' + patient_id + '/prescriptions', data=json.dumps(prescription), headers=headers)
  if resp.status_code != 200:
    raise APIError('POST /patients/' + patient_id + '/prescriptions {}'.format(resp.status_code))
  # dummy()
