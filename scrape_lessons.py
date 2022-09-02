import json
from requests import get
from time import sleep
from telegram_notifier import TelegramNotifier
from datetime import timedelta, datetime


now = datetime.now
timeout = now()


class Lessons:
    def __init__(self, imp=None):
        if imp is None:
            self._fetch_data()
        elif type(imp) is dict:
            self._fetch_local_data(imp)
        else:
            raise TypeError(f"Imported data must be of type \"dict\", (\"{type(imp)}\" supplied)")

    def _fetch_data(self):
        _corsi_text = get("https://easyacademy.unitn.it/"
                         "/AgendaStudentiUnitn/combo.php?sw=ec_&aa=2022&page=corsi&_=1662124901773").text

        _text_stripped = _corsi_text.replace(";", "").strip().replace("var elenco_corsi = ", "").replace("var elenco_cdl = elenco_corsi\n\nvar elenco_scuole = []", "").strip()
        self.data = json.loads(_text_stripped)
        print(json.dumps(self.data, indent=4))

    def _fetch_local_data(self, imp):
        self.data = imp

    def courses_list(self):
        _known = set()
        for _i in self.data:
            if _i["facolta_code"] not in _known:
                yield _i
            _known.add(_i["facolta_code"])


try:
    courses_old = json.load(open("store.json"))
except FileNotFoundError:
    courses_old = []


les = Lessons()
ing, notify = False, False
tg_not = TelegramNotifier("1944900825:AAEG6y9x3rvLbqW0-I2IUecFgnoNcwlsimE", parse_mode="HTML", chat_id="461073396")
while True:
    if now() >= timeout:
        courses_new = []
        timeout = now() + timedelta(hours=4)
        for i in les.courses_list():
            if i["facolta_code"] not in [j["facolta_code"] for j in courses_old]:
                notify = True
                courses_old.append(i)
                courses_new.append(i)
                if "informat" in i["periodi"][0]["label"].lower():
                    ing = True
        if notify:
            notify = False
            tg_not.send("New courses have been added to "
                        "<a href=\"https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=home&_lang=it\">"
                        "easyacademy.unitn.it</a>:\n"
                        "\"" + "\", \"".join([f"{i['label']} ({i['valore']})" for i in courses_new]) + "\"")
            if ing:
                ing = False
                tg_not.send("And one of them appears to be yours...")
            json.dump(courses_old, open("store.json", "w+"))
    sleep(60)
