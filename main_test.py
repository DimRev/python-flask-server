from app.services.selenium_service import RequestProcessor


def main():
    processor = RequestProcessor()
    processor.add_request("MNDY:NASDAQ")
    processor.add_request("AAPL:NASDAQ")
    processor.add_request("GOOGL:NASDAQ")
    processor.start()
    processor.stop()

    # Access the results after stopping the processor
    results = processor.get_results()
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
