# ============================================================================
# EXAMPLE ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s imio.schedule -t test_example.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src imio.schedule.testing.IMIO_SCHEDULE_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/imio/schedule/tests/robot/test_example.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a member I want to be able to log into the website
  [Documentation]  Example of a BDD-style (Behavior-driven development) test.
  Log in as admin


*** Keywords *****************************************************************

Suite Setup
    Open test browser
    Log in as admin

Log in as admin
    Go to  ${PLONE_URL}/login
    Input text  id=__ac_name  test-user
    Input password  id=__ac_password  secret
    Click Button  submit
