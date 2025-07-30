import pytest
import torch
import torch.nn as nn

from sample.models.policy import PolicyValueCommon


class TestPolicyValueCommon:
    # Test hyperparameters
    BATCH_SIZE = 2
    SEQ_LEN = 3
    DEPTH = 2
    DIM = 8
    OBS_DIM = 16
    ACTION_CHOICES = [3, 4, 2]  # Three discrete action dimensions

    @pytest.fixture
    def policy_value_model(self):
        return PolicyValueCommon(
            self.OBS_DIM, self.ACTION_CHOICES, self.DIM, self.DEPTH, self.DIM * 2
        )

    @pytest.fixture
    def observation(self):
        return torch.randn(self.BATCH_SIZE, self.SEQ_LEN, self.OBS_DIM)

    @pytest.fixture
    def hidden(self):
        return torch.randn(self.BATCH_SIZE, self.DEPTH, self.DIM)

    def test_forward(self, policy_value_model, observation, hidden):
        """Test forward pass of PolicyValueCommon model."""
        # Run forward pass
        policy_dist, value, next_hidden = policy_value_model(observation, hidden)

        policy_sample = policy_dist.sample()
        assert policy_sample.shape == (
            self.BATCH_SIZE,
            self.SEQ_LEN,
            len(self.ACTION_CHOICES),
        )

        assert value.shape == (self.BATCH_SIZE, self.SEQ_LEN)
        assert next_hidden.shape == (
            self.BATCH_SIZE,
            self.DEPTH,
            self.SEQ_LEN,
            self.DIM,
        )

        # Test with different batch sizes
        single_obs = observation[:1]
        single_hidden = hidden[:1]

        single_policy_dist, single_value, single_next_hidden = policy_value_model(
            single_obs, single_hidden
        )
        single_policy_sample = single_policy_dist.sample()

        assert single_policy_sample.shape == (
            1,
            self.SEQ_LEN,
            len(self.ACTION_CHOICES),
        )
        assert single_value.shape == (1, self.SEQ_LEN)
        assert single_next_hidden.shape == (
            1,
            self.DEPTH,
            self.SEQ_LEN,
            self.DIM,
        )

        # Test distribution properties
        log_prob = policy_dist.log_prob(policy_sample)
        assert log_prob.shape == (
            self.BATCH_SIZE,
            self.SEQ_LEN,
            len(self.ACTION_CHOICES),
        )
