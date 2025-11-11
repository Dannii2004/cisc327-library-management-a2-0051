import services.library_service as svc


def test_pay_late_fees_internal_success(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 4.50})
    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"title": "Omega Title"})

    class _AuroraGateway:
        def process_payment(self, patron_id=None, amount=None, description=None, **_):
            return True, "txn_aur", "Success"

    monkeypatch.setattr(svc, "PaymentGateway", _AuroraGateway, raising=True)

    ok_bit, out_msg, txn_key = svc.pay_late_fees("123456", 1)

    assert ok_bit is True

    assert "payment successful" in out_msg.lower()

    assert txn_key == "txn_aur"

def test_pay_late_fees_internal_failure(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 2.00})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"title": "Sigma Title"})

    class _OrionGateway:
        def process_payment(self, **_):
            return False, "", "Declined"

    monkeypatch.setattr(svc, "PaymentGateway", _OrionGateway, raising=True)

    ok_bit, out_msg, txn_key = svc.pay_late_fees("123456", 1)

    assert ok_bit is False

    assert "payment failed" in out_msg.lower()

    assert txn_key is None

def test_pay_late_fees_internal_exception(monkeypatch):

    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda p, b: {"fee_amount": 1.00})

    monkeypatch.setattr(svc, "get_book_by_id", lambda b: {"title": "Zeta Title"})

    class _CometGateway:
        def process_payment(self, **_):
            raise Exception("gateway down")

    monkeypatch.setattr(svc, "PaymentGateway", _CometGateway, raising=True)

    ok_bit, out_msg, txn_key = svc.pay_late_fees("123456", 1)

    assert ok_bit is False

    assert "processing error" in out_msg.lower()

    assert txn_key is None
