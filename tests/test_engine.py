import json
from pathlib import Path
import pytest

from claimcheck.engine import load_policy, verify_claim

ROOT = Path(__file__).resolve().parents[1]


def load_cases():
    return json.loads((ROOT / 'examples' / 'synthetic_cases.json').read_text(encoding='utf-8'))


def test_all_synthetic_cases_match_expected_status():
    policy = load_policy(ROOT / 'claimcheck' / 'policies.json')
    cases = load_cases()
    assert len(cases) >= 10
    for case in cases:
        report = verify_claim(case, policy)
        assert report['status'] == case['expected_status'], (case['claim_id'], case['description'], report)


def test_duplicate_document_type_is_reported():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-003'))
    assert 'death_certificate' in report['duplicate_document_types']


def test_mismatch_includes_document_evidence():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-004'))
    mismatch = next(x for x in report['field_mismatches'] if x['field'] == 'deceased_name')
    assert {x['document_id'] for x in mismatch['observations']} == {'D1', 'D2'}


def test_unknown_claim_type_does_not_apply_rules():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-009'))
    assert report['status'] == 'REVIEW_REQUIRED'
    assert report['missing_documents'] == []


def test_unreadable_required_field_is_flagged_for_review():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-010'))
    assert report['status'] == 'REVIEW_REQUIRED'
    assert any(x['document_id'] == 'D2' and x['field'] == 'date_of_death' for x in report['missing_or_unreadable_fields'])


def test_unknown_document_type_is_flagged():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-011'))
    assert report['status'] == 'REVIEW_REQUIRED'
    assert report['unrecognised_document_types'] == ['mystery_document']


def test_invalid_confidence_is_flagged():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-012'))
    assert report['status'] == 'REVIEW_REQUIRED'
    assert report['invalid_confidence_metadata'][0]['value'] == 2.0


def test_empty_required_fields_in_present_documents_are_flagged():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-013'))
    assert report['status'] == 'REVIEW_REQUIRED'
    assert len(report['missing_or_unreadable_fields']) == 4


def test_equivalent_date_formats_do_not_create_mismatch():
    report = verify_claim(next(c for c in load_cases() if c['claim_id'] == 'SYN-014'))
    assert report['status'] == 'CHECKS_PASSED'
    assert not any(x['field'] == 'date_of_death' for x in report['field_mismatches'])


def test_confidence_above_one_is_not_accepted_as_valid():
    case = {'claim_id':'BAD-1','claim_type':'nominee','documents':[
        {'document_id':'1','document_type':'claim_form','fields':{'deceased_name':'A','date_of_death':'2026-01-01'},'field_confidence':{'deceased_name':1.5}},
        {'document_id':'2','document_type':'death_certificate','fields':{'deceased_name':'A','date_of_death':'2026-01-01'}},
        {'document_id':'3','document_type':'nominee_kyc','fields':{'claimant_name':'B'}}
    ]}
    report = verify_claim(case)
    assert report['status'] == 'REVIEW_REQUIRED'


def test_malformed_documents_input_is_rejected():
    with pytest.raises(ValueError):
        verify_claim({'claim_id':'BAD-2','claim_type':'nominee','documents':'not-a-list'})
