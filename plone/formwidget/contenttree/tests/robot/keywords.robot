*** Settings ***

Documentation  *WARNING* This resource is not stable yet and keywords may be
...            renamed, removed or relocated without notice.

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

*** Variables ***


*** Keywords ***
Wait Until ContentTree Finished Loading
    Wait Until Page Does Not Contain  css=div.contenttreeWidget .wait

Click Add In ContentTree Widget
    [Arguments]  ${field_id}
    Wait Until Element Is Visible  css=#${field_id}-widgets-query + input.searchButton
    Click Button  css=#${field_id}-widgets-query + input.searchButton
    Wait Until ContentTree Finished Loading

Open Folderish In ContentTree
    [Documentation]  Returns the current title, which can be used as parent.
    [Arguments]  ${title}  ${parent}=${EMPTY}
    Run Keyword If  '${parent}'
    ...        Click Element  xpath=//div[contains(@class, 'contenttreeWidget')]//li[.//span[text()='${parent}']]//li//span[text()='${title}']/..
    ...  ELSE  Click Element  xpath=//div[contains(@class, 'contenttreeWidget')]//li//span[text()='${title}']/..
    Wait Until ContentTree Finished Loading
    [Return]  ${title}

Choose Item With Title In ContentTree
    [Arguments]  ${title}
    Wait Until Page Contains Element  xpath=//div[contains(@class, 'contenttreeWidget')]//li//span[text()='${title}']/..
    Scroll Element Into View  xpath=//div[contains(@class, 'contenttreeWidget')]//li//span[text()='${title}']/..
    Click Element  xpath=//div[contains(@class, 'contenttreeWidget')]//li//span[text()='${title}']/..


Item With Title Cannot Be Chosen In ContentTree
    [Arguments]  ${title}
    Click Element  xpath=//div[contains(@class, 'contenttreeWidget')]//li//span[text()='${title}']/..
    ${success} =  Run Keyword And Return Status  Wait until keyword succeeds  10s  1s  Page Should Contain Element  sizzle=div.contenttreeWidget li.navTreeCurrentItem span:contains(${title})
    Should Not Be True  ${success}  The item with title ${title} should not have been able to chosen.

Confirm Item Selection In ContentTree
    Click Element  css=input.contentTreeAdd

Get Found Item Count In ContentTree
    ${value} =  Get Element Count  css=.contenttreeWidget li
    [Return]  ${value}