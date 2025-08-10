# Django Deployment Script for thecied.dev
# Usage: .\deploy-simple.ps1

Write-Host "Starting deployment to thecied.dev..." -ForegroundColor Green

# Step 1: Push changes to GitHub
Write-Host "Pushing changes to GitHub..." -ForegroundColor Yellow
git add .

$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrEmpty($commitMessage)) {
    $commitMessage = "Deploy changes - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git commit -m $commitMessage
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git push failed. Trying master branch..." -ForegroundColor Yellow
    git push origin master
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git push failed. Please check your changes and try again." -ForegroundColor Red
        exit 1
    }
}

# Step 2: Deploy to server
Write-Host "Deploying to server..." -ForegroundColor Yellow
ssh -i "C:\Users\BenAn\Downloads\LightSailDjango.pem" bitnami@98.87.71.5 "/home/bitnami/deploy.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Your site is live at: https://thecied.dev" -ForegroundColor Cyan
    Write-Host "Alternative URL: https://www.thecied.dev" -ForegroundColor Cyan
} else {
    Write-Host "Deployment failed. Check the logs above." -ForegroundColor Red
}

Write-Host "Done!" -ForegroundColor Green
