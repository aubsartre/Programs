#!/usr/bin/python3
# -*- coding: utf-8 -*-

__version__ = '0.0.6'

from datetime import datetime, date
import yaml

DATE_FORMAT = '%Y%m%d'  # eg 20210123


class Patient:
    """Represents a patient who is receiving periodontic treatment.

    Accepts a dictionary of strings as an argument and builds a patient object containing relevant information for a
    patient receiving this type of treatment.

    - self.mrn (MRM) is an individualized unique health assigned to each patient upon first arrival at the clinic.
        Program does not need to handle generating or changing MRN numbers.
    - self.first = First name
    - self.last = Last name
    - self.birthday = Birthday. Always represented as yyyymmdd.
    - self.sex = Sex. Always represented in long-form as male/female.
    - self.appointments = List of appointment objects handled by the Appointment class."""

    def __init__(self, patient_record):  # Accepts a dictionary of patient information.
        self.mrn = patient_record['mrn']  # MRN is a individual health number unique to each patient.
        self.first = patient_record['first']
        self.last = patient_record['last']
        # Convert the birthday string to a datetime object representing birthday.
        self.birthday = datetime.strptime(patient_record['birthday'], DATE_FORMAT).date()
        self.sex = patient_record['sex']
        self.appointments = []  # Appointment Objects.

    def __eq__(self, other):
        """Patients are determined to be equal if their MRN numbers match.

        Can accept as argument:
            - Dictionary (compares key['mrn'] to Patient object MRN).
            - String representing an MRN.
            - Patient object."""

        if type(other) is dict:
            return self.mrn == other['mrn']
        elif type(other) is str:
            return self.mrn == other
        else:
            return self.mrn == other.mrn

    def __repr__(self):

        # repr_ variable created to eliminate '\' from return string.
        repr_ = f'Patient(dict(mrn: {self.mrn}, first: {self.first.title()}, last: {self.last.title()}, ' \
               f'birthday: {self.birthday}, sex: {self.sex})'

        return repr_

    def __str__(self):

        # str_ variable created to eliminate '\' from return string.
        str_ = f'Patient: {self.first.title()} {self.last.title()}, MRN: {self.mrn}, {self.sex.title()}, ' \
               f'Birthday: {self.birthday}'

        return str_

    def to_dict(self):
        """Return a dictionary representation of a patient excluding self.appointments."""

        record = {
            'mrn': self.mrn,
            'first': self.first,
            'last': self.last,
            'birthday': self.birthday.strftime(DATE_FORMAT),
            'sex': self.sex,
        }

        return record


class _Appointment:
    """(ABC) Appointments are either Appointments or Exams representing various Periodontal visit types.

    - self.date = Appointment date.
    - self.asa = asa represents a number from 1 - 5 indicating the general health of a patient. Assigned during
        appointment.
    - self.note = Note created by Periodontist to summarize the appointment."""

    def __init__(self, date, asa='No ASA number.', note='No note.'):
        self.date = datetime.strptime(date, DATE_FORMAT).date()
        self.asa = asa  # range from 1 to 5. Identifies overall patient health.
        self.note = note

    def to_dict(self):
        """Return a dictionary representation of _Appointment."""

        record = {
            'date': self.date.strftime(DATE_FORMAT),
            'asa': self.asa,
            'note': self.note,
        }

        return record


class PeriodicExam(_Appointment):
    """Child class of Appointment."""
    # TODO (GS): say what a Periodoc exam is in the docstring

    def __init__(self, exam_dict):

        super().__init__(date=exam_dict['date'],
                         asa=exam_dict.get('asa'),
                         note=exam_dict.get('note')
                         )

    def __str__(self):
        return f'Periodic Exam on {self.date}'

    def __eq__(self, other):
        """If other is an appointment object returns True if dates and class name are the same. If other is a date
        object returns true if date is the same as self.date."""

        if type(other) is date:
            return self.date == other

        return self.date == other.date and self.__class__.__name__ == other.__class__.__name__

    def to_dict(self):
        """Returns a dictionary representation of a Periodic Exam.

        Adds key/value 'appointment_type': 'PeriodicExam' for use in saving and loading."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'asa': super().to_dict()['asa'],
            'note': super().to_dict()['note']
        }

        return record

    def to_stats_dict(self):
        """Returns a dictionary representation of a Periodic Exam with the information needed for processing
        statistics.

        - Adds key/value 'appointment_type': 'PeriodicExam' for use in saving and loading.
        - Leaves out self.notes and self.asa."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
        }

        return record


