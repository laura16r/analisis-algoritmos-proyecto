from src.extractors.yahoo_extractor         import run_extraction
from src.processors.market_processor        import build_master_dataset
from src.cleaners.market_cleaner            import clean_dataset
from src.validators.dataset_validator       import validate_dataset
from src.utils.io                           import FileUtils
from src.analytics.returns                  import calculate_daily_returns
from src.statistics.historical_volatility   import calculate_historical_volatility_by_ticker

from config import (
    CLEAN_DATASET_PATH,
    DAILY_RETURNS_PATH,)

def separator(title: str) -> None:
    print("\n" + "█" * 60)
    print(f"  {title}")
    print("█" * 60 + "\n")


def main() -> None:
    separator("PASO 1/ — EXTRACCION DE DATOS FINANCIEROS")
    #run_extraction()

    separator("PASO 2/ — CONSTRUCCION DEL DATASET MAESTRO")
    #build_master_dataset()

    separator("PASO 3/ — LIMPIEZA Y TRANSFORMACION")
    #clean_dataset()

    separator("PASO 4/ — VALIDACION DEL DATASET")
    #validate_dataset()

    separator("PASO 5/ — CALCULO DE RETORNOS DIARIOS")
    clean_dataset = FileUtils.load_json(CLEAN_DATASET_PATH)
    calculate_daily_returns(clean_dataset)

    separator("PASO 6/ — CALCULAR VOLATILIDAD HISTÓRICA")
    dataset_with_returns = FileUtils.load_json(DAILY_RETURNS_PATH)
    calculate_historical_volatility_by_ticker(dataset_with_returns)

    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO.")
    print("  Resultado: data/results/clean_dataset.json")
    print("  Reporte:   data/results/validation_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()