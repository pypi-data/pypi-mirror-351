# 🤖 `git-ai-commit`

<a href="https://pypi.org/project/git-ai-commit"><img src="https://img.shields.io/pypi/v/git-ai-commit" alt="Current version"></a>
![PyPI - Downloads](https://img.shields.io/pypi/dm/git-ai-commit)

Tl;DR

- AI that writes your commit messages.

- A CLI and git hook that summarizes your changes every time you run `git commit`.

- Integrates with the [`pre-commit`](https://pre-commit.com/) framework, working alongside all your git hooks.

## 📺 Usage

![Usage Demo](assets/videos/ai-commit-msg.gif)

`git-ai-commit` currently support the following LLM providers...

- **Open AI**: `gpt-4o-mini`(default), `gpt-4`, `gpt-3.5`, and [more...](https://github.com/ming1in/ai-commit-msg/blob/a1e62be64c1f877bfa26c45d2d61508f94504ec0/ai_commit_msg/utils/models.py#L1)

- **Anthropic**: `claude-3-haiku`, `claude-3-sonnet`, `claude-3-opus`
  - [Wiki: Setup Anthropic Model](./wiki/anthropic.md)

- **Local Ollama**: `llama3`, `mistral`, `phi-3`, `gemma`, and [more..](https://github.com/ming1in/ai-commit-msg/blob/a1e62be64c1f877bfa26c45d2d61508f94504ec0/ai_commit_msg/utils/models.py#L1)
  - [Wiki: Using local Ollama LLM model](./wiki/ollama.md)

## 🚀 Getting Started

1. Install the `git-ai-commit` tool via pip

```bash
pip install git-ai-commit

git-ai-commit --version # verify installation
```

2. Start configuring your tool

```bash
git-ai-commit config --setup
```

3. Your done, happy committing! Check out our fun range of command, the LLM can even help you, just run...

```bash
git-ai-commit help-ai [question?]

# or get help the ol fashion way

git-ai-commit --help
```

## ⚡️ Quick Start: Setup Git Hook

To quickly setup your [`prepare-commit-msg`](<https://git-scm.com/docs/githooks#_prepare_commit_msg>) git hook, execute the command below.

Caution, this will override any existing `prepare-commit-msg` hooks you may have. To coordinate multiple git hook, check out the [`pre-commit`](https://pre-commit.com/) framework.

```bash
git-ai-commit hook --setup
```

That is all, your good to go! Now every time you run `git commit`, let AI present you with a commit message.

## 🪝 Integrate with `pre-commit` framework

`git-ai-commit` integrates easily with your other git hook using the `pre-commit` framework. Follow the instructions below to get set up.

1. Install the [`pre-commit`](https://pre-commit.com/) git hooks framework

```bash
brew install pre-commit
pre-commit --version 
```

2. Create a `.pre-commit-config.yaml` files and add the following config.

```bash
touch .pre-commit-config.yaml 
```

```yaml
# .pre-commit-config.yaml 

default_install_hook_types: 
  # make sure you include `prepare-commit-msg` in `default_install_hook_types`
  - prepare-commit-msg
repos:
  - repo: https://github.com/the-cafe/git-ai-commit
    rev: v1.0.13
    hooks:
    -   id: git-ai-commit
```

3. Based on the config above, install your `pre-commit` hook scripts.

```bash
pre-commit install 
```

4. Setup your OpenAI key, [see their docs for help](https://platform.openai.com/docs/quickstart).

```bash
git-ai-commit config --openai-key=...
```

## 🎯 Cursor IDE Integration

`git-ai-commit` integrates seamlessly with Cursor IDE to enhance your AI-powered development workflow. The tool works alongside Cursor's AI capabilities to provide consistent, high-quality commit messages.

### 📁 Setup `.cursorrules` Integration

Add git-ai-commit to your project's `.cursorrules` file to ensure Cursor always suggests using AI-generated commit messages:

```markdown
# Git AI Commit Integration

## Commit Workflow
When making commits, always use the `git-ai-commit` CLI tool instead of regular `git commit`. This tool automatically generates AI-powered commit messages based on your staged changes.

### Recommended Commands:
- Use `git-ai-commit` instead of `git commit` for AI-generated commit messages
- Use `git-ai-commit conventional` for conventional commit format
- Use `git-ai-commit summarize` to get a quick overview of changes before committing

### Workflow Integration:
- Before committing, stage your changes with `git add`
- Instead of `git commit -m "message"`, simply run `git-ai-commit`
- The tool will analyze your changes and suggest an appropriate commit message
```

### 💬 Example Cursor Prompts

Here are some effective prompts to use with Cursor when working with git-ai-commit:

**For committing changes:**
```
"I've made some changes to my code. Please stage the files and use git-ai-commit to generate an appropriate commit message."
```

**For conventional commits:**
```
"Stage my changes and use git-ai-commit conventional to create a conventional commit message for this feature/fix/refactor."
```

**For code review before committing:**
```
"Before committing, please run git-ai-commit summarize to show me what changes I've made, then proceed with the commit."
```

**For complete workflow:**
```
"Please help me commit my changes using this workflow: 1) Stage relevant files, 2) Use git-ai-commit to generate the message, 3) Review the commit message, 4) Push to the remote repository."
```

### 🔄 Recommended Workflow with Cursor

1. **Make your code changes** using Cursor's AI assistance
2. **Stage changes**: Ask Cursor to `git add` the relevant files
3. **Generate commit message**: Use `git-ai-commit` instead of manual commit messages
4. **Review and commit**: Let the AI analyze your changes and create descriptive commit messages
5. **Push changes**: Complete the workflow with `git push`

This integration ensures that both your code and commit messages maintain high quality and consistency throughout your development process.

### 🤖 For Claude AI Users

If you're using Claude or other AI assistants, check out our [`CLAUDE.md`](./CLAUDE.md) file for specific integration guidelines and workflow recommendations.

## 🛠️ CLI Commands & Options

✨ `git-ai-commit  config`

Display your current config settings. Option flags can be used to configure various settings in your configuration. For example...

```bash
git-ai-commit config

git-ai-commit config --openai-key=... --model=gpt-4o-mini
```
  
- `-k` `--openai-key`

  Set or update the OpenAI API key to access their GPT models.

- `-a` `--anthropic-key`

  Set or update the Anthropic API key to access their Claude models.

- `-m` `--model`

  *default:  "gpt-4o-mini"*

  Select a model to power our tool from our supported provider. To use a [Ollama](./wiki/ollama.md) model, prefix `ollama/<model>`.

- `-ou` `--ollama-url`

  *default:  "<http://localhost:11434/api/chat>"*

  Set the URL for interacting with your local Ollama models.

- `-s` `--setup`

  Config your git hook, model, and API keys via the NUX flow.

- `-l` `--logger`

  *default:  false*

  A toggle for enabling logs that are saved to a local file - `.git/ai_commit_message.log`. This was intended to be used as a local debug tool.

- `-r` `--reset`

  Resets your entire config settings to the default state. This will reset all settings, including API keys and model.

- `-p` `--prefix`

  Set a prefix for the generate commit messages.

- `-ml` `--max-length`

  Set the character limit for the LLM response. In our testing, the greater the limit the more details are included in the commit messages.

---

🔎 `git-ai-commit summarize`

Get a quick summary of your local changes

```bash
git-ai-commit summarize
```

- `-u` `--unstaged`

  Summarize your local *unstaged* changes.

- `-d` `--diff`

  Provide a .diff file from the local file system to summarize

---

🏷️ `git-ai-commit conventional`

Generate commit messages in the [Conventional Commits](https://www.conventionalcommits.org/) format (`type(scope): description`).

This command:
1. Analyzes your staged changes using AI
2. Suggests the most appropriate commit type based on your changes
3. Suggests a relevant scope based on the affected components
4. Allows you to accept the suggestions or choose your own
5. Formats the message according to conventional commit standards
6. Gives you the option to commit and push

Available commit types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

---

📌 `git-ai-commit  help`, `-h`

Displays a list of available command and options to help you setup our tool.

```bash
git-ai-commit help # -h
```

---
🪝 `git-ai-commit hook`

Manage and setup `git-ai-commit` as a [`prepare-commit-msg`](<https://git-scm.com/docs/githooks#_prepare_commit_msg>) git hook.

```bash
git-ai-commit hook --setup
```

- `-s` `--setup`

  Adds a git hook by generating a `.git/hooks/prepare-commit-msg` script in your git repo.

- `-sh` `--setup-husky`

  Integrate our hook into your [husky git hooks](https://typicode.github.io/husky/) by generating a `.husky/prepare-commit-msg` script in your git repo.

- `-r` `--remove`

  Removes the git hook.

- `-x` `--run`

  Executes the custom logic for our git hook. This option was intended to only run from the [`prepare-commit-msg`](https://git-scm.com/docs/githooks#_prepare_commit_msg) git hook.

## 🤝 Wanna Contribute?

Do you love our tool and wanna support us? Drop us a star 🌟

Have some feedback on what we could do better? [Create a issue](https://github.com/the-cafe/git-ai-commit/issues/new) we'll respond in 24hrs we promise 😄

Wanna contribute code and improve our product, check out our
[Local Development Wiki](./wiki/local_development.md) to get started.

Right now we're focused on

- Improving our prompting strategy to generate the best commit message possible

- Super charge our CLI to support broad developer use cases and build the best interface we can

- Build some tests

## 🎉 Fun Facts

- In this repository, every commit prefixed with `✨` was generated by AI.
