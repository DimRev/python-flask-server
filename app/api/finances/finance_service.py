from datetime import datetime, timedelta, timezone
import threading

from sqlalchemy.exc import SQLAlchemyError

from app.utils.api_exceptions import APIError
from app.api.finances.finance_model import Finance, FinanceHistory
from app.services.selenium_service import SeleniumRequestProcessor
from db.db import Database

selenium_request_processor = SeleniumRequestProcessor()


class FinanceService:
    def __init__(self):
        self.db = Database()
        self.is_running = False
        self.lock = threading.Lock()

    def get_all_finances_symbols(self):
        try:
            with self.db.session_local() as session:
                finances = session.query(
                    Finance.id, Finance.symbol, Finance.is_tracking
                ).all()
                return [
                    {
                        "id": finance.id,
                        "symbol": finance.symbol,
                        "is_tracking": finance.is_tracking,
                    }
                    for finance in finances
                ]
        except SQLAlchemyError as e:
            raise APIError("Failed to retrieve finances", str(e), 500) from e

    def get_finance_details_by_symbol(
        self, symbol, include_history=False, from_ts=None, to_ts=None
    ):
        try:

            if from_ts is None:
                from_ts = datetime.now(timezone.utc) - timedelta(days=7)
            if to_ts is None:
                to_ts = datetime.now(timezone.utc)

            with self.db.session_local() as session:
                finance = session.query(Finance).filter_by(symbol=symbol).first()
                if not finance:
                    raise APIError(
                        "Finance not found",
                        f"Finance with symbol {symbol} not found",
                        404,
                    )

                finance_history = []
                if include_history:
                    finance_history = (
                        session.query(FinanceHistory)
                        .filter(
                            FinanceHistory.finance_id == finance.id,
                            FinanceHistory.created_at > from_ts,
                            FinanceHistory.created_at < to_ts,
                        )
                        .all()
                    )

                formatted_result = {
                    "id": finance.id,
                    "symbol": finance.symbol,
                    "is_tracking": finance.is_tracking,
                    "last_closing_price": finance.last_closing_price,
                    "daily_change_value": finance.daily_change_value,
                    "daily_change_percentage": finance.daily_change_percentage,
                    "created_at": finance.created_at,
                    "updated_at": finance.updated_at,
                    "finance_history": [
                        {
                            "current_price": history.current_price,
                            "created_at": history.created_at,
                        }
                        for history in finance_history
                    ],
                }

                return formatted_result

        except SQLAlchemyError as e:
            raise APIError("Failed to retrieve finance", str(e), 500) from e

    def create_finance_by_symbol(self, symbol):
        try:
            with self.db.session_local() as session:
                finance = session.query(Finance).filter_by(symbol=symbol).first()
                if finance:
                    raise APIError(
                        "Finance already exists",
                        f"Finance with symbol {symbol} already exists",
                        409,
                    )

                new_finance = Finance(symbol=symbol)
                session.add(new_finance)
                session.commit()

                return {"id": new_finance.id, "symbol": new_finance.symbol}

        except SQLAlchemyError as e:
            raise APIError("Failed to create finance", str(e), 500) from e

    def update_finance_by_symbol(
        self,
        symbol,
        is_tracking=None,
        last_closing_price=None,
        daily_change_value=None,
        daily_change_percentage=None,
    ):
        try:
            with self.db.session_local() as session:
                # Check if the Finance exists
                finance = session.query(Finance).filter_by(symbol=symbol).first()
                if not finance:
                    raise APIError(
                        "Finance not found",
                        f"Finance with symbol {symbol} not found",
                        404,
                    )

                if is_tracking is not None:
                    finance.is_tracking = is_tracking
                if last_closing_price is not None:
                    finance.last_closing_price = last_closing_price
                if daily_change_value is not None:
                    finance.daily_change_value = daily_change_value
                if daily_change_percentage is not None:
                    finance.daily_change_percentage = daily_change_percentage

                session.commit()

                return {"id": finance.id, "symbol": finance.symbol}

        except SQLAlchemyError as e:
            raise APIError("Failed to update finance", str(e), 500) from e

    def delete_finance_by_symbol(self, symbol):
        try:
            with self.db.session_local() as session:
                finance = session.query(Finance).filter_by(symbol=symbol).first()
                if not finance:
                    raise APIError(
                        "Finance not found",
                        f"Finance with symbol {symbol} not found",
                        404,
                    )

                session.delete(finance)
                session.commit()

                return {"message": "Finance deleted successfully"}

        except SQLAlchemyError as e:
            raise APIError("Failed to delete finance", str(e), 500) from e

    def create_finance_history(self, finance_id, current_price, created_at):
        try:
            with self.db.session_local() as session:
                finance_history = FinanceHistory(
                    finance_id=finance_id,
                    current_price=current_price,
                    created_at=created_at,
                )
                session.add(finance_history)
                session.commit()

                return {
                    "id": finance_history.id,
                    "created_at": finance_history.created_at,
                }

        except SQLAlchemyError as e:
            raise APIError("Failed to create finance history", str(e), 500) from e

    def execute_finance_crawl_by_symbols(self):
        with self.lock:
            if self.is_running:
                return {
                    "message": "Request processor currently running.",
                }

            self.is_running = True

        thread = threading.Thread(target=self._run_crawl_process)
        thread.start()
        return {
            "message": "Request processor started.",
        }

    def _run_crawl_process(self):
        try:
            finances = self.get_all_finances_symbols()

            # Add requests to the processor
            for finance in finances:
                selenium_request_processor.add_request(finance["symbol"])

            # Start processing
            selenium_request_processor.start()
            selenium_request_processor.stop()

            # Process results
            for result in selenium_request_processor.get_results():
                matching_finance = next(
                    (
                        finance
                        for finance in finances
                        if finance["symbol"] == result["symbol"]
                    ),
                    None,
                )
                if matching_finance:
                    # Strip "$" sign from the price
                    current_price = float(result["price"][1:])
                    self.create_finance_history(
                        finance_id=matching_finance["id"],
                        current_price=current_price,
                        created_at=result["timestamp"],
                    )

        finally:
            with self.lock:
                self.is_running = False

    def is_crawler_running(self):
        if self.is_running:
            return {
                "message": "Request processor currently running",
            }
        return {
            "message": "Request processor is available",
        }
