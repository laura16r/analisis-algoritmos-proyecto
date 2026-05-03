from src.extractors.yahoo_extractor   import run_extraction
from src.processors.market_processor  import build_master_dataset
from src.cleaners.market_cleaner      import clean_dataset
from src.validators.dataset_validator import validate_dataset


def separator(title: str) -> None:
    print("\n" + "█" * 60)
    print(f"  {title}")
    print("█" * 60 + "\n")


def main() -> None:
    separator("PASO 1/4 — EXTRACCION DE DATOS FINANCIEROS")
    run_extraction()

    separator("PASO 2/4 — CONSTRUCCION DEL DATASET MAESTRO")
    build_master_dataset()

    separator("PASO 3/4 — LIMPIEZA Y TRANSFORMACION")
    clean_dataset()

    separator("PASO 4/4 — VALIDACION DEL DATASET")
    validate_dataset()

    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO.")
    print("  Resultado: data/results/clean_dataset.json")
    print("  Reporte:   data/results/validation_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()