import ctypes
import os
import platform
from ctypes import c_char_p, c_double, c_int, POINTER, create_string_buffer
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import json
from dataclasses import dataclass, asdict

# Buffer size constants
DEFAULT_BUFFER_SIZE = 1024 * 1024
LARGE_BUFFER_SIZE = 1024 * 1024 * 8
EXTRA_LARGE_BUFFER_SIZE = 1024 * 1024 * 64


@dataclass
class TradeResponse:
    error: Optional[str]
    data: Any

    def __repr__(self) -> str:
        if isinstance(self.data, list):
            data_preview = self.data[:2] if len(
                self.data) > 2 else self.data  # Show only the first 2 entries if too long
            return (f"TradeResponse(data={data_preview!r}... ({len(self.data)} items), "
                    f"error={self.error!r})")
        return f"TradeResponse(data={self.data!r}, error={self.error!r})"


class TradeData:
    """Base class for trade-related dataclasses to reduce method duplication."""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        raise NotImplementedError("Subclasses must implement from_dict")


@dataclass
class TradeOrder(TradeData):
    contract_id: str = ''
    order_date: str = ''
    order_time: str = ''
    code: str = ''
    name: str = ''
    operation: str = ''
    remark: str = ''
    order_quantity: int = 0
    trade_quantity: int = 0
    cancel_quantity: int = 0
    order_price: float = 0.0
    trade_price: float = 0.0
    market: str = ''
    source_data: Dict[str, Any] = None

    def time(self) -> datetime:
        return datetime.strptime(f"{self.order_date} {self.order_time}", "%Y%m%d %H:%M:%S")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeOrder':
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items() if k != 'source_data'},
                   source_data=data.get('source_data', {}))


@dataclass
class TradeInfo(TradeData):
    sequence: int = 0
    contract_id: str = ''
    market: str = ''
    market_id: str = ''
    trade_date: str = ''
    trade_time: str = ''
    code: str = ''
    name: str = ''
    operation: str = ''
    trade_price: float = 0.0
    trade_quantity: int = 0
    trade_amount: float = 0.0
    account_id: str = ''
    trade_id: str = ''
    source_data: Dict[str, Any] = None

    def time(self) -> datetime:
        return datetime.strptime(f"{self.trade_date} {self.trade_time}", "%Y%m%d %H:%M:%S")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeInfo':
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items() if k != 'source_data'},
                   source_data=data.get('source_data', {}))


@dataclass
class TradePosition(TradeData):
    sequence: int = 0
    code: str = ''
    name: str = ''
    frozen_qty: int = 0
    available_qty: int = 0
    stock_balance: int = 0
    actual_qty: int = 0
    market_price: float = 0.0
    market_value: float = 0.0
    cost_price: float = 0.0
    profit_loss_rate: float = 0.0
    profit_loss: float = 0.0
    account_id: str = ''
    market_id: str = ''
    market: str = ''
    source_data: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradePosition':
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items() if k != 'source_data'},
                   source_data=data.get('source_data', {}))


@dataclass
class AccountInfo(TradeData):
    available_cash: float = 0.0
    total_value: float = 0.0
    source_data: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountInfo':
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items() if k != 'source_data'},
                   source_data=data.get('source_data', {}))


class TradeClientError(Exception):
    """Custom exception for TradeClient errors."""

    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.response = response


