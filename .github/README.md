# GitHub Configuration

This directory contains GitHub-specific configuration files for the project.

## Files

### `copilot-instructions.md`

**Purpose**: Provides context and instructions to GitHub Copilot for code generation.

**How it works**:
- GitHub Copilot **automatically reads** this file when working in this repository
- It uses the instructions to provide better, project-specific code suggestions
- The file should be updated as the project evolves

**When to update**:
- ✅ After completing major implementation phases
- ✅ When architecture decisions change
- ✅ When adding new technologies or patterns
- ✅ When common issues/solutions are discovered
- ✅ After learning what works/doesn't work

**Usage**:
- Copilot reads this automatically - no action needed
- Reference it explicitly: `@.github/copilot-instructions.md implement the DiarizationService`
- Keep it focused on **implementation** details, not design discussions

**Current Status**: 
- 📝 Initial version created
- 🎯 Ready for Phase 1 implementation (Core Services)

---

### Future Files (may be added later)

- `workflows/` - GitHub Actions CI/CD pipelines
- `CODEOWNERS` - Code ownership rules
- `ISSUE_TEMPLATE/` - Issue templates for bug reports, features
- `PULL_REQUEST_TEMPLATE.md` - PR template

---

**Last Updated**: October 21, 2025  
**Maintained By**: Development Team
