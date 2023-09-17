from django.shortcuts import render
import json
import requests
from bs4 import BeautifulSoup
from .forms import TarifsFilterForm
from mts.models import Tarifs


def index(request):
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price or max_price or min_price == max_price == "":
        return index_filter(request)
    Tarifs.objects.all().delete()
    headers = {
        "authority": "moskva.mts.ru",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/"
                  "webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/116.0.0.0 Safari/537.36",
    }

    url = "https://moskva.mts.ru/personal/mobilnaya-svyaz/tarifi/vse-tarifi/mobile-tv-inet"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    text_response = response.text
    soup = BeautifulSoup(text_response, "html.parser")
    scripts = soup.find_all("script")
    data = [
        script for script in scripts if "window.globalSettings.tariffs =" in script.text
    ][0]
    data_text = data.text.split(" = ")[-1].strip()[:-1]
    data_json = json.loads(data_text)
    actual_tariffs = data_json.get("actualTariffs")
    for tariff in actual_tariffs:
        # Публичные тарифы МТС (связь интернет, тв)
        if tariff.get("categoryOrder") == 100:
            article = tariff.get("id")

            title = tariff.get("title")

            parametrs = {}
            for characteristic in tariff.get("productCharacteristics"):
                if characteristic.get("title"):
                    parametrs[characteristic.get("title")] = characteristic.get("value")
                else:
                    parametrs["ТВ-каналы"] = characteristic.get("value")

            options = ""
            if tariff.get("benefitsDescription", {}).get("description"):
                options += tariff.get("benefitsDescription").get("description")
            if tariff.get("description"):
                options += "," + tariff.get("description")
                new_options = (
                    options.replace("&nbsp;", "")
                    .replace("</nobr>", "")
                    .replace("<nobr>", "")
                    .replace("&mdash;", "")
                )
                options = new_options.lstrip(",")

            price = (
                tariff.get("convergentTariffSettings", {})
                .get("offer", {})
                .get("totalPrice", {})
                .get("value")
            )

            price_old = (
                tariff.get("convergentTariffSettings", {})
                .get("offer", {})
                .get("totalPrice", {})
                .get("oldValue")
            )
            if price is None:
                price = (
                    tariff.get("homeTariffSettings", {})
                    .get("offer", {})
                    .get("totalPrice", {})
                    .get("value")
                )
                price_old = (
                    tariff.get("homeTariffSettings", {})
                    .get("offer", {})
                    .get("totalPrice", {})
                    .get("oldValue")
                )
            if price is None:
                if tariff.get("subscriptionFee"):
                    price = tariff.get("subscriptionFee", {}).get("numValue", {})
            Tarifs(
                article=article,
                title=title,
                parametrs=parametrs,
                price=price,
                price_old=price_old,
                options=options,
            ).save()
    return index_filter(request)


def index_filter(request):
    tarifs = Tarifs.objects.all()
    form = TarifsFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data["min_price"]:
            tarifs = tarifs.filter(price__gte=form.cleaned_data["min_price"])
        if form.cleaned_data["max_price"]:
            tarifs = tarifs.filter(price__lte=form.cleaned_data["max_price"])
        if form.cleaned_data["ordering"]:
            tarifs = tarifs.order_by(form.cleaned_data["ordering"])
    context = {"tarifs": tarifs, "form": form}
    return render(request, "index.html", context)
