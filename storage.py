#!/usr/bin/python3
# -*- coding: utf-8 -*-

from core import Patient, LimitedExam, PeriodicExam, ComprehensiveExam, Surgery
import logging
import yaml

RECORDS_PATH = 'records.yaml'  # Default filename for saving and loading records.
LOGGER_PATH = 'storage.log'  # Default filename for saving logging information for this module.
LOGGING_LEVEL = logging.DEBUG  # Default logging level

# Configure logging.
logger = logging.getLogger(__name__)  # Include module name.
logger.setLevel(LOGGING_LEVEL)  # Set logging recording leve.

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler(LOGGER_PATH)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Repo:

    def __init__(self, records_path=RECORDS_PATH):
        """(Initialization)

        Args:
            records_path (string): A file name in which to save and load patient/appointment information. File type must
            by .yaml. Arg defaults to 'records-v6.yaml' when left blank.
        Return:
            None
        """

        self.records_path = records_path
        self.patients = []  # List of all patients as objects.

    def load(self):
        """Loads saved information from source files.

        Args:
            None
        Return:
            None

        Populates self.patients with a complete list of Patient objects.
        """

        # records is a dictionary representing all patient appointments, and includes patient and appointment data.
        records = self._get_from_yaml()
        self._load_obj(records)
        logger.debug('Program loaded')

    def _load_obj(self, records):
        # Passes each patient record (as a dictionary) to self.new_record() where it will become a Patient object with
        # Patient.appointments populated with appropriate Appointment objects.
        for record in records:
            self._add_record(record)

    def _get_from_yaml(self):
        # Retrieves dictionary representations of patient and appointment information from a .yaml file.
        raw_records = []
        with open(RECORDS_PATH, 'r') as infile:
            records = yaml.full_load(infile)
            for record in records:
                raw_records.append(record)
        logger.debug(f'Records pulled from {RECORDS_PATH}')
        return raw_records

    def save(self, patients):
        """Saves all information to source file.

        Args:
            patients (list): A list of patient objects
        Return:
            None

        Converts patient objects to dictionary representations and then uses self._push_to_yaml to populate
        self.patients with a complete list of Patient objects.
        """

        records = []  # List of appointment dictionaries.

        for patient in patients:
            patient_info = patient.to_dict()
            for appointment in patient.appointments:
                appointment_info = appointment.to_dict()
                record = {**patient_info, **appointment_info}
                records.append(record)
                logger.debug(f'Patient {record["mrn"]}, appointment on date {record["date"]}, converted to dict and '
                             f'compiled for saving')

        self._push_to_yaml(records)

        logger.debug('Program saved')

    def _push_to_yaml(self, records):
        """Saves all information to a .yaml file.

        Args:
            records (list): A list of dictionaries representing patient appointments.
        Return:
            None

        Uses self._push_to_yaml to populate self.patients with a complete list of Patient objects.
        """

        with open(RECORDS_PATH, 'w') as yaml_outfile:
            yaml.dump(records, yaml_outfile)
        logger.debug(f'Records pushed to {RECORDS_PATH}')

    def _add_record(self, apt):
        """Substantiates Patient objects with relevant information and adds patient to self.patients.

        Args:
            apt (dict): A dictionary containing patient and appointment information for one appointment.
        Return:
            None

        Helper function for self.load to populate self.patients with a list of patient objects.
        """

        if apt['_type'] == 'PeriodicExam':
            exam = PeriodicExam(apt)
        elif apt['_type'] == 'LimitedExam':
            exam = LimitedExam(apt)
        elif apt['_type'] == 'ComprehensiveExam':
            exam = ComprehensiveExam(apt)
        elif apt['_type'] == 'Surgery':
            exam = Surgery(apt)
        else:
            logger.critical(f'Could not load record due to missing _type')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:
                    patient.appointments.append(exam)
                    logger.debug(
                        f'Patient {apt["mrn"]}, appointment date {apt["date"]}, substantiated as object and added to '
                        f'self.patients')
                    return

        new_patient = Patient(apt)
        new_patient.appointments.append(exam)
        self.patients.append(new_patient)
        logger.debug(f'Patient {apt["mrn"]}, appointment date {apt["date"]}, substantiated as object and added to '
                     f'self.patients')
