"""OOF 실수 분석: run 별·구간별 F1 / 잘못 판정(FP) / 놓침(FN), 틀린 행 보기, test 제출 차이.

python analyze.py --y y.npy --oof runs/A/oof.npy runs/B/oof.npy --groups g.npy
"""
import argparse
import os

import numpy as np
import pandas as pd


def load_arr(spec):
    if ":" in spec and spec.rsplit(":", 1)[0].endswith(".csv"):
        path, col = spec.rsplit(":", 1)
        return pd.read_csv(path)[col].values
    if spec.endswith(".npy"):
        return np.load(spec, allow_pickle=True)
    if spec.endswith(".pkl"):
        return pd.read_pickle(spec).values.ravel()
    raise ValueError(f"읽을 수 없는 형식: {spec}")


def best_f1(y, p):
    """p >= 기준값을 양성으로 볼 때 F1 이 가장 높은 (F1, 기준값). 같은 값끼리는 함께 자름."""
    order = np.argsort(-p, kind="mergesort")
    ps, ys = p[order], y[order]
    tp = np.cumsum(ys)
    f1 = 2 * tp / (np.arange(1, len(p) + 1) + ys.sum())
    ok = np.r_[ps[1:] != ps[:-1], True]
    i = int(np.argmax(np.where(ok, f1, -1)))
    return float(f1[i]), float(ps[i])


def counts(y, pred):
    tp = int((pred & y).sum()); fp = int((pred & (1 - y)).sum()); fn = int(((1 - pred) & y).sum())
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else float("nan")
    return dict(F1=round(f1, 5), 맞힘=tp, 잘못판정=fp, 놓침=fn, 양성=int(y.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--y", required=True)
    ap.add_argument("--oof", nargs="+", required=True)
    ap.add_argument("--thr", type=float)
    ap.add_argument("--groups")
    ap.add_argument("--exclude-mask")
    ap.add_argument("--show-errors", action="store_true")
    ap.add_argument("--features")
    ap.add_argument("--cols", default="")
    ap.add_argument("--max-rows", type=int, default=40)
    ap.add_argument("--test-csv", nargs="*", default=[])
    a = ap.parse_args()

    y = load_arr(a.y).astype(int)
    groups = load_arr(a.groups) if a.groups else None
    excl = load_arr(a.exclude_mask).astype(bool) if a.exclude_mask else None

    rows, preds = [], {}
    for path in a.oof:
        name = os.path.basename(os.path.dirname(os.path.abspath(path))) or path
        p = np.load(path)
        thr = a.thr if a.thr is not None else best_f1(y, p)[1]
        pred = (p >= thr).astype(int)
        preds[name] = (p, pred, thr)
        rows.append(dict(run=name, 구간="전체", 기준값=round(thr, 4), **counts(y, pred)))
        if excl is not None:
            m = ~excl
            f, t2 = best_f1(y[m], p[m])
            rows.append(dict(run=name, 구간="제외 구간 뺌(기준값 다시)", 기준값=round(t2, 4), **counts(y[m], (p[m] >= t2).astype(int))))
        if groups is not None:
            for gv in pd.unique(groups):
                m = groups == gv
                rows.append(dict(run=name, 구간=f"그룹 {gv}", 기준값=round(thr, 4), **counts(y[m], pred[m])))
    print(pd.DataFrame(rows).to_string(index=False))

    if a.show_errors:
        name = next(iter(preds))
        p, pred, thr = preds[name]
        err = np.where(pred != y)[0]
        print(f"\n== {name} 틀린 행 {len(err)}개 (기준값 {thr:.4f}) — 처음 {a.max_rows}개")
        df = pd.DataFrame({"행": err, "정답": y[err], "확률": p[err].round(3)})
        if groups is not None:
            df["그룹"] = groups[err]
        for other, (po, _, _) in list(preds.items())[1:]:
            df[other] = po[err].round(3)
        if a.features:
            X = pd.read_pickle(a.features) if a.features.endswith(".pkl") else pd.read_csv(a.features)
            cols = [c for c in a.cols.split(",") if c] or list(X.columns[:10])
            df = pd.concat([df.reset_index(drop=True), X.iloc[err][cols].reset_index(drop=True)], axis=1)
        print(df.head(a.max_rows).round(3).to_string(index=False))

    if len(a.test_csv) >= 2:
        subs = {os.path.basename(f): pd.read_csv(f) for f in a.test_csv}
        names = list(subs)
        base = subs[names[0]]
        idc, pc = base.columns[0], base.columns[1]
        print("\n== test 판정 수:", {n: int((s[pc] == s[pc].max()).sum()) for n, s in subs.items()})
        for n in names[1:]:
            m = base.merge(subs[n], on=idc, suffixes=("_a", "_b"))
            d = m[m[pc + "_a"] != m[pc + "_b"]]
            print(f"   {names[0]} vs {n}: 다른 행 {len(d)}개", d[idc].tolist()[:30])


if __name__ == "__main__":
    main()
