Products.MeetingLalouviere Changelog
====================================

The Products.MeetingCommunes version must be the same as the Products.PloneMeeting version

4.2.14 (2025-05-28)
-------------------

- Fixed transition `Propose to budget reviewer` as it it not managed by
  `MeetingConfig.itemWFValidationLevels`, we have to manage it in
  `MeetingItemMLLWorkflowConditions.mayCorrect`.
  [gbastien]

4.2.13 (2025-05-27)
-------------------

- Removed override of `MeetingConfig.MEETING_STATES_ACCEPTING_ITEMS`
  that does not exist anymore.
  [gbastien]
- Changed group linked to item `proposed_to_dg` WF state to use
  `direction-generale-validation`.
  [gbastien]
- Adapted code to manage `referent-integrite` group for which the WF does not
  include the `proposed_to_dg` state, but only
  `itemcreated/proposed_to_director/validated`.
  [gbastien]

4.2.12 (2024-11-07)
-------------------

- Adapted `meetingitem_edit.pt` and `meetingitem_view.pt` to include recent
  changes from `PloneMeeting` (new fields `restrictedCopyGroups`,
  `meetingDeadlineDate` and `emergencyMotivation`).
  [gbastien]

4.2.11 (2024-07-05)
-------------------

- Overrided `test_pm_ItemDecidedWithReturnToProposingGroup` as it is possible to
  send an item back to `itempublished` from `returned_to_proposing_group`.
  [gbastien]
- Remove overrided `test_pm_ItemDecidedWithReturnToProposingGroup` and
  add a specific test `test_pm_ItemDecidedWithReturnToProposingGroupCouncil`
  [aduchene]
- Changed adapters.CUSTOM_RETURN_TO_PROPOSING_GROUP_MAPPINGS to be different in meeting-config-council
  [aduchene]

4.2.10 (2024-03-28)
-------------------

- Revert `CUSTOM_RETURN_TO_PROPOSING_GROUP_MAPPINGS['backTo_itemfrozen_from_returned_to_proposing_group']`.
  [aduchene]


4.2.9 (2024-03-25)
------------------

- Fixed POD templates `deliberation.odt` and `deliberation_recto_verso.odt`,
  `MeetingItem.getCertifiedSignatures` is no more an adaptable method
  (removed `.adapted()`).
  [gbastien]
- Cleanup and isort.
  [gbastien]
- Fixed issue related to item send to proposing group when meeting is in published state.
  [aduchene]

4.2.8 (2024-01-05)
------------------

- Fixed issue with budgetreviewer that could not add annex when item was
  in proposed_to_budgetreviewer state.
  [aduchene]


4.2.7 (2023-10-13)
------------------

- Adapted code as field `MeetingConfig.useCopies` was removed.
  [gbastien]
- Fix issue with alderman that could see items at the proposed_to_dg state.
  [aduchene]

4.2.6 (2023-08-17)
------------------

- Add a WFA to enable "Alderman cannot send item back..." so it doesn't
  break all tests.
  [aduchene]

4.2.5 (2023-08-17)
------------------

- Alderman cannot send item back to all previous validation levels.
  Use a new custom method `MeetingItemMLLWorkflowConditions.may_user_send_back`
  that will probably be backported to PloneMeeting.
  [aduchene]

4.2.4 (2023-06-02)
------------------

- Fix providedFollowUp quickEdit access.
  [odelaere]
- Fix searchproposedtobudgetreviewer label.
  [odelaere]


4.2.3 (2023-05-24)
------------------

- Fix get_all_committees_items.
  [aduchene]

4.2.2 (2023-05-12)
------------------

- Fix get_all_committees_items.
  [odelaere]


4.2.1 (2023-05-02)
------------------

- Revert `set correct migration profile_name`.
  [odelaere]


4.2.0 (2023-05-02)
------------------

- Revert access rights of field "observations" to default from MeetingCommunes.
  [odelaere]
- set correct migration profile_name.
  [odelaere]
- adapt vote config in migration.
  [odelaere]
- Fixed translation of `Data that will be used on new item` on `meetingitem_view.pt`.
  [gbastien]


4.2.0rc4 (2023-04-19)
---------------------

- Apply todos after migration.
  [odelaere]


4.2.0rc3 (2023-04-18)
---------------------

- Apply to do portlet searches in migration.
  [odelaere]


4.2.0rc2 (2023-04-18)
---------------------

- Ensure 'decisionSuite' is removed from used items attributes.
  [odelaere]
- Fix custom WFA back transitions labels.
  [odelaere]


