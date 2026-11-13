import hashlib
import importlib.util
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'apps/webapp/src/competence_hub_api/portal_ui'
PINS={
    'datepicker-v134.js':'e41523183662ff9708cdda4d5d34de96b415303f161d7d0e7859bcee6f9d0ba4',
    'datepicker-de-v134.js':'841b3980a71ad33d56d8bd13e0e7eea0e5e3389413575ade92cc18f6f59487a4',
    'datepicker-v134.css':'15cb239e7e66edbd2382800ebeda386183d59106f9f56c968728177e5c987f00',
    'datepicker-license.txt':'fc128e54c03aa96a27de02d0bb9c468a6869faca42c62942abcdffa25eaa3810',
}


def test_vendored_calendar_dependency_is_exact_and_has_license():
    for name,digest in PINS.items():assert hashlib.sha256((ASSETS/name).read_bytes()).hexdigest()==digest
    assert 'Permission is hereby granted' in (ASSETS/'datepicker-license.txt').read_text(encoding='utf8')
    assert 'http' not in (ASSETS/'datepicker-de-v134.js').read_text(encoding='utf8')


def test_committed_export_includes_exact_dependency_without_allowing_arbitrary_text():
    spec=importlib.util.spec_from_file_location('v12_release_test',ROOT/'scripts/webapp_release_source.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    prefix='apps/webapp/src/competence_hub_api/portal_ui/'
    for name in PINS:assert source.destination(prefix+name)=='package-source/src/competence_hub_api/portal_ui/'+name
    for name in ('passwords.txt','key.txt','database.dump','../private.txt'):
        assert source.destination(prefix+name) is None


def test_dependency_hashes_survive_windows_git_checkout():
    paths=['apps/webapp/src/competence_hub_api/portal_ui/'+name for name in PINS]
    result=subprocess.run(['git','-C',str(ROOT),'check-attr','eol','--',*paths],capture_output=True,text=True,check=True)
    assert len(result.stdout.splitlines())==4
    assert all(line.endswith(': eol: lf') for line in result.stdout.splitlines())
