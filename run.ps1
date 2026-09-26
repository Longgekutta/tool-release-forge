# PowerShell runner for tool-release-forge
param(
    [string]$Command = "health",
    [string]$Target = ".",
    [string]$Tag = "v0.1.0"
)

switch ($Command) {
    "setup"  { python main.py setup }
    "run"    { python main.py run --target $Target }
    "test"   { python main.py test }
    "health" { python main.py health }
    "clean"  { python main.py clean }
    "forge"  { python main.py forge --target $Target --tag $Tag }
    "notes"  { python main.py notes --target $Target --tag $Tag }
    Default  { python main.py $Command }
}
