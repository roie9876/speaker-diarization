# Pre-Push Checklist for Speaker Diarization Project

Use this checklist before pushing to GitHub to ensure everything is ready.

## ✅ Configuration Files

- [x] `.gitignore` - Excludes sensitive files and build artifacts
- [x] `.env.example` - Template for environment variables
- [x] `requirements.txt` - Python dependencies
- [x] `.python-version` - Python version specification
- [x] `pyproject.toml` - Project metadata and tool configuration
- [x] `LICENSE` - MIT License
- [x] `setup.sh` - Automated setup script

## ✅ Documentation

- [x] `README.md` - Project overview and quick start
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `CHANGELOG.md` - Version history
- [x] `docs/` - Complete documentation suite (12 files)
- [x] `.github/copilot-instructions.md` - AI-assisted development guide

## ✅ Project Structure

- [x] `src/` - Source code directory with `__init__.py` files
- [x] `data/` - Data directories with `.gitkeep` files
- [x] `tests/` - Test directory structure
- [x] `logs/` - Logs directory with `.gitkeep`

## 🔒 Before First Push - Security Check

### ⚠️ IMPORTANT: Verify these items

1. **No sensitive data committed**
   ```bash
   # Check for API keys, tokens, or passwords
   git grep -i "api.key\|token\|password\|secret" || echo "✓ No sensitive data found"
   ```

2. **No .env file in git**
   ```bash
   # Verify .env is gitignored
   git check-ignore .env && echo "✓ .env is properly ignored" || echo "❌ WARNING: .env not ignored!"
   ```

3. **No large files**
   ```bash
   # Check for large files (audio files, models)
   find . -type f -size +10M -not -path "./.git/*" -not -path "./venv/*" || echo "✓ No large files"
   ```

## 📋 Pre-Push Commands

Run these commands before pushing:

```bash
# 1. Initialize git repository (if not done)
git init

# 2. Check what will be committed
git status

# 3. Stage all files
git add .

# 4. Verify nothing sensitive is staged
git diff --cached --name-only

# 5. Create initial commit
git commit -m "Initial commit: Project setup with complete documentation"

# 6. Create repository on GitHub (via web interface)
# Then add remote and push:
git remote add origin https://github.com/yourusername/speaker-diarization.git
git branch -M main
git push -u origin main
```

## 🔍 Final Verification

After pushing, check on GitHub:

- [ ] README.md displays correctly on homepage
- [ ] Documentation is accessible in `docs/` directory
- [ ] `.github/copilot-instructions.md` is present
- [ ] No sensitive files visible
- [ ] LICENSE is recognized by GitHub
- [ ] All directories have proper structure

## 📌 Post-Push Setup (for collaborators)

When others clone your repository, they should:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/speaker-diarization.git
cd speaker-diarization

# 2. Run setup script
./setup.sh

# 3. Configure environment
# Edit .env with their API keys
```

## 🎯 Repository Settings (on GitHub)

After creating the repository, configure:

1. **About section**:
   - Description: "Speaker Diarization & Selective Transcription using Azure Speech Service"
   - Topics: `python`, `azure`, `speech-recognition`, `speaker-diarization`, `streamlit`, `pyannote`

2. **Settings**:
   - Enable Issues
   - Enable Discussions (optional)
   - Set branch protection for `main` (recommended)

3. **Secrets** (if using GitHub Actions):
   - Add `AZURE_SPEECH_KEY`
   - Add `HUGGING_FACE_HUB_TOKEN`

---

## ✅ All Set!

Your project is now ready to push to GitHub! 🚀

**What's included**:
- Complete documentation (12 MD files, ~30,000 words)
- Project structure with proper organization
- Configuration files for development
- Security-hardened `.gitignore`
- MIT License
- Contributing guidelines
- Automated setup script
- GitHub Copilot integration

**What's NOT included** (properly gitignored):
- API keys and tokens (.env)
- Virtual environment (venv/)
- Cache files and build artifacts
- User-specific data
- Large audio files
