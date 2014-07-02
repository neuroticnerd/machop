MACHOP
======

summary
-------
automation tools for flake8 and testing of python code

goals
-----
- support manual running of tasks/task chains
- support timed (cron) running of tasks
- support file change running of tasks
- support task dependencies and file dependencies
- tasks are just functions
- each task receives info about what triggered it
- tasks return true/false to indicate success
- runner catches all exceptions in case task fails

requirements
------------
- Python 2.7
- watchdog
