import path from 'path';
import * as vscode from 'vscode';
import fs from 'fs';

// Helper function to detect the preferred package manager
function getCommandSuffix(workspaceRoot: string): string {
    const poetryLockPath = path.join(workspaceRoot, 'poetry.lock');
    const uvLockPath = path.join(workspaceRoot, 'uv.lock');
    const pyprojectTomlPath = path.join(workspaceRoot, 'pyproject.toml');

    // 1. Check for Poetry (poetry.lock or [tool.poetry] in pyproject.toml)
    if (fs.existsSync(poetryLockPath)) {
        console.log(`[Kanna] Found poetry.lock in ${workspaceRoot}. Using Poetry.`);
        return 'poetry run kanna';
    }
    if (fs.existsSync(pyprojectTomlPath)) {
        try {
            const pyprojectContent = fs.readFileSync(pyprojectTomlPath, 'utf8');
            if (pyprojectContent.includes('[tool.poetry]')) {
                console.log(`[Kanna] Found [tool.poetry] in pyproject.toml in ${workspaceRoot}. Using Poetry.`);
                return 'poetry run kanna';
            }
        } catch (error) {
            console.error(`[Kanna] Error reading pyproject.toml: ${error}`);
            // Fall through to other checks if file read fails
        }
    }

    // 2. Check for UV (uv.lock)
    if (fs.existsSync(uvLockPath)) {
        console.log(`[Kanna] Found uv.lock in ${workspaceRoot}. Using UV.`);
        return 'uv run kanna';
    }
    // Note: UV typically uses `uv run` for executing commands within its environment.
    // It generally doesn't have a `[tool.uv]` section in pyproject.toml like Poetry.
    // `uv.lock` is the most reliable indicator for a uv-managed project.

    // 3. Fallback to plain Python
    console.log(`[Kanna] Neither Poetry nor UV detected in ${workspaceRoot}. Falling back to 'python -m kanna'.`);
    return 'python';
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Kanna Tasks extension is active!');

    let disposeRunCommand = vscode.commands.registerCommand('kanna.runTask', (taskName: string) => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('Kanna Tasks: No workspace folder open.');
            return;
        }

        const workspaceRoot = workspaceFolders[0].uri.fsPath; 
        
        const commandSuffix = getCommandSuffix(workspaceRoot);
        let command = `${commandSuffix} ${taskName}`
        
        console.log(`[Kanna] Executing command: ${command}`);

        const task = new vscode.Task(
            { type: 'kanna', task: taskName }, // Definition for the task (identifies it)
            vscode.TaskScope.Workspace, // Task scope (Workspace or Folder)
            `Kanna: ${taskName}`, // Task name
            'Kanna', // Source of the task
            new vscode.ShellExecution(command, { cwd: workspaceRoot }), // The actual command to run
            [] // Problem matchers (optional, for parsing build errors)
        );

        // Configure task presentation (optional)
        task.presentationOptions = {
            reveal: vscode.TaskRevealKind.Always,
            panel: vscode.TaskPanelKind.Shared,
            clear: true
        };

        vscode.tasks.executeTask(task);
        vscode.window.showInformationMessage(`Running Kanna task: ${taskName}`);
    });

    let disposePlanCommand = vscode.commands.registerCommand('kanna.planTask', (taskName: string) => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('Kanna Tasks: No workspace folder open.');
            return;
        }

        const workspaceRoot = workspaceFolders[0].uri.fsPath; 
        
        const commandSuffix = getCommandSuffix(workspaceRoot);
        let command = `${commandSuffix} ${taskName} --plan`
        
        console.log(`[Kanna] Executing command: ${command}`);

        const task = new vscode.Task(
            { type: 'kanna', task: taskName }, // Definition for the task (identifies it)
            vscode.TaskScope.Workspace, // Task scope (Workspace or Folder)
            `Kanna: ${taskName}`, // Task name
            'Kanna', // Source of the task
            new vscode.ShellExecution(command, { cwd: workspaceRoot }), // The actual command to run
            [] // Problem matchers (optional, for parsing build errors)
        );

        // Configure task presentation (optional)
        task.presentationOptions = {
            reveal: vscode.TaskRevealKind.Always,
            panel: vscode.TaskPanelKind.Shared,
            clear: true
        };

        vscode.tasks.executeTask(task);
        vscode.window.showInformationMessage(`Planning Kanna task: ${taskName}`);
    });

    // Register our CodeLens provider
    let disposableCodeLens = vscode.languages.registerCodeLensProvider(
        { language: 'toml', pattern: '**/pyproject.toml' }, // Selector matches pyproject.toml
        new KannaTasksCodeLensProvider()
    );

    context.subscriptions.push(disposeRunCommand, disposePlanCommand, disposableCodeLens);
}

export function deactivate() {
    console.log('Kanna Tasks extension is deactivated!');
}

class KannaTasksCodeLensProvider implements vscode.CodeLensProvider {
    // This method provides the CodeLens objects
    public provideCodeLenses(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens[]> {
        const codeLenses: vscode.CodeLens[] = [];
        const text = document.getText();
        
        // Regex to find [tool.kanna.tasks] section
        const tasksSectionRegex = /\[tool\.kanna\.tasks\]/;
        const tasksSectionMatch = text.match(tasksSectionRegex);

        if (!tasksSectionMatch || tasksSectionMatch.index === undefined) {
            return []; // No Kanna tasks section found
        }

        const tasksSectionStartLine = document.positionAt(tasksSectionMatch.index).line;

        // Regex to find task definitions within the tasks section
        // Matches lines like 'a = { command = "..." }' or 'my-task = "..."'
        // We look for a line starting with a word character or hyphen, followed by ' = '
        // We'll capture the task name.
        const taskDefinitionRegex = /^([\w-]+)\s*=\s*(?:\{|\")/gm; // Use global and multiline flags

        // Iterate through lines after the tasks section header
        for (let i = tasksSectionStartLine + 1; i < document.lineCount; i++) {
            const line = document.lineAt(i);
            // Stop if we hit another TOML section
            if (line.text.trim().startsWith('[') && i > tasksSectionStartLine + 1) {
                break;
            }

            const match = taskDefinitionRegex.exec(line.text);
            if (match) {
                const taskName = match[1]; // Captured task name
                const range = new vscode.Range(line.lineNumber, 0, line.lineNumber, line.text.length);

                // Create the CodeLens for the "Run Task" button
                codeLenses.push(
                    new vscode.CodeLens(range, {
                        title: `Run Task`,
                        command: 'kanna.runTask',
                        arguments: [taskName] // Pass the task name to our command handler
                    })
                );
                codeLenses.push(
                    new vscode.CodeLens(range, {
                        title: `Plan Task`,
                        command: 'kanna.planTask',
                        arguments: [taskName] // Pass the task name to our command handler
                    })
                );
            }
            // Reset regex lastIndex to ensure it works for subsequent lines (due to 'gm' flag)
            // This is crucial when exec() is used in a loop.
            if (taskDefinitionRegex.lastIndex > 0) {
                taskDefinitionRegex.lastIndex = 0;
            }
        }

        return codeLenses;
    }
}