#!/usr/bin/env python3
"""Read-only readiness checks for the three documented Phase 1 workflows.

Modes deliberately differ: VS Code is a REQUIRED tool for the documented
Nordic firmware development workflow, but it is NOT a runtime dependency of
Robot Framework or the simulator. Detection cannot prove an IDE is configured
correctly, that a firmware build is current, or that a DK is physically wired.

Run from any directory:
    python scripts/check_environment.py --mode simulator
    python scripts/check_environment.py --mode development
    python scripts/check_environment.py --mode hardware --port COM3
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(label, ok, explanation, required=True):
    status = 'PASS' if ok else ('FAIL' if required else 'INFO')
    print(f'[{status}] {label}: {explanation}')
    return bool(ok or not required)


def vscode_executable():
    """Locate the VS Code CLI; Windows installations need not be on PATH."""
    command = shutil.which('code') or shutil.which('code.cmd')
    if command:
        return command
    if os.name == 'nt':
        candidates = [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Microsoft VS Code/bin/code.cmd',
            Path(os.environ.get('ProgramFiles', '')) / 'Microsoft VS Code/bin/code.cmd',
            Path(os.environ.get('ProgramFiles(x86)', '')) / 'Microsoft VS Code/bin/code.cmd',
        ]
        return next((str(path) for path in candidates if path.is_file()), None)
    return None


def vscode_extensions(command):
    try:
        result = subprocess.run([command, '--list-extensions'], capture_output=True,
                                text=True, timeout=15, check=False)
        if result.returncode == 0:
            return set(result.stdout.lower().splitlines())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('simulator', 'development', 'hardware'),
                        default='simulator')
    parser.add_argument('--port', help='Serial port for hardware mode, e.g. COM3')
    args = parser.parse_args()
    good = True
    print(f'\nEmbedded HIL preflight — {args.mode} mode\n')
    good &= check('Python', sys.version_info >= (3, 12),
                  f'{sys.version.split()[0]} (supported baseline: Python 3.12+)')
    for module, name in [('robot', 'Robot Framework'), ('serial', 'PySerial')]:
        good &= check(name, importlib.util.find_spec(module) is not None,
                      'import available' if importlib.util.find_spec(module) else
                      'missing; run: python -m pip install -r requirements.txt')
    for file in ('config/boards.json', 'libraries/DeviceLibrary.py',
                 'libraries/serial_adapter.py', 'tests/common/01_boot_firmware.robot'):
        good &= check(file, (ROOT / file).is_file(), 'present' if (ROOT / file).is_file() else 'missing')
    if args.mode == 'development':
        code = vscode_executable()
        good &= check('VS Code', bool(code),
                      code or 'not detected; install VS Code (required for documented firmware build workflow)')
        if code:
            extensions = vscode_extensions(code)
            if extensions is None:
                print('[MANUAL] VS Code extensions: CLI could not enumerate extensions; inspect Extensions view.')
            else:
                nordic = any(item.startswith('nordic-semiconductor.nrf-connect') for item in extensions)
                good &= check('nRF Connect VS Code extension', nordic,
                              'detected' if nordic else 'not detected; install Nordic nRF Connect extension')
        for tool in ('west', 'cmake', 'ninja'):
            path = shutil.which(tool)
            print(f'[INFO] {tool}: {path or "not on this terminal PATH; may be available inside nRF Connect terminal"}')
        print('[MANUAL] Confirm SDK v3.2.0, matching toolchain, board target nrf52840dk/nrf52840,')
        print('         successful pristine build and successful flash in nRF Connect for VS Code.')
        print('         This script does NOT build, flash, or certify SDK configuration.')
    elif args.mode == 'hardware':
        good &= check('Serial port argument', bool(args.port),
                      args.port or 'missing; use --port COM3')
        if args.port and importlib.util.find_spec('serial'):
            sys.path.insert(0, str(ROOT / 'libraries'))
            try:
                from serial_adapter import SerialDevice
                device = SerialDevice(args.port)
                try:
                    status = device.request('STATUS')
                    identity = device.request('IDENTITY')
                    capabilities = device.request('CAPABILITIES')
                finally:
                    device.close()
                ready = status.get('status') == 'READY' and identity.get('board') == 'nrf52840dk'
                ready &= 'gpio' in capabilities.get('features', [])
                ready &= isinstance(capabilities.get('led_count'), int) and capabilities['led_count'] >= 1
                good &= check('Flashed DK protocol', ready,
                              json.dumps({'status': status, 'identity': identity,
                                          'capabilities': capabilities}))
            except Exception as exc:
                good &= check('Flashed DK protocol', False, str(exc))
        print('[MANUAL] Confirm the DK is powered and visually observe each LED during the Robot test.')
        print('         VS Code and SDK are NOT required to run tests on already-flashed firmware.')
    print('\nRESULT:', 'READY for selected automated checks' if good else 'NOT READY')
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
