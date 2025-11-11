import pytest

from unittest.mock import Mock
import services.library_service as svc

def test_pay_late_fees_ok_stub(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 5.75})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"id": b, "title": "Nebula Vector"})

    class GateClone:
        def process_payment(self, patron_id, amount, description=""):
            return True, "txn_Z9", "OKAY"

    verdict, note, receipt = svc.pay_late_fees("246810", 42, payment_gateway=GateClone())

    assert verdict is True

    assert receipt == "txn_Z9"

    assert "success" in note.lower()

def test_pay_late_fees_decline_mock(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 7.20})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"id": b, "title": "Quantum Lattice"})

    proxy = Mock()

    proxy.process_payment.return_value = (False, "", "DECLINED")

    verdict, note, receipt = svc.pay_late_fees("135790", 7, payment_gateway=proxy)

    assert verdict is False

    assert receipt is None

    proxy.process_payment.assert_called_once_with(patron_id="135790", amount=7.20, description="Late fees for 'Quantum Lattice'")

def test_pay_late_fees_zero_fee(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 0.0})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"id": b, "title": "Silent Orbit"})

    proxy = Mock()

    verdict, note, receipt = svc.pay_late_fees("555555", 3, payment_gateway=proxy)

    assert verdict is False

    assert receipt is None

    assert "no late fees" in note.lower()

    proxy.process_payment.assert_not_called()

def test_pay_late_fees_gateway_boom(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 4.50})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"id": b, "title": "Crystal Echo"})

    proxy = Mock()

    proxy.process_payment.side_effect = Exception("wire cut")

    verdict, note, receipt = svc.pay_late_fees("777777", 9, payment_gateway=proxy)

    assert verdict is False

    assert receipt is None

    assert "error" in note.lower()

def test_refund_ok_mock():

    proxy = Mock()

    proxy.refund_payment.return_value = (True, "Refund OK")

    verdict, note = svc.refund_late_fee_payment("txn_omega", 6.25, payment_gateway=proxy)

    assert verdict is True

    assert "refund" in note.lower() or "ok" in note.lower()

    proxy.refund_payment.assert_called_once_with("txn_omega", 6.25)

def test_refund_bad_amount_not_called():

    proxy = Mock()

    verdict, note = svc.refund_late_fee_payment("txn_sigma", -2.00, payment_gateway=proxy)

    assert verdict is False

    assert "greater than 0" in note.lower()

    proxy.refund_payment.assert_not_called()

def test_refund_overcap_not_called():

    proxy = Mock()

    verdict, note = svc.refund_late_fee_payment("txn_tau", 25.00, payment_gateway=proxy)

    assert verdict is False

    assert "exceeds maximum" in note.lower()

    proxy.refund_payment.assert_not_called()

def test_refund_gateway_boom():

    proxy = Mock()

    proxy.refund_payment.side_effect = Exception("grid offline")

    verdict, note = svc.refund_late_fee_payment("txn_phi", 8.00, payment_gateway=proxy)

    assert verdict is False

    assert "error" in note.lower()
