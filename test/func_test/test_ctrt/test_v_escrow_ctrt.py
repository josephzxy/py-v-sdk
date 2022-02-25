import asyncio
import time

import pytest

import py_v_sdk as pv
from test.func_test import conftest as cft


class TestVEscrowCtrt:
    """
    TestVEscrowCtrt is the collection of functional tests of V Escrow Contract.
    """

    ORDER_AMOUNT = 10
    RCPT_DEPOSIT_AMOUNT = 2
    JUDGE_DEPOSIT_AMOUNT = 3
    ORDER_FEE = 4
    REFUND_AMOUNT = 5
    CTRT_DEPOSIT_AMOUNT = 30

    @pytest.fixture
    def maker(self, acnt0: pv.Account) -> pv.Account:
        """
        maker is the fixture that returns the maker account used in the tests.

        Args:
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.Account: The account.
        """
        return acnt0

    @pytest.fixture
    def judge(self, acnt0: pv.Account) -> pv.Account:
        """
        judge is the fixture that returns the judge account used in the tests.

        Args:
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.Account: The account.
        """
        return acnt0

    @pytest.fixture
    def payer(self, acnt1: pv.Account) -> pv.Account:
        """
        payer is the fixture that returns the payer account used in the tests.

        Args:
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.Account: The account.
        """
        return acnt1

    @pytest.fixture
    def recipient(self, acnt2: pv.Account) -> pv.Account:
        """
        recipient is the fixture that returns the recipient account used in the tests.

        Args:
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.Account: The account.
        """
        return acnt2

    @pytest.fixture
    async def new_sys_ctrt(self, chain: pv.Chain) -> pv.SysCtrt:
        """
        new_sys_ctrt is the fixture that returns a system contract instance.

        Args:
            chain (pv.Chain): The chain object.

        Returns:
            pv.SysCtrt: The system contract instance.
        """
        return pv.SysCtrt.for_testnet(chain)

    async def _new_ctrt(
        self,
        new_sys_ctrt: pv.SysCtrt,
        maker: pv.Account,
        judge: pv.Account,
        payer: pv.Account,
        recipient: pv.Account,
        duration: int,
    ) -> pv.VEscrowCtrt:
        """
        _new_ctrt registers a new V Escrow Contract where the payer duration & judge duration
        are all the given duration.

        Args:
            new_sys_ctrt (pv.SysCtrt): The system contract instance.
            maker (pv.Account): The account of the contract maker.
            judge (pv.Account): The account of the contract judge.
            payer (pv.Account): The account of the contract payer.
            recipient (pv.Account): The account of the contract recipient.
            duration (int): The duration in seconds.

        Returns:
            pv.VEscrowCtrt: The VEscrowCtrt instance.
        """
        sc = new_sys_ctrt
        api = maker.api

        vc = await pv.VEscrowCtrt.register(
            by=maker,
            tok_id=sc.tok_id,
            duration=duration,
            judge_duration=duration,
        )
        await cft.wait_for_block()

        judge_resp, payer_resp, rcpt_resp = await asyncio.gather(
            sc.deposit(judge, vc.ctrt_id, self.CTRT_DEPOSIT_AMOUNT),
            sc.deposit(payer, vc.ctrt_id, self.CTRT_DEPOSIT_AMOUNT),
            sc.deposit(recipient, vc.ctrt_id, self.CTRT_DEPOSIT_AMOUNT),
        )
        await cft.wait_for_block()

        await asyncio.gather(
            cft.assert_tx_success(api, judge_resp["id"]),
            cft.assert_tx_success(api, payer_resp["id"]),
            cft.assert_tx_success(api, rcpt_resp["id"]),
        )
        return vc

    @pytest.fixture
    async def new_ctrt_with_ten_mins_duration(
        self,
        new_sys_ctrt: pv.SysCtrt,
        maker: pv.Account,
        judge: pv.Account,
        payer: pv.Account,
        recipient: pv.Account,
    ) -> pv.VEscrowCtrt:
        """
        new_ctrt_with_ten_mins_duration is the fixture that registers
        a new V Escrow Contract where the payer duration & judge duration
        are all 10 mins

        Args:
            new_sys_ctrt (pv.SysCtrt): The system contract instance.
            maker (pv.Account): The account of the contract maker.
            judge (pv.Account): The account of the contract judge.
            payer (pv.Account): The account of the contract payer.
            recipient (pv.Account): The account of the contract recipient.

        Returns:
            pv.VEscrowCtrt: The VEscrowCtrt instance.
        """
        ten_mins = 10 * 60
        return await self._new_ctrt(
            new_sys_ctrt,
            maker,
            judge,
            payer,
            recipient,
            ten_mins,
        )

    @pytest.fixture
    async def new_ctrt_with_five_secs_duration(
        self,
        new_sys_ctrt: pv.SysCtrt,
        maker: pv.Account,
        judge: pv.Account,
        payer: pv.Account,
        recipient: pv.Account,
    ) -> pv.VEscrowCtrt:
        """
        new_ctrt_with_ten_mins_duration is the fixture that registers
        a new V Escrow Contract where the payer duration & judge duration
        are all 5 secs.

        Args:
            new_sys_ctrt (pv.SysCtrt): The system contract instance.
            maker (pv.Account): The account of the contract maker.
            judge (pv.Account): The account of the contract judge.
            payer (pv.Account): The account of the contract payer.
            recipient (pv.Account): The account of the contract recipient.

        Returns:
            pv.VEscrowCtrt: The VEscrowCtrt instance.
        """
        five_secs = 5
        return await self._new_ctrt(
            new_sys_ctrt,
            maker,
            judge,
            payer,
            recipient,
            five_secs,
        )

    async def test_register(
        self,
        new_sys_ctrt: pv.SysCtrt,
        new_ctrt_with_ten_mins_duration: pv.VEscrowCtrt,
        maker: pv.Account,
    ) -> pv.VEscrowCtrt:
        """
        test_register tests the method register.

        Args:
            new_sys_ctrt (pv.SysCtrt): The system contract instance.
            new_ctrt_with_ten_mins_duration (pv.VEscrowCtrt): The V Escrow contract instance.
            maker (pv.Account): The account of the contract maker.

        Returns:
            pv.VEscrowCtrt: The VEscrowCtrt instance.
        """

        sc = new_sys_ctrt
        vc = new_ctrt_with_ten_mins_duration

        assert (await vc.maker).data == maker.addr.b58_str
        assert (await vc.judge).data == maker.addr.b58_str

        tok_id = await vc.tok_id
        assert tok_id.data == sc.tok_id

        ten_mins = 10 * 60
        duration = await vc.duration
        assert duration.unix_ts == ten_mins

        judge_duration = await vc.judge_duration
        assert judge_duration.unix_ts == ten_mins

        assert (await vc.unit) == (await sc.unit)

    async def test_supersede(
        self,
        new_ctrt_with_ten_mins_duration: pv.VEscrowCtrt,
        acnt0: pv.Account,
        acnt1: pv.Account,
    ) -> pv.VEscrowCtrt:
        """
        test_supersede tests the method supersede

        Args:
            new_ctrt_with_ten_mins_duration (pv.VEscrowCtrt): The V Escrow contract instance.
            acnt0 (pv.Account): The account of nonce 0.
            acnt1 (pv.Account): The account of nonce 1.

        Returns:
            pv.VEscrowCtrt: The VEscrowCtrt instance.
        """

        vc = new_ctrt_with_ten_mins_duration
        api = acnt0.api

        judge = await vc.judge
        assert judge.data == acnt0.addr.b58_str

        resp = await vc.supersede(acnt0, acnt1.addr.b58_str)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        judge = await vc.judge
        assert judge.data == acnt1.addr.b58_str
