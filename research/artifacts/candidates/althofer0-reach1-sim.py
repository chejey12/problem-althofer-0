"""
althofer-0: 隨機 Collatz ±1 變體的計算實驗 (candidate-only, bounded)
問題: 從任意奇正整數 n 開始, 每步以 1/2 機率選 odd(3n+1) 或 odd(3n-1),
      證明最終到達 1 的機率為 1。

研究價值: 建立大規模模擬證據 (bounded, exact integer arithmetic),
量化到達 1 的步數分佈、漂移率、以及尋找「發散軌道」的存在性證據。
這是 math-computation 路線的第一個有界實驗。

數學背景: 每步 n -> odd(3n±1)。注意 3n±1 都是偶數, odd part 至少把 2 除去。
log n 期望變化: E[log odd(3n±1)] ≈ log 3 - E[v2] * log 2, E[v2] = 2 (幾何分布),
所以平均每次縮小 log n 約 log 3 - 2 log 2 = log(3/4) < 0 → 直覺上收斂到 1。
嚴格證明 (機率 1) 是開放問題, 但可以建立強計算證據。
"""
import random
import json
import hashlib
from datetime import datetime, timezone

SEED = 20260915
MAX_STEPS = 200000
SAMPLES = 50000
RANGES = [(3, 1000), (1001, 100000), (100001, 10**7), (10**7 + 1, 10**9)]


def odd_part(m: int) -> int:
    return m >> ((m & -m).bit_length() - 1)


def steps_to_one(n: int, rng: random.Random) -> int:
    steps = 0
    while n != 1:
        n = odd_part(3 * n + 1) if rng.random() < 0.5 else odd_part(3 * n - 1)
        steps += 1
        if steps > MAX_STEPS:
            return -1
    return steps


def main():
    rng = random.Random(SEED)
    results = {}
    all_max_steps = 0
    failures = []
    total_steps = 0
    count = 0
    for lo, hi in RANGES:
        bucket_steps = []
        for _ in range(SAMPLES // len(RANGES)):
            n = rng.randrange(lo, hi + 1) * 2 + 1  # 奇數
            s = steps_to_one(n, rng)
            if s < 0:
                bucket_steps.append(None)
                failures.append(n)
            else:
                bucket_steps.append(s)
                total_steps += s
                count += 1
                all_max_steps = max(all_max_steps, s)
        ok = [s for s in bucket_steps if s is not None]
        results[f'{lo}-{hi}'] = {
            'samples': len(bucket_steps),
            'reached1': len(ok),
            'stuck': len(bucket_steps) - len(ok),
            'mean_steps': round(sum(ok) / len(ok), 2) if ok else None,
            'max_steps': max(ok) if ok else None,
        }
    summary = {
        'experiment': 'althofer-0 random-collatz reach-one simulation',
        'seed': SEED,
        'max_steps_per_traj': MAX_STEPS,
        'samples_total': SAMPLES,
        'buckets': results,
        'global_max_steps': all_max_steps,
        'unreached_within_budget': len(failures),
        'failure_samples': failures[:10],
        'python': '3.11', 'random_module': 'Mersenne Twister',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
        'note': ('Expected log-drift per step is log3 - 2*log2 = log(3/4) < 0, '
                 'consistent with convergence; finite simulation cannot establish probability-1 claim.'),
    }
    out = json.dumps(summary, ensure_ascii=False, indent=1)
    print(out)
    with open('/tmp/althofer0_exp1.json', 'w') as f:
        f.write(out)


if __name__ == '__main__':
    main()