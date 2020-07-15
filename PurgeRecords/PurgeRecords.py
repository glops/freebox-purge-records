from datetime import datetime
from hashlib import sha1
import hmac
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional
from dateutil.relativedelta import relativedelta
from time import sleep

import requests
import logging


class PurgeRecords(object):
    def __init__(self, simulation: bool, scriptPath: Path) -> None:
        self.simulation = simulation
        self.baseUrl = "http://mafreebox.freebox.fr/api/v5/"

        self.confPath = scriptPath / "conf"
        self.confPath.mkdir(exist_ok=True)
        self.appTokenPath = self.confPath / "app_token.json"
        self.sessionTokenPath = self.confPath / "session_token.txt"
        self.sessionToken: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self.appId = "RecordsPurger"

    def requestAppToken(self):
        data = {
            "app_id": self.appId,
            "app_name": self.appId,
            "app_version": "0.0.1",
            "device_name": "PC",
        }

        res = self.req("login/authorize/", json=data)

        trackId = res.get("result").get("track_id")

        maxRetries = 100

        for i in range(0, maxRetries):
            res2 = self.req(f"login/authorize/{trackId}")

            if res2.get("result").get("status") == "granted":
                self.logger.info("Authorization granted")
                break
            elif res2.get("result").get("status") in ["timeout", "denied", "unknown"] or i == maxRetries - 1:
                self.logger.error("Impossible d'obtenur l'autorisation. Avez-vous appuyé sur OK sur la Freebox ?")
                exit(1)

            self.logger.debug("En attente de l'autorisation. Merci d'appuyer sur OK sur la Freebox")
            sleep(2)

        with self.appTokenPath.open(mode="w") as f:
            json.dump(res, f)

    def requestSessionToken(self) -> str:
        if not self.appTokenPath.exists():
            self.requestAppToken()
        with self.appTokenPath.open(mode="r") as f:
            token = json.load(f)

            app_token = token.get("result").get("app_token")

            if app_token is None:
                self.logger.error("Erreur lors de la récupération du token")
                exit(1)

            r = requests.get(self.baseUrl + "login/")

            res = r.json()
            challenge = res.get("result").get("challenge")

            if challenge is None:
                self.logger.error("Erreur lors de la récupération du challenge")
                exit(1)

            h = hmac.new(str(app_token).encode("utf8"), str(challenge).encode("utf8"), sha1)
            password = h.hexdigest()

            data = {"app_id": self.appId, "password": password}

            r = requests.post(self.baseUrl + "login/session/", json=data)

            res = r.json()
            # print(res)
            self.sessionToken = res.get("result").get("session_token")

            if self.sessionToken is None:
                self.logger.error("Erreur lors de la récupération du token")
                exit(1)

            with self.sessionTokenPath.open(mode="w") as f2:
                f2.write(self.sessionToken)

            return self.sessionToken

    def getSessionToken(self) -> str:
        if self.sessionToken is None:
            return self.requestSessionToken()

        return self.sessionToken

    def req(
        self, url: str, headers: Optional[Dict] = None, json: Optional[Any] = None, method=None,
    ):

        if method == None and json is None:
            method = "GET"
        elif json is not None:
            method = "POST"

        r = requests.request(method, self.baseUrl + url, json=json, headers=headers)

        res = r.json()

        if res.get("success") != True:
            self.logger.debug(f"url: {r.url}")
            self.logger.debug(f"response: {json.dumps(res, indent=4)}")
            self.logger.error(f'Error: {res.get("msg")}')
            self.logger.error(f'Code: {res.get("error_code")}')
            exit(1)
        else:
            return res

    def getRecords(self):
        sessionToken = self.getSessionToken()

        headers = {"X-Fbx-App-Auth": sessionToken}
        res = self.req("pvr/finished/", headers=headers)

        for record in res["result"]:
            id: int = record["id"]
            name: str = record["name"]
            subname: str = record["subname"]
            end = datetime.fromtimestamp(record["end"])

            self.logger.debug(f"##################")
            self.logger.debug(f"id: {id}")
            self.logger.debug(f"name: {name}")
            self.logger.debug(f"subname: {subname}")
            self.logger.debug(f"end: {end}")

            reg = re.compile(
                r"(delete|suppression)\s*:\s*([0-9]+)\s*(day|month|week|jour|mois|semaine)s?", flags=re.I,
            )

            m = reg.match(subname)

            if m:
                number = int(m.group(2))
                unit = m.group(3)
                if unit == "jour":
                    unit = "day"
                elif unit == "mois":
                    unit = "month"
                elif unit == "semaine":
                    unit = "week"

                if unit == "week":
                    unit = "day"
                    number = number * 7

                self.logger.debug(f"number: {number}")
                self.logger.debug(f"unit: {unit}")

                if unit == "month":
                    rd = relativedelta(months=number)
                else:
                    rd = relativedelta(days=number)

                if end + rd < datetime.now():
                    if not self.simulation:
                        self.deleteRecord(id)
                    else:
                        self.logger.info(f"L'enregistrement {id} serait supprimé - mode simulation")
                else:
                    self.logger.debug("Ne pas supprimer pour le moment")
                    self.logger.debug(f"Sera supprimé après {end + rd}")
            else:
                self.logger.debug("Pas d'instruction de suppression")

    def deleteRecord(self, id: int):
        sessionToken = self.getSessionToken()

        headers = {"X-Fbx-App-Auth": sessionToken}
        self.req(f"pvr/finished/{id}", headers=headers, method="DELETE")
        self.logger.info(f"Enregistrement {id} supprimé")

