from bs4 import BeautifulSoup
from fake_headers import Headers
from tkinter import BooleanVar, Button, Checkbutton, Entry, Label, \
                    OptionMenu, Radiobutton, StringVar, Tk, W

import csv
import requests

root = Tk()
root.title("ЦИАН")

select_var = StringVar(root)
select_var.set("Москва и МО")
select = OptionMenu(root, select_var, "Москва и МО", "Белгород", "Брянск",
                    "Владимир", "Воронеж", "Иваново", "Калуга", "Кострома",
                    "Курск", "Липецк", "Орел", "Рязань", "Смоленск", "Тамбов",
                    "Тверь", "Тула", "Ярославль")

city_dict = {"Москва и МО": "-1", "Белгород": "4671", "Брянск": "4691",  # коды городов на ЦИАН
             "Владимир": "4703", "Воронеж": "4713", "Иваново": "4767",
             "Калуга": "4780", "Кострома": "175050", "Курск": "4835",
             "Липецк": "4847", "Орел": "175604", "Рязань": "4963",
             "Смоленск": "4987", "Тамбов": "5011", "Тверь": "176083",
             "Тула": "5020", "Ярославль": "5075"}

radio_var_1 = BooleanVar()
radio_var_1.set(0)
r1 = Radiobutton(text="Торговое", variable=radio_var_1, value=0)
r2 = Radiobutton(text="Офисное", variable=radio_var_1, value=1)

radio_var_2 = BooleanVar()
radio_var_2.set(0)
r2_1 = Radiobutton(text='Любой этаж', variable=radio_var_2, value=0)
r2_2 = Radiobutton(text='От 1-го этажа', variable=radio_var_2, value=1)

price_filter = Label(root, text="Цена за кв. метр до:", fg="black",
                     width=20, height=2)

price_entry = Entry(root, width=10, font='Arial 16')

check_box_1 = BooleanVar()
check_box_1.set(0)
c1 = Checkbutton(text="Пятерочка", variable=check_box_1,
                 onvalue=1, offvalue=0, height=2)

check_box_2 = BooleanVar()
check_box_2.set(0)
c2 = Checkbutton(text="Пятёрочка", variable=check_box_2,
                 onvalue=1, offvalue=0, height=2)

check_box_3 = BooleanVar()
check_box_3.set(0)
c3 = Checkbutton(text="Дикси", variable=check_box_3,
                 onvalue=1, offvalue=0, height=2)

check_box_4 = BooleanVar()
check_box_4.set(0)
c4 = Checkbutton(text="Перекресток", variable=check_box_4,
                 onvalue=1, offvalue=0, height=2)

check_box_5 = BooleanVar()
check_box_5.set(0)
c5 = Checkbutton(text="Магнит", variable=check_box_5,
                 onvalue=1, offvalue=0, height=2)

check_box_6 = BooleanVar()
check_box_6.set(0)
c6 = Checkbutton(text="Вкус-Вилл", variable=check_box_6,
                 onvalue=1, offvalue=0, height=2)

check_box_1_1 = BooleanVar()
check_box_1_1.set(0)
c1_1 = Checkbutton(text="МАП", variable=check_box_1_1,
                   onvalue=1, offvalue=0, height=2)

check_box_1_2 = BooleanVar()
check_box_1_2.set(0)
c1_2 = Checkbutton(text="ГАП", variable=check_box_1_2,
                   onvalue=1, offvalue=0, height=2)


def get_html(url):
    headers = Headers(headers=True).generate()
    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        return result.text
    except(requests.RequestException, ValueError):
        print("Сетевая ошибка")
        return False


dict_list = []


