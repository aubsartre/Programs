#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy
from datetime import datetime, date
import logging
from logging.handlers import RotatingFileHandler
import uuid

DATE_FORMAT = '%Y%m%d'  # eg 20210123.
LOG_FILENAME = 'core.log'  # Default filename for saving logging information for this module.
DEFAULT_LOG_LEVEL = logging.DEBUG  # Default logging level
RUNTIME_ID = uuid.uuid4()  # Sets unique id for each runtime.

# Configure logging.
log = logging.getLogger(__name__)  # Include module name.
log.setLevel(DEFAULT_LOG_LEVEL)  # Set logging recording level.


class Patient:
    """Objects of this type represent periodontal patients."""

    def __init__(self, patient_record):  # Accepts a dictionary of patient information.
        """(Initialization)

        Args:
             patient_record (dict): A record of patient details.  The following str keys are expected:
                first: Patient's first name
                last:  Patient's last name
                birthday: Patients birthday in DATE_FORMAT; eg 20011204
                sex: Patient's sex; must be "male" or "female"
        """

        self.mrn = patient_record['mrn']  # MRN is a individual health number unique to each patient.
        self.first = patient_record['first']
        self.last = patient_record['last']
        self.birthday = datetime.strptime(patient_record['birthday'], DATE_FORMAT).date()
        self.sex = patient_record['sex']
        self.appointments = []  # Appointment Objects

        log.debug(f'{RUNTIME_ID} Patient(): Patient instance instantiated {self.mrn}, {self.first} {self.last}')

    def __eq__(self, other):
        """Return True if MRN numbers match, False otherwise.

        Args:
            other (Patient): A Patient to compare with
            other (dict): A dictionary containing a 'mrn' key
            other (str): A string representation of a mrn number
        Return:
            is_equivalent (bool): True if MRN numbers match, False otherwise
        """

        if type(other) is dict:
            is_equivalent = self.mrn == other['mrn']
            log_other = '{} {}'.format(other['mrn'], other['first'], other['last'])
        elif type(other) is str:
            is_equivalent = self.mrn == other
            log_other = other  # Created for logging.
        else:
            is_equivalent = self.mrn == other.mrn
            log_other = f'{other.mrn}, {other.first} {other.last}'  # Created for logging.

        log.debug(f'{RUNTIME_ID} Patient.__eq__: Patient ({self.mrn}, {self.first} {self.last}), compared with Other '
                  f'Patient ({log_other}), equality = {is_equivalent}')
        return is_equivalent

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
        """Return a copy of a dictionary representation of this Patient excluding self.appointments.

        Args:
            None
        Return:
            record (dict): A dictionary of this object's attrs as keys, and their values
        """

        # copy.copy used so record.pop('appointments') will not change Patient object.
        record = copy.copy(self.__dict__)
        record['birthday'] = self.birthday.strftime(DATE_FORMAT)
        record.pop('appointments')

        log.debug(f'{RUNTIME_ID} Patient.to_dict(): Dictionary representation created for ({self.mrn}, {self.first} '
                  f'{self.last})')
        return record


class _Appointment:
    """(ABC) Appointments are either Appointments or Exams representing various Periodontal visit types."""

    def __init__(self, date_, asa='No ASA number.', note='No note.'):
        """(Initialization)

        Args:
            date_ (object): datetime object.
            asa (str): OPTIONAL. String representation of an mrn number.
            note (str): OPTIONAL. Appointment note.
        """

        self.date = datetime.strptime(date_, DATE_FORMAT).date()
        self.asa = asa  # range from 1 to 5. Identifies overall patient health.
        self.note = note

        log.debug(f'{RUNTIME_ID} Appointment(): Appointment instance instantiated: {self}')

    def to_dict(self):
        """Return a dictionary representation of this appointment.

        Args:
            None
        Return:
            record (dict): A dictionary of this object's attrs as keys, and their values
        """

        record = copy.copy(self.__dict__)
        record['date'] = self.date.strftime(DATE_FORMAT)
        record['_type'] = self.__class__.__name__

        log.debug(f'{RUNTIME_ID} Appointment.to_dict(): ({self})')

        return record

    def to_stats_dict(self):
        """Returns a copy of a dictionary representation of this Appointment with only the information needed for
        processing statistics.

        Args:
            None
        Return:
            record (dict): A dictionary copy of this object's attrs as keys, and their values, excluding self.note and
            self.asa.
        """

        record = copy.copy(self.to_dict())  # Copy dictionary so manipulation will not affect the instance.
        record.pop('note')
        record.pop('asa')

        log.debug(f'{RUNTIME_ID} Appointment.to_stats_dict(): ({self})')

        return record

    def __str__(self):
        return f'{self.__class__.__name__} on {self.date}'


