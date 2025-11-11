import services.library_service as svc



def test_refund_path_internal_success(monkeypatch):

    class _QuasarGateway:
        def refund_payment(self, tid, amt):
            return True, "ok"

    monkeypatch.setattr(svc, "PaymentGateway", _QuasarGateway, raising=True)

    flag_ok, txt_msg = svc.refund_late_fee_payment("txn_123", 5.00)

    assert flag_ok is True

    assert txt_msg == "ok"

def test_refund_path_internal_failure(monkeypatch):

    class _NebulaGateway:
        def refund_payment(self, tid, amt):
            return False, "declined"

    monkeypatch.setattr(svc, "PaymentGateway", _NebulaGateway, raising=True)

    flag_ok, txt_msg = svc.refund_late_fee_payment("txn_555", 3.25)

    assert flag_ok is False

    assert "refund failed" in txt_msg.lower()

    assert "declined" in txt_msg.lower()

def test_refund_path_internal_exception(monkeypatch):

    class _PulsarGateway:
        def refund_payment(self, tid, amt):
            raise Exception("network timeout")

    monkeypatch.setattr(svc, "PaymentGateway", _PulsarGateway, raising=True)

    flag_ok, txt_msg = svc.refund_late_fee_payment("txn_999", 2.00)

    assert flag_ok is False

    assert "processing error" in txt_msg.lower()
