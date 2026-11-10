*** Settings ***
Documentation    Optional features demonstrate intentional SKIP rather than false PASS.
Resource         ../../resources/device.resource
Suite Setup      Connect To Device
Suite Teardown   Disconnect From Device

*** Test Cases ***
Accelerometer Is Optional
    [Tags]    optional    conditional    regression
    Require Device Feature    accelerometer
    Fail    Implement accelerometer assertions when the firmware supports this feature

External Actuator Is Optional
    [Tags]    optional    conditional    regression
    Require Device Feature    external_actuator
    Fail    Implement fixture tests when external actuation is available