class PeriodicExam(_Appointment):
    """Child class of Appointment."""

    # TODO (GS): say what a Periodoc exam is in the docstring

    def __init__(self, exam_dict):

        super().__init__(date_=exam_dict['date'],
                         asa=exam_dict.get('asa'),
                         note=exam_dict.get('note')
                         )

    def __eq__(self, other):
        """Return True if other is deemed equal to this PeriodicExam.

        Args:
            other (date object): A date object to compare against the date object of this class
            other (_Appointment object): True if class names match AND dates match
        Return:
            is_equivalent (bool): True if other is a date object and date objects match, or true if other is a class
            object and date objects and class name objects match, False otherwise
        """

        if type(other) is date:
            is_equivalent = self.date == other
        else:
            is_equivalent = self.date == other.date and self.__class__.__name__ == other.__class__.__name__

        return is_equivalent

    def to_dict(self):
        """Return a dictionary representation of this PeriodicExam.

        Args:
            None
        Return:
            record (dict): A dictionary representation of this object's attrs as keys, and their values
        """

        record = super().to_dict()

        return record


class LimitedExam(_Appointment):
    """Child class of Appointment."""

    # TODO (GS) say what a Limited Exam is in the docstring.

    def __init__(self, exam_dict):

        super().__init__(date_=exam_dict['date'],
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

    def __eq__(self, other):
        """Return True if other is deemed equal to this LimitedExam.

        Args:
            other (date object): A date object to compare against the date object of this class
            other (_Appointment object): True if class names match AND dates match
        Return:
            is_equivalent (bool): True if other is a date object and date objects match, or true if other is a class
            object and date objects and class name objects match, False otherwise
        """

        if type(other) is date:
            is_equivalent = self.date == other
        else:
            is_equivalent = self.date == other.date and self.__class__.__name__ == other.__class__.__name__

        return is_equivalent

    def to_dict(self):
        """Return a dictionary representation of this LimitedExam.
        Args:
            None
        Return:
            record (dict): A dictionary representation of this object's attrs as keys, and their values
            """

        record = super().to_dict()

        return record


class ComprehensiveExam(_Appointment):
    """Child class of Appointment."""
    # TODO (GS): Say what a Comprehensive Exam is
    def __init__(self, exam_dict):
        super().__init__(date_=exam_dict['date'],
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

    def __eq__(self, other):
        """Return True if other is deemed equal to this ComprehensiveExam.

        Args:
            other (date object): A date object to compare against the date object of this class
            other (_Appointment object): True if class names match AND dates match
        Return:
            is_equivalent (bool): True if other is a date object and date objects match, or true if other is a class
            object and date objects and class name objects match, False otherwise
        """

        if type(other) is date:
            is_equivalent = self.date == other
        else:
            is_equivalent = self.date == other.date and self.__class__.__name__ == other.__class__.__name__

        return is_equivalent

    def to_dict(self):
        """Return a dictionary representation of this ComprehensiveExam.
        Args:
            None
        Return:
            record (dict): A dictionary representation of this object's attrs as keys, and their values
        """

        record = super().to_dict()

        return record


class Surgery(_Appointment):
    """Child class of Appointment."""

    def __init__(self, exam_dict):

        super().__init__(date_=exam_dict['date'],
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

    def __eq__(self, other):
        """Return True if other is deemed equal to this Surgery.

        Args:
            other (date object): A date object to compare against the date object of this class
            other (_Appointment object): True if class names match AND dates match
        Return:
            is_equivalent (bool): True if other is a date object and date objects match, or true if other is a class
            object and date objects and class name objects match, False otherwise
        """

        if type(other) is date:
            is_equivalent = self.date == other
        else:
            is_equivalent = self.date == other.date and self.__class__.__name__ == other.__class__.__name__

        return is_equivalent

    def to_dict(self):
        """Return a dictionary representation of this Surgery.
        Args:
            None
        Return:
            record (dict): A dictionary representation of this object's attrs as keys, and their values
        """

        record = super().to_dict()

        return record


def main():

    # Logging.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 ** 107, backupCount=5)
    handler.setFormatter(formatter)

    log.addHandler(handler)

    # Testing.
    self_test()


def self_test():
    pass


if __name__ == '__main__':

    main()
