import re
from collections import UserDict
import datetime
import json


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value  

    def _validate_value(self, value):
        pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._validate_value(new_value)
        self._value = new_value

    def __str__(self):
        return str(self._value)


class Name(Field):
    pass


class Phone(Field):
    def _validate_value(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number")
        super()._validate_value(value)


class Birthday(Field):
    def _validate_value(self, value):
        if not re.match(r'\d{4}-\d{2}-\d{2}', value):
            raise ValueError("Invalid date format, please use YYYY-MM-DD")
        super()._validate_value(value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.birthday = Birthday(birthday)

    def set_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday.value = birthday

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.date.today()
            birthday_components = self.birthday.value.split("-")
            birth_year = int(birthday_components[0])
            birth_month = int(birthday_components[1])
            birth_day = int(birthday_components[2])

            next_birthday = datetime.date(today.year, birth_month, birth_day)
            if today > next_birthday:
                next_birthday = datetime.date(today.year + 1, birth_month, birth_day)

            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found")

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p.value) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            return None

    def iterator(self, n=1):
        for i in range(0, len(self.data), n):
            yield list(self.data.values())[i:i + n]
    def save_to_file(self, filename):
            with open(filename, "w") as file:
                json.dump([record.to_dict() for record in self.data.values()], file)
    
    def load_from_file(self, filename):
        with open(filename, "r") as file:
            data = json.load(file)
            for entry in data:
                record = Record(entry["name"], entry["birthday"])
                for phone in entry["phones"]:
                    record.add_phone(phone)
                self.add_record(record)

    def search(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record._name.value.lower() or any(query.lower() in p.value.lower() for p in record._phones):
                results.append(record)
        return results