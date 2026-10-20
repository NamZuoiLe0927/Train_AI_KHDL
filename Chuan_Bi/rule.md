# Project Agent Rules

## 1. File Safety

The agent must NEVER delete any file or directory.

The agent must NEVER intentionally remove, destroy, or discard
existing project files.

The agent must NEVER use destructive commands to delete files
or directories.

Examples of prohibited commands include:

- del
- erase
- rd
- rmdir
- Remove-Item
- git clean
- git rm
- any equivalent destructive command

If a task appears to require deleting a file or directory:

1. STOP.
2. Explain why deletion appears necessary.
3. Ask the user for explicit confirmation.
4. Do not perform the deletion automatically.

---

## 2. Allowed File Operations

The agent MAY:

- Read existing files.
- Create new files.
- Modify existing files.
- Create new directories.
- Modify the project structure.
- Rename files only when explicitly requested by the user.
- Move files only when explicitly requested by the user.

The agent must preserve existing user data.

---

## 3. Modification Policy

Before modifying an existing file:

1. Read the file first.
2. Understand its current structure.
3. Make the smallest necessary change.
4. Preserve unrelated code and data.
5. Do not replace the entire file unless necessary.

Never delete and recreate a file simply because doing so is easier.

Prefer:

READ → ANALYZE → MODIFY → VERIFY

Never:

DELETE → RECREATE

---

## 4. Project Boundary

Only access files inside the current workspace/project.

Do not access files outside the project unless the user explicitly
authorizes the operation.

Do not access:

- Windows system files
- User personal files
- Other projects
- Browser profiles
- SSH keys
- Credentials
- Environment secrets

---

## 5. Terminal Safety

Do not execute destructive terminal commands.

Before executing a command that can modify or remove project data,
ask for user confirmation.

Commands that modify dependencies, system settings, environment
variables, permissions, or external resources require confirmation
unless explicitly authorized.

---

## 6. Git Safety

Do not execute destructive Git operations automatically.

Never run:

- git clean
- git reset --hard
- git rm
- git checkout -- <file>
- git restore <file>

without explicit user confirmation.

Safe inspection commands such as:

- git status
- git diff
- git log

are allowed.

---

## 7. Before Structural Changes

Before changing the project structure:

1. Inspect the current directory structure.
2. Identify affected files.
3. Explain the intended structural change.
4. Preserve existing files unless the user explicitly requests deletion.

---

## 8. User Confirmation

The following operations always require explicit confirmation:

- Deleting files
- Deleting directories
- Renaming files
- Moving files
- Replacing large portions of an existing project
- Destructive Git operations
- Modifying files outside the workspace
- Changing system configuration

---

## 9. Default Behavior

When uncertain about whether an operation may destroy data:

STOP and ASK.

Data preservation has priority over automation.