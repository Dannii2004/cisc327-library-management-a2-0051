import pytest
from services.library_service import refund_late_fee_payment

class DummyGateway:
    def refund_payment(self, txn_id, amount):
        # Simulate a successful refund
        return True, "Refund processed successfully"

def test_refund_late_fee_success(monkeypatch):
    # Mock the PaymentGateway so no network calls happen
    gw = DummyGateway()
    ok, msg = refund_late_fee_payment("TX-123", 5.00, payment_gateway=gw)
    assert ok is True
    assert "refund" in msg.lower()

def test_refund_late_fee_invalid_amount():
    ok, msg = refund_late_fee_payment("TX-123", -1.00)
    assert ok is False
    assert "greater than 0" in msg.lower()

def test_refund_late_fee_exceeds_limit():
    ok, msg = refund_late_fee_payment("TX-123", 20.00)
    assert ok is False
    assert "exceeds maximum" in msg.lower()

def test_refund_late_fee_gateway_error(monkeypatch):
    class BadGateway:
        def refund_payment(self, txn_id, amount):
            raise Exception("network timeout")

    gw = BadGateway()
    ok, msg = refund_late_fee_payment("TX-123", 5.00, payment_gateway=gw)
    assert ok is False
    assert "error" in msg.lower()