def parser(url, page_counter=1):
    html = get_html(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        offers_list = soup.find_all("div", {"data-name": "HorizontalCard"})
        if len(offers_list) == 0:
            return print("капча")
        for offer in offers_list:  # парсим каждую карточку со страницы
            url = offer.find("a")["href"]
            html = get_html(url)
            if html:
                soup2 = BeautifulSoup(html, "html.parser")
                full_dict = {}
                address = soup2.find(
                    "div", {"data-name": "Geo"}
                    ).find("address")
                full_dict["Адрес"] = address.text[:-8]
                full_dict["Ссылка"] = url
                ids = soup2.find("div", {"data-name": "AuthorAsideBrand"})
                if "ID" in ids.text:
                    ids = ids.find("h2").text
                    full_dict["ID"] = ids[3:]
                else:
                    if ids.find("a", {"data-name": "Link"}) is not None:
                        ids = ids.find("a", {"data-name": "Link"})
                        full_dict["ID"] = ids["href"]
                    else:
                        full_dict["ID"] = "Нельзя извлечь со страницы"
                print(full_dict["ID"])
                full_dict["Телефон"] = soup2.find(
                    "div", {"data-name": "OfferContactsAside"}
                    ).find("a").text
                square = soup2.find("h1").text.split(",")[1]
                full_dict["Площадь"] = square.strip()
                price = soup2.find("span", {"itemprop": "price"})
                if price is not None:
                    price = int(price["content"])
                    full_dict["Цена"] = str(price) + " руб."
                else:
                    price = "0"
                    full_dict["Цена"] = "Ценовой диапазон"
                full_dict["МАП"] = str(price//100000) + " мес."      # расчет параметров
                full_dict["ГАП"] = str(price//1200000*12) + " мес."  # для заказчика
                if "от" in full_dict["Площадь"]:
                    full_dict["Цена за кв. м"] = "Диапазон площадей"
                else:
                    full_dict["Цена за м2"] = price//int(square.split(" ")[1])
                description = soup2.find("p", {"itemprop": "description"})
                full_dict["Описание"] = description.text
                dict_list.append(full_dict)
                print(len(dict_list))
        pagination = soup.find("div", {"data-name": "Pagination"})
        if pagination is not None:  # проверяем наличие других страниц
            pagination = pagination.find_all("li")
            for page in pagination:
                if page.find("span") is not None:
                    print("next")
                elif page.find("a") is not None:
                    if int(page.find("a").text) < page_counter:
                        print("next")
                    else:
                        page_counter += 1
                        print(page_counter)
                        page = page.find("a")
                        url = page["href"]
                        if "https://" not in url:
                            url = "https://www.cian.ru" + url
                        print("пошел на новую страницу")
                        print(url)
                        return parser(url, page_counter)
    return dict_write(). # отправляем все на запись в csv


def dict_write():
    with open("tables.csv", "a", newline='') as f:
        fieldnames = ["Ссылка", "ID", "Адрес", "Телефон", "Площадь",
                      "Цена", "МАП", "ГАП", "Цена за кв. м",
                      "Описание"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for i in dict_list:
            w.writerow(i)
    finished["fg"] = "green"
    return


def search_url():  # собираем конструктор url из tkinter
    city = select_var.get()

    property_type = "2"
    if radio_var_1.get():
        property_type = "1"

    max_price = price_entry.get()
    if len(max_price) < 4:
        max_price = "9999999"

    min_floor = "0"
    if radio_var_2.get():
        min_floor = "1"

    city = city_dict[select_var.get()]

    key_list_1 = []
    if property_type == "2":
        if check_box_1.get() is True:
            key_word_1 = c1["text"]
        else:
            key_word_1 = ""
        if check_box_2.get() is True:
            key_word_2 = c2["text"]
        else:
            key_word_2 = ""
        if check_box_3.get() is True:
            key_word_3 = c3["text"]
        else:
            key_word_3 = ""
        if check_box_4.get() is True:
            key_word_4 = c4["text"]
        else:
            key_word_4 = ""
        if check_box_5.get() is True:
            key_word_5 = c5["text"]
        else:
            key_word_5 = ""
        if check_box_6.get() is True:
            key_word_6 = c6["text"]
        else:
            key_word_6 = ""

        key_list_1 = [key_word_1, key_word_2, key_word_3,
                      key_word_4, key_word_5, key_word_6]

        while True:
            try:
                key_list_1.remove("")
            except ValueError:
                break

    if check_box_1_1.get() is True:
        key_word_1_1 = c1_1["text"]
    else:
        key_word_1_1 = ""
    if check_box_1_2.get() is True:
        key_word_1_2 = c1_2["text"]
    else:
        key_word_1_2 = ""

    key_list_2 = [key_word_1_1, key_word_1_2]
    while True:
        try:
            key_list_2.remove("")
        except ValueError:
            break

    if len(key_list_1) == 0:
        if len(key_list_2) == 2:
            key_words = (",").join(key_list_2).replace(" ", "%7")
        elif len(key_list_2) == 1:
            key_words = key_list_2[0]
        elif len(key_list_2) == 0:
            url = "https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&m2=1&maxprice=" + max_price + "&minfloor=" + min_floor + "&offer_type=offices&office_type%5B0%5D=" + property_type + "&p=1&region=" + city
            return parser(url)
    else:
        if len(key_list_2) == 0:
            key_words = (",").join(key_list_1).replace(",", "%7C")
        else:
            key_words = []
            for key_2 in key_list_2:
                for key_1 in key_list_1:
                    key_words.append(key_1 + "+" + key_2)
            key_words = (",").join(key_words).replace(",", "%7C")
    url = "https://www.cian.ru/cat.php?context="\
        + key_words + \
        "&currency=2&deal_type=sale&engine_version=2&m2=1&maxprice="\
        + max_price + "&minfloor=" + min_floor\
        + "&offer_type=offices&office_type%5B0%5D="\
        + property_type + "&p=1&region=" + city
    return parser(url)


but1 = Button(root, text="Искать", command=search_url,
              width=20, height=2)

finished = Label(root, text="Готово!", fg="white",
                 width=20, height=3)

select.grid(row=0, column=0, sticky=W)

r1.grid(row=1, column=0, sticky=W)
r2.grid(row=1, column=1, sticky=W)
r2_1.grid(row=2, column=0, sticky=W)
r2_2.grid(row=2, column=1, sticky=W)

c1.grid(row=5, column=0, sticky=W)
c2.grid(row=6, column=0, sticky=W)
c3.grid(row=7, column=0, sticky=W)
c4.grid(row=8, column=0, sticky=W)
c5.grid(row=9, column=0, sticky=W)
c6.grid(row=10, column=0, sticky=W)

c1_1.grid(row=5, column=1)
c1_2.grid(row=6, column=1)

price_filter.grid(row=3, column=0, sticky=W)
price_entry.grid(row=3, column=1, sticky=W)

but1.grid(row=11, column=0, columnspan=2)

finished.grid(row=12, column=0, columnspan=2)

root.mainloop()
