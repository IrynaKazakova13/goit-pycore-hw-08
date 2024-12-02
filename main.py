from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


class Field:  # Базовий клас для полів запису.
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):  # Клас для зберігання імені контакту. Обов'язкове поле
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):  # Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
    # Реалізовано валідацію номера телефону (має бути перевірка на 10 цифр).
    # Наслідує клас Field. Значення зберігaється в полі value .

    def __init__(self, value):
        if not len(value) == 10 or not value.isdigit():
            raise ValueError
        super().__init__(value)


class Birthday(Field):  # наслідується від класу Field. Значення зберігається в полі value. Тип - рядок формата DD.MM.YYYY.
    def __init__(self, value):
        try:
            # Додано перевірку коректності даних. Дата народження має бути у форматі DD.MM.YYYY. перетворіть рядок на об'єкт datetime
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:  # Клас для зберігання інформації про контакт.

    # Реалізовано зберігання об'єкта Name в атрибуті name.
    # Реалізовано зберігання списку об'єктів Phone в атрибуті phones.
    # Реалізовано поле birthday для дня народження, має бути класу Birthday, не обов'язкове, але може бути тільки одне.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Реалізовано метод для додавання дати народження до контакту
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        # print(f'Birthday date {birthday} added to the contact of {self.name}')

    # Реалізовано метод для додавання - add_phone
    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        # print(f'Phone {phone} added to the contact of {self.name}')

    # Реалізовано метод для видалення - remove_phone.
    def remove_phone(self, phone: str):
        if phone in [p.value for p in self.phones]:
            for p in self.phones:
                if p.value == phone:
                    self.phones.remove(p)
                    # print(f'Phone number {phone} for the contact of {self.name} successfully removed')
        else:
            print(f"Phone number {phone} for the contact of {self.name} not identified")

    # Реалізовано метод для редагування - edit_phone.
    def edit_phone(self, phone: str, new_phone: str):
        if phone in [p.value for p in self.phones]:
            for p in self.phones:
                if p.value == phone:
                    if not len(new_phone) == 10 or not new_phone.isdigit():
                        raise ValueError
                    else:
                        p.value = new_phone
                    # print(f'Phone number {phone} for the contact of {self.name} changed into {new_phone}')
        else:
            raise ValueError

    # Реалізовано метод для пошуку об'єктів Phone - find_phone.
    def find_phone(self, phone: str):
        if phone in [p.value for p in self.phones]:
            for p in self.phones:
                if p.value == phone:
                    return p
                    # print(f'Phone number {phone} found in the Contact of {self.name}')

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {str(self.birthday)}"


class AddressBook(UserDict):  # Клас для зберігання та управління записами.

    # Реалізовано метод add_record, який додає запис до self.data.
    def add_record(self, record):
        self.data[record.name.value] = record

    # Реалізовано метод find, який знаходить запис за ім'ям.
    def find(self, name: str):
        return self.data.get(name)

    # Реалізовано метод delete, який видаляє запис за ім'ям.
    def delete(self, name: str):
        del self.data[name]

    # Реалізовано метод get_upcoming_birthdays, який визначає контакти, у яких день народження припадає вперед на 7 днів включаючи поточний день.
    # Метод має повертати список словників. Кожен словник містить два значення - ім’я з ключем "name", та дата привітання з ключем "birthday”

    def string_to_date(self, date_string):
        return datetime.strptime(date_string, "%d.%m.%Y").date()

    def date_to_string(self, date):
        return date.strftime("%d.%m.%Y")

    def prepare_user_list(self, user_data):
        prepared_list = []
        for user in user_data:
            prepared_list.append(
                {"name": user["name"], "birthday": string_to_date(user["birthday"])}
            )
            return prepared_list

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is not None:
                birthday_this_year = self.string_to_date(record.birthday.value).replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = self.string_to_date(record.birthday.value).replace(year=today.year + 1)

                # Додано перевірку, чи не буде припадати день народження вже наступного року.
                if 0 <= (birthday_this_year - today).days <= days:

                    # Додано перенесення дати привітання на наступний робочий день, якщо день народження припадає на вихідний.
                    birthday_this_year = self.adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = self.date_to_string(birthday_this_year)
                    upcoming_birthdays.append(
                        {"name": record.name.value, "birthday": congratulation_date_str}
                    )
        return upcoming_birthdays
    
    # Реалізовано pickle протокол серіалізації/десеріалізації: методи, які дозволяють зберегти всі дані у файл і завантажити їх із файлу
    def save_data(self, book, filename="addressbook.pkl"):
        with open(filename, "wb") as file:
            pickle.dump(book, file)

    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

    # Реалізовано магічний метод __str__ для красивого виводу об’єкту класу AddressBook .
    def __str__(self):
        string = "AdressBook:"
        for i in self.data:
            string += "\n"
            string += str(self.data[i])
        return string
        # return "\n".join(str(record) for record in self.data.values()) как альтернатива


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone, please."
        except KeyError:
            return "Oops, contact not found. Enter the existing in Contacts name."
        except IndexError:
            return "Enter the argument for the command, please."

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    return [record.value for record in record.phones]


@input_error
def show_all(book: AddressBook):
    return book


@input_error
def add_contact_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    return record.birthday.value


@input_error
def birthdays_list(book: AddressBook):
    return book.get_upcoming_birthdays()


def main():
    book = AddressBook()
    book = book.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_data(book)  # Викликається перед виходом з програми
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_contact_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays_list(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()


# # Створення нової адресної книги
# book = AddressBook()

# # Створення запису для John
# john_record = Record("John")
# john_record.add_phone("1111111111")
# john_record.add_phone("2222222222")
# john_record.add_birthday("28.11.1989")


# print(john_record)

# # Додавання запису John до адресної книги
# book.add_record(john_record)

# # Редагування запису John
# # john_record.remove_phone("2222222222")
# # print(john_record)

# # john_record.edit_phone("1111111111", "3333333333")
# # print(john_record)

# # john_record.remove_phone("2222222222")
# # print(john_record)

# # Пошук конкретного телефону у записі John
# # print(john_record.find_phone("333333333"))


# # Створення та додавання нового запису для Jane
# jane_record = Record("Jane")
# jane_record.add_phone("4444444444")
# jane_record.add_phone("5555555555")
# jane_record.add_birthday("29.11.1967")
# print(jane_record)

# # Додавання запису Jane до адресної книги
# book.add_record(jane_record)

# # Редагування запису Jane
# # jane_record.remove_phone("5555555555")
# # print(jane_record)

# # jane_record.edit_phone("4444444444", "666666666")
# # print(jane_record)

# # Пошук конкретного телефону у записі Jane
# # print(jane_record.find_phone("5555555555"))

# # Виведення всіх записів у книзі
# print(book)

# # Знаходження та редагування телефону для John
# # john = book.find("John")
# # john.edit_phone("1111111111", "6666666666")

# # print(john)  # Виведення: Contact name: John, phones: ........

# # Пошук конкретного телефону у записі John
# # found_phone = john.find_phone("6666666666")
# # print(f"{john.name}: {found_phone}")  # Виведення: John: ........

# # # Видалення запису Jane
# # book.delete("Jane")
# # print(book)

# list_of_birthdays = book.get_upcoming_birthdays()
# print(list_of_birthdays)
# add Max 4567890654
# add Max 7689000098
# add-birthday Max 1.12.2000

# add Maria 7655443322
# phone Maria
# show-birthday Max
# birthdays
# add-birthday Maria 04.12.1990
# add John 3456789767
# add-birthday John 4.02.1990
# add Dan 7654378968
