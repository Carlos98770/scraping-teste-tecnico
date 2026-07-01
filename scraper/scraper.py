import json
import logging
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper.config import (
    BASE_URL,
    COOKIE,
    INERTIA_VER,
    WORKERS,
    TOTAL_PAGES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/scraper.log")],
)
log = logging.getLogger(__name__)

def build_session(cookie: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "X-Inertia":         "true",
        "X-Inertia-Version": INERTIA_VER,
        "Accept":            "application/json",
        "Cookie":            cookie,
        "User-Agent": USER_AGENT,
        "Referer": BASE_URL,
    })
    return s


def cookie_is_valid(session: requests.Session) -> bool:
    try:
        resp = session.get(BASE_URL, params={"page": 1}, timeout=REQUEST_TIMEOUT)
        data = resp.json()
        return data.get("component") == "Dashboard"
    except Exception:
        return False


def pedir_novo_cookie() -> str:
    print("\n" + "=" * 60)
    print("COOKIE EXPIRADO ou INVÁLIDO.")
    print("1. Abra https://teste-tecnico-dados.hubbi.app no seu browser")
    print("2. F12 → Console → digite: document.cookie")
    print("3. Copie o resultado e cole abaixo")
    print("=" * 60)
    novo = input("Novo cookie: ").strip()
    return novo

def fetch_page(session: requests.Session, page: int) -> list[dict] | None:
    try:
        resp = session.get(BASE_URL, params={"page": page}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("component") != "Dashboard":
            return None 

        return data["props"]["parts"]["data"]
    except Exception as e:
        log.warning(f"Página {page} erro: {e}")
        return None


def fetch_all_parts(cookie_inicial: str) -> list[dict]:
    cookie = cookie_inicial
    session = build_session(cookie)

    if not cookie_is_valid(session):
        cookie = pedir_novo_cookie()
        session = build_session(cookie)

    all_parts = []
    pendentes = list(range(1, TOTAL_PAGES + 1))

    while pendentes:
        falhas = []
        concluidas_nesta_rodada = 0

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(fetch_page, session, page): page
                for page in pendentes
            }

            for future in as_completed(futures):
                page = futures[future]
                result = future.result()

                if result is None:
                    falhas.append(page)
                else:
                    all_parts.extend(result)
                    concluidas_nesta_rodada += 1
                    log.info(
                        f"Página {page} → {len(result)} peças | "
                        f"Total acumulado: {len(all_parts)} | "
                        f"Restantes: {len(pendentes) - concluidas_nesta_rodada}"
                    )

        if falhas:
            log.warning(f"{len(falhas)} páginas falharam (possível cookie expirado).")
            cookie = pedir_novo_cookie()
            session = build_session(cookie)
            pendentes = falhas 
        else:
            pendentes = []

    log.info(f"Coleta concluída: {len(all_parts)} peças")
    return all_parts

