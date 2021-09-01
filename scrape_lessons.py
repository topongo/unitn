import json
from requests import get


corsi_text = get("https://easyacademy.unitn.it/"
                 "AgendaStudentiUnitn/combo_call_new.php?sw=ec_&aa=2021&page=attivita&_=1630507410213").text

text_stripped = corsi_text.replace(";", "").strip().replace("var elenco_attivita = ", "")
data = json.loads(text_stripped)

print(json.dumps([i["nome_insegnamento"] for i in data], indent=4))
