import pytest
import torch

from src.sample.models.components.qlstm import QLSTM, scan

BATCH = 4
DEPTH = 8
DIM = 16
DIM_FF_HIDDEN = 32
LEN = 64
DROPOUT = 0.1


class TestScan:
    def test_scan(self):
        a = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
        b = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
        expected = torch.tensor([[1, 4, 15, 64, 325, 1956, 13699, 109600]])
        for i in range(1, 9):
            torch.allclose(scan(a[:, :i], b[:, :i]), expected[:, :i])


class TestQLSTM:
    @pytest.fixture
    def qlstm(self):
        qlstm = QLSTM(DEPTH, DIM, DIM_FF_HIDDEN, DROPOUT)
        return qlstm

    def test_qlstm(self, qlstm):
        x_shape = (BATCH, LEN, DIM)
        x = torch.randn(*x_shape)
        hidden_shape = (BATCH, DEPTH, LEN, DIM)
        hidden = torch.randn(*hidden_shape)

        x, hidden = qlstm(x, hidden[:, :, -1, :])
        assert x.shape == x_shape
        assert hidden.shape == hidden_shape

        x, hidden = qlstm(x, hidden[:, :, -1, :])
        assert x.shape == x_shape
        assert hidden.shape == hidden_shape
