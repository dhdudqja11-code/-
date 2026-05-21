param(
    [string]$Prompt = "Hello from PowerShell",
    [string]$Model = "text-bison-001",
    [int]$MaxOutputTokens = 512,
    [double]$Temperature = 0.2
)

# Obtain an access token using Application Default Credentials (gcloud)
$token = & gcloud auth application-default print-access-token 2>$null
if (-not $token) {
    Write-Error "gcloud authentication failed. Run 'gcloud auth application-default login' first."
    exit 1
}

$uri = "https://generativemodels.googleapis.com/v1/models/$Model:generateText"

$body = @{
    prompt = @{ text = $Prompt }
    maxOutputTokens = $MaxOutputTokens
    temperature = $Temperature
} | ConvertTo-Json -Depth 5

try {
    $resp = Invoke-RestMethod -Method Post -Uri $uri -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } -Body $body
    if ($resp) {
        # Try to print common response fields
        if ($resp.candidates) {
            $resp.candidates | ForEach-Object { $_.content }
        } elseif ($resp.output) {
            # some APIs return output.text
            if ($resp.output[0].content) { $resp.output[0].content }
            elseif ($resp.output[0].text) { $resp.output[0].text }
        } else {
            $resp | ConvertTo-Json -Depth 4
        }
    } else {
        Write-Error "No response received."
    }
} catch {
    Write-Error "Request failed: $_"
    exit 1
}
