import pytest
from griddot.provision_keycloak import wait_for_keycloak_to_start, get_realms
from tests.provision_keycloak_tests import wait_for_keycloak_and_get_token, build_keycloak_images, run_keycloak


def setup_keycloak_with_provisioner(clean, build_images):
    if build_images:
        build_keycloak_images()

    if clean:
        run_keycloak("dev-with-provisioner.yaml")


def test_provisioner():
    setup_keycloak_with_provisioner(True, False)
    url, token = wait_for_keycloak_and_get_token("https://localhost:9443")

    realms = get_realms(url, token)
    realms_names = [realm["realm"] for realm in realms]
    assert len(realms) == 2, "No realms found in Keycloak"
    assert "master" in realms_names, "Master realm not found"
    assert "platform" in realms_names, "Platform realm not found"