4.2.0rc1 (2023-04-14)
---------------------

- Fix missing getFollowUp index.
  [odelaere]
- Deleted neededFollowUp.
  [odelaere]


4.2.0b3 (2023-04-13)
--------------------

- Added full committees to apply.
  [odelaere]


4.2.0b2 (2023-04-06)
--------------------

- Adapt MLLItemDocumentGenerationHelperView.
  [odelaere]
- Fix searchproposedtodirector translation.
  [odelaere]


4.2.0b1 (2023-04-05)
--------------------

- Added a `IMeetingLalouviereLayer BrowserLayer`.
  [odelaere]

4.2.0a6 (2023-04-04)
--------------------

- get_all_commission_items.
  [odelaere]
- Fine tuning migration.
  [odelaere]


4.2.0a5 (2023-03-28)
--------------------

- Fix item references.
  [odelaere]


4.2.0a4 (2023-03-24)
--------------------

- Fix meetingconfig migration.
  [odelaere]
- Fix search configurations.
  [odelaere]


4.2.0a3 (2023-03-17)
--------------------

- Fix commission - committee bindings.
  [odelaere]


4.2.0a2 (2023-03-08)
--------------------

- Fix migration error because some object are empty.
  [odelaere]


4.2.0-alpha1 (2023-03-06)
-------------------------

- Migrated to 4.2.
  [odelaere]


4.1.6.5 (2021-05-27)
--------------------

- Fix onItemLocalRolesUpdated for commissionTranscript.
  [odelaere]


4.1.6.4 (2021-05-20)
--------------------

- Fixed MeetingItem reference for council items.
  [odelaere]
- Fixed print method for commission.
  [odelaere]


4.1.6.3 (2021-04-16)
--------------------

- Updated with latests MC backports.
  [odelaere]


4.1.6.2 (2021-04-13)
--------------------

- Fix commission label.
  [odelaere]
- Rollback Fix commission label. Finally we'll use the field real name and drop this customization.
  [odelaere]


4.1.6.1 (2021-04-12)
--------------------

- Release migration to classifiers.
  [odelaere]


4.1.6.0 (2021-04-12)
--------------------

- Use classifiers instead of categories for commissions.
  [odelaere]
- Removed old DEF plug in because they use rest api endpoint now.
  [odelaere]


4.1.5.3 (2021-01-27)
--------------------

- Fix alderman access to validated items.
  [odelaere]


4.1.5.2 (2021-01-14)
--------------------

- Fix commission on 01/01/21
  [odelaere]


4.1.5.1 (2020-08-25)
--------------------

- Fix commission order.
  [odelaere]


4.1.5 (2020-08-21)
------------------

- Adapted code and tests regarding DX meetingcategory.
  [gbastien]
- Adapted templates regarding last changes in Products.PloneMeeting.
  [gbastien]


4.1.4.4 (2020-06-24)
--------------------

- Fix WF conditions.
  [odelaere]


4.1.4.3 (2020-06-24)
--------------------

- Display `groupsInCharge` on the item view : when field `MeetingItem.groupsInCharge` is used, from the proposingGroup when
  `MeetingConfig.includeGroupsInChargeDefinedOnProposingGroup=True` or from the category when
  `MeetingConfig.includeGroupsInChargeDefinedOnCategory=True`.
  Set `autoInclude=True` by default instead `False` for `MeetingItem.getGroupsInCharge`


4.1.4.2 (2020-06-09)
--------------------

- Added DecisionSuite on item views.
  [odelaere]


4.1.4.1 (2020-06-04)
--------------------

- Use the UID from prod for DEF instead of trying to find it.
  [odelaere]


4.1.4 (2020-06-04)
------------------

- Fix for DEF intranet.
  [odelaere]


4.1.3 (2020-06-03)
------------------

- Fixed mayGenerateFinanceAdvice.
  [duchenean]


4.1.2 (2020-06-03)
------------------

- Fix budget reviewers access.
  [odelaere]


4.1.1 (2020-05-27)
------------------

- Fix sendMailIfRelevant.
  [odelaere]


4.1.1rc3 (2020-05-08)
---------------------

- Fixed printing methods.
  [duchenean]


4.1.1rc2 (2020-04-29)
---------------------

- Fixed item reference method.
  [odelaere]
- updated migration script to patch new workflow and its adaptations properly.
  [odelaere]


4.1.1rc1 (2020-04-24)
---------------------
- upgrade La Louvière profile whith MeetingCommunes 4.1.x features.
  [odelaere]
