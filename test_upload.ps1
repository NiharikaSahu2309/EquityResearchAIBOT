# Test file upload endpoint
$filePath = "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\Stock data\indexData.csv"
$uri = "http://localhost:8081/upload/csv"

try {
    # Read file content
    $fileContent = Get-Content $filePath -Raw
    $fileName = Split-Path $filePath -Leaf
    
    # Create multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: text/csv",
        "",
        $fileContent,
        "--$boundary--",
        ""
    ) -join $LF
    
    # Make the request
    $response = Invoke-WebRequest -Uri $uri -Method POST -Body $bodyLines -ContentType "multipart/form-data; boundary=$boundary"
    
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Response: $($_.Exception.Response)"
}
