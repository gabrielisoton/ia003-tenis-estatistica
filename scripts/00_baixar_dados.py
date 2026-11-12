"""Passo 0 — baixa os CSVs anuais da TML-Database (ATP, 2000–2025).

Fonte: https://github.com/Tennismylife/TML-Database (mesmo esquema de colunas
da antiga base JeffSackmann/tennis_atp, removida do GitHub em 2026).
"""
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "dados" / "raw"
URL = "https://raw.githubusercontent.com/Tennismylife/TML-Database/master/{ano}.csv"
ANOS = range(2000, 2026)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for ano in ANOS:
        destino = RAW / f"{ano}.csv"
        if destino.exists():
            continue
        urllib.request.urlretrieve(URL.format(ano=ano), destino)
        print(f"baixado {destino.name} ({destino.stat().st_size / 1024:.0f} KB)")
    print(f"{len(list(RAW.glob('*.csv')))} arquivos em {RAW}")


if __name__ == "__main__":
    main()
