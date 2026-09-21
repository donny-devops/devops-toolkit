#!/usr/bin/env python3
"""dtk — DevOps Toolkit: cloud health checks, log anomaly detection, cluster triage."""
import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone


def run(args, timeout=12):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{args[0]}: not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"{args[0]}: timed out"


def check_disk(path="/"):
    try:
        u = shutil.disk_usage(path)
        pct = u.used / u.total * 100
        return {"path": path, "total_gb": round(u.total / 1e9, 1),
                "used_gb": round(u.used / 1e9, 1), "pct": round(pct, 1), "ok": pct < 90}
    except Exception as e:
        return {"path": path, "error": str(e), "ok": False}


def check_http(url, timeout=5):
    import urllib.request
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dtk/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status,
                    "latency_ms": round((time.time() - t0) * 1000), "ok": 200 <= r.status < 400}
    except Exception as e:
        return {"url": url, "error": str(e), "ok": False}


def check_ports(host, ports=(22, 80, 443, 3306, 5432, 6379)):
    opened = []
    for p in ports:
        s = socket.socket()
        s.settimeout(1.2)
        try:
            s.connect((host, p))
            opened.append(p)
        except Exception:
            pass
        finally:
            s.close()
    return opened


def cmd_doctor(a):
    print("== dtk doctor ==")
    print(f"  host: {socket.gethostname()} | platform: {platform.system()} {platform.release()}")

    d = check_disk()
    if d.get("ok") is None:
        print(f"  disk {d['path']}: {d['error']}")
    else:
        flag = "OK" if d["ok"] else "WARN >90%"
        print(f"  disk {d['path']}: {d['used_gb']}GB / {d['total_gb']}GB ({d['pct']}%)  [{flag}]")

    if platform.system() == "Linux" and os.path.exists("/proc/loadavg"):
        try:
            load = open("/proc/loadavg").read().split()[:3]
            print(f"  load average (1/5/15m): {' '.join(load)}")
        except Exception:
            pass

    if a.url:
        h = check_http(a.url)
        if "status" in h:
            print(f"  http {h['url']}: {h['status']} in {h['latency_ms']}ms  [{'OK' if h['ok'] else 'FAIL'}]")
        else:
            print(f"  http {h['url']}: {h['error']}  [FAIL]")

    if a.host:
        opened = check_ports(a.host)
        print(f"  ports {a.host}: open = {opened or 'none'}")


def cmd_logs(a):
    path = a.file
    if not os.path.exists(path):
        print(f"error: {path} not found")
        return 1
    patterns = ["error", "fatal", "exception", "traceback", "out of memory",
                "oom", "killed", "panic", "critical", "segfault"]
    counts = {p: 0 for p in patterns}
    samples = {}
    with open(path, errors="ignore") as f:
        for line in f:
            low = line.lower()
            for p in patterns:
                if p in low:
                    counts[p] += 1
                    samples.setdefault(p, line.strip()[:100])
    total = sum(counts.values())
    print(f"== dtk logs: {path} ==")
    print(f"  anomalies detected: {total}")
    for p, c in sorted(counts.items(), key=lambda x: -x[1]):
        if c:
            print(f"    {p:16s} {c:6d}  e.g. {samples.get(p, '')[:64]}")
    return 0


def cmd_audit(_a):
    print("== dtk audit ==")
    rc, out, err = run(["kubectl", "get", "pods", "--all-namespaces"])
    if rc == 127:
        print("  k8s: kubectl not found (skipping)")
    elif rc == 0:
        pods = [l for l in out.splitlines() if l and not l.startswith("NAMESPACE")]
        print(f"  k8s: {len(pods)} pods across namespaces")
    else:
        print(f"  k8s: {err[:90]}")
    rc, out, err = run(["aws", "iam", "list-users", "--max-items", "5"])
    if rc == 127:
        print("  aws: aws cli not found (skipping)")
    elif rc == 0:
        print("  aws iam: list-users succeeded")
    else:
        print(f"  aws: {err[:90]}")


def cmd_config(a):
    path = os.path.expanduser("~/.dtk.json")
    if a.init:
        data = {"created": datetime.now(timezone.utc).isoformat(), "version": "1.0.0"}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"config written: {path}")
        return
    if os.path.exists(path):
        print(open(path).read())
    else:
        print(f"no config at {path} — run 'dtk config init'")


def main():
    p = argparse.ArgumentParser(prog="dtk", description="DevOps Toolkit (health, logs, audit)")
    sub = p.add_subparsers(dest="cmd")
    d = sub.add_parser("doctor", help="system + cloud health checks")
    d.add_argument("--url", help="HTTP URL to health-check")
    d.add_argument("--host", help="host to scan common ports on")
    d.add_argument("--all", action="store_true", help="run every check")
    l = sub.add_parser("logs", help="detect anomalies in a log file")
    l.add_argument("file", help="path to log file")
    sub.add_parser("audit", help="k8s + AWS IAM resource audit (best-effort)")
    c = sub.add_parser("config", help="view/init config")
    c.add_argument("--init", action="store_true", help="create ~/.dtk.json")
    a = p.parse_args()
    if a.cmd == "doctor":
        return cmd_doctor(a)
    if a.cmd == "logs":
        return cmd_logs(a)
    if a.cmd == "audit":
        return cmd_audit(a)
    if a.cmd == "config":
        return cmd_config(a)
    p.print_help()


if __name__ == "__main__":
    sys.exit(main() or 0)
