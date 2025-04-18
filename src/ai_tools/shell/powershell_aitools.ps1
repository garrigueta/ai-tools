# PowerShell integration script for AI-Tools
# This provides Windows equivalent functionality to the bash_aitools script

# Define the aitools command based on installed package
$AITOOLS_CMD = "aitools"

# Create an alias similar to bash's 'mop'
function global:mop {
    & $AITOOLS_CMD @args
}

# Check if Ollama is running and print a warning if not
function global:Check-Ollama {
    try {
        $ollama_host = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { "localhost" }
        $ollama_port = if ($env:OLLAMA_PORT) { $env:OLLAMA_PORT } else { "11434" }
        $response = Invoke-WebRequest -Uri "http://${ollama_host}:${ollama_port}/api/tags" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            return $true
        }
    }
    catch {
        Write-Host "⚠️  Warning: Ollama server appears to be offline at ${ollama_host}:${ollama_port}" -ForegroundColor Yellow
        Write-Host "    Please start Ollama or check your connection settings." -ForegroundColor Yellow
        return $false
    }
    return $false
}

# Check if the specified model is available
function global:Check-Model {
    if (Check-Ollama) {
        $ollama_host = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { "localhost" }
        $ollama_port = if ($env:OLLAMA_PORT) { $env:OLLAMA_PORT } else { "11434" }
        $ollama_model = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "gemma3:27b" }
        
        try {
            $response = Invoke-WebRequest -Uri "http://${ollama_host}:${ollama_port}/api/tags" -UseBasicParsing
            $models = $response.Content | ConvertFrom-Json
            
            $model_found = $false
            foreach ($model in $models.models) {
                if ($model.name -eq $ollama_model) {
                    $model_found = $true
                    break
                }
            }
            
            if (-not $model_found) {
                Write-Host "⚠️  Warning: Model '$ollama_model' not found in available models." -ForegroundColor Yellow
                Write-Host "    Available models:" -ForegroundColor Yellow
                foreach ($model in $models.models) {
                    Write-Host "    - $($model.name)" -ForegroundColor Cyan
                }
                return $false
            }
        }
        catch {
            Write-Host "⚠️  Error checking models: $_" -ForegroundColor Red
            return $false
        }
    }
    else {
        return $false
    }
    return $true
}

# Function to check which models are available
function global:Check-Models {
    if (Check-Ollama) {
        $ollama_host = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { "localhost" }
        $ollama_port = if ($env:OLLAMA_PORT) { $env:OLLAMA_PORT } else { "11434" }
        $ollama_model = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "gemma3:27b" }
        
        try {
            $response = Invoke-WebRequest -Uri "http://${ollama_host}:${ollama_port}/api/tags" -UseBasicParsing
            $models = $response.Content | ConvertFrom-Json
            
            Write-Host "📊 Available Ollama models:" -ForegroundColor Cyan
            foreach ($model in $models.models) {
                Write-Host "    - $($model.name)" -ForegroundColor Cyan
            }
            
            $model_found = $false
            foreach ($model in $models.models) {
                if ($model.name -eq $ollama_model) {
                    $model_found = $true
                    break
                }
            }
            
            if (-not $model_found) {
                Write-Host "❓ Your current model ($ollama_model) is not in the list. Consider changing OLLAMA_MODEL." -ForegroundColor Yellow
            }
            else {
                Write-Host "✅ Your current model ($ollama_model) is available." -ForegroundColor Green
            }
        }
        catch {
            Write-Host "⚠️  Error checking models: $_" -ForegroundColor Red
        }
    }
}

# Function to test the Ollama setup with a simple prompt
function global:Test-Ollama {
    if (Check-Ollama -and Check-Model) {
        Write-Host "🔍 Testing Ollama with a simple prompt..." -ForegroundColor Cyan
        & $AITOOLS_CMD prompt "Hello, are you working correctly? Please respond with a very brief message."
        Write-Host "✅ Test complete." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Cannot test: Ollama setup is incomplete or incorrect." -ForegroundColor Red
    }
}

# Add initialization function to check everything on startup
function global:Initialize-OllamaTools {
    Write-Host "🤖 Initializing Ollama tools..." -ForegroundColor Cyan
    Check-Ollama | Out-Null
    Check-Model | Out-Null
    
    # Check if the aitools command exists
    try {
        Get-Command $AITOOLS_CMD -ErrorAction Stop | Out-Null
        Write-Host "✅ aitools command found" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Warning: aitools command not found." -ForegroundColor Yellow
        Write-Host "    Please check your installation and ensure aitools is in your PATH." -ForegroundColor Yellow
    }
    
    Write-Host "🤖 Ollama tools setup complete." -ForegroundColor Cyan
}

# Error handling function similar to the bash trap
# This needs to be used at the end of commands or in a wrapper script
function global:Handle-CommandError {
    param (
        [string]$Command,
        [int]$ExitCode
    )
    
    # Skip if this is an aitools command itself
    if ($Command -like "*$AITOOLS_CMD*" -or $Command -like "*mop*") {
        return
    }
    
    Write-Host "🤖 Oops! `"$Command`" failed with exit code $ExitCode." -ForegroundColor Red
    
    # Check if command is available
    try {
        Get-Command $AITOOLS_CMD -ErrorAction Stop | Out-Null
    }
    catch {
        Write-Host "🤖 Error: The aitools command is not found." -ForegroundColor Red
        Write-Host "    Please check your installation and make sure the package is installed correctly." -ForegroundColor Yellow
        return
    }
    
    # Only run error analysis if Ollama is available
    if (Check-Ollama) {
        Write-Host "🤖 Analyzing error..." -ForegroundColor Cyan
        
        # Properly quote the command and error message to avoid parsing issues
        $QuotedCommand = $Command -replace '"', '\"'
        $ErrorMsg = "Command failed with exit code $ExitCode"
        
        # Call aitools to analyze the error
        & $AITOOLS_CMD error "$QuotedCommand" "$ErrorMsg"
    }
    else {
        Write-Host "⚠️  Cannot analyze error: Ollama server is not available." -ForegroundColor Yellow
    }
    
    Write-Host "🤖 Please try again." -ForegroundColor Cyan
}

# Create a wrapper for PowerShell command execution to enable error handling
function global:Invoke-WithErrorHandling {
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [scriptblock]$ScriptBlock
    )
    
    $command = $ScriptBlock.ToString()
    
    try {
        & $ScriptBlock
        if (-not $?) {
            $exitCode = if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 }
            Handle-CommandError -Command $command -ExitCode $exitCode
        }
    }
    catch {
        Handle-CommandError -Command $command -ExitCode 1
        Write-Host "Error details: $_" -ForegroundColor Red
    }
}

# Define a shortened command for the error handling wrapper
function global:iweh {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
        [string[]]$Command
    )
    
    $commandString = $Command -join " "
    $scriptBlock = [scriptblock]::Create($commandString)
    Invoke-WithErrorHandling $scriptBlock
}

Write-Host "AI-Tools PowerShell integration loaded! Use 'mop' as a shorthand for 'aitools'" -ForegroundColor Green
Write-Host "Use 'iweh' to run commands with error handling, e.g.: iweh { npm install }" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  Check-Ollama         - Check if Ollama is running" -ForegroundColor Cyan
Write-Host "  Check-Model          - Check if your model is available" -ForegroundColor Cyan
Write-Host "  Check-Models         - List all available models" -ForegroundColor Cyan
Write-Host "  Test-Ollama          - Test Ollama with a simple prompt" -ForegroundColor Cyan
Write-Host "  Initialize-OllamaTools - Initialize and check Ollama setup" -ForegroundColor Cyan