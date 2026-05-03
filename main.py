from src.extractors.yahoo_extractor         import run_extraction
from src.processors.market_processor        import build_master_dataset
from src.cleaners.market_cleaner            import clean_dataset
from src.validators.dataset_validator       import validate_dataset
from src.utils.io                           import FileUtils
from src.analytics.returns                  import calculate_daily_returns
from src.statistics.historical_volatility   import calculate_historical_volatility_by_ticker
from src.statistics.risk_classification     import classify_assets_by_risk

from config import (
    CLEAN_DATASET_PATH,
    DAILY_RETURNS_PATH,
    HISTORICAL_VOLATILITY_PATH,
    RISK_CLASSIFICATION_PATH,
    )

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
    dataset_with_returns = calculate_daily_returns(
        dataset=clean_dataset,
        price_field="close"
    )
    FileUtils.save_json(
        DAILY_RETURNS_PATH,
        dataset_with_returns,
    )

    separator("PASO 6/ — CALCULAR VOLATILIDAD HISTÓRICA")
    dataset_with_returns = FileUtils.load_json(DAILY_RETURNS_PATH)
    historical_volatility = calculate_historical_volatility_by_ticker(
        dataset=dataset_with_returns,
        return_field="daily_return",
        annualize=True,
    )
    FileUtils.save_json(
        HISTORICAL_VOLATILITY_PATH,
        historical_volatility,
    )

    separator("PASO 7/ — CLASIFICAR ACTIVOS POR RIESGO")
    historical_volatility = FileUtils.load_json(HISTORICAL_VOLATILITY_PATH)
    classified_assets = classify_assets_by_risk(
        volatility_data=historical_volatility,
        volatility_field="annual_volatility",
    )
    FileUtils.save_json(
        RISK_CLASSIFICATION_PATH,
        classified_assets,
    )

    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO.")
    print("  Resultado: data/results/clean_dataset.json")
    print("  Reporte:   data/results/validation_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()