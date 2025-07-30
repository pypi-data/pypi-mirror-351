# Security Policy

## Supported Versions

We provide security updates for the following versions of LLM List:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security issues seriously and appreciate your efforts to responsibly disclose your findings. To report a security issue, please follow these steps:

1. **Do not** create a public GitHub issue for security vulnerabilities.
2. Email your findings to [security@yourdomain.com](mailto:security@yourdomain.com).
3. Include a clear description of the vulnerability, steps to reproduce, and any potential impact.
4. We will acknowledge your email within 48 hours and provide a more detailed response within 72 hours.
5. After the issue has been fixed, we will publish a security advisory on GitHub.

### What We Consider a Security Vulnerability

- Remote code execution
- Authentication bypass
- Data exposure or leakage
- Privilege escalation
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Server-side request forgery (SSRF)
- SQL injection
- XML external entity (XXE) injection
- Insecure deserialization
- Security misconfigurations with security implications

### Out of Scope

- Clickjacking on pages with no sensitive actions
- CSRF on forms that are available to anonymous users
- Missing security headers which do not lead to a vulnerability
- Self-XSS
- Issues that require physical access to the victim's device
- Issues that require social engineering
- Issues that require root or administrator access to the target system
- Theoretical issues without proof of exploitability

## Security Updates

When security vulnerabilities are reported, we will:

1. Acknowledge the report and investigate the issue.
2. Develop a fix and test it thoroughly.
3. Release a new version with the security fix.
4. Publish a security advisory with details about the vulnerability and the fix.

We recommend always using the latest version of LLM List to ensure you have all security updates.

## Security Best Practices

To enhance the security of your LLM List installation:

1. Keep your Python environment and dependencies up to date.
2. Run LLM List with the minimum required permissions.
3. Use strong, unique passwords for any authentication mechanisms.
4. Regularly audit your LLM List installation for unauthorized changes.
5. Keep your operating system and server software updated.

## Responsible Disclosure Timeline

We are committed to addressing security issues in a timely manner:

- Time to first response: 48 hours
- Time to triage: 3 business days
- Time to patch: Depends on the severity and complexity
- Public disclosure: After a patch is available and users have had time to update

## Credits

We appreciate the security researchers and users who help us keep LLM List secure by responsibly disclosing vulnerabilities. Contributors will be credited in the security advisory unless they prefer to remain anonymous.
