Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.0 (2025-05-27)
------------------

Breaking changes:


- Fix interpretation logic of conditions that was wrong in few case (e.g. AND, OR, AND) (URB-3154)


New features:


- Allow additional delay to be a TAL expression
  [mpeeters] (URB-3005)
- Add debug functionality
  [mpeeters] (URB-3070)


Internal:


- Black
  [mpeeters] (SUP-27104)
- Fix tests
  [mpeeters] (URB-3005)


2.2.2 (2024-04-25)
------------------

New features:


- Allow additional delay to be a TAL expression
  [mpeeters] (URB-3005)


Internal:


- Black
  [mpeeters] (SUP-27104)
- Fix tests
  [mpeeters] (URB-3005)


2.2.1 (2024-04-10)
------------------

- Fix object deserializer
  [jchandelle]


2.2.0 (2024-03-30)
------------------

- URB-3005: Add a deserializer for objects that also handle vocabulary specificities
  [mpeeters]

- URB-3005: Add converters for schedule objects
  [mpeeters]


2.1.0 (2023-12-26)
------------------

- Underline close due dates [URB-2515]
  [ndemonte]


2.0.2 (2023-09-01)
------------------

- Add specificity to upgradestep check [URB-2868]
  [jchandelle]


2.0.1 (2023-08-01)
------------------

- Fix order of upgrade steps [URB-2627]
  [mpeeters]


2.0.0 (2023-07-03)
------------------

- Migrate to use `collective.eeafaceted.collectionwidget` [URB-2627]
  [mpeeters]


1.9.0 (2023-07-03)
------------------

- URB-1537 - Change collection column name
  [jchandelle]


1.8 (2023-04-06)
----------------

- Allow multiple interfaces to be registered on schedule config.
  [sdelcourt]

- Get tasks and subtasks attribute exploration rather than catalog.
  [sdelcourt]

- Add method 'get_closed_tasks' on TaskConfig.
  [sdelcourt]

- Add util method 'end_all_open_tasks' of a container.
  [sdelcourt]


1.6 (2018-08-30)
----------------

- Only display active tasks in the collection widget.
  [sdelcourt]


1.5 (2017-06-20)
----------------

- Bugfix for dashboard collection creation.
  [sdelcourt]


1.4 (2017-06-20)
----------------

- Register title colums for default dashboard collection of schedule config.
  [sdelcourt]


1.3 (2017-06-20)
----------------

- Recreate dashboard collection 'all' if its missing.
  [sdelcourt]


1.2 (2017-06-16)
----------------

- Implement an adapter for extra holidays
  [mpeeters]


1.1 (2017-04-28)
----------------

- Release on internal egge server.

- Update the compute_due_date method to handle working days
  [mpeeters]

- Add a class to manage working days for date calculation
  [mpeeters]

- Handle working days for additional delay
  [mpeeters]


1.0 (2017-04-28)
----------------

- Initial release.
  [sdelcourt]
