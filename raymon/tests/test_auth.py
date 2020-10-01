import pytest

from raymon.auth import (load_secret_env,
                         save_secret,
                         verify,
                         load_secret_file)

def test_load_env(monkeypatch):
    monkeypatch.setenv('RAYMON_AUTH0_URL', 'url')
    monkeypatch.setenv('RAYMON_AUDIENCE', 'audience')
    monkeypatch.setenv('RAYMON_CLIENT_ID', 'client_id')
    monkeypatch.setenv('RAYMON_CLIENT_SECRET', 'client_secret')
    monkeypatch.setenv('RAYMON_GRANT_TYPE', 'client_credentials')
    
    secret = load_secret_env()
    
    assert secret['auth_url'] == 'url'
    assert secret['audience'] == 'audience'
    assert secret['client_id'] == 'client_id'
    assert secret['client_secret'] == 'client_secret'
    assert secret['grant_type'] == 'client_credentials'


def test_save_secret_single(tmp_path):
    
    tmp_file = tmp_path / 'secret.json'
    save_secret(project_name="testing_project", 
                auth_endpoint='http://testing-url', 
                audience='test_audience', 
                client_id="test_id", 
                client_secret="test_secret", 
                grant_type="test_grant", 
                out=tmp_file)
    
    secret = load_secret_file(project_name="testing_project", fpath=tmp_file)
    assert verify(secret)
    assert secret['auth_url'] == 'http://testing-url'
    assert secret['audience'] == 'test_audience'
    assert secret['client_id'] == 'test_id'
    assert secret['client_secret'] == 'test_secret'
    assert secret['grant_type'] == 'test_grant'
    

def test_save_secret_multiple(tmp_path):
    tmp_file = tmp_path / 'secret.json'
    save_secret(project_name="testing_project",
                auth_endpoint='http://testing-url',
                audience='test_audience',
                client_id="test_id",
                client_secret="test_secret",
                grant_type="test_grant",
                out=tmp_file)
    
    save_secret(project_name="testing_project2",
                auth_endpoint='url',
                audience='audience',
                client_id="client_id",
                client_secret="client_secret",
                grant_type="client_credentials",
                out=tmp_file)
    
    secret = load_secret_file(project_name="testing_project", fpath=tmp_file)
    assert verify(secret)
    assert secret['auth_url'] == 'http://testing-url'
    assert secret['audience'] == 'test_audience'
    assert secret['client_id'] == 'test_id'
    assert secret['client_secret'] == 'test_secret'
    assert secret['grant_type'] == 'test_grant'

    secret = load_secret_file(project_name="testing_project2", fpath=tmp_file)
    assert verify(secret)
    assert secret['auth_url'] == 'url'
    assert secret['audience'] == 'audience'
    assert secret['client_id'] == 'client_id'
    assert secret['client_secret'] == 'client_secret'
    assert secret['grant_type'] == 'client_credentials'
    
    
def test_verify():
    
    secret_good = {
        'auth_url': 'url',
        'audience': 'audience',
        'client_id': 'client_id',
        'client_secret': 'client_secret',
        'grant_type': 'client_credentials',
    }
    assert verify(secret_good)
    
    secret_bad1 = {
        'audience': 'audience',
        'client_id': 'client_id',
        'client_secret': 'client_secret',
        'grant_type': 'client_credentials'
    }
    try:
        verify(secret_bad1)
        pytest.fail("Expected Failure on auth_url key")
    except:
        pass
    
    secret_bad2 = {
        'auth_url': 'url',
        'audience': 'audience',
        'client_id': 'client_id',
        'grant_type': 'client_credentials'
    }
    try:
        verify(secret_bad2)
        pytest.fail("Expected Failure on client_secret key")
    except:
        pass
