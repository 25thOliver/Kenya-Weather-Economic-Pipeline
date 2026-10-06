from loaders.postgres import PostgresLoader

def load_processed_data():
    print()
    print("Starting PostgreSQL loading...")

    loader = PostgresLoader()

    try:
        economic_path = (
            "/app/data/processed/worldbank/"
            "world_bank_clean.json"
        )

        weather_path = (
            "/app/data/processed/weather/"
            "weather_daily.json"
        )


        economic_inserted = (
            loader.load_economic_indicators(
                economic_path
            )
        )

        print(
            f"Economic records inserted: "
            f"{economic_inserted}"
        )

        weather_inserted = (
            loader.load_daily_weather(
                weather_path
            )
        )

        print(
            f"Weather records inserted: "
            f"{weather_inserted}"
        )

        return {
            "economic_inserted": economic_inserted,
            "weather_inserted": weather_inserted,
        }

    finally:
        loader.close()