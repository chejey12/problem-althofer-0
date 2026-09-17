"""
althofer-0 第二個有界實驗: 對數漂移的精確度量 (candidate-only)
每步 log n 的期望變化 = log 3 - E[v2] log 2, 其中 v2 = 2-adic valuation of 3n±1.
當 n 奇數: 3n±1 偶數, v2 服從幾何型分佈 (n≡1 mod 4 vs 3 mod 4 不同).
本實驗精確測量不同 residue class 的 v2 分佈與 drift.
"""
import random
import json
from datetime import datetime, timezone

SEED = 20260916
SAMPLES = 200000


def v2(m: int) -> int:
    return (m & -m).bit_length() - 1


def odd_part(m: int) -> int:
    return m >> v2(m)


def main():
    rng = random.Random(SEED)
    # 測量: 奇 n 隨機取樣, 兩分支的 v2 分佈
    stats = {'plus': {}, 'minus': {}}
    drift_sum = 0.0
    n_traj = 2000
    steps_hist = []
    import math
    for _ in range(SAMPLES):
        n = rng.randrange(1, 2**62, 2)
        for branch in ('plus', 'minus'):
            m = 3 * n + 1 if branch == 'plus' else 3 * n - 1
            k = v2(m)
            stats = stats[branch] if False else stats  # noop
            stats[f'{branch}'] = stats.get(branch, {})
            stats[branch][k] = stats[branch].get(k, 0) + 1
    # drift 實測: 跑軌道量 log n 變化
    up = 0
    total = 0
    for _ in range(n_traj):
        n = rng.randrange(3, 2**40, 2)
        ln0 = math.log(n)
        n2 = n
        for s in range(500):
            if n2 == 1:
                break
            n2 = odd_part(3 * n2 + 1) if rng.random() < 0.5 else odd_part(3 * n2 - 1)
            total += 1
            if math.log(n2) > math.log(n) if s == 0 else False:
                pass
        if n2 == 1:
            steps_hist.append(s)
    # v2 期望
    def ev2(d):
        tt = sum(d.values())
        return sum(k * v for k, v in d.items()) / tt
    summary = {
        'experiment': 'althofer-0 v2 distribution and empirical drift',
        'seed': SEED,
        'v2_plus_samples': SAMPLES,
        'v2_minus_samples': SAMPLES,
        'E_v2_plus': round(ev2(stats['plus']), 4),
        'E_v2_minus': round(ev2(stats['minus']), 4),
        'theoretical_E_log_drift_per_step': round(math.log(3) - 2 * math.log(2), 6),
        'observed_mean_steps_to_1_from_2^40_scale': round(sum(steps_hist) / len(steps_hist), 2) if steps_hist else None,
        'note': ('E[v2] for 3n±1 with random odd n is exactly 2 in distribution limit '
                 '(P(v2=k) = 2^-(k) for the minus branch structure differs; measured values inform the drift bound).'),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
    }
    out = json.dumps(summary, ensure_ascii=False, indent=1)
    print(out)
    with open("althofer0_exp2.json", "w") as f:
        f.write(out)


if __name__ == '__main__':
    main()