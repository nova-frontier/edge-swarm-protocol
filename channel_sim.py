"""Seeded discrete-event broadcast channel probe; not a swarm policy benchmark."""
import argparse, json, math, random


def finite(value, name, low=0):
    if not math.isfinite(value) or value < low:
        raise ValueError(f"{name} must be finite and >= {low}")


def simulate(
    nodes=3,
    rounds=5,
    seed=7,
    loss=0,
    latency_ms=0,
    jitter_ms=0,
    bandwidth_bps=10000,
    payload_bytes=64,
    interval_ms=100,
    horizon_ms=5000,
    blackout=None,
):
    for v, name, minimum in [
        (nodes, "nodes", 2),
        (rounds, "rounds", 1),
        (payload_bytes, "payload_bytes", 1),
    ]:
        if isinstance(v, bool) or not isinstance(v, int) or v < minimum:
            raise ValueError(f"{name} must be integer >= {minimum}")
    for v, n in [
        (loss, "loss"),
        (latency_ms, "latency_ms"),
        (jitter_ms, "jitter_ms"),
        (bandwidth_bps, "bandwidth_bps"),
        (interval_ms, "interval_ms"),
        (horizon_ms, "horizon_ms"),
    ]:
        finite(v, n)
    if loss > 1 or bandwidth_bps <= 0 or horizon_ms <= 0:
        raise ValueError("loss <= 1; bandwidth and horizon > 0 required")
    if blackout is not None:
        start, end = blackout
        finite(start, "blackout start")
        finite(end, "blackout end")
        if end <= start:
            raise ValueError("blackout end must exceed start")
    rng = random.Random(seed)
    ready = [0.0] * nodes
    events = []
    delivered = dropped = late = 0
    delays = []
    for r in range(rounds):
        generated = r * interval_ms
        for sender in range(nodes):
            for receiver in range(nodes):
                if sender == receiver:
                    continue
                tx = max(generated, ready[sender])
                end = tx + payload_bytes * 8 / bandwidth_bps * 1000
                ready[sender] = end
                arrival = end + latency_ms + rng.uniform(0, jitter_ms)
                black = blackout is not None and (
                    blackout[0] <= tx < blackout[1]
                    or blackout[0] <= arrival < blackout[1]
                )
                if rng.random() < loss or black:
                    status = "dropped"
                    dropped += 1
                elif arrival > horizon_ms:
                    status = "late"
                    late += 1
                else:
                    status = "delivered"
                    delivered += 1
                    delays.append(arrival - generated)
                events.append(
                    {
                        "round": r,
                        "sender": sender,
                        "receiver": receiver,
                        "generated_ms": generated,
                        "tx_start_ms": tx,
                        "arrival_ms": arrival,
                        "status": status,
                    }
                )
    return {
        "scope": "synthetic_channel_probe_only",
        "seed": seed,
        "attempted": len(events),
        "delivered": delivered,
        "dropped": dropped,
        "late": late,
        "bytes_scheduled": len(events) * payload_bytes,
        "delivery_fraction": delivered / len(events),
        "mean_delivered_latency_ms": sum(delays) / len(delays) if delays else None,
        "events": events,
        "model": "Each sender has one serialized uplink; blackout drops packets at send/arrival. No retransmission or physical robot model.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in [
        ("nodes", 3),
        ("rounds", 5),
        ("seed", 7),
        ("payload-bytes", 64),
    ]:
        p.add_argument("--" + name, type=int, default=default)
    for name, default in [
        ("loss", 0),
        ("latency-ms", 0),
        ("jitter-ms", 0),
        ("bandwidth-bps", 10000),
        ("interval-ms", 100),
        ("horizon-ms", 5000),
    ]:
        p.add_argument("--" + name, type=float, default=default)
    p.add_argument("--blackout", type=float, nargs=2, metavar=("START_MS", "END_MS"))
    a = p.parse_args()
    try:
        print(json.dumps(simulate(**vars(a)), indent=2, allow_nan=False))
    except ValueError as e:
        p.error(str(e))


if __name__ == "__main__":
    main()
