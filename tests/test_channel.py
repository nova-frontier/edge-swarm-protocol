import unittest
from channel_sim import simulate


class ChannelTests(unittest.TestCase):
    def test_ideal_accounting(self):
        r = simulate()
        self.assertEqual(r["attempted"], 30)
        self.assertEqual(r["delivered"], 30)

    def test_full_loss_and_determinism(self):
        self.assertEqual(simulate(loss=1)["delivered"], 0)
        self.assertEqual(simulate(loss=0.3), simulate(loss=0.3))

    def test_bandwidth_creates_queue_and_late(self):
        r = simulate(bandwidth_bps=1, horizon_ms=1)
        self.assertEqual(r["late"], r["attempted"])
        self.assertIsNone(r["mean_delivered_latency_ms"])

    def test_blackout(self):
        self.assertEqual(simulate(blackout=[0, 100000])["dropped"], 30)

    def test_invalid_input(self):
        for args in [
            {"nodes": 1},
            {"loss": 1.1},
            {"bandwidth_bps": 0},
            {"blackout": [3, 2]},
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                simulate(**args)


if __name__ == "__main__":
    unittest.main()
