#!/usr/bin/python3
# -*- coding: utf-8 -*-

from core import Patient, LimitedExam, PeriodicExam, ComprehensiveExam, Surgery, RUNTIME_ID
import logging
from logging.handlers import RotatingFileHandler
import yaml

RECORDS_FILENAME = 'records.yaml'  # Default filename for saving and loading records.
LOG_FILENAME = 'storage.log'  # Default filename for saving logging information for this module.
DEFAULT_LOG_LEVEL = logging.DEBUG  # Default logging level.

# Configure logging.
log = logging.getLogger(__name__)  # Include module name.
log.setLevel(DEFAULT_LOG_LEVEL)  # Set logging recording leve.


class Repo:

    def __init__(self, records_path=RECORDS_FILENAME):
        """(Initialization)

        Args:
            records_path (string): A file name in which to save and load patient/appointment information. File type must
            by .yaml. Arg defaults to 'records-v6.yaml' when left blank.
        Return:
            None
        """

        self.records_path = records_path
        self.patients = []  # List of all patients as objects.
        log.debug(f'{RUNTIME_ID} Repo(): Repo instance instantiated.')

    def load(self):
        """Loads saved information from source files.

        Args:
            None
        Return:
            None

        Populates self.patients with a complete list of Patient objects.
        """

        log.debug(f'{RUNTIME_ID} load(): instantiated.')

        # records is a dictionary representing all patient appointments, and includes patient and appointment data.
        records = self._get_from_yaml()
        self._load_obj(records)

        log.debug(f'{RUNTIME_ID} load(): Program records loaded in Repo.patients')

    def _load_obj(self, records):
        # Passes each patient record (as a dictionary) to self.new_record() where it will become a Patient object with
        # Patient.appointments populated with appropriate Appointment objects.
        for record in records:
            self._add_record(record)

    def _get_from_yaml(self):
        # Retrieves dictionary representations of patient and appointment information from a .yaml file.
        raw_records = []
        with open(RECORDS_FILENAME, 'r') as infile:
            records = yaml.full_load(infile)
            for record in records:
                raw_records.append(record)
        log.debug(f'{RUNTIME_ID} _get_from_yaml(): Records pulled from {RECORDS_FILENAME}')
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

        log.debug(f'{RUNTIME_ID} save() instantiated.')

        records = []  # List of appointment dictionaries.

        for patient in patients:
            patient_info = patient.to_dict()
            for appointment in patient.appointments:
                appointment_info = appointment.to_dict()
                record = {**patient_info, **appointment_info}
                records.append(record)
                log.debug(f'{RUNTIME_ID} save(): Patient {record["mrn"]}, appointment on date {record["date"]}, '
                          f'converted to dict and compiled for saving')

        self._push_to_yaml(records)

        log.debug(f'{RUNTIME_ID} save(): Program saved')

    def _push_to_yaml(self, records):
        """Saves all information to a .yaml file.

        Args:
            records (list): A list of dictionaries representing patient appointments.
        Return:
            None

        Uses self._push_to_yaml to populate self.patients with a complete list of Patient objects.
        """

        log.debug(f'{RUNTIME_ID} _push_to_yaml(): instantiated.')

        with open(RECORDS_FILENAME, 'w') as yaml_outfile:
            yaml.dump(records, yaml_outfile)
        log.debug(f'{RUNTIME_ID} _push_to_yaml(): Records pushed to {RECORDS_FILENAME}')

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
            log.critical(f'{RUNTIME_ID} _add_record(): Could not load record due to missing _type')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:
                    patient.appointments.append(exam)
                    log.debug(
                        f'{RUNTIME_ID} _add_record(): Patient {apt["mrn"]}, appointment date {apt["date"]}. Patient '
                        f'object exists. Appointment substantiated as object and added existing patient object '
                        f'appointments list.')
                    return

        new_patient = Patient(apt)
        new_patient.appointments.append(exam)
        self.patients.append(new_patient)
        log.debug(f'{RUNTIME_ID} _add_record(): Patient {apt["mrn"]}, appointment date {apt["date"]}, Patient and '
                  f'appointment substantiated as objects. Apt added to patient objects appointment list, and patient '
                  f'added to self.patients')


def main():

    # Logging
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10**107, backupCount=5)
    handler.setFormatter(formatter)

    log.addHandler(handler)

    # Testing.
    self_test()


def self_test():
    log.debug(f'{RUNTIME_ID} self_test()')

    pass

    # TODO (GS): Make self_test()


if __name__ == '__main__':

    main()
