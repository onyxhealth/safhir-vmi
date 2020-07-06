from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, IndividualIdentifier
import csv
# import random


FIRST_NAME = ["Adam", "Ben", "Colin", "Derek", "Edward", "Fred", "George", "Henry", "Ian", "John", "Kevin",
              "Larry", "Michael", "Norman", "Oliver", "Peter", "Quin", "Roger", "Steven", "Trevor", "Ulrich",
              "Victor", "William", "Xavier", "Yan", "Zen"]

LADY_NAME = ["Avril", "Britney", "Carly", "Denise", "Erica", "Franchesca", "Gabriella", "Henrietta", "Ileen",
             "July", "Karen", "Lisa", "Mellisa", "Nancy", "Ophelia", "Penny", "Quennie", "Rachel", "Sally",
             "Tammy", "Unice", "Veronica", "Wanda", "Xavier", "Yolanda", "Zara"]

LAST_NAME = ["Adamson", "Bell", "Campbell", "Drane", "Edwards", "Fox", "Garrison", "Howard", "Ingle", "Jameson",
             "Kline", "Lamb", "Marks", "North", "Overton", "Pendle", "Queen", "Rogers", "Standish", "Thompson",
             "Underwood", "Vargas", "Winston", "Xander", "Young", "Zoo"]

SEX_CHOICE = ['male', 'female']

SUB_DIVISION = ["AL", "AK",	"AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI",
                "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
                "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
                "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
                "WV", "WI", "WY"]

# Patient File mapping:
# NEW [0 = 'Member id', 1 = 'Date of birth', 2 = 'Date of death', 3 = 'County', 4 = 'State',
#  5 = 'Country', 6 = 'Zip code', 15 = 'Race code', 16 = 'Ethnicity', 17 = 'Gender code',
#  18 = 'Birth sex', 19 = 'Name']

PATIENT_RECORD_MAP = {
    "member_id": 0,
    "dob": 1,
    "dod": 2,
    "home_county": 3,
    "home_state": 4,
    "home_country": 5,
    "home_zip": 6,
    "bill_county": 7,
    "bill_state": 8,
    "bill_country": 9,
    "bill_zip": 10,
    "work_county": 11,
    "work_state": 12,
    "work_country": 13,
    "work_zip": 14,
    "race_code": 15,
    "ethnicity": 16,
    "gender": 17,
    "birth_sex": 18,
    "name": 19,
}

STATES = {"alabama": "AL",
          "alaska": "AK",
          "american samoa": "AS",
          "arizona": "AZ",
          "arkansas": "AR",
          "california": "CA",
          "colorado": "CO",
          "connecticut": "CT",
          "delaware": "DE",
          "district of columbia": "DC",
          "federated states of micronesia": "FM",
          "florida": "FL",
          "georgia": "GA",
          "guam": "GU",
          "hawaii": "HI",
          "idaho": "ID",
          "illinois": "IL",
          "indiana": "IN",
          "iowa": "IA",
          "kansas": "KS",
          "kentucky": "KY",
          "louisiana": "LA",
          "maine": "ME",
          "marshall islands": "MH",
          "maryland": "MD",
          "massachusetts": "MA",
          "michigan": "MI",
          "minnesota": "MN",
          "mississippi": "MS",
          "missouri": "MO",
          "montana": "MT",
          "nebraska": "NE",
          "nevada": "NV",
          "new hampshire": "NH",
          "new jersey": "NJ",
          "new mexico": "NM",
          "new york": "NY",
          "north carolina": "NC",
          "north dakota": "ND",
          "northern mariana islands": "MP",
          "ohio": "OH",
          "oklahoma": "OK",
          "oregon": "OR",
          "palau": "PW",
          "pennsylvania": "PA",
          "puerto rico": "PR",
          "rhode island": "RI",
          "south Carolina": "SC",
          "south dakota": "SD",
          "tennessee": "TN",
          "texas": "TX",
          "utah": "UT",
          "vermont": "VT",
          "virgin islands": "VI",
          "virginia": "VA",
          "washington": "WA",
          "west virginia": "WV",
          "wisconsin": "WI",
          "wyoming": "WY"}

