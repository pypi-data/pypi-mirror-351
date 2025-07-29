# Security Scanning Guide

This document provides guidance on security scanning tools integrated into the openssl_encrypt project development workflow.

## Local Development Scanning

We use pre-commit hooks to run security checks before code is committed. This helps catch security issues early in the development process.

### Setting Up Pre-commit Hooks

1. Install pre-commit:

```bash
pip install pre-commit
```

2. Install the git hooks:

```bash
cd /path/to/openssl_encrypt
pre-commit install
```

This will install all the hooks defined in `.pre-commit-config.yaml`.

### Available Security Checks

The following security checks are included in the pre-commit configuration:

#### 1. Bandit

[Bandit](https://github.com/PyCQA/bandit) is a tool designed to find common security issues in Python code, such as:

- Use of weak cryptographic algorithms
- Hard-coded passwords and secret keys
- SQL injection vulnerabilities
- Command injection vulnerabilities
- Use of unsafe functions and modules

Configuration is in `.bandit.yaml`.

#### 2. pip-audit

[pip-audit](https://github.com/pypa/pip-audit) checks your installed dependencies against a database of known vulnerabilities. It is maintained by Google and provides reliable vulnerability scanning. It will:

- Scan the requirements files
- Compare against the Python security advisory database using the PyPI advisory database and OSV
- Block commits that would introduce known vulnerable dependencies
- Work reliably without requiring login or API keys

### Running Checks Manually

You can run the checks without committing:

```bash
pre-commit run --all-files
```

Or run specific checkers:

```bash
pre-commit run bandit --all-files
pre-commit run pip-audit --all-files
```

## Interpreting Results

### Bandit Results

Bandit reports are presented in the following format:

```
>> Issue: [B506:yaml_load] Use of unsafe yaml load. Allows instantiation of arbitrary objects.
   Severity: Medium   Confidence: High
   Location: filename.py:123:4
   More Info: https://bandit.readthedocs.io/en/latest/plugins/b506_yaml_load.html
```

Each issue includes:
- Issue ID and description
- Severity (Low/Medium/High)
- Confidence (Low/Medium/High)
- File location
- Link to more information

### pip-audit Results

pip-audit reports vulnerable dependencies with details:

```
Found 1 known vulnerability in 1 package
cryptography 44.0.3: PYSEC-2024-XXXX - CVE-2024-XXXXX: Vulnerability description
  Vulnerable versions: <45.0.0
  Fixed versions: >=45.0.0
```

When used with JSON output, it provides more detailed structured information:

```json
[
  {
    "name": "cryptography",
    "version": "44.0.3",
    "vulnerabilities": [
      {
        "id": "PYSEC-2024-XXXX",
        "description": "Detailed vulnerability description...",
        "fix_versions": ["45.0.0"],
        "cve_id": "CVE-2024-XXXXX"
      }
    ]
  }
]
```

## Responding to Findings

### Severity Guidelines

Follow these guidelines when addressing security issues:

- **High Severity**: Must be fixed immediately before committing
- **Medium Severity**: Should be fixed before committing, or documented with justification if not fixed
- **Low Severity**: Should be reviewed and addressed when practical

### False Positives

If you believe a finding is a false positive:

1. Document your reasoning in a comment near the code in question
2. If appropriate, update the configuration to exclude the specific false positive
3. Never ignore security warnings without proper documentation

Example comment for a justified exception:

```python
# bandit: disable=B101
# Justification: This use of assert is in a test file and not in production code
assert result == expected, "Test failed"
```

## Regular Security Reviews

In addition to automated scanning, perform regular security reviews:

1. Quarterly dependency vulnerability scanning
2. Manual code reviews with security focus
3. Update the security tools to the latest versions

## Additional Security Tools

Besides the pre-commit hooks, we recommend:

1. [pyre-check](https://github.com/facebook/pyre-check) - Type checking that can detect some security issues
2. [pysa](https://github.com/facebook/pyre-check/tree/main/pysa) - Static analysis for Python security issues

## Security Reporting

If you discover a security vulnerability, please follow our [Security Policy](SECURITY.md) for responsible disclosure.