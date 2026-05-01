from src.extractors.yahoo_extractor  import run_extraction
from src.processors.market_processor import build_master_dataset
from src.cleaners.market_cleaner     import clean_dataset


def separator(title: str) -> None:
    print("\n" + "█" * 60)
    print(f"  {title}")
    print("█" * 60 + "\n")


def main() -> None:
    separator("PASO 1/3 — EXTRACCION DE DATOS FINANCIEROS")
    run_extraction()

    separator("PASO 2/3 — CONSTRUCCION DEL DATASET MAESTRO")
    build_master_dataset()

    separator("PASO 3/3 — LIMPIEZA Y TRANSFORMACION")
    clean_dataset()

    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO.")
    print("  Resultado: data/results/clean_master_dataset.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