class Command(BaseCommand):
    help = 'Create Sample VMI Users. Sample Syntax: create_sample_vmi_users -s 1001 -u dmnd -p du -f /home/ubuntu/patients.csv  -o /home/ubuntu/patient_list.csv -i "Diamond Health" -m /home/ubuntu/member_meta.csv 1'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')
        parser.add_argument('-s', '--start', type=int, help='starting number for userprefix + number as account name')
        parser.add_argument('-u', '--userprefix', type=str, help='Define a username prefix in lower case')
        parser.add_argument('-p', '--pwdprefix', type=str, help='Define a password prefix in lower case')
        parser.add_argument('-f', '--patientfile', type=str, help='absolute path to patient.csv file')
        parser.add_argument('-o', '--outfile', type=str, help='absolute path for output csv file')
        parser.add_argument('-m', '--metafile', type=str, help='absolute path for output csv meta file')
        parser.add_argument('-i', '--issuer', type=str, help='health plan name')



    def read_patient_csv(self, patientfile):

        with open(patientfile, 'r') as f:
            reader = csv.reader(f)
            patient_list = list(reader)
        f.close()

        return patient_list

    def write_user_account_csv(self, outfile, outlist):

        with open(outfile, 'w') as w:
            writer = csv.writer(w)
            writer.writerows(outlist)

        w.close()
        return

    def write_metadata_csv(self, metafile, metalist):

        with open(metafile, 'w') as m:
            writer = csv.writer(m)
            writer.writerows(metalist)

        m.close()
        return

    def get_state_id(self, state_name):

        if state_name.lower() in STATES:
            state = STATES[state_name.lower()]
        else:
            state = ""

        return state

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        start = kwargs['start']
        userprefix = kwargs['userprefix']
        pwdprefix = kwargs['pwdprefix']
        patientfile = kwargs['patientfile']
        outfile = kwargs['outfile']
        metafile = kwargs['metafile']
        issuer = kwargs['issuer']


        if start:
            start_from = start
        else:
            start_from = 1

        if userprefix:
            u_p = userprefix.lower()
        else:
            u_p = ""

        if pwdprefix:
            p_p = pwdprefix.lower()
        else:
            p_p = ""

        if patientfile:
            patient_list = self.read_patient_csv(patientfile)
            # override total with number of records in csv file
            total = len(patient_list) - 1
            # ['Member id', 'Date of birth', 'Date of death, 'Home_County' , 'Home_State',
            #   'Home_Country', Home_Zip code,
            #   Bill_County,Bill_State,Bill_Country,Bill_Zip code,
            #   Work_County,Work_State,Work_Country,Work_Zip code,
            #   Race code,Ethnicity,Gender code,Birth sex,Name
            # OLD ['Member id', 'Date of birth', 'Date of death', 'County', 'State',
            #  'Country', 'Race code', 'Ethnicity', 'Gender code',
            #  'Name', 'Zip code']
            # NEW [0 = 'Member id', 1 = 'Date of birth', 2 = 'Date of death', 3 = 'County', 4 = 'State',
            #  5 = 'Country', 6 = 'Zip code', 15 = 'Race code', 16 = 'Ethnicity', 17 = 'Gender code',
            #  18 = 'Birth sex', 19 = 'Name']

            #  6 = 'Race code', 7 = 'Ethnicity', 8 = 'Gender code',
            #  9 = 'Name', 10 = 'Zip code']
        else:
            patient_list = []

        if not outfile:
            outfile = patientfile
            outfile.replace(".csv", "_out.csv")

        if not metafile:
            metafile = patientfile
            metafile.replace(".csv", "_meta.csv")
            print("MetaFile: %s" % metafile)

        # writer, written_file = self.write_user_account_csv(outfile)
        outlist = []
        metalist = []
        line = ["member", "subject", "first", "last", "userid", "password"]
        outlist.append(line)

        metaline = ["memberid", "subject"]
        metalist.append(metaline)

        ct = 1

        sex = "male"
        first = ""
        last = ""

        for i in range(start_from, start_from + total):
            line = ""
            i_padded = "{0:07d}".format(i)
            password = p_p + i_padded + "!"
            # print(u_p + i_padded, password)

            if len(patient_list) > 0 and ct < len(patient_list):
                patient_record = patient_list[ct]
                if len(patient_record) > 0:
                    # Change field
                    patient_name = patient_record[PATIENT_RECORD_MAP['name']].split(" ")

                    print(ct, patient_name, u_p + i_padded)

                    got_patient = True
                    if patient_record[PATIENT_RECORD_MAP['gender']] == "M":
                        sex = "male"
                    else:
                        sex = "female"
                    dob = patient_record[PATIENT_RECORD_MAP['dob']]
                    first = patient_name[0]

                    last = patient_name[len(patient_name) - 1]

                    insurance_id = patient_record[PATIENT_RECORD_MAP['member_id']]
                    # mpi = u_p + patient_record[PATIENT_RECORD_MAP['member_id']]

                    sub_division = self.get_state_id(patient_record[PATIENT_RECORD_MAP['home_state']])

                    write_record = True
                else:
                    write_record = False
            # else:
            #     got_patient = False
            #     mod = i % 2
            #     if mod > 0:
            #         sex = SEX_CHOICE[1]
            #         first = LADY_NAME[random.randrange(25)]
            #         last = LAST_NAME[random.randrange(25)]
            #     else:
            #         sex = SEX_CHOICE[0]
            #         first = FIRST_NAME[random.randrange(25)]
            #         last = LAST_NAME[random.randrange(25)]
            #     dob = "%s-%s-%s" % (random.randrange(1935,2019),
            #                         random.randrange(1,12),
            #                         random.randrange(1,28)
            #                         )
            #     insurance_id = "%s-%s" % (u_p, i_padded)
            #     sub_division = SUB_DIVISION[random.randrange(50)]

            if write_record:

                u = User.objects.create_user(
                    username=u_p + i_padded,
                    first_name=first,
                    last_name=last,
                    email=u_p + i_padded + "@" + u_p + ".com"
                )

                u.set_password(password)
                u.is_staff = False
                u.is_superuser = False
                u.is_active = True
                u.save()

                # print(u.password)

                profile = UserProfile.objects.create(user=u)
                profile.nickname = u_p +  i_padded
                profile.sex = sex
                profile.birth_date = dob
                profile.save()


                f_identifier = IndividualIdentifier.objects.create(
                    user=u,
                    type="MPI",
                    country="US",
                    issuer=issuer,
                    subdivision=sub_division,
                    value=profile.subject,
                    name="%s-%s_MPI_for_%s_%s" % (u_p, profile.subject, u.first_name, u.last_name)
                )

                p_identifier = IndividualIdentifier.objects.create(
                    user=u,
                    type="INSURANCE_ID",
                    country="US",
                    subdivision=sub_division,
                    value=insurance_id,
                    name="%s-INSURANCE_ID_for_%s_%s" % (insurance_id, u.first_name, u.last_name)
                )
                line = [insurance_id, profile.subject, first, last, u_p + i_padded, password]
                outlist.append(line)

                metaline = [insurance_id, profile.subject]
                metalist.append(metaline)

            ct += 1


        self.write_user_account_csv(outfile, outlist)
        self.write_metadata_csv(metafile, metalist)
