#!/usr/bin/python3
# -*- coding: utf-8 -*-

__version__ = '0.0.9'

import argparse
from core import Patient, LimitedExam, PeriodicExam, ComprehensiveExam, Surgery, DATE_FORMAT, RUNTIME_ID
from datetime import datetime, date
import logging
from logging.handlers import RotatingFileHandler
from storage import Repo
import sys


LOG_FILENAME = 'application.log'  # Default filename for saving logging information for this module.
DEFAULT_LOG_LEVEL = logging.DEBUG  # Default logging level.

# Configure logging.
log = logging.getLogger(__name__)  # Include module name.
log.setLevel(DEFAULT_LOG_LEVEL)  # Set logging recording level.


class Application:
    """Handles interaction between UI layer and other layers."""

    def __init__(self):
        """(Initialization) Upon startup calls Repo to populate self.patients as a list of saved patient objects.

        Args:
            None
        Return:
            None
        """

        self.repo = Repo()
        self.repo.load()
        self.patients = self.repo.patients  # List of patient objects.

        log.debug(f'({RUNTIME_ID}) Application() instantiated.')

    def add_appointment(self, apt):
        """Saves appointment information.

        Args:
            apt (dict): A dictionary containing information on patient and appointment.
        Return:
            None

        Locates existing Patient if Patient exists, or instantiate new Patient, and instantiate _Appointment.
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
            log.error(f'({RUNTIME_ID}) Could not load record due to missing _type: {apt}')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:
                    patient.appointments.append(exam)
                    log.debug(f'({RUNTIME_ID}) add_appointment(): {exam}')
                    return

        new_patient = Patient(apt)
        new_patient.appointments.append(exam)
        self.patients.append(new_patient)

        log.debug(f'({RUNTIME_ID}) add_appointment(): {exam}')

    def save(self):
        """Saves all information.

        Args:
            None
        Return:
            None

        Saves all Patient information to file.
        """

        self.repo.save(self.patients)

        log.debug(f'({RUNTIME_ID}) save()')

    def modify_patient(self, person):
        """Saves appointment information.

        Args:
            person (dict): A dictionary of patient attributes.
        Return:
            String describing changes.

        Locates existing Patient if exists or replaces Patient object with object instantiated from argument.
        """

        if type(person) != dict:
            log.error(f'({RUNTIME_ID}) modify_patient(): Argument type must be a dictionary. Current type is {type(person)}.')

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

                log.debug(f'({RUNTIME_ID}) modify_patient() has made the following changes have been made. {before} '
                          f'has been changed to {after}.')

        log.debug(f'({RUNTIME_ID}) modify_patient(): Patient not found.')

    def modify_appointment(self, apt):
        """Changes an appointments information.

        Args:
            apt (dict): A dictionary of appointment and patient attributes.
        Return:
            String describing changes.

        Locates existing _Appointment if exists or replaces _Appointment object with object instantiated from argument.
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
            log.error(f'({RUNTIME_ID}) modify_appointment(): Could not load record due to missing type: {apt}')

        if len(self.patients) > 0:
            for patient in self.patients:
                if patient == apt:

                    for appointment in patient.appointments:
                        if appointment == exam:
                            patient.appointments.remove(appointment)
                            patient.appointments.append(exam)
                            return f'{patient} appointment on {exam.date} has been updated.'

        log.error(f'({RUNTIME_ID}) modify_appointment(): Patient not found.')

    def return_patient_records(self, mrn):
        """Returns a dictionary of Patient attributes as well as a list of dictionaries containing specific
        appointment attributes.

        Args:
            mrn (str): A string containing a representation of a patients mrn number.
            mrn (int): An integer representing a patients mrn number.
        Return:
            patient_info (dict): Patient information.
            apt_records (list): List of dictionaries consisting of appointment information for patient.
        """

        log.debug(f'({RUNTIME_ID}) return_patient_records(mrn): {mrn}')

        if type(mrn) is int:  # Convert integer to string.
            mrn = str(mrn)

        if type(mrn) is not str:
            log.error(f'({RUNTIME_ID}) return_patient_records(): Argument type must be a string or integer. Current '
                      f'type is {type(mrn)}.')

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
#
        if patient_info:
            log.debug('({}) return_patient_records(): Returning records for ({}, {} {})'
                      .format(RUNTIME_ID, patient_info['mrn'], patient_info['first'], patient_info['last']))

            return patient_info, apt_records

        else:
            log.error(f'({RUNTIME_ID}) Patient not found. Check MRN.')

    def delete_apt(self, apt):
        """Deletes appointment.

        Args:
            apt (dict): Dictionary of Patient and _Appointment attributes.
        Return:
            String describing success or failure of method.
        """

        for patient in self.patients:
            if patient.mrn == apt['mrn']:

                # Make datetime.date() object for date comparison.
                date_ = datetime.strptime(apt['date'], DATE_FORMAT).date()

                for appointment in patient.appointments:
                    if appointment == date_:
                        patient.appointments.remove(appointment)
                        log.debug(f'({RUNTIME_ID}) delete_apt(): Appointment on {date_} for {patient.first.title()} '
                                  f'{patient.last.title()} has been deleted.')
                        return

        log.error(f'({RUNTIME_ID}) delete_apt({apt}): Appointment not found.')

    def delete_patient(self, p):
        """Deletes patient.

        Args:
            p (object): A patient object to be deleted.
            p (dict): A dictionary containing the mrn of the patient to be deleted.
            p (str): A string representation of the mrn for the patient to be deleted.
        Return:
            String describing success or failure of method.
        """

        for patient in self.patients:
            if patient == p:
                self.patients.remove(patient)
                log.debug(f'({RUNTIME_ID}) delete_patient(): {patient} has been deleted!')

        log.error(f'({RUNTIME_ID}) delete_patient(): {p} has NOT been deleted! The patient cannot be found!')

    def tally_stats(self, date_1=None, date_2=None):
        """Returns totals of relevant appointments information for each _Appointment subclass for all Patients.

        Args:
            date_1 (object): OPTIONAL. A date object for minimum date for range. yyyymmdd format.
            date_2 (object): OPTIONAL. A date object for maximum date in range. yyyymmdd format.
        Return:
            List of dictionaries containing procedure totals for each _Appointment subclass.
        """

        log.debug(f'({RUNTIME_ID}) tally_stats({date_1}, {date_2})')

        apts = []  # Dictionary of appointment stats for each _Appointment subclass.

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

        periodic = {'PeriodicExam': 0}
        limited = {'LimitedExam': 0}
        comprehensive = {'ComprehensiveExam': 0}
        surgery = {'Surgery': 0}

        for apt in apts:

            if apt['_type'] == 'PeriodicExam':
                periodic['PeriodicExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in periodic:
                            periodic[k] += 1
                        elif k != '_type':
                            periodic[k] = 1

            elif apt['_type'] == 'LimitedExam':
                limited['LimitedExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            limited[k] += 1
                        elif k != '_type':
                            limited[k] = 1

            elif apt['_type'] == 'ComprehensiveExam':
                comprehensive['ComprehensiveExam'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            comprehensive[k] += 1
                        elif k != '_type':
                            comprehensive[k] = 1

            elif apt['_type'] == 'Surgery':
                surgery['Surgery'] += 1
                for k, v in apt.items():
                    if v is not None:  # Eliminate procedure keys that did not happen during an appointment.
                        if k in limited:
                            surgery[k] += 1
                        elif k != '_type':
                            surgery[k] = 1

        stats = [periodic, limited, comprehensive, surgery]

        log.debug(f'({RUNTIME_ID}) tally_stats() Return: {stats}')

        return stats

    def find_patient(self, mrn):
        """Returns a patient object.

        Args:
            mrn (str): A string representation of a mrn number.
            mrn (int): An integer representation of a mrn number.
        Return:
            Patient object.
        """

        if type(mrn) is int:
            mrn = str(mrn)

        if type(mrn) is not str:
            log.error(f'({RUNTIME_ID}) find_patient({mrn}): Argument type must be a string or integer. Current type '
                      f'is {type(mrn)}.')

        for patient in self.patients:
            if patient.mrn == mrn:
                log.debug(f'({RUNTIME_ID}) find_patient({mrn}) Return: {patient}')
                return patient

        log.debug(f'({RUNTIME_ID}) find_patient({mrn}): Patient not found.')

    def today_date(self):
        """Returns a datetime object representing today's date.

        Args:
            None
        Return:
            datetime object.
        """

        log.debug(f'({RUNTIME_ID}) today_date() Return: {date.today()}')
        return date.today()


# TODO (GS): look into argv=sys.argv
def parse_args(argv=sys.argv):
    """For operating program from the terminal.

    Args:
        Dependant on request.
    Return:
        Dependant on request.
    """

    log.debug(f'({RUNTIME_ID}) parse_args()')

    parser = argparse.ArgumentParser(description='For manipulating patient records.')

    # Application.find_patient('mrn')
    parser.add_argument('-f', '--find',
                        help='Return patient information',
                        nargs=1,
                        default=False,
                        metavar='mrn'
                        )
    # Application.today_date()
    parser.add_argument('-t', '--today',
                        help='Return todays date',
                        action='store_true',
                        default=False
                        )
    # Application.tally_stats()
    parser.add_argument('-s', '--stats',
                        help='Return stats for all patients',
                        action='store_true',
                        default=False
                        )
    # Application.delete_patient('mrn')
    parser.add_argument('-dp', '--delete_patient',
                        help='Delete specified patient',
                        default=False,
                        metavar='mrn'
                        )
    # Application.delete_apt('mrn', 'birthday(yyyymmdd)')
    parser.add_argument('-da', '--delete_apt',
                        help='Deletes appointment for specified patient(mrn) & appointment date(yyyymmdd)',
                        nargs=2,
                        default=False,
                        metavar=('mrn', 'date')
                        )
    # Application.return_patient_records('mrn')
    parser.add_argument('-r', '--return_records',
                        help='Return records for patient.',
                        nargs=1,
                        default=False,
                        metavar='mrn'
                        )
    # Application.modify_patient('mrn', 'first', 'last', 'birthday(yyyymmdd)', 'sex(male/female)')
    parser.add_argument('-mp', '--modify_patient',
                        help='Modify patient record for with inputted information. Birthday must be yyyymmdd, sex must '
                             'be male/female.',
                        nargs=5,
                        default=False,
                        metavar=('mrn', 'first', 'last', 'birthday', 'sex')
                        )
    # Application.add_appointment('mrn', '_type', 'DATE:yyyymmdd', 'optional attributes specific to appointment types')
    parser.add_argument('-a', '--add_appointment',
                        help='Add appointment. Requires patient mrn, appointment date, appointment type, '
                             'followed by appointment attributes. If appointment note is included it must start with '
                             '(NOTE:), and each word in the note must be separated with a ( - ) rather than a space. '
                             'If asa is included the asa number must be immediately preceded by (ASA:). Example(ASA:5).'
                             'Required attributes for every appointment: MRN, Type(PeriodicExam, ComprehensiveExam, '
                             'LimitedExam, Surgery), Appointment Date(DATE:yyyymmdd). Appointment date must be '
                             'immediatly preceded by (DATE:). Optional attributes are specific to each appointment '
                             'type: PeriodicExam(asa, note), LimitedExam(asa, note, abscess, crown_lengthening, '
                             'cv_exam, extraction, frenectomy, fracture, implant, oral_path, periodontitis, '
                             'peri_implantitis, postop, return_, recession, re_evaluation, miscellaneous.) '
                             'ComprehensiveExam(asa, note, periodontitis, executive_health, recession, hygiene, '
                             'return_, oncology, implant, oral_path), Surgery(asa, note, biopsy, extractions, '
                             'uncovery, implant, crown_lengthening, soft_tissue, perio, miscellaneous, sinus, '
                             'peri_implantitis). Input example (mrn, apt_attribute1, apt_attribute2, apt_attribute3, '
                             'this-is-the-apt-note).',
                        default=False,

                        # All cmd arguments will be collected into a list. Error message will be gathered if there is
                        # not at least one argument.
                        nargs='+',
                        metavar=('mrn', 'date type')
                        )
    # Application.modify_appointment('mrn', '_type', 'DATE:yyyymmdd', 'optional attributes specific to appointment
    # types')
    parser.add_argument('-m', '--modify_appointment',
                        help='Modify appointment. Will replace any existing appointment with given appointment.'
                             'Specific formatting instructions are the same as --add_appointment. Input example '
                             '(mrn, apt_attribute1, apt_attribute2, apt_attribute3, this-is-the-apt-note).',
                        default=False,

                        # All cmd arguments will be collected into a list. Error message will be gathered if there is
                        # not at least one argument.
                        nargs='+',
                        metavar=('mrn', 'date type')
                        )

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'({RUNTIME_ID}) parse_args() Return: {args}')
    return args


def _add_mod_apt(instance, args):
    """Helper function for main when taking inputs from the terminal and need to add or modify an appointment.

    Args:
        args (List): A list of arguments from the terminal argument parser.
    Return:
        return_dict (Dictionary): Dictionary of patient and appointment attributes for the new or modified appointment.

    With argument mrn constructs a dictionary of patient attributes and combines that with a dictionary of
    appointment attributes.
    """

    log.debug(f'({RUNTIME_ID}) _add_mod_apt({instance}, {args})')

    mrn = args[0]

    if not mrn.isdecimal():
        log.error(f'({RUNTIME_ID}) mrn must be all numerical digits. Provided mrn: {mrn}')
        return

    patient = Application.find_patient(instance, mrn)  # Get patient object with mrn.
    patient_dict = {
        'mrn': patient.mrn,
        'first': patient.first,
        'last': patient.last,
        'birthday': patient.birthday.strftime(DATE_FORMAT),
        'sex': patient.sex
    }

    apt_dict = {}
    apt_args = args[1:]

    # Deal with possible patient note. A note must be preceded with 'NOTE:', and each word must be separated with
    # '-' rather than ' '.
    note = None
    for attribute in apt_args:
        if attribute[:5] == 'NOTE:':
            note = attribute[5:]  # Remove NOTE:
            note = note.replace('-', ' ')
            apt_dict['note'] = note
            apt_args.remove(attribute)
            continue

    # Deal with possible patient asa.
    asa = None
    for attribute in apt_args:
        if attribute[:5] == 'ASA:'.lower():
            asa = attribute[5:]  # Remove asa:
            apt_dict['asa'] = asa
            apt_args.remove(attribute)
            continue

    # Deal with appointment date.
    date_ = None
    for attribute in apt_args:
        if attribute[:5] == 'DATE:':
            date_ = attribute[5:]
            apt_dict['date'] = date_
            apt_args.remove(attribute)
            continue
    if date_ is None:
        log.error(f'({RUNTIME_ID}) Appointment date must be included.')
        return

    # Deal with appointment type.
    apt_dict['_type'] = None
    for attribute in apt_args:
        if attribute == 'PeriodicExam':
            apt_dict['_type'] = 'PeriodicExam'
            apt_args.remove(attribute)
            continue
        elif attribute == 'LimitedExam':
            apt_dict['_type'] = 'LimitedExam'
            apt_args.remove(attribute)
            continue
        elif attribute == 'ComprehensiveExam':
            apt_dict['_type'] = 'ComprehensiveExam'
            apt_args.remove(attribute)
            continue
        elif attribute == 'Surgery':
            apt_dict['_type'] = 'Surgery'
            apt_args.remove(attribute)
            continue
    if apt_dict['_type'] is None:
        log.error(f'({RUNTIME_ID}) Appointment type must be included.')
        return

    # Populate the rest of apt_dict with remaining attributes.
    for attribute in apt_args:
        apt_dict[attribute] = True

    return_dict = {**patient_dict, **apt_dict}

    log.debug(f'({RUNTIME_ID}) _add_mod_apt() Return: {return_dict}')
    return return_dict


def main():
    # Initialize logging.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 ** 107, backupCount=5)
    handler.setFormatter(formatter)

    log.addHandler(handler)
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')

    log.debug(f'({RUNTIME_ID}) main()')

    # Following 12ish lines of code and following if/else statement determine if program should execute inputs or run
    # self testing.
    # Check parse_args() for program inputs from cmd.
    args = parse_args()

    run_args = False  # Changed to True when input is found.
    arguments = args.__dict__
    for k, v in arguments.items():
        if v is not False:
            run_args = True
            continue

    # Check for possible inputs from cmd.
    # True only when inputs received from cmd.
    if run_args is True:

        log.debug(f'({RUNTIME_ID}) main() determined that program IS being run from cmd')

        app = Application()

        # Application.find_patient('mrn')
        if args.find:
            print(app.find_patient(args.find[0]))

        # Application.today_date()
        elif args.today:
            print(app.today_date())

        # Application.tally_stats()
        elif args.stats:
            print(app.tally_stats())

        # Application.delete_patient('mrn')
        elif args.delete_patient:
            print(app.delete_patient(args.delete_patient))

        # Application.delete_apt('mrn', 'birthday(yyyymmdd)')
        elif args.delete_apt:
            x = {'mrn': args.delete_apt[0], 'date': args.delete_apt[1]}
            print(app.delete_apt(x))

        # Application.return_patient_records('mrn')
        elif args.return_records:
            print(app.return_patient_records(args.return_records[0]))

        # Application.modify_patient('mrn', 'first', 'last', 'birthday(yyyymmdd)', 'sex(male/female)')
        elif args.modify_patient:
            patient = {
                'mrn': args.modify_patient[0],
                'first': args.modify_patient[1],
                'last': args.modify_patient[2],
                'birthday': args.modify_patient[3],
                'sex': args.modify_patient[4]
                }
            print(app.modify_patient(patient))

        # Application.add_appointment(dict{patient & appointment attributes})
        elif args.add_appointment:
            arguments = args.add_appointment
            appointment = _add_mod_apt(app, arguments)  # takes instance and appointment attributes.
            app.add_appointment(appointment)

        # Application.modify_appointment(dict{patient & appointment attributes})
        elif args.modify_appointment:
            arguments = args.modify_appointment
            appointment = _add_mod_apt(app, arguments)  # takes instance and appointment attributes.
            app.modify_appointment(appointment)

        # Used when no optional argument is provided.
        else:
            log.error(f'({RUNTIME_ID}) At least one optional argument is required. Use -h to access help menu.')

        app.save()

    # TODO (GS): find something useful for else
    else:
        log.debug(f'({RUNTIME_ID}) main(): Determined that program is NOT being run from cmd')

        self_test()


def self_test():
    log.debug(f'({RUNTIME_ID}) test()')
    app = Application()
    # run tests below

    x = {
        '_type': 'Surgery',
        'asa': '2',
        'birthday': '19830303',
        'first': 'tom',
        'last': 'wagar',
        'mrn': '222',
        'sex': 'male',
        'biopsy': 'True',
        'implant': 'True',
        'sinus': 'True',
        'note': 'Another Test',
        'date': '20210909'
    }

    # app.add_appointment(x)
    # print(app.return_patient_records(111))


    app.return_patient_records(111)

    app.save()


if __name__ == '__main__':

    main()
