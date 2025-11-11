import pytest
from unittest.mock import Mock
from services import library_service
from services.payment_service import PaymentGateway

@pytest.fixture
def stub_calculate_late_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value=5.0)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "Python 101"})
    return True

@pytest.fixture
def mock_gateway():
    gateway = Mock(spec=PaymentGateway)
    return gateway

def test_pay_late_fees_success(mocker, stub_calculate_late_fee, mock_gateway):
    mock_gateway.process_payment.return_value = True
    result = library_service.pay_late_fees("123456", 1, mock_gateway)
    assert result[0] is True
    mock_gateway.process_payment.assert_called_once()

def test_pay_late_fees_declined(mocker, stub_calculate_late_fee, mock_gateway):
    mock_gateway.process_payment.return_value = False
    result = library_service.pay_late_fees("123456", 1, mock_gateway)
    assert result[0] is False
    mock_gateway.process_payment.assert_called_once()

def test_pay_late_fees_invalid_patron(mock_gateway):
    result = library_service.pay_late_fees("12", 1, mock_gateway)
    assert result[0] is False
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_fee(mocker, mock_gateway):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1})
    result = library_service.pay_late_fees("123456", 1, mock_gateway)
    assert result[0] is False
    mock_gateway.process_payment.assert_not_called()

def test_refund_success(mock_gateway):
    mock_gateway.refund_payment.return_value = True
    result = library_service.refund_late_fee_payment("T123", 10.0, mock_gateway)
    assert result[0] is True
    mock_gateway.refund_payment.assert_called_once_with("T123", 10.0)

def test_refund_invalid_transaction(mock_gateway):
    result = library_service.refund_late_fee_payment("", 10.0, mock_gateway)
    assert result[0] is False
    mock_gateway.refund_payment.assert_not_called()

def test_refund_invalid_amount(mock_gateway):
    result = library_service.refund_late_fee_payment("T123", -5.0, mock_gateway)
    assert result[0] is False
    mock_gateway.refund_payment.assert_not_called()
