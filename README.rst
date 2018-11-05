# module Homework

https://github.com/cvut/filabel/tree/modular

## Pypi
https://test.pypi.org/project/filabel-bezstpav/

## Module build

```
python setup.py bdist_wheel
python setup.py sdist
```



## Help

```
Usage: filabel.py [OPTIONS] [REPOSLUGS]...

  CLI tool for filename-pattern-based labeling of GitHub PRs

Options:
  -s, --state [open|closed|all]   Filter pulls by state.  [default: open]
  -d, --delete-old / -D, --no-delete-old
                                  Delete labels that do not match anymore.
                                  [default: True]
  -b, --base BRANCH               Filter pulls by base (PR target) branch
                                  name.
  -a, --config-auth FILENAME      File with authorization configuration.
                                  [required]
  -l, --config-labels FILENAME    File with labels configuration.  [required]
  --help                          Show this message and exit.
```

## Test respository

https://github.com/bezstpav/dummy

## Python webpage

http://paul94cz.pythonanywhere.com/

/ - get info
/[POST] - listening for webhook
/webhook [POST] - listening for webhook

## PIP Requirements

```
astroid==2.0.4
atomicwrites==1.2.1
attrs==18.2.0
autopep8==1.4
certifi==2018.8.24
chardet==3.0.4
Click==7.0
Flask==1.0.2
idna==2.7
isort==4.3.4
itsdangerous==0.24
Jinja2==2.10
lazy-object-proxy==1.3.1
MarkupSafe==1.0
mccabe==0.6.1
more-itertools==4.3.0
pluggy==0.7.1
py==1.6.0
pycodestyle==2.4.0
pylint==2.1.1
pytest==3.8.2
requests==2.19.1
six==1.11.0
typed-ast==1.1.0
urllib3==1.23
Werkzeug==0.14.1
wrapt==1.10.11
```

## Test result
```
=============================================================== test session starts ===============================================================
platform darwin -- Python 3.6.3, pytest-3.8.2, py-1.6.0, pluggy-0.7.1 -- /Users/paul/Documents/fit/mi-pyt/filabel/__venv__/bin/python3.6
cachedir: .pytest_cache
rootdir: /Users/paul/Documents/fit/mi-pyt/filabel, inifile:
collected 36 items                                                                                                                                

filabel/test/test_behavior.py::test_empty_labels PASSED                                                                                     [  2%]
filabel/test/test_behavior.py::test_404_repos PASSED                                                                                        [  5%]
filabel/test/test_behavior.py::test_foreign_repos PASSED                                                                                    [  8%]
filabel/test/test_behavior.py::test_abc_labels PASSED                                                                                       [ 11%]
filabel/test/test_behavior.py::test_abc_labels_again PASSED                                                                                 [ 13%]
filabel/test/test_behavior.py::test_nine_labels PASSED                                                                                      [ 16%]
filabel/test/test_behavior.py::test_empty_labels_wont_remove PASSED                                                                         [ 19%]
filabel/test/test_behavior.py::test_empty_globs_remove_disabled PASSED                                                                      [ 22%]
filabel/test/test_behavior.py::test_closed_prs_no_labels PASSED                                                                             [ 25%]
filabel/test/test_behavior.py::test_closed_prs_get_labels PASSED                                                                            [ 27%]
filabel/test/test_behavior.py::test_all_prs_get_labels PASSED                                                                               [ 30%]
filabel/test/test_behavior.py::test_master_base PASSED                                                                                      [ 33%]
filabel/test/test_behavior.py::test_custom_base PASSED                                                                                      [ 36%]
filabel/test/test_behavior.py::test_diffs PASSED                                                                                            [ 38%]
filabel/test/test_behavior.py::test_empty_globs PASSED                                                                                      [ 41%]
filabel/test/test_errors.py::test_no_config PASSED                                                                                          [ 44%]
filabel/test/test_errors.py::test_no_auth_config PASSED                                                                                     [ 47%]
filabel/test/test_errors.py::test_unusable_auth_config PASSED                                                                               [ 50%]
filabel/test/test_errors.py::test_no_labels_config PASSED                                                                                   [ 52%]
filabel/test/test_errors.py::test_unusable_labels_config PASSED                                                                             [ 55%]
filabel/test/test_errors.py::test_invalid_repolsug PASSED                                                                                   [ 58%]
filabel/test/test_errors.py::test_invalid_second_repolsug PASSED                                                                            [ 61%]
filabel/test/test_help.py::test_usage PASSED                                                                                                [ 63%]
filabel/test/test_help.py::test_description PASSED                                                                                          [ 66%]
filabel/test/test_help.py::test_state PASSED                                                                                                [ 69%]
filabel/test/test_help.py::test_delete_old PASSED                                                                                           [ 72%]
filabel/test/test_help.py::test_branch PASSED                                                                                               [ 75%]
filabel/test/test_help.py::test_config_auth PASSED                                                                                          [ 77%]
filabel/test/test_help.py::test_config_labels PASSED                                                                                        [ 80%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_empty PASSED                                                                 [ 83%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_add PASSED                                                                   [ 86%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_remove PASSED                                                                [ 88%]
filabel/test/test_web_smoke.py::test_app_imports PASSED                                                                                     [ 91%]
filabel/test/test_web_smoke.py::test_app_get_has_username PASSED                                                                            [ 94%]
filabel/test/test_web_smoke.py::test_ping_pongs PASSED                                                                                      [ 97%]
filabel/test/test_web_smoke.py::test_bad_secret PASSED                                                                                      [100%]

=========================================================== 36 passed in 288.68 seconds ===========================================================
```