class TradeClient:
    """A Python class to interact with the trade.so shared library."""

    def __init__(self, ops: Optional[Dict[str, Any]] = None):
        self._ops = ops
        self._client_id = None
        base_dir = os.path.dirname(__file__)
        # Determine the shared library extension based on the operating system
        system = platform.system()
        if system == "Linux":
            lib_extension = ".so"
        elif system == "Darwin":  # macOS
            lib_extension = ".dylib"
        elif system == "Windows":
            lib_extension = ".dll"
        else:
            raise TradeClientError(f"Unsupported operating system: {system}")

        lib_path = os.path.join(base_dir, f"trade{lib_extension}")
        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError as e:
            raise TradeClientError(f"Failed to load library {lib_path}: {e}")
        self._setup_functions()

    def __enter__(self):
        self.connect(self._ops)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _setup_functions(self):
        """Configure argument and return types for library functions."""
        c_int_p = POINTER(c_int)
        c_double_p = POINTER(c_double)

        func_configs = [
            ("Connect", [c_char_p, c_char_p, c_int], c_int),
            ("Disconnect", [c_char_p, c_char_p, c_int], c_int),
            ("Buy", [c_char_p, c_char_p, c_double_p, c_int_p, c_char_p, c_int], c_int),
            ("Sell", [c_char_p, c_char_p, c_double_p, c_int_p, c_char_p, c_int], c_int),
            ("CancelOrder", [c_char_p, c_char_p, c_char_p, c_char_p, c_int], c_int),
            ("AccountInfo", [c_char_p, c_char_p, c_int], c_int),
            ("GetOrder", [c_char_p, c_char_p, c_char_p, c_char_p, c_int], c_int),
            ("GetOrders", [c_char_p, c_char_p, c_int], c_int),
            ("GetOpenOrders", [c_char_p, c_char_p, c_int], c_int),
            ("GetOrdersHistory", [c_char_p, c_int_p, c_int_p, c_char_p, c_int], c_int),
            ("GetPositions", [c_char_p, c_char_p, c_int], c_int),
            ("GetPosition", [c_char_p, c_char_p, c_char_p, c_int], c_int),
            ("GetTrades", [c_char_p, c_char_p, c_int], c_int),
            ("GetTradesHistory", [c_char_p, c_int_p, c_int_p, c_char_p, c_int], c_int),
            ("IPO", [c_char_p, c_char_p, c_int], c_int),
        ]

        for name, argtypes, restype in func_configs:
            func = getattr(self.lib, name)
            func.argtypes = argtypes
            func.restype = restype

    def _call_library_function(self, func_name: str, buffer_size: int,
                               data_class: Optional[type], is_list: bool,
                               *args) -> Tuple[Any, Optional[str]]:
        """Generic method to call a library function and parse its response."""
        out = create_string_buffer(buffer_size)
        func = getattr(self.lib, func_name)
        status = func(*args, out, buffer_size)
        parse_result = self._parse_buffer(status, out.value)

        if data_class and parse_result.data is not None:
            data = ([data_class.from_dict(item) for item in parse_result.data]
                    if is_list and isinstance(parse_result.data, list)
                    else data_class.from_dict(parse_result.data))
        else:
            data = parse_result.data

        return data, parse_result.error

    def _parse_buffer(self, status: int, result: Optional[bytes]) -> TradeResponse:
        """Parse the C function response into a Python dictionary."""
        if status != 0:
            return TradeResponse(error=f"Status error [{status}]", data=None)
        if not result:
            return TradeResponse(error="Empty response from library", data=None)

        try:
            response = json.loads(result.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return TradeResponse(error=f"Failed to parse response: {e}", data=None)

        error = response.get("error")
        data = response.get("data")
        error = None if error in {"", "nil", "<nil>", "<null>", "null", "None", "<None>"} else error
        return TradeResponse(error=error, data=data)

    def connect(self, ops: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[str]]:
        """Initialize a new trading session with the given configuration."""
        if ops is None:
            ops = self._ops or {}
        result, error = self._call_library_function("Connect", DEFAULT_BUFFER_SIZE, None, False,
                                                    json.dumps(ops or {}).encode('utf-8'))
        if not error:
            self._client_id = result
        return result, error

    def disconnect(self) -> Tuple[None, Optional[str]]:
        """Disconnect the trading session for the given client ID."""
        result, error = self._call_library_function("Disconnect", DEFAULT_BUFFER_SIZE, None, False,
                                                    self._client_id.encode('utf-8'))
        if not error:
            self._client_id = None
        return result, error

    def buy(self, code: str, price: float, qty: int) -> Tuple[None, Optional[str]]:
        """Place a buy order for the given client ID, code, price, and quantity."""
        return self._call_library_function("Buy", DEFAULT_BUFFER_SIZE, None, False,
                                           self._client_id.encode('utf-8'),
                                           code.encode('utf-8'),
                                           ctypes.byref(c_double(price)),
                                           ctypes.byref(c_int(qty)))

    def sell(self, code: str, price: float, qty: int) -> Tuple[None, Optional[str]]:
        """Place a sell order for the given client ID, code, price, and quantity."""
        return self._call_library_function("Sell", DEFAULT_BUFFER_SIZE, None, False,
                                           self._client_id.encode('utf-8'),
                                           code.encode('utf-8'),
                                           ctypes.byref(c_double(price)),
                                           ctypes.byref(c_int(qty)))

    def cancel_order(self, code: str, oid: str) -> Tuple[None, Optional[str]]:
        """Cancel an order for the given client ID, code, and order ID."""
        return self._call_library_function("CancelOrder", DEFAULT_BUFFER_SIZE, None, False,
                                           self._client_id.encode('utf-8'),
                                           code.encode('utf-8'),
                                           oid.encode('utf-8'))

    def account_info(self) -> Tuple[AccountInfo, Optional[str]]:
        """Retrieve account information for the given client ID."""
        return self._call_library_function("AccountInfo", DEFAULT_BUFFER_SIZE, AccountInfo, False,
                                           self._client_id.encode('utf-8'))

    def get_order(self, code: str, oid: str) -> Tuple[TradeOrder, Optional[str]]:
        """Retrieve a specific order for the given client ID, code, and order ID."""
        return self._call_library_function("GetOrder", DEFAULT_BUFFER_SIZE, TradeOrder, False,
                                           self._client_id.encode('utf-8'),
                                           code.encode('utf-8'),
                                           oid.encode('utf-8'))

    def get_orders(self) -> Tuple[List[TradeOrder], Optional[str]]:
        """Retrieve all orders for the given client ID."""
        return self._call_library_function("GetOrders", LARGE_BUFFER_SIZE, TradeOrder, True,
                                           self._client_id.encode('utf-8'))

    def get_open_orders(self) -> Tuple[List[TradeOrder], Optional[str]]:
        """Retrieve all open orders for the given client ID."""
        return self._call_library_function("GetOpenOrders", LARGE_BUFFER_SIZE, TradeOrder, True,
                                           self._client_id.encode('utf-8'))

    def get_orders_history(self, start_date: int, end_date: int) -> Tuple[List[TradeOrder], Optional[str]]:
        """Retrieve order history for the given client ID and date range."""
        return self._call_library_function("GetOrdersHistory", EXTRA_LARGE_BUFFER_SIZE, TradeOrder, True,
                                           self._client_id.encode('utf-8'),
                                           ctypes.byref(c_int(start_date)),
                                           ctypes.byref(c_int(end_date)))

    def get_positions(self) -> Tuple[List[TradePosition], Optional[str]]:
        """Retrieve all positions for the given client ID."""
        return self._call_library_function("GetPositions", LARGE_BUFFER_SIZE, TradePosition, True,
                                           self._client_id.encode('utf-8'))

    def get_position(self, code: str) -> Tuple[TradePosition, Optional[str]]:
        """Retrieve a specific position for the given client ID and code."""
        return self._call_library_function("GetPosition", DEFAULT_BUFFER_SIZE, TradePosition, False,
                                           self._client_id.encode('utf-8'),
                                           code.encode('utf-8'))

    def get_trades(self) -> Tuple[List[TradeInfo], Optional[str]]:
        """Retrieve all trades for the given client ID."""
        return self._call_library_function("GetTrades", EXTRA_LARGE_BUFFER_SIZE, TradeInfo, True,
                                           self._client_id.encode('utf-8'))

    def get_trades_history(self, start_date: int, end_date: int) -> Tuple[List[TradeInfo], Optional[str]]:
        """Retrieve trade history for the given client ID and date range."""
        return self._call_library_function("GetTradesHistory", EXTRA_LARGE_BUFFER_SIZE, TradeInfo, True,
                                           self._client_id.encode('utf-8'),
                                           ctypes.byref(c_int(start_date)),
                                           ctypes.byref(c_int(end_date)))
