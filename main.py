from src.extractors.yahoo_extractor         import run_extraction
from src.processors.market_processor        import build_master_dataset
from src.cleaners.market_cleaner            import clean_dataset
from src.validators.dataset_validator       import validate_dataset
from src.utils.io                           import FileUtils
from src.analytics.returns                  import calculate_daily_returns
from src.analytics.historical_volatility    import calculate_historical_volatility_by_ticker
from src.analytics.risk_classification      import classify_assets_by_risk
from src.analytics.correlation              import calculate_pearson_between_assets
from src.analytics.similarity               import (
    calculate_euclidean_similarity_between_assets,
    calculate_dtw_similarity_between_assets,
    calculate_cosine_similarity_between_assets,
)
from src.analytics.visualization_preparer   import (
    prepare_risk_ranking,
    prepare_asset_comparison,
)

from config import (
    CLEAN_DATASET_PATH,
    DAILY_RETURNS_PATH,
    HISTORICAL_VOLATILITY_PATH,
    RISK_CLASSIFICATION_PATH,
    CORRELATION_PATH,
    SIMILARITY_PATH,
    DTW_PATH,
    COSINE_SIMILARITY_PATH,
    RISK_RANKING_PATH,
    ASSET_COMPARISON_PATH,
)

def separator(title: str) -> None:
    print("\n" + "█" * 60)
    print(f"  {title}")
    print("█" * 60 + "\n")


def main() -> None:
    separator("PASO 1/ — EXTRACCION DE DATOS FINANCIEROS")
    run_extraction()

    separator("PASO 2/ — CONSTRUCCION DEL DATASET MAESTRO")
    build_master_dataset()

    separator("PASO 3/ — LIMPIEZA Y TRANSFORMACION")
    clean_dataset()

    separator("PASO 4/ — VALIDACION DEL DATASET")
    validate_dataset()

    separator("PASO 5/ — CALCULO DE RETORNOS DIARIOS")
    clean_data = FileUtils.load_json(CLEAN_DATASET_PATH)
    dataset_with_returns = calculate_daily_returns(
    dataset=clean_data,
    price_field="close"
    )
    FileUtils.save_json(
        file_path=DAILY_RETURNS_PATH,
        data=dataset_with_returns,
    )

    separator("PASO 6/ — CALCULAR VOLATILIDAD HISTÓRICA")
    dataset_with_returns = FileUtils.load_json(DAILY_RETURNS_PATH)
    historical_volatility = calculate_historical_volatility_by_ticker(
        dataset=dataset_with_returns,
        return_field="daily_return",
        annualize=True,
    )
    FileUtils.save_json(
        file_path=HISTORICAL_VOLATILITY_PATH,
        data=historical_volatility,
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


    separator("PASO 7.1/ — VISUALIZACIÓN DE CLASIFICACIÓN POR RIESGO")
    classified_assets = FileUtils.load_json(RISK_CLASSIFICATION_PATH)
    risk_ranking = prepare_risk_ranking(
        risk_data=classified_assets,
        volatility_field="annual_volatility",
    )
    FileUtils.save_json(
        file_path=RISK_RANKING_PATH,
        data=risk_ranking,
    )

    separator("PASO 8/ — SIMILITUD DE DISTANCIA EUCLIDIANA (Dos activos)")
    ticker_a = "AAPL"
    ticker_b = "MSFT"
    similarity_result = calculate_euclidean_similarity_between_assets(
        dataset=dataset_with_returns,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field="daily_return",
    )
    FileUtils.save_json(
        file_path=SIMILARITY_PATH,
        data=similarity_result,
    )

    separator("PASO 9/ — CORRELACIÓN DE PEARSON (Dos activos)")
    ticker_a = "AAPL"
    ticker_b = "MSFT"
    correlation_result = calculate_pearson_between_assets(
        dataset=dataset_with_returns,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
    )
    FileUtils.save_json(
        file_path=CORRELATION_PATH,
        data=correlation_result,
    )

    separator("PASO 10/ — DYNAMIC TIME WARPING - DTW (Dos activos)")
    ticker_a = "AAPL"
    ticker_b = "MSFT"
    dtw_result = calculate_dtw_similarity_between_assets(
        dataset=dataset_with_returns,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field="daily_return",
    )
    FileUtils.save_json(
        file_path=DTW_PATH,
        data=dtw_result,
    )

    separator("PASO 11/ — SIMILITUD POR COSENO (Dos activos)")
    ticker_a = "AAPL"
    ticker_b = "MSFT"
    cosine_similarity_result = calculate_cosine_similarity_between_assets(
        dataset=dataset_with_returns,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field="daily_return",
    )
    FileUtils.save_json(
        file_path=COSINE_SIMILARITY_PATH,
        data=cosine_similarity_result,
    )

    separator("PASO 12/ — VISUALIZACIÓN DE CALCULOS DE SIMILITUD")
    correlation_result = FileUtils.load_json(CORRELATION_PATH)
    similarity_result = FileUtils.load_json(SIMILARITY_PATH)
    dtw_result = FileUtils.load_json(DTW_PATH)
    cosine_similarity_result = FileUtils.load_json(COSINE_SIMILARITY_PATH)
    asset_comparison = prepare_asset_comparison(
        pearson_result=correlation_result,
        euclidean_result=similarity_result,
        dtw_result=dtw_result,
        cosine_result=cosine_similarity_result,
    )

    FileUtils.save_json(
        data=asset_comparison,
        file_path=ASSET_COMPARISON_PATH,
    )

    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO.")
    print("  Resultado: data/results/clean_dataset.json")
    print("  Reporte:   data/results/validation_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()