class LimitedExam(_Appointment):
    """Child class of Appointment."""
    # TODO (GS) say what a Limited Exam is in the docstring.

    def __init__(self, exam_dict):

        super().__init__(date=exam_dict['date'],
                         asa=exam_dict.get('asa'),
                         note=exam_dict.get('note')
                         )

        self.abscess = exam_dict.get('abscess')
        self.crown_lengthening = exam_dict.get('crown_lengthening')
        self.cv_exam = exam_dict.get('cv_exam')
        self.extraction = exam_dict.get('extraction')
        self.frenectomy = exam_dict.get('frenectomy')
        self.fracture = exam_dict.get('fracture')
        self.implant = exam_dict.get('implant')
        self.oral_path = exam_dict.get('oral_path')
        self.periodontitis = exam_dict.get('periodontitis')
        self.peri_implantitis = exam_dict.get('peri_implantitis')
        self.postop = exam_dict.get('postop')
        self.return_ = exam_dict.get('return_')
        self.recession = exam_dict.get('recession')
        self.re_evaluation = exam_dict.get('re_evaluation')
        self.miscellaneous = exam_dict.get('miscellaneous')

    def __str__(self):
        return f'Limited Exam on {self.date}'

    def __eq__(self, other):
        """If other is an appointment object returns True if dates and class name are the same. If other is a date
        object returns true if date is the same as self.date."""

        if type(other) is date:
            return self.date == other

        return self.date == other.date and self.__class__.__name__ == other.__class__.__name__

    def to_dict(self):
        """Returns a dictionary representation of a Limited Exam.

        Adds key/value 'appointment_type': 'LimitedExam' for use in saving and loading."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'asa': super().to_dict()['asa'],
            'note': super().to_dict()['note'],
            'abscess': self.abscess,
            'crown_lengthening': self.crown_lengthening,
            'cv_exam': self.cv_exam,
            'extraction': self.extraction,
            'frenectomy': self.frenectomy,
            'fracture': self.fracture,
            'implant': self.implant,
            'oral_path': self.oral_path,
            'periodontitis': self.periodontitis,
            'peri_implantitis': self.peri_implantitis,
            'postop': self.postop,
            'return_': self.return_,
            'recession': self.recession,
            're_evaluation': self.re_evaluation,
            'miscellaneous': self.miscellaneous
        }

        return record

    def to_stats_dict(self):
        """Returns a dictionary representation of a Limited Exam with the information needed for processing
        statistics.

        - Adds key/value 'appointment_type': 'LimitedExam' for use in saving and loading.
        - Leaves out self.notes and self.asa."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'abscess': self.abscess,
            'crown_lengthening': self.crown_lengthening,
            'cv_exam': self.cv_exam,
            'extraction': self.extraction,
            'frenectomy': self.frenectomy,
            'fracture': self.fracture,
            'implant': self.implant,
            'oral_path': self.oral_path,
            'periodontitis': self.periodontitis,
            'peri_implantitis': self.peri_implantitis,
            'postop': self.postop,
            'return_': self.return_,
            'recession': self.recession,
            're_evaluation': self.re_evaluation,
        }

        return record


class ComprehensiveExam(_Appointment):
    """Child class of Appointment."""

    def __init__(self, exam_dict):
        super().__init__(date=exam_dict['date'],
                         asa=exam_dict.get('asa'),
                         note=exam_dict.get('note')
                         )

        self.periodontitis = exam_dict.get('periodontitis')
        self.executive_health = exam_dict.get('executive_health')
        self.recession = exam_dict.get('recession')
        self.hygiene = exam_dict.get('hygiene')
        self.return_ = exam_dict.get('return_')
        self.oncology = exam_dict.get('oncology')
        self.implant = exam_dict.get('implant')
        self.oral_path = exam_dict.get('oral_path')

    def __str__(self):
        return f'Comprehensive Exam on {self.date}'

    def __eq__(self, other):
        """If other is an appointment object returns True if dates and class name are the same. If other is a date
        object returns true if date is the same as self.date."""

        if type(other) is date:
            return self.date == other

        return self.date == other.date and self.__class__.__name__ == other.__class__.__name__

    def to_dict(self):
        """Returns a dictionary representation of a Limited Exam.

        Adds key/value 'appointment_type': 'ComprehensiveExam' for use in saving and loading."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'asa': super().to_dict()['asa'],
            'note': super().to_dict()['note'],
            'periodontitis': self.periodontitis,
            'executive_health': self.executive_health,
            'recession': self.recession,
            'hygiene': self.hygiene,
            'return_': self.return_,
            'oncology': self.oncology,
            'implant': self.implant,
            'oral_path': self.oral_path,
        }

        return record

    def to_stats_dict(self):
        """Returns a dictionary representation of a Comprehensive Exam with the information needed for processing
        statistics.

        - Adds key/value 'appointment_type': 'ComprehensiveExam' for use in saving and loading.
        - Leaves out self.notes and self.asa."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'periodontitis': self.periodontitis,
            'executive_health': self.executive_health,
            'recession': self.recession,
            'hygiene': self.hygiene,
            'return_': self.return_,
            'oncology': self.oncology,
            'implant': self.implant,
            'oral_path': self.oral_path,
        }

        return record


