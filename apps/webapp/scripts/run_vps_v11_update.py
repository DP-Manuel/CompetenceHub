"""Bound private V1 -> V1.1 update; no installer or historical resume."""
import argparse
import importlib.util
from pathlib import Path
import re

spec=importlib.util.spec_from_file_location('v11_operator',Path(__file__).with_name('run_vps_update.py'))
operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)
operator.configure_v11()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true');parser.add_argument('--quiet',action='store_true')
    parser.add_argument('--source',required=True);parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args();args.resume=''
    try:operator.main(args)
    except BaseException as error:
        code=str(error) if isinstance(error,operator.backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)) else type(error).__name__
        print('VPS_V11_UPDATE=STOP CODE='+code+' NO_AUTOMATIC_RETRY=TRUE',flush=True)
        raise SystemExit(1) from None
