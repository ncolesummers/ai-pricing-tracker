# AI Pricing Tracker Custom Roles

This directory contains custom role definitions for use with Claude Code. These roles help transform Claude into specialized experts for different aspects of the AI Pricing Tracker project.

## Available Roles

- **deployment-specialist**: Expert in deploying applications and services to production environments
- **devops-engineer**: Specialist in development operations, CI/CD pipelines, and infrastructure automation
- **open-source-maintainer**: Expert in open source project management, community engagement, and contribution workflows
- **scraper**: AI Pricing Data Scraper Specialist - Expert in web scraping, data extraction, and processing for pricing data
- **security-specialist**: Expert in application security, secure coding practices, and vulnerability assessment
- **technical-writer**: Specialist in creating clear, concise, and comprehensive technical documentation
- **testing-specialist**: Expert in software testing methodologies, test automation, and quality assurance

## Usage

To use a project-specific role in Claude Code, type `/` followed by a few characters of the role name. Then select the appropriate role command with tab completion.

The format for using these roles is:

```
/project:role-name <task description>
```

For example:
```
/project:scraper extract pricing data from OpenAI's API documentation
```

You can easily discover available roles by typing `/project:` and using tab completion to see the list of available project-specific commands.

## Creating New Roles

To create a new role:

1. Add a new markdown file named after the role (e.g., `analyzer.md`)
2. Follow the structure of existing role files
3. Define the role's expertise, core responsibilities, task approach, and standards

Role priming is one of the most effective ways to improve Claude's performance on specialized tasks.