class Surgery(_Appointment):
    """Child class of Appointment."""

    def __init__(self, exam_dict):

        super().__init__(date=exam_dict['date'],
                         asa=exam_dict.get('asa'),
                         note=exam_dict.get('note')
                         )

        self.biopsy = exam_dict.get('biopsy')
        self.extractions = exam_dict.get('extractions')
        self.uncovery = exam_dict.get('uncovery')
        self.implant = exam_dict.get('implant')
        self.crown_lengthening = exam_dict.get('crown_lengthening')
        self.soft_tissue = exam_dict.get('soft_tissue')
        self.perio = exam_dict.get('perio')
        self.miscellaneous = exam_dict.get('miscellaneous')
        self.sinus = exam_dict.get('sinus')
        self.peri_implantitis = exam_dict.get('peri_implantitis')

    def __str__(self):
        return f'Surgery on {self.date}'

    def __eq__(self, other):
        """If other is an appointment object returns True if dates and class name are the same. If other is a date
        object returns true if date is the same as self.date."""

        if type(other) is date:
            return self.date == other

        return self.date == other.date and self.__class__.__name__ == other.__class__.__name__

    def to_dict(self):
        """Returns a dictionary representation of a Limited Exam.

        Adds key/value 'appointment_type': 'Surgery' for use in saving and loading."""

        exam = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'asa': super().to_dict()['asa'],
            'note': super().to_dict()['note'],
            'biopsy': self.biopsy,
            'extractions': self.extractions,
            'uncovery': self.uncovery,
            'implant': self.implant,
            'crown_lengthening': self.crown_lengthening,
            'soft_tissue': self.soft_tissue,
            'perio': self.perio,
            'miscellaneous': self.miscellaneous,
            'sinus': self.sinus,
            'peri_implantitis': self.peri_implantitis
        }

        return exam

    def to_stats_dict(self):
        """Returns a dictionary representation of a Surgery appointment the information needed for processing
        statistics.

        - Adds key/value 'appointment_type': 'Surgery' for use in saving and loading.
        - Leaves out self.notes and self.asa."""

        record = {
            'type': self.__class__.__name__,
            'date': super().to_dict()['date'],
            'biopsy': self.biopsy,
            'extractions': self.extractions,
            'uncovery': self.uncovery,
            'implant': self.implant,
            'crown_lengthening': self.crown_lengthening,
            'soft_tissue': self.soft_tissue,
            'perio': self.perio,
            'miscellaneous': self.miscellaneous,
            'sinus': self.sinus,
            'peri_implantitis': self.peri_implantitis
        }

        return record


class Repo:
    """Handles loading and saving information.

    self.load() - Upon self.load(), populates self.patients as a list of patients objects and corresponding appointment
        objects. self.patients is the way loaded information is passed to upper layers.
    self.save() = Accepts a list of patient objects and stores that information to an external file."""

    # TODO (GS): remove 'records-v6.yaml'
    def __init__(self, records_path='records-v6.yaml'):
        self.records_path = records_path
        self.patients = []  # List of all patients as objects.

    def load(self):
        """Populates self.patients as a list of patients objects and corresponding appointment objects."""

        # records is a dictionary representing all patient appointments, and includes patient and appointment data.
        records = self._get_from_yaml()
        self._load_obj(records)

    def _load_obj(self, records):
        # Passes each patient record (as a dictionary) to self.new_record() where it will become a Patient object with
        # Patient.appointments populated with appropriate Appointment objects.
        for record in records:
            self._add_record(record)

    def _get_from_yaml(self):
        # Retrieves dictionary representations of patient and appointment information from a .yaml file.
        raw_records = []
        with open('records-v6.yaml', 'r') as infile:
            records = yaml.full_load(infile)
            for record in records:
                raw_records.append(record)
        return raw_records

    def save(self, patients):
        """Saves patient objects to external file.

        Accepts a list of patient objects."""

        records = []  # Is a list.

        for patient in patients:
            patient_info = patient.to_dict()
            for appointment in patient.appointments:
                appointment_info = appointment.to_dict()
                record = {**patient_info, **appointment_info}
                records.append(record)

        with open('records-save-test-v6.yaml', 'w') as yaml_outfile:
            yaml.dump(records, yaml_outfile)

    def _add_record(self, apt):
        """Takes a dictionary containing patient and appointment information and adds that information to the
        self.patient_obj_lst."""

        if apt['type'] == 'PeriodicExam':
            exam = PeriodicExam(apt)
        elif apt['type'] == 'LimitedExam':
            exam = LimitedExam(apt)
        elif apt['type'] == 'ComprehensiveExam':
            exam = ComprehensiveExam(apt)
        elif apt['type'] == 'Surgery':
            exam = Surgery(apt)
        else:
            raise ValueError(f'Could not load record due to missing type: {apt}')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:
                    patient.appointments.append(exam)
                    return

        new_patient = Patient(apt)
        new_patient.appointments.append(exam)
        self.patients.append(new_patient)


