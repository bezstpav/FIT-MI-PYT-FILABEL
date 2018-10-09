# filabel Homework

https://github.com/cvut/filabel/tree/basic

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

## PIP Requirements

```
astroid==2.0.4
atomicwrites==1.2.1
attrs==18.2.0
autopep8==1.4
certifi==2018.8.24
chardet==3.0.4
Click==7.0
idna==2.7
isort==4.3.4
lazy-object-proxy==1.3.1
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
wrapt==1.10.11
```

## Test result
```
================================================================= test session starts ==================================================================
platform darwin -- Python 3.6.3, pytest-3.8.2, py-1.6.0, pluggy-0.7.1 -- /Users/paul/Documents/fit/mi-pyt/hw-filabel/__venv__/bin/python
cachedir: .pytest_cache
rootdir: /Users/paul/Documents/fit/mi-pyt/hw-filabel, inifile:
collected 32 items                                                                                                                                     

filabel/test/test_behavior.py::test_empty_labels PASSED                                                                                          [  3%]
filabel/test/test_behavior.py::test_404_repos PASSED                                                                                             [  6%]
filabel/test/test_behavior.py::test_foreign_repos PASSED                                                                                         [  9%]
filabel/test/test_behavior.py::test_abc_labels PASSED                                                                                            [ 12%]
filabel/test/test_behavior.py::test_abc_labels_again PASSED                                                                                      [ 15%]
filabel/test/test_behavior.py::test_nine_labels PASSED                                                                                           [ 18%]
filabel/test/test_behavior.py::test_empty_labels_wont_remove PASSED                                                                              [ 21%]
filabel/test/test_behavior.py::test_empty_globs_remove_disabled PASSED                                                                           [ 25%]
filabel/test/test_behavior.py::test_closed_prs_no_labels PASSED                                                                                  [ 28%]
filabel/test/test_behavior.py::test_closed_prs_get_labels PASSED                                                                                 [ 31%]
filabel/test/test_behavior.py::test_all_prs_get_labels PASSED                                                                                    [ 34%]
filabel/test/test_behavior.py::test_master_base PASSED                                                                                           [ 37%]
filabel/test/test_behavior.py::test_custom_base PASSED                                                                                           [ 40%]
filabel/test/test_behavior.py::test_diffs PASSED                                                                                                 [ 43%]
filabel/test/test_behavior.py::test_empty_globs PASSED                                                                                           [ 46%]
filabel/test/test_errors.py::test_no_config PASSED                                                                                               [ 50%]
filabel/test/test_errors.py::test_no_auth_config PASSED                                                                                          [ 53%]
filabel/test/test_errors.py::test_unusable_auth_config PASSED                                                                                    [ 56%]
filabel/test/test_errors.py::test_no_labels_config PASSED                                                                                        [ 59%]
filabel/test/test_errors.py::test_unusable_labels_config PASSED                                                                                  [ 62%]
filabel/test/test_errors.py::test_invalid_repolsug PASSED                                                                                        [ 65%]
filabel/test/test_errors.py::test_invalid_second_repolsug PASSED                                                                                 [ 68%]
filabel/test/test_help.py::test_usage PASSED                                                                                                     [ 71%]
filabel/test/test_help.py::test_description PASSED                                                                                               [ 75%]
filabel/test/test_help.py::test_state PASSED                                                                                                     [ 78%]
filabel/test/test_help.py::test_delete_old PASSED                                                                                                [ 81%]
filabel/test/test_help.py::test_branch PASSED                                                                                                    [ 84%]
filabel/test/test_help.py::test_config_auth PASSED                                                                                               [ 87%]
filabel/test/test_help.py::test_config_labels PASSED                                                                                             [ 90%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_empty PASSED                                                                      [ 93%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_add PASSED                                                                        [ 96%]
filabel/test/test_radioactive_waste.py::test_radioactive_waste_remove PASSED                                                                     [100%]

============================================================= 32 passed in 272.51 seconds ==============================================================

```