class Application:
    """Handles interaction between UI layer and Objects."""

    def __init__(self):
        self.repo = Repo()
        self.repo.load()
        self.patients = self.repo.patients  # List of patient objects.

    def add_appointment(self, apt):
        """Takes a dictionary containing patient and appointment information and adds that information to the
        self.patient."""

        if apt['type'] == 'PeriodicExam':
            exam = PeriodicExam(apt)
        elif apt['type'] == 'LimitedExam':
            exam = LimitedExam(apt)
        elif apt['type'] == 'ComprehensiveExam':
            exam = ComprehensiveExam(apt)
        elif apt['type'] == 'Surgery':
            exam = Surgery(apt)
        else:
            raise ValueError(f'Could not load record due to missing type: {apt}')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:
                    patient.appointments.append(exam)
                    return

        new_patient = Patient(apt)
        new_patient.appointments.append(exam)
        self.patients.append(new_patient)

    def save(self):
        """Uses Repo to save all stored information."""

        self.repo.save(self.patients)

    def modify_patient(self, person):
        """Accepts a dictionary of patient attributes. Finds and replaces patient object with matching MRN Number."""

        if type(person) != dict:
            raise ValueError(f'Argument type must be a dictionary. Current type is {type(person)}.')

    # TODO (GS): simplify this method so it is easier to understand.

        for patient in self.patients:
            if patient == person:
                original = patient.to_dict()

                before = {}
                after = {}

                for k, v in original.items():
                    if v != person[k]:
                        before[k] = v
                        after[k] = person[k]

                appointments = patient.appointments
                person = Patient(person)
                for appointment in appointments:
                    person.appointments.append(appointment)

                self.patients.remove(patient)
                self.patients.append(person)

                return f'The following changes have been make. {before} has been changed to {after}.'

        return 'Patient not found.'

    def modify_appointment(self, apt):
        """Accepts a dictionary of appointment and patient attributes and replaces appointment object attributes with
        argument attributes.

        Finds Patient by comparing MRN numbers, then finds Appointment by comparing dates. Creates new Appointment
        object from argument, and replaces existing Appointment object."""

        if apt['type'] == 'PeriodicExam':
            exam = PeriodicExam(apt)
        elif apt['type'] == 'LimitedExam':
            exam = LimitedExam(apt)
        elif apt['type'] == 'ComprehensiveExam':
            exam = ComprehensiveExam(apt)
        elif apt['type'] == 'Surgery':
            exam = Surgery(apt)
        else:
            raise ValueError(f'Could not load record due to missing type: {apt}')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:

                    for appointment in patient.appointments:
                        if appointment == exam:
                            patient.appointments.remove(appointment)
                            patient.appointments.append(exam)
                            return f'{patient} appointment on {exam.date} has been updated.'

        return 'Patient not found.'

    def return_patient_records(self, mrn):
        """Presents patient appointment records in date order starting with mose recent.

        Accepts a patient MRN as a string or integer and displays the appropriate patient records information if
        possible. Returns a dictionary of patient information and a list of dictionaries containing appointment
        information."""

        if type(mrn) is int:
            mrn = str(mrn)

        if type(mrn) is not str:
            raise ValueError(f'Argument type must be a string or integer. Current type is {type(mrn)}.')

        patient_info = None
        apt_records = []

        # Determine if patient exists.
        for patient in self.patients:
            if patient == mrn:
                patient_info = patient.to_dict()

                # Compile patient records.
                for record in patient.appointments:
                    apt_records.append(record.to_dict())

                # Sort patient records by date starting with most recent.
                if len(apt_records) > 1:
                    apt_records.sort(key=lambda x: x['date'], reverse=True)
                break

        if patient_info:
            return patient_info, apt_records

        else:
            return 'Patient not found. Check MRN.'

    def delete_apt(self, apt):
        """Finds appropriate patient appointment and removes it from records.

        Accepts an appointment dictionary including patient and appointment information, and deletes an appointment
        of the patients that has the same date as found in the argument."""

        for patient in self.patients:
            if patient.mrn == apt['mrn']:

                # Make datetime.date() object for date comparison.
                date_ = datetime.strptime(apt['date'], DATE_FORMAT).date()

                for appointment in patient.appointments:
                    if appointment == date_:
                        patient.appointments.remove(appointment)
                        return f'Appointment on {date_} for {patient.first.title()} {patient.last.title()} has been ' \
                               f'deleted.'

        return f'Appointment on not found.'

    def delete_patient(self, p):
        """Deletes patient.

        Argument p can be a Patient Object, a dictionary containing a key/value for MRN, or a string of the MRN."""

        for patient in self.patients:
            if patient == p:
                self.patients.remove(patient)
                return f'{patient} has been deleted!'

        return f'{p} has NOT been deleted! The patient cannot be found!'

    def tally_stats(self, date_1=None, date_2=None):
        """Returns a list of dictionaries containing statistics for each procedure performed within each Appointment
        Type.

        Will return all available stats if date arguments are not provided. Will return stats between date_1 (min date)
        and date_2 (max date), if both date arguments are provided. Accepts date range arguments as strings in
        yyyymmdd format."""

        apts = []

        # Executes when both date arguments are provided.
        if date_1 and date_2:

            # If dates are type integer, convert to type string.
            if type(date_1) is int:
                date_1 = str(date_1)
            if type(date_2) is int:
                date_2 = str(date_2)

            # Convert dates to datetime objects.
            if type(date_1) is str:
                date_1 = datetime.strptime(date_1, DATE_FORMAT).date()
            if type(date_2) is str:
                date_2 = datetime.strptime(date_2, DATE_FORMAT).date()

            for patient in self.patients:
                for appointment in patient.appointments:
                    if date_1 < appointment.date < date_2:  # Isolate dates within argument date ranges.
                        apts.append(appointment.to_stats_dict())

        # Executes when date arguments are not provided.
        else:
            for patient in self.patients:
                for appointment in patient.appointments:
                    apts.append(appointment.to_stats_dict())

        # TODO (GS): reduce abstraction leak within this method.

        periodic = {'PeriodicExam': 0}
        limited = {'LimitedExam': 0}
        comprehensive = {'ComprehensiveExam': 0}
        surgery = {'Surgery': 0}

        for apt in apts:

            if apt['type'] == 'PeriodicExam':
                periodic['PeriodicExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in periodic:
                            periodic[k] += 1
                        elif k != 'type':
                            periodic[k] = 1

            elif apt['type'] == 'LimitedExam':
                limited['LimitedExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            limited[k] += 1
                        elif k != 'type':
                            limited[k] = 1

            elif apt['type'] == 'ComprehensiveExam':
                comprehensive['ComprehensiveExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            comprehensive[k] += 1
                        elif k != 'type':
                            comprehensive[k] = 1

            elif apt['type'] == 'Surgery':
                surgery['Surgery'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            surgery[k] += 1
                        elif k != 'type':
                            surgery[k] = 1

        stats = [periodic, limited, comprehensive, surgery]

        return stats

    def find_patient(self, mrn):
        """Retrieves a patient object based on the input mrn number.

        Accepts the MRN number as either a string or integer."""

        if type(mrn) is int:
            mrn = str(mrn)

        if type(mrn) is not str:
            raise ValueError(f'Argument type must be a string or integer. Current type is {type(mrn)}.')

        for patient in self.patients:
            if patient.mrn == mrn:
                return patient

        return 'Patient not found.'

    def today_date(self):
        """Returns today's date as an object."""

        return date.today()

    # TODO (GS): ADD function to return total number of a patients visits.


def test():
    app = Application()
    # run tests below

    d = {
    'type': 'PeriodicExam',
    'asa': '3',
    'birthday': '19850101',
    'date': '20210707',
    'first': 'shayla',
    'mrn': '111',
    'last': 'schaefer',
    'note': 'Is this different.',
    'sex': 'male'
    }

    print(app.tally_stats(20000303, 20220404))


def main():
    test()


if __name__ == '__main__':
    main